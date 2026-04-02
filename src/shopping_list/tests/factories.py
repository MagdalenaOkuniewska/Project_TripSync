import factory
from datetime import date
from django.contrib.auth import get_user_model
from trips.models import Trip
from shopping_list.models import ShoppingList, ShoppingItem

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


class ShoppingListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShoppingList

    trip = factory.SubFactory(TripFactory)


class ShoppingItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShoppingItem

    shopping_list = factory.SubFactory(ShoppingListFactory)
    item_name = "Test Item"
    item_quantity = 1
    added_by = factory.SubFactory(UserFactory)
