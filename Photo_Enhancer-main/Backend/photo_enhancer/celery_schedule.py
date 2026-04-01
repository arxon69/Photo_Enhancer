"""PhotoEnhancer - Celery Schedule Configuration"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Run cleanup daily at 2 AM
    'cleanup-deleted-photos-daily': {
        'task': 'accounts.tasks.cleanup_deleted_photos',
        'schedule': crontab(hour=2, minute=0),
    },
    # Reset monthly usage on the 1st of each month at 1 AM
    'reset-monthly-usage': {
        'task': 'accounts.tasks.reset_monthly_usage',
        'schedule': crontab(hour=1, minute=0, day_of_month=1),
    },
    # Optimize storage weekly on Sunday at 3 AM
    'optimize-storage-weekly': {
        'task': 'accounts.tasks.optimize_storage',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
}
