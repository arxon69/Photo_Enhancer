from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ('profile_picture', 'bio', 'is_verified', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name')
    list_filter = ('is_active', 'date_joined')
    readonly_fields = ('date_joined', 'last_login')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
