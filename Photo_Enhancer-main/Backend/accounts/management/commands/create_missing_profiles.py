from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for any users that are missing one'

    def handle(self, *args, **options):
        users = User.objects.all()
        count = 0

        for user in users:
            try:
                # Try to access profile
                _ = user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                UserProfile.objects.create(user=user)
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for user: {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal profiles created: {count}')
        )
