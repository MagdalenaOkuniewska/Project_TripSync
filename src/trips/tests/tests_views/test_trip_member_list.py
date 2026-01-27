from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()


class TripMemberListViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="testpass123")

        self.participant = User.objects.create_user(
            username="participant", password="testpass123"
        )

        self.trip = Trip.objects.create(
            title="Test Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.owner,
        )

        self.url = reverse("trip-member-list", kwargs={"trip_id": self.trip.pk})

        TripMember.objects.create(trip=self.trip, user=self.participant)

    def login_user(self):
        self.client.login(username="owner", password="testpass123")

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f"{reverse('login')}?next={self.url}"

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_owner_can_view_members(self):
        self.login_user()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_member_list.html")

    def participant_can_view_members(self):
        self.login_user()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_member_list.html")

    def test_random_user_cannot_view_members(self):
        self.client.login(username="random", password="testpass123")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("trip-list", response.url)

    def test_random_user_sees_error_message(self):
        self.client.login(username="random", password="testpass123")

        response = self.client.get(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("only members and owners", str(messages[0]))

    def test_displays_trip_members_list(self):
        self.login_user()
        response = self.client.get(self.url)

        self.assertContains(response, "participant")

    def test_trip_in_context(self):
        self.login_user()
        response = self.client.get(self.url)

        self.assertIn("trip", response.context)
        self.assertEqual(response.context["trip"], self.trip)
