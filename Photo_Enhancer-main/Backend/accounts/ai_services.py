"""
AI Enhancer API Services for PhotoEnhancer
Integrates Remove.bg and Deep-Image.ai APIs
"""

import os
import requests
from typing import Optional, Dict, Any
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
import logging

logger = logging.getLogger('accounts')


class RemoveBgService:
    """
    Service for Remove.bg API - Background Removal
    API Docs: https://www.remove.bg/
    """
    
    # ============================================
    # CONFIGURE THESE IN settings.py OR .env
    # API_KEY: 'REMOVE_BG_API_KEY'
    # ============================================
    API_KEY = getattr(settings, 'REMOVE_BG_API_KEY', '')
    BASE_URL = 'https://api.remove.bg/v1.0'
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if API key is configured"""
        return bool(cls.API_KEY and cls.API_KEY not in ['', 'your-remove-bg-api-key'])
    
    @classmethod
    def remove_background(cls, image_bytes: bytes, size: str = 'auto', 
                          bg_color: Optional[str] = None,
                          bg_image_url: Optional[str] = None) -> Optional[BytesIO]:
        """
        Remove background from image using Remove.bg API
        
        Args:
            image_bytes: Raw image data
            size: Output size ('auto', 'preview', 'small', 'regular', 'full')
            bg_color: Background color (e.g., 'FFFFFF', 'blue')
            bg_image_url: URL of background image to replace with
            
        Returns:
            BytesIO with processed image or None if failed
        """
        if not cls.is_configured():
            logger.warning("Remove.bg API key not configured")
            return None
        
        try:
            files = {'image_file': ('image.jpg', image_bytes, 'image/jpeg')}
            
            data = {
                'size': size,
                'type': 'auto',  # product, person, auto
            }
            
            # Optional parameters
            if bg_color:
                data['bg_color'] = bg_color
            if bg_image_url:
                data['bg_image_url'] = bg_image_url
            
            headers = {
                'X-Api-Key': cls.API_KEY,
            }
            
            logger.info("Sending request to Remove.bg API")
            
            response = requests.post(
                f"{cls.BASE_URL}/removebg",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return BytesIO(response.content)
            else:
                logger.error(f"Remove.bg API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Remove.bg API timeout")
            return None
        except Exception as e:
            logger.error(f"Remove.bg service error: {str(e)}")
            return None
    
    @classmethod
    def get_account_info(cls) -> Dict[str, Any]:
        """Get account credits and info"""
        if not cls.is_configured():
            return {'error': 'API key not configured'}
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/account",
                headers={'X-Api-Key': self.API_KEY},
                timeout=10
            )
            return response.json() if response.status_code == 200 else {'error': response.text}
        except Exception as e:
            return {'error': str(e)}


class DeepImageService:
    """
    Service for Deep-image.ai API - Photo Enhancement
    API Docs: https://deep-image.ai/
    """
    
    # ============================================
    # CONFIGURE THESE IN settings.py OR .env
    # API_KEY: 'DEEP_IMAGE_API_KEY'
    # ============================================
    API_KEY = getattr(settings, 'DEEP_IMAGE_API_KEY', '')
    BASE_URL = 'https://api.deep-image.ai/v1'
    
    # Enhancement presets
    PRESETS = {
        'enhance': 'general_enhance',      # General enhancement
        'colorize': 'colorize',             # Colorize black & white
        'denoise': 'denoise',               # Remove noise
        'upscale_2x': 'upscale_2x',         # 2x upscale
        'upscale_4x': 'upscale_4x',         # 4x upscale
        'upscale_8x': 'upscale_8x',         # 8x upscale
        'hdr': 'hdr',                       # HDR effect
        'portrait': 'portrait_enhance',   # Portrait enhancement
        'night': 'night_enhance',           # Night photo enhancement
        'color_enhance': 'color_enhance',  # Color enhancement
        'sharp_enhance': 'sharp_enhance',  # Sharpness enhancement
    }
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if API key is configured"""
        return bool(cls.API_KEY and cls.API_KEY not in ['', 'your-deep-image-api-key'])
    
    @classmethod
    def enhance_photo(cls, image_bytes: bytes, preset: str = 'enhance',
                     width: Optional[int] = None,
                     height: Optional[int] = None) -> Optional[BytesIO]:
        """
        Enhance photo using Deep-image.ai API
        
        Args:
            image_bytes: Raw image data
            preset: Enhancement preset (see PRESETS)
            width: Target width (optional)
            height: Target height (optional)
            
        Returns:
            BytesIO with enhanced image or None if failed
        """
        if not cls.is_configured():
            logger.warning("Deep-image.ai API key not configured")
            return None
        
        try:
            headers = {
                'x-api-key': cls.API_KEY,
                'Content-Type': 'application/octet-stream',
            }
            
            # Get preset name
            preset_key = cls.PRESETS.get(preset, 'general_enhance')
            
            params = {
                'preset': preset_key,
            }
            
            # Optional dimensions
            if width:
                params['width'] = width
            if height:
                params['height'] = height
            
            logger.info(f"Sending request to Deep-image.ai API with preset: {preset_key}")
            
            response = requests.post(
                f"{cls.BASE_URL}/generation/enhance",
                params=params,
                headers=headers,
                data=image_bytes,
                timeout=120  # Larger timeout for AI processing
            )
            
            if response.status_code == 200:
                return BytesIO(response.content)
            else:
                logger.error(f"Deep-image.ai API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Deep-image.ai API timeout")
            return None
        except Exception as e:
            logger.error(f"Deep-image.ai service error: {str(e)}")
            return None
    
    @classmethod
    def enhance_photo_async(cls, image_bytes: bytes, preset: str = 'enhance') -> Optional[str]:
        """
        Async enhancement - returns job ID to poll for results
        
        Args:
            image_bytes: Raw image data
            preset: Enhancement preset
            
        Returns:
            Job ID string or None
        """
        if not cls.is_configured():
            logger.warning("Deep-image.ai API key not configured")
            return None
        
        try:
            headers = {
                'x-api-key': cls.API_KEY,
                'Content-Type': 'application/octet-stream',
            }
            
            preset_key = cls.PRESETS.get(preset, 'general_enhance')
            
            logger.info(f"Starting async enhancement: {preset_key}")
            
            response = requests.post(
                f"{cls.BASE_URL}/generation/enhance/async",
                params={'preset': preset_key},
                headers=headers,
                data=image_bytes,
                timeout=60
            )
            
            if response.status_code == 202:
                data = response.json()
                job_id = data.get('job_id')
                logger.info(f"Deep-image async job started: {job_id}")
                return job_id
            else:
                logger.error(f"Deep-image async start error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Deep-image async error: {str(e)}")
            return None
    
    @classmethod
    def check_async_status(cls, job_id: str) -> Dict[str, Any]:
        """
        Check status of async job
        
        Returns:
            Dict with 'status', 'url' (if completed), 'error'
        """
        if not cls.is_configured():
            return {'status': 'error', 'message': 'API not configured'}
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/generation/enhance/async/{job_id}",
                headers={'x-api-key': cls.API_KEY},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': data.get('status'),  # pending, processing, completed, failed
                    'url': data.get('output_url'),
                    'progress': data.get('progress', 0)
                }
            else:
                return {'status': 'error', 'message': response.text}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def get_available_presets(cls) -> list:
        """Return list of available enhancement presets"""
        return [
            {'key': key, 'name': key.replace('_', ' ').title()}
            for key in cls.PRESETS.keys()
        ]


class AIEnhancerConfig:
    """
    Configuration helper for AI Enhancer services
    Check which services are available
    """
    
    @classmethod
    def get_available_services(cls) -> Dict[str, bool]:
        """Get which AI services are configured"""
        return {
            'remove_bg': RemoveBgService.is_configured(),
            'deep_image': DeepImageService.is_configured(),
        }
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate configuration and return list of issues"""
        issues = []
        
        if not RemoveBgService.is_configured():
            issues.append("Remove.bg API key not configured (settings.REMOVE_BG_API_KEY)")
        
        if not DeepImageService.is_configured():
            issues.append("Deep-image.ai API key not configured (settings.DEEP_IMAGE_API_KEY)")
        
        return issues


# Legacy function for compatibility
def enhance_with_removebg(image_path: str) -> Optional[BytesIO]:
    """Legacy wrapper for Remove.bg service"""
    with open(image_path, 'rb') as f:
        return RemoveBgService.remove_background(f.read())


def enhance_with_deepimage(image_path: str, preset: str = 'enhance') -> Optional[BytesIO]:
    """Legacy wrapper for Deep-image service"""
    with open(image_path, 'rb') as f:
        return DeepImageService.enhance_photo(f.read(), preset=preset)
