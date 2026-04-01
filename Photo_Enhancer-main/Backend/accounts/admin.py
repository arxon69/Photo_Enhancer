from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, Photo, PhotoProcessingJob, UserSubscription


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ('profile_picture', 'bio', 'is_verified', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class UserSubscriptionInline(admin.StackedInline):
    model = UserSubscription
    can_delete = False
    verbose_name_plural = 'Subscription'
    fields = ('tier', 'is_active', 'current_period_end', 'photos_used_this_month')
    readonly_fields = ('photos_used_this_month',)
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline, UserSubscriptionInline)
    list_display = ('username', 'email', 'first_name', 'is_active', 'get_tier', 'is_verified', 'date_joined', 'get_photos_count')
    list_display_links = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'profile__is_verified', 'subscription__tier')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_tier(self, obj):
        try:
            return obj.subscription.tier
        except UserSubscription.DoesNotExist:
            return 'free'
    get_tier.short_description = 'Tier'
    get_tier.admin_order_field = 'subscription__tier'
    
    def is_verified(self, obj):
        try:
            return obj.profile.is_verified
        except UserProfile.DoesNotExist:
            return False
    is_verified.boolean = True
    is_verified.short_description = 'Verified'
    is_verified.admin_order_field = 'profile__is_verified'
    
    def get_photos_count(self, obj):
        return obj.photos.filter(is_deleted=False).count()
    get_photos_count.short_description = 'Photos'


# Register User models
if User in admin.site._registry:
    admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Register UserProfile separately for direct access
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at', 'updated_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'status', 'original_resolution', 'enhanced_resolution', 'processing_duration_display', 'created_at')
    list_filter = ('status', 'is_deleted', 'created_at')
    search_fields = ('uuid', 'user__username', 'user__email', 'error_message')
    readonly_fields = ('uuid', 'original_resolution', 'enhanced_resolution', 'processing_duration', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def original_resolution(self, obj):
        if obj.original_width and obj.original_height:
            return f"{obj.original_width}x{obj.original_height}"
        return "-"
    original_resolution.short_description = 'Original'
    
    def enhanced_resolution(self, obj):
        if obj.enhanced_width and obj.enhanced_height:
            return f"{obj.enhanced_width}x{obj.enhanced_height}"
        return "-"
    enhanced_resolution.short_description = 'Enhanced'
    
    def processing_duration_display(self, obj):
        if obj.processing_duration:
            return f"{obj.processing_duration.total_seconds():.1f}s"
        return "-"
    processing_duration_display.short_description = 'Duration'
    
    actions = ['reprocess_photos', 'soft_delete_photos']
    
    def reprocess_photos(self, request, queryset):
        from .tasks import process_photo
        for photo in queryset.filter(status__in=['pending', 'failed']):
            process_photo.delay(photo.id)
        self.message_user(request, f"Queued {queryset.count()} photos for reprocessing")
    reprocess_photos.short_description = "Reprocess selected photos"
    
    def soft_delete_photos(self, request, queryset):
        for photo in queryset:
            photo.delete(soft=True)
        self.message_user(request, f"Soft deleted {queryset.count()} photos")
    soft_delete_photos.short_description = "Soft delete selected photos"


@admin.register(PhotoProcessingJob)
class PhotoProcessingJobAdmin(admin.ModelAdmin):
    list_display = ('photo', 'status', 'priority', 'retry_count', 'created_at', 'completed_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('photo__uuid', 'celery_task_id')
    readonly_fields = ('created_at', 'started_at', 'completed_at')
    raw_id_fields = ('photo',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'is_active', 'photos_used_this_month', 'current_period_end', 'created_at')
    list_filter = ('tier', 'is_active', 'cancel_at_period_end', 'created_at')
    search_fields = ('user__username', 'user__email', 'stripe_customer_id', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at', 'photos_used_this_month')
    date_hierarchy = 'created_at'
    
    actions = ['upgrade_to_pro', 'reset_usage']
    
    def upgrade_to_pro(self, request, queryset):
        queryset.update(tier=UserSubscription.Tier.PRO)
        self.message_user(request, f"Upgraded {queryset.count()} users to Pro")
    upgrade_to_pro.short_description = "Upgrade to Pro"
    
    def reset_usage(self, request, queryset):
        from django.utils import timezone
        queryset.update(photos_used_this_month=0, photos_reset_at=timezone.now())
        self.message_user(request, f"Reset usage for {queryset.count()} users")
    reset_usage.short_description = "Reset monthly usage"
