from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember
from django.urls import reverse

User = get_user_model()


class TripListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass123")

        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

        self.trip = Trip.objects.create(
            title="My Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.user,
        )

        self.url = reverse("trip-list")

    def login_user(self):
        self.client.login(username="user", password="testpass123")

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f"{reverse('login')}?next={self.url}"

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_page_loads_correctly(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_list.html")

    def test_show_owned_trips(self):
        self.login_user()
        response = self.client.get(self.url)

        self.assertContains(response, "My Trip")

    def test_show_member_trips(self):
        self.login_user()
        self.member_trip = Trip.objects.create(
            title="Member Trips",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.other_user,
        )
        TripMember.objects.create(trip=self.member_trip, user=self.user)

        response = self.client.get(self.url)

        self.assertContains(response, "Member Trips")

    def test_does_not_show_other_user_trips(self):
        self.login_user()

        self.other_trip = Trip.objects.create(
            title="Other Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.other_user,
        )

        response = self.client.get(self.url)

        self.assertNotContains(response, "Other Trip")
