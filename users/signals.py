from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone


# ------------------------------------------------------------------
# 1. Auto-create UserProfile when a new User is registered
# ------------------------------------------------------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from users.models import UserProfile
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ------------------------------------------------------------------
# 2. Update WaterDailySummary when WaterLog changes
# ------------------------------------------------------------------

def _refresh_water_summary(user, date):
    from nutrition.models import WaterLog, WaterDailySummary

    total = WaterLog.objects.filter(
        user=user, log_date=date
    ).aggregate(total=Sum('amount_ml'))['total'] or 0

    goal = 2000
    if hasattr(user, 'profile'):
        goal = user.profile.daily_water_goal_ml

    WaterDailySummary.objects.update_or_create(
        user=user,
        date=date,
        defaults={
            'total_ml':     total,
            'goal_ml':      goal,
            'goal_reached': total >= goal,
        },
    )


def on_water_log_save(sender, instance, **kwargs):
    _refresh_water_summary(instance.user, instance.log_date)


def on_water_log_delete(sender, instance, **kwargs):
    _refresh_water_summary(instance.user, instance.log_date)