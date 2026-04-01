import os
import time
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.files import File
from .models import Photo, PhotoProcessingJob
from .ai_services import RemoveBgService, DeepImageService
import logging

logger = logging.getLogger('accounts')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_photo(self, photo_id):
    """
    Celery task to process/enhance a photo.
    Supports both Remove.bg and Deep-image.ai APIs
    """
    try:
        photo = Photo.objects.select_related('user').get(id=photo_id)
        
        if photo.status == Photo.Status.PROCESSING:
            return
        
        photo.start_processing()
        
        job, _ = PhotoProcessingJob.objects.get_or_create(
            photo=photo,
            defaults={'celery_task_id': self.request.id}
        )
        job.status = PhotoProcessingJob.Status.PROCESSING
        job.celery_task_id = self.request.id
        job.started_at = time.time()
        job.save()
        
        # Get enhancement type from settings
        enhancement_type = photo.enhancement_settings.get('type', 'enhance')
        preset = photo.enhancement_settings.get('preset', 'enhance')
        
        # Read original image
        with photo.original.open('rb') as f:
            image_bytes = f.read()
        
        try:
            result_image = None
            service_used = None
            
            # Route to appropriate service
            if enhancement_type == 'remove_bg':
                # ============================================
                # REMOVE.BG API INTEGRATION
                # ============================================
                logger.info(f"Processing photo {photo_id} with Remove.bg API")
                
                if not RemoveBgService.is_configured():
                    raise Exception("Remove.bg API key not configured. Please add REMOVE_BG_API_KEY to settings.")
                
                bg_color = photo.enhancement_settings.get('bg_color')
                result_image = RemoveBgService.remove_background(
                    image_bytes,
                    bg_color=bg_color
                )
                service_used = 'remove_bg'
                
            elif enhancement_type == 'enhance':
                # ============================================
                # DEEP-IMAGE.AI API INTEGRATION
                # ============================================
                logger.info(f"Processing photo {photo_id} with Deep-image.ai API - preset: {preset}")
                
                if not DeepImageService.is_configured():
                    raise Exception("Deep-image.ai API key not configured. Please add DEEP_IMAGE_API_KEY to settings.")
                
                # Check user's tier for upscale limits
                max_preset = 'upscale_4x'  # default
                if hasattr(photo.user, 'subscription'):
                    max_resolution = photo.user.subscription.get_max_resolution()
                    if max_resolution == '1080p':
                        max_preset = 'upscale_2x'
                    elif max_resolution == '4k':
                        max_preset = 'upscale_4x'
                    elif max_resolution == '8k':
                        max_preset = 'upscale_8x'
                
                # Limit upscale based on tier
                if preset.startswith('upscale_') and preset > max_preset:
                    preset = max_preset
                    logger.info(f"Limited preset to {preset} based on subscription tier")
                
                result_image = DeepImageService.enhance_photo(
                    image_bytes,
                    preset=preset
                )
                service_used = 'deep_image'
                
            elif enhancement_type == 'both':
                # First remove background, then enhance
                logger.info(f"Processing photo {photo_id} with both services")
                
                if not RemoveBgService.is_configured():
                    raise Exception("Remove.bg API not configured")
                if not DeepImageService.is_configured():
                    raise Exception("Deep-image.ai API not configured")
                
                # Step 1: Remove background
                intermediate = RemoveBgService.remove_background(image_bytes)
                if not intermediate:
                    raise Exception("Remove.bg processing failed")
                
                # Step 2: Enhance
                result_image = DeepImageService.enhance_photo(
                    intermediate.getvalue(),
                    preset='enhance'
                )
                service_used = 'both'
            
            else:
                # Fallback to basic PIL enhancement if no API
                logger.warning(f"Unknown enhancement type: {enhancement_type}, using fallback")
                result_image = _fallback_enhancement(image_bytes, preset)
                service_used = 'fallback'
            
            if result_image:
                # Save enhanced image
                filename = f"enhanced_{photo.uuid}.png" if enhancement_type == 'remove_bg' else f"enhanced_{photo.uuid}.jpg"
                photo.complete_processing(File(result_image, name=filename))
                
                # Update job
                job.status = PhotoProcessingJob.Status.COMPLETED
                job.completed_at = time.time()
                job.error_details = {'service_used': service_used}
                job.save()
                
                # Update user's photo count
                if hasattr(photo.user, 'subscription'):
                    photo.user.subscription.increment_usage()
                
                logger.info(f"Photo {photo_id} processed successfully using {service_used}")
                
                return {
                    'status': 'completed',
                    'photo_id': photo_id,
                    'service': service_used
                }
            else:
                raise Exception(f"{service_used.capitalize()} processing failed - no output")
                
        except Exception as e:
            # Mark as failed
            error_msg = str(e)
            photo.fail_processing(error_msg)
            
            # Update job
            job.status = PhotoProcessingJob.Status.FAILED
            job.error_details = {
                'error': error_msg,
                'service': enhancement_type,
                'traceback': str(self.request)
            }
            job.save()
            
            logger.error(f"Photo {photo_id} processing failed: {error_msg}")
            
            # Retry if needed
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.last_retry_at = time.time()
                job.status = PhotoProcessingJob.Status.QUEUED
                job.save()
                raise self.retry(exc=e, countdown=60 * job.retry_count)
            
            raise
            
    except Photo.DoesNotExist:
        logger.error(f"Photo {photo_id} not found")
        return {'status': 'error', 'message': 'Photo not found'}
    except MaxRetriesExceededError:
        logger.error(f"Photo {photo_id} max retries exceeded")
        return {'status': 'failed', 'message': 'Max retries exceeded'}
    except Exception as e:
        logger.error(f"Photo {photo_id} unexpected error: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def _fallback_enhancement(image_bytes: bytes, preset: str):
    """
    Fallback enhancement using Pillow when APIs are not available
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import io
        
        img = Image.open(io.BytesIO(image_bytes))
        
        # Apply basic enhancements
        if preset == 'enhance' or preset == 'general_enhance':
            # Brightness
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
            # Contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            # Sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.3)
            # Color
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
        
        elif preset == 'upscale_2x':
            new_size = (int(img.width * 2), int(img.height * 2))
            img = img.resize(new_size, Image.LANCZOS)
        
        elif preset == 'denoise':
            img = img.filter(ImageFilter.MedianFilter(size=3))
        
        # Save to buffer
        output = io.BytesIO()
        img_format = img.format or 'JPEG'
        img.save(output, format=img_format, quality=95)
        output.seek(0)
        
        return output
        
    except Exception as e:
        logger.error(f"Fallback enhancement failed: {str(e)}")
        return None


@shared_task
def process_removebg_photo(photo_id: int, bg_color: str = None):
    """
    Dedicated task for Remove.bg processing
    Can be called directly for background removal
    """
    try:
        photo = Photo.objects.get(id=photo_id)
        
        if not RemoveBgService.is_configured():
            photo.fail_processing("Remove.bg API not configured")
            return {'status': 'error', 'message': 'API not configured'}
        
        with photo.original.open('rb') as f:
            image_bytes = f.read()
        
        result = RemoveBgService.remove_background(image_bytes, bg_color=bg_color)
        
        if result:
            filename = f"removebg_{photo.uuid}.png"
            photo.complete_processing(File(result, name=filename))
            return {'status': 'completed', 'photo_id': photo_id}
        else:
            photo.fail_processing("Remove.bg processing failed")
            return {'status': 'failed', 'photo_id': photo_id}
            
    except Photo.DoesNotExist:
        return {'status': 'error', 'message': 'Photo not found'}


@shared_task
def process_deepimage_photo(photo_id: int, preset: str = 'enhance'):
    """
    Dedicated task for Deep-image.ai processing
    Can be called directly for enhancement
    """
    try:
        photo = Photo.objects.get(id=photo_id)
        
        if not DeepImageService.is_configured():
            photo.fail_processing("Deep-image.ai API not configured")
            return {'status': 'error', 'message': 'API not configured'}
        
        with photo.original.open('rb') as f:
            image_bytes = f.read()
        
        result = DeepImageService.enhance_photo(image_bytes, preset=preset)
        
        if result:
            filename = f"enhanced_{photo.uuid}.jpg"
            photo.complete_processing(File(result, name=filename))
            return {'status': 'completed', 'photo_id': photo_id, 'preset': preset}
        else:
            photo.fail_processing("Deep-image enhancement failed")
            return {'status': 'failed', 'photo_id': photo_id}
            
    except Photo.DoesNotExist:
        return {'status': 'error', 'message': 'Photo not found'}


# =============================================================================
# MAINTENANCE TASKS
# =============================================================================

@shared_task
def cleanup_deleted_photos():
    """Periodic task to hard delete soft-deleted photos older than 30 days"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    old_photos = Photo.objects.filter(is_deleted=True, deleted_at__lt=cutoff_date)
    
    count = 0
    for photo in old_photos:
        try:
            photo.delete(soft=False)
            count += 1
        except Exception as e:
            logger.error(f"Error deleting photo {photo.id}: {str(e)}")
    
    logger.info(f"Cleaned up {count} old photos")
    return {'deleted': count}


@shared_task
def reset_monthly_usage():
    """Periodic task to reset monthly photo usage counters"""
    from django.utils import timezone
    from .models import UserSubscription
    
    subscriptions = UserSubscription.objects.all()
    count = subscriptions.update(photos_used_this_month=0, photos_reset_at=timezone.now())
    
    logger.info(f"Reset usage for {count} users")
    return {'reset': count}


@shared_task
def optimize_storage():
    """Optimize storage by compressing old photos"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=90)
    old_photos = Photo.objects.filter(
        status=Photo.Status.COMPLETED,
        created_at__lt=cutoff_date,
        is_deleted=False
    ).select_related('user')
    
    logger.info(f"Storage optimization: {old_photos.count()} old photos")
    return {'optimized': 0, 'total_old': old_photos.count()}


@shared_task
def check_ai_service_status():
    """Check which AI services are available"""
    from .ai_services import AIEnhancerConfig
    
    services = AIEnhancerConfig.get_available_services()
    issues = AIEnhancerConfig.validate_config()
    
    if issues:
        logger.warning(f"AI Service configuration issues: {issues}")
    else:
        logger.info("All AI services are configured and ready")
    
    return {'services': services, 'issues': issues}
