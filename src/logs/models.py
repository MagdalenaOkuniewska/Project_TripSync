from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLog(models.Model):
    ACTIONS_CHOICES = [
        ("member_added", "Member added"),
        ("member_removed", "Member removed"),
        ("member_left", "Member left"),
        ("invite_sent", "Invite sent"),
        ("invite_declined", "Invite declined"),
    ]

    class Meta:
        ordering = ["-timestamp"]

    # Generic relation - może wskazywać na DOWOLNY model np. (wyjazd, event, ...)
    # Django ma wbudowaną appkę django.contrib.contenttypes która śledzi wszystkie modele w projekcie.
    # Każdy model ma swój wpis w tabeli ContentType
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    # Python który łączy content_type + object_id i zwraca gotowy obiekt

    action = models.CharField(max_length=50, choices=ACTIONS_CHOICES)
    performed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="audit_actions"
    )
    affected_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="audit_events"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    extra_data = models.JSONField(default=dict, blank=True)
