from .models import Notification


def count_unread_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
    else:
        notifications = 0
    return {"unread_notifications_count": notifications}
