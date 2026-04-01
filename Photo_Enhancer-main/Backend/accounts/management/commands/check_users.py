from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from datetime import datetime

class Command(BaseCommand):
    help = 'Check all stored user credentials in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Check specific user by username'
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify credentials by attempting authentication'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        verify = options.get('verify')

        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('User Credentials Database Check'))
        self.stdout.write(self.style.SUCCESS('='*70))

        if username:
            # Check specific user
            try:
                user = User.objects.get(username=username)
                self._display_user(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found in database'))
        else:
            # List all users
            users = User.objects.all()
            if not users.exists():
                self.stdout.write(self.style.WARNING('No users found in database'))
                return

            self.stdout.write(f'\nTotal Users: {users.count()}\n')
            for i, user in enumerate(users, 1):
                self._display_user(user, index=i)

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))

    def _display_user(self, user, index=None):
        """Display user information"""
        prefix = f'{index}. ' if index else ''
        
        self.stdout.write(self.style.SUCCESS(f'\n{prefix}User Details:'))
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Full Name: {user.get_full_name() or "Not set"}')
        self.stdout.write(f'  Active: {user.is_active}')
        self.stdout.write(f'  Staff: {user.is_staff}')
        self.stdout.write(f'  Superuser: {user.is_superuser}')
        self.stdout.write(f'  Last Login: {user.last_login or "Never"}')
        self.stdout.write(f'  Created: {user.date_joined}')

        # Check if profile exists
        try:
            profile = user.profile
            self.stdout.write(self.style.SUCCESS(f'\n  Profile Details:'))
            self.stdout.write(f'    Verified: {profile.is_verified}')
            self.stdout.write(f'    Profile Picture: {"Yes" if profile.profile_picture else "No"}')
            self.stdout.write(f'    Bio: {profile.bio[:50] + "..." if profile.bio else "Not set"}')
            self.stdout.write(f'    Profile Created: {profile.created_at}')
            self.stdout.write(f'    Profile Updated: {profile.updated_at}')
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.WARNING('  Profile: Not created'))

        # Display password hash (for verification)
        self.stdout.write(self.style.WARNING(f'\n  Password Hash (first 40 chars): {user.password[:40]}...'))
