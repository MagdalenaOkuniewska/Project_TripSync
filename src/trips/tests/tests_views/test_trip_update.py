from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ..factories import UserFactory, TripFactory


class TripUpdateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.other = UserFactory()
        self.trip = TripFactory(owner=self.user, title="Original Trip")
        self.url = reverse("trip-update", kwargs={"pk": self.trip.pk})
        self.client.force_login(self.user)
        self.valid_data = {
            "title": "Updated Trip",
            "destination": "Example",
            "start_date": "2026-07-01",
            "end_date": "2026-07-14",
        }

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_owner_can_update_trip(self):
        self.client.post(self.url, self.valid_data)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.title, "Updated Trip")

    def test_update_redirects_to_trip_detail(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )

    def test_shows_success_message_after_update(self):
        response = self.client.post(self.url, self.valid_data)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("has been updated", str(msgs[0]))

    def test_non_owner_cannot_update_trip(self):
        self.client.force_login(self.other)
        self.client.post(self.url, self.valid_data)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.title, "Original Trip")

    def test_non_owner_sees_error_message(self):
        self.client.force_login(self.other)
        response = self.client.get(self.url)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Only the Trip Owner", str(msgs[0]))

    def test_form_shows_current_trip_data(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Original Trip")
