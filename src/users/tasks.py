from celery import shared_task
from django.core.mail import send_mail


def send_activation_email(user_email, activation_link):
    email_subject = "Confirm Registration"

    send_mail(
        email_subject,
        message=f"Click the link to activate your account {activation_link}",
        from_email="noreply@tripsync.com",
        recipient_list=[user_email],
    )


@shared_task(
    bind=True,
)
def send_activation_email_async(self, user_email, activation_link):
    try:
        send_activation_email(user_email, activation_link)
    except Exception as e:  # noqa: BLE001
        raise self.retry(exc=e, countdown=5)
