import factory
from datetime import date
from django.contrib.auth import get_user_model
from trips.models import Trip
from packing_lists.models import (
    PackingList,
    PackingItem,
    PackingListTemplate,
    PackingItemTemplate,
)

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


class PackingListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackingList

    trip = factory.SubFactory(TripFactory)
    list_type = "private"
    user = factory.SubFactory(UserFactory)


class PackingItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackingItem

    packing_list = factory.SubFactory(PackingListFactory)
    item_name = "Test Item"
    item_quantity = 1
    added_by = factory.SubFactory(UserFactory)


class PackingListTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackingListTemplate

    name = "Test Template"
    user = factory.SubFactory(UserFactory)


class PackingItemTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackingItemTemplate

    template = factory.SubFactory(PackingListTemplateFactory)
    name = "Template Item"
    quantity = 1
