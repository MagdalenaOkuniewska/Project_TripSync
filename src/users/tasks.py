from celery import shared_task
from django.core.mail import send_mail


@shared_task(
    bind=True,
)
def send_invite_email(self, user_email, activation_link):
    try:
        email_subject = "Confirm Registration"

        send_mail(
            email_subject,
            message=f"Click the link to activate your account {activation_link}",
            from_email="noreply@tripsync.com",
            recipient_list=[user_email],
        )
    except Exception as e:
        raise self.retry(exc=e, countdown=5)
