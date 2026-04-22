from django.test import TestCase
from django.urls import reverse
from ...models import TripMember
from ..factories import UserFactory, TripFactory, TripMemberFactory


class TripListViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user, title="My Trip")
        self.url = reverse("trip-list")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_list.html")

    def test_shows_owned_trips(self):
        response = self.client.get(self.url)
        self.assertContains(response, "My Trip")

    def test_shows_member_trips(self):
        other = UserFactory()
        member_trip = TripFactory(owner=other, title="Member Trip")
        TripMemberFactory(trip=member_trip, user=self.user)
        response = self.client.get(self.url)
        self.assertContains(response, "Member Trip")

    def test_does_not_show_other_user_trips(self):
        other = UserFactory()
        TripFactory(owner=other, title="Other Trip")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Other Trip")
