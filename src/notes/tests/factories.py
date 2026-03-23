import factory
from datetime import date
from django.contrib.auth import get_user_model
from trips.models import Trip
from notes.models import Note

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


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = "Test Note"
    content = "Some content"
    note_type = "private"
    user = factory.SubFactory(UserFactory)
    trip = factory.SubFactory(TripFactory)
