from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


def log_action(
    action, content_object, performed_by, affected_user=None, extra_data=None
):
    AuditLog.objects.create(
        content_type=ContentType.objects.get_for_model(content_object),
        object_id=content_object.pk,
        content_object=content_object,
        action=action,
        performed_by=performed_by,
        affected_user=affected_user,
        extra_data=extra_data or {},
    )
