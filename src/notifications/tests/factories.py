import factory
from datetime import date
from django.contrib.auth import get_user_model
from trips.models import Trip
from notifications.models import Notification

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


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory(UserFactory)
    sender = factory.SubFactory(UserFactory)
    notification_type = "trip_invite"
    trip = factory.SubFactory(TripFactory)
    message = "You have been invited to a trip."
    is_read = False
