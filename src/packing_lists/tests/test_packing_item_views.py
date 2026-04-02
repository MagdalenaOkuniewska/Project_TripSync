from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from trips.models import TripMember
from packing_lists.models import PackingItem
from .factories import UserFactory, TripFactory, PackingListFactory, PackingItemFactory


class PackingItemCreateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.packing_list = PackingListFactory(
            trip=self.trip, user=self.user, list_type="private"
        )
        self.url = reverse(
            "packing-item-create", kwargs={"list_pk": self.packing_list.pk}
        )
        self.client.force_login(self.user)
        self.data = {"item_name": "Sunscreen", "item_quantity": 2}

    def test_owner_can_create_item(self):
        self.client.post(self.url, self.data)
        self.assertTrue(PackingItem.objects.filter(item_name="Sunscreen").exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_add_to_private_list(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("trip-list"))

    def test_participant_can_add_to_shared_list(self):
        shared_list = PackingListFactory(trip=self.trip, user=None, list_type="shared")
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        url = reverse("packing-item-create", kwargs={"list_pk": shared_list.pk})
        self.client.post(url, self.data)
        self.assertTrue(
            PackingItem.objects.filter(
                item_name="Sunscreen", packing_list=shared_list
            ).exists()
        )

    def test_added_by_set_to_current_user(self):
        self.client.post(self.url, self.data)
        item = PackingItem.objects.get(item_name="Sunscreen")
        self.assertEqual(item.added_by, self.user)

    def test_redirects_to_packing_list_detail(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(
            response,
            reverse("packing-list-details", kwargs={"pk": self.packing_list.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("successfully added", str(messages[0]))


class PackingItemUpdateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.packing_list = PackingListFactory(
            trip=self.trip, user=self.user, list_type="private"
        )
        self.item = PackingItemFactory(
            packing_list=self.packing_list, added_by=self.user
        )
        self.url = reverse("packing-item-update", kwargs={"pk": self.item.pk})
        self.client.force_login(self.user)
        self.data = {"item_name": "Updated Item", "item_quantity": 5}

    def test_owner_can_update_item(self):
        self.client.post(self.url, self.data)
        self.item.refresh_from_db()
        self.assertEqual(self.item.item_name, "Updated Item")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_update_private_list_item(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("trip-list"))

    def test_redirects_to_packing_list_detail(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(
            response,
            reverse("packing-list-details", kwargs={"pk": self.packing_list.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("updated", str(messages[0]))


class PackingItemDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.packing_list = PackingListFactory(
            trip=self.trip, user=self.user, list_type="private"
        )
        self.item = PackingItemFactory(
            packing_list=self.packing_list, added_by=self.user
        )
        self.url = reverse("packing-item-delete", kwargs={"pk": self.item.pk})
        self.client.force_login(self.user)

    def test_owner_can_delete_item(self):
        self.client.post(self.url)
        self.assertFalse(PackingItem.objects.filter(pk=self.item.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_delete_private_list_item(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("trip-list"))
        self.assertTrue(PackingItem.objects.filter(pk=self.item.pk).exists())

    def test_redirects_to_packing_list_detail(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("packing-list-details", kwargs={"pk": self.packing_list.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))
