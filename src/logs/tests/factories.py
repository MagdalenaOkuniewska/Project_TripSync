import factory
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from trips.models import Trip
from logs.models import AuditLog

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class TripFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trip

    title = "Test Trip"
    destination = "Paris"
    start_date = date(2026, 7, 1)
    end_date = date(2026, 7, 14)
    owner = factory.SubFactory(UserFactory)


class AuditLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLog

    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(Trip)
    )
    object_id = factory.SelfAttribute("content_object.pk")
    content_object = factory.SubFactory(TripFactory)
    action = "member_added"
    performed_by = factory.SubFactory(UserFactory)
    affected_user = factory.SubFactory(UserFactory)
    extra_data = {}
