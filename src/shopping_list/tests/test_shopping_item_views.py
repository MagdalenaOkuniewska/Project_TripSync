from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from trips.models import TripMember
from shopping_list.models import ShoppingItem
from .factories import (
    UserFactory,
    TripFactory,
    ShoppingListFactory,
    ShoppingItemFactory,
)


class ShoppingItemCreateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.shopping_list = ShoppingListFactory(trip=self.trip)

        self.url = reverse(
            "shopping-item-create", kwargs={"shopping_list_pk": self.shopping_list.pk}
        )
        self.client.force_login(self.user)
        self.data = {"item_name": "Apples", "item_quantity": 3}

    def test_owner_can_create_item(self):
        self.client.post(self.url, self.data)

        self.assertTrue(ShoppingItem.objects.filter(item_name="Apples").exists())

    def test_participant_can_create_item(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        self.client.post(self.url, self.data)

        self.assertTrue(ShoppingItem.objects.filter(item_name="Apples").exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_cannot_create(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)

        self.assertRedirects(response, reverse("trip-list"))

    def test_added_by_set_to_current_user(self):
        self.client.post(self.url, self.data)
        item = ShoppingItem.objects.get(item_name="Apples")

        self.assertEqual(item.added_by, self.user)

    def test_redirects_to_shopping_list_detail(self):
        response = self.client.post(self.url, self.data)

        self.assertRedirects(
            response,
            reverse("shopping-list-details", kwargs={"pk": self.shopping_list.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("successfully added", str(messages[0]))


class ShoppingItemUpdateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.shopping_list = ShoppingListFactory(trip=self.trip)
        self.item = ShoppingItemFactory(
            shopping_list=self.shopping_list, added_by=self.user
        )

        self.url = reverse("shopping-item-update", kwargs={"pk": self.item.pk})
        self.client.force_login(self.user)
        self.data = {"item_name": "Updated Item", "item_quantity": 5}

    def test_owner_can_update_item(self):
        self.client.post(self.url, self.data)
        self.item.refresh_from_db()

        self.assertEqual(self.item.item_name, "Updated Item")
        self.assertEqual(self.item.item_quantity, 5)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_cannot_update(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)

        self.assertRedirects(response, reverse("trip-list"))

    def test_redirects_to_shopping_list_detail(self):
        response = self.client.post(self.url, self.data)

        self.assertRedirects(
            response,
            reverse("shopping-list-details", kwargs={"pk": self.shopping_list.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("updated", str(messages[0]))


class ShoppingItemDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.shopping_list = ShoppingListFactory(trip=self.trip)
        self.item = ShoppingItemFactory(
            shopping_list=self.shopping_list, added_by=self.user
        )

        self.url = reverse("shopping-item-delete", kwargs={"pk": self.item.pk})
        self.client.force_login(self.user)

    def test_owner_can_delete_item(self):
        self.client.post(self.url)

        self.assertFalse(ShoppingItem.objects.filter(pk=self.item.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_cannot_delete(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("trip-list"))
        self.assertTrue(ShoppingItem.objects.filter(pk=self.item.pk).exists())

    def test_redirects_to_shopping_list_detail(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("shopping-list-details", kwargs={"pk": self.shopping_list.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))
