from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from trips.models import TripMember
from shopping_list.models import ShoppingList
from .factories import UserFactory, TripFactory, ShoppingListFactory


class ShoppingListCreateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)

        self.url = reverse("shopping-list-create", kwargs={"trip_pk": self.trip.pk})
        self.client.force_login(self.user)

    def test_owner_can_create_shopping_list(self):
        self.client.post(self.url)

        self.assertTrue(ShoppingList.objects.filter(trip=self.trip).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_owner_cannot_create(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("trip-list"))

    def test_redirects_to_shopping_list_detail(self):
        response = self.client.post(self.url)
        shopping_list = ShoppingList.objects.get(trip=self.trip)

        self.assertRedirects(
            response, reverse("shopping-list-details", kwargs={"pk": shopping_list.pk})
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("created", str(messages[0]))

    def test_creating_duplicate_shows_warning(self):
        ShoppingListFactory(trip=self.trip)
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("already exists", str(messages[0]))


class ShoppingListDetailViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)

        self.shopping_list = ShoppingListFactory(trip=self.trip)
        self.url = reverse(
            "shopping-list-details", kwargs={"pk": self.shopping_list.pk}
        )
        self.client.force_login(self.user)

    def test_owner_can_view(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shopping_list/shopping_list_details.html")

    def test_participant_can_view(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_is_redirected(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("trip-list"))


class ShoppingListDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.shopping_list = ShoppingListFactory(trip=self.trip)

        self.url = reverse("shopping-list-delete", kwargs={"pk": self.shopping_list.pk})
        self.client.force_login(self.user)

    def test_owner_can_delete(self):
        self.client.post(self.url)

        self.assertFalse(ShoppingList.objects.filter(pk=self.shopping_list.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_owner_cannot_delete(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("trip-list"))
        self.assertTrue(ShoppingList.objects.filter(pk=self.shopping_list.pk).exists())

    def test_redirects_to_trip_detail_after_delete(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))
