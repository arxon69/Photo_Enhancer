import os
import time
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.files import File
from .models import Photo, PhotoProcessingJob


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_photo(self, photo_id):
    """
    Celery task to process/enhance a photo.
    This runs asynchronously to avoid blocking the web server.
    """
    try:
        # Get photo
        photo = Photo.objects.select_related('user').get(id=photo_id)
        
        # Skip if already processing
        if photo.status == Photo.Status.PROCESSING:
            return
        
        # Mark as processing
        photo.start_processing()
        
        # Update job status
        job, _ = PhotoProcessingJob.objects.get_or_create(
            photo=photo,
            defaults={'celery_task_id': self.request.id}
        )
        job.status = PhotoProcessingJob.Status.PROCESSING
        job.celery_task_id = self.request.id
        job.started_at = time.time()
        job.save()
        
        try:
            # Import AI libraries here to avoid import overhead
            from PIL import Image, ImageEnhance, ImageFilter
            
            # Simulate processing (replace with actual AI model)
            time.sleep(2)  # Simulate AI processing
            
            # Load original image
            img = Image.open(photo.original.path)
            
            # Apply enhancements based on settings
            enhancements = photo.enhancement_settings or {}
            
            # Apply enhancements
            if enhancements.get('brightness', False):
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.2)
            
            if enhancements.get('contrast', False):
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)
            
            if enhancements.get('sharpness', False):
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.3)
            
            if enhancements.get('color', False):
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.1)
            
            if enhancements.get('denoise', False):
                img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # Apply upscale if specified
            upscale_factor = enhancements.get('upscale', 1)
            if upscale_factor > 1:
                new_size = (int(img.width * upscale_factor), int(img.height * upscale_factor))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Save enhanced image
            import io
            output = io.BytesIO()
            img_format = img.format or 'JPEG'
            img.save(output, format=img_format, quality=95)
            output.seek(0)
            
            # Save to Photo model
            filename = os.path.basename(photo.original.name)
            photo.complete_processing(File(output, name=f"enhanced_{filename}"))
            
            # Update job status
            job.status = PhotoProcessingJob.Status.COMPLETED
            job.completed_at = time.time()
            job.save()
            
            # Update user's photo count
            if hasattr(photo.user, 'subscription'):
                photo.user.subscription.increment_usage()
            
            return {'status': 'completed', 'photo_id': photo_id}
            
        except Exception as e:
            # Mark as failed
            photo.fail_processing(str(e))
            
            # Update job
            job.status = PhotoProcessingJob.Status.FAILED
            job.error_details = {'error': str(e), 'traceback': str(self.request)}
            job.save()
            
            # Retry if needed
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.last_retry_at = time.time()
                job.status = PhotoProcessingJob.Status.QUEUED
                job.save()
                raise self.retry(exc=e, countdown=60 * job.retry_count)
            
            raise
            
    except Photo.DoesNotExist:
        return {'status': 'error', 'message': 'Photo not found'}
    except MaxRetriesExceededError:
        return {'status': 'failed', 'message': 'Max retries exceeded'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def cleanup_deleted_photos():
    """
    Periodic task to hard delete soft-deleted photos older than 30 days.
    Run daily via Celery beat.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    old_photos = Photo.objects.filter(is_deleted=True, deleted_at__lt=cutoff_date)
    
    count = 0
    for photo in old_photos:
        photo.delete(soft=False)
        count += 1
    
    return {'deleted': count}


@shared_task
def reset_monthly_usage():
    """
    Periodic task to reset monthly photo usage counters.
    Run on the 1st of each month via Celery beat.
    """
    from django.utils import timezone
    from .models import UserSubscription
    
    subscriptions = UserSubscription.objects.all()
    count = subscriptions.update(photos_used_this_month=0, photos_reset_at=timezone.now())
    
    return {'reset': count}


@shared_task
def optimize_storage():
    """
    Optimize storage by compressing old photos or moving to cold storage.
    Run weekly via Celery beat.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Photos older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    old_photos = Photo.objects.filter(
        status=Photo.Status.COMPLETED,
        created_at__lt=cutoff_date,
        is_deleted=False
    ).select_related('user')
    
    optimized = 0
    # Add compression logic here if needed
    
    return {'optimized': optimized, 'total_old': old_photos.count()}
