from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ...models import Trip
from ..factories import UserFactory, TripFactory


class TripDeleteViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.other = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.url = reverse("trip-delete", kwargs={"pk": self.trip.pk})
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_owner_can_view_delete_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_delete.html")

    def test_owner_can_delete_trip(self):
        self.client.post(self.url)
        self.assertFalse(Trip.objects.filter(pk=self.trip.pk).exists())

    def test_delete_redirects_to_trip_list(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("trip-list"))

    def test_shows_success_message_after_delete(self):
        response = self.client.post(self.url, follow=True)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("deleted successfully", str(msgs[0]))

    def test_non_owner_cannot_delete_trip(self):
        self.client.force_login(self.other)
        self.client.post(self.url)
        self.assertTrue(Trip.objects.filter(pk=self.trip.pk).exists())

    def test_non_owner_sees_error_message(self):
        self.client.force_login(self.other)
        response = self.client.post(self.url, follow=True)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Only the Trip Owner", str(msgs[0]))
