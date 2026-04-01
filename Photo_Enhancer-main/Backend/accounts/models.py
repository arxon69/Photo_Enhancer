from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import os


# =============================================================================
# USER PROFILE MODEL
# =============================================================================

class UserProfile(models.Model):
    """Extended user profile model to store additional user information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# =============================================================================
# USER SUBSCRIPTION MODEL
# =============================================================================

class UserSubscription(models.Model):
    """Track user subscription tiers and limits"""
    
    class Tier(models.TextChoices):
        FREE = 'free', 'Free'
        STARTER = 'starter', 'Starter'
        PRO = 'pro', 'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'
    
    TIER_LIMITS = {
        'free': {'photos_per_month': 5, 'max_resolution': '1080p', 'features': ['basic']},
        'starter': {'photos_per_month': 25, 'max_resolution': '1080p', 'features': ['basic', 'smart_crop']},
        'pro': {'photos_per_month': float('inf'), 'max_resolution': '4k', 'features': ['all']},
        'enterprise': {'photos_per_month': float('inf'), 'max_resolution': '8k', 'features': ['all', 'api']},
    }
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.FREE)
    
    # Subscription period
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    photos_used_this_month = models.PositiveIntegerField(default=0)
    photos_reset_at = models.DateTimeField(default=timezone.now)
    
    # Billing
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.tier}"
    
    def get_photos_remaining(self):
        """Returns remaining photos for this month"""
        limit = self.TIER_LIMITS[self.tier]['photos_per_month']
        if limit == float('inf'):
            return float('inf')
        return max(0, limit - self.photos_used_this_month)
    
    def can_process_photo(self):
        """Check if user can process another photo"""
        # Reset counter if month has passed
        if timezone.now() > self.photos_reset_at.replace(month=self.photos_reset_at.month + 1):
            self.photos_used_this_month = 0
            self.photos_reset_at = timezone.now()
            self.save()
        
        remaining = self.get_photos_remaining()
        return remaining > 0 or remaining == float('inf')
    
    def increment_usage(self):
        """Increment photo usage counter"""
        self.photos_used_this_month += 1
        self.save(update_fields=['photos_used_this_month'])
    
    def get_max_resolution(self):
        """Get max resolution for user's tier"""
        return self.TIER_LIMITS[self.tier]['max_resolution']
    
    def has_feature(self, feature):
        """Check if user has access to a specific feature"""
        features = self.TIER_LIMITS[self.tier]['features']
        return feature in features or 'all' in features


# =============================================================================
# PHOTO MODELS
# =============================================================================

def photo_upload_path(instance, filename):
    """Generate unique upload path for photos"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', str(instance.user.id), filename)


def enhanced_photo_path(instance, filename):
    """Generate path for enhanced photos"""
    ext = filename.split('.')[-1]
    filename = f"enhanced_{uuid.uuid4()}.{ext}"
    return os.path.join('enhanced', str(instance.user.id), filename)


class Photo(models.Model):
    """Model to store user uploaded photos and their enhanced versions"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    
    # Original photo
    original = models.ImageField(upload_to=photo_upload_path)
    original_width = models.PositiveIntegerField(null=True, blank=True)
    original_height = models.PositiveIntegerField(null=True, blank=True)
    original_file_size = models.PositiveBigIntegerField(null=True, blank=True)
    
    # Enhanced photo
    enhanced = models.ImageField(upload_to=enhanced_photo_path, null=True, blank=True)
    enhanced_width = models.PositiveIntegerField(null=True, blank=True)
    enhanced_height = models.PositiveIntegerField(null=True, blank=True)
    enhanced_file_size = models.PositiveBigIntegerField(null=True, blank=True)
    
    # Processing info
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Enhancement settings
    enhancement_settings = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['uuid']),
        ]
    
    def __str__(self):
        return f"Photo {self.uuid} by {self.user.username}"
    
    def delete(self, soft=True, *args, **kwargs):
        """Soft delete by default"""
        if soft:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])
        else:
            # Hard delete - remove files
            if self.original:
                self.original.delete(save=False)
            if self.enhanced:
                self.enhanced.delete(save=False)
            super().delete(*args, **kwargs)
    
    def start_processing(self):
        """Mark photo as processing"""
        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.save(update_fields=['status', 'processing_started_at', 'updated_at'])
    
    def complete_processing(self, enhanced_file):
        """Mark photo as completed"""
        from PIL import Image
        
        self.enhanced = enhanced_file
        self.status = self.Status.COMPLETED
        self.processing_completed_at = timezone.now()
        
        if self.processing_started_at:
            self.processing_duration = self.processing_completed_at - self.processing_started_at
        
        # Get enhanced image dimensions
        if self.enhanced:
            try:
                img = Image.open(self.enhanced.path)
                self.enhanced_width, self.enhanced_height = img.size
                self.enhanced_file_size = os.path.getsize(self.enhanced.path)
            except Exception:
                pass
        
        self.save(update_fields=[
            'enhanced', 'status', 'processing_completed_at',
            'processing_duration', 'enhanced_width', 'enhanced_height',
            'enhanced_file_size'
        ])
    
    def fail_processing(self, error_message):
        """Mark photo as failed"""
        self.status = self.Status.FAILED
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
    
    def save(self, *args, **kwargs):
        """Extract metadata on save"""
        if self.original:
            from PIL import Image
            try:
                img = Image.open(self.original.path)
                self.original_width, self.original_height = img.size
                self.original_file_size = os.path.getsize(self.original.path)
            except Exception:
                pass
        super().save(*args, **kwargs)


class PhotoProcessingJob(models.Model):
    """Track async photo processing jobs"""
    
    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE, related_name='job')
    celery_task_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    priority = models.PositiveSmallIntegerField(default=5)  # 1 = highest, 10 = lowest
    retry_count = models.PositiveSmallIntegerField(default=0)
    max_retries = models.PositiveSmallIntegerField(default=3)
    last_retry_at = models.DateTimeField(null=True, blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['celery_task_id']),
        ]


# =============================================================================
# SIGNALS - Automatically create connected objects when User is created
# =============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        UserSubscription.objects.get_or_create(user=instance)
