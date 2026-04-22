from django.test import TestCase
from django.urls import reverse
from ..factories import UserFactory, TripFactory, TripInviteFactory


class TripInviteSentListViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.url = reverse("trip-invite-sent")
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_invite_sent_list.html")

    def test_shows_sent_invites(self):
        invited = UserFactory()
        TripInviteFactory(trip=self.trip, user=invited, invited_by=self.owner)
        response = self.client.get(self.url)
        self.assertContains(response, invited.username)
