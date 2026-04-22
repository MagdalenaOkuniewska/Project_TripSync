from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from ..factories import UserFactory, TripFactory, TripInviteFactory


class TripInviteListViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.owner = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.url = reverse("trip-invite-list")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_invite_list.html")

    def test_does_not_show_accepted_invites(self):
        TripInviteFactory(
            trip=self.trip, user=self.user, invited_by=self.owner, status="accepted"
        )
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["invites"]), 0)

    def test_does_not_show_declined_invites(self):
        TripInviteFactory(
            trip=self.trip, user=self.user, invited_by=self.owner, status="declined"
        )
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["invites"]), 0)

    def test_does_not_show_other_users_invites(self):
        other = UserFactory()
        TripInviteFactory(trip=self.trip, user=other, invited_by=self.owner)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["invites"]), 0)

    def test_expired_invites_are_marked(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.user,
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.client.get(self.url)
        invite.refresh_from_db()
        self.assertEqual(invite.status, "expired")
