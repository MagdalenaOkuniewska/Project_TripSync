from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ...forms import TripForm
from ...models import Trip, TripMember
from ..factories import UserFactory, TripFactory


class TripCreateViewTest(TestCase):

    def setUp(self):
        self.url = reverse("trip-create")
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.valid_data = {
            "title": "TestTrip",
            "destination": "Example",
            "start_date": "2026-07-01",
            "end_date": "2026-07-14",
        }

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_create.html")
        self.assertIsInstance(response.context["form"], TripForm)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_trip_created_successfully(self):
        response = self.client.post(self.url, self.valid_data)
        trip = Trip.objects.get(title="TestTrip")
        self.assertRedirects(response, reverse("trip-detail", kwargs={"pk": trip.pk}))

    def test_logged_user_is_set_as_owner(self):
        self.client.post(self.url, self.valid_data)
        trip = Trip.objects.get(title="TestTrip")
        self.assertEqual(trip.owner, self.user)

    def test_trip_member_created_for_owner(self):
        self.client.post(self.url, self.valid_data)
        trip = Trip.objects.get(title="TestTrip")
        self.assertTrue(TripMember.objects.filter(trip=trip, user=self.user).exists())

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.valid_data)
        msgs = list(get_messages(response.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertIn("has been created", str(msgs[0]))
