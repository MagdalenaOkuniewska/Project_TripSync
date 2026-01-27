from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripInvite
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

User = get_user_model()


class TripInviteListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass123")

        self.owner = User.objects.create_user(username="owner", password="testpass123")

        self.trip = Trip.objects.create(
            title="Test Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.owner,
        )

        self.url = reverse("trip-invite-list")

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
        self.assertTemplateUsed(response, "trips/trip_invite_list.html")

    def test_shows_pending_invites(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertContains(response, "Test Trip")

    def test_does_not_show_accepted_invites(self):
        self.login_user()

        self.pending_invite = TripInvite.objects.create(
            trip=self.trip, user=self.user, invited_by=self.owner, status="pending"
        )

        self.pending_invite.status = "accepted"
        self.pending_invite.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["invites"]), 0)
        self.assertContains(response, "No pending invitations.")

    def test_does_not_show_declined_invites(self):
        self.login_user()

        self.pending_invite = TripInvite.objects.create(
            trip=self.trip, user=self.user, invited_by=self.owner, status="pending"
        )

        self.pending_invite.status = "declined"
        self.pending_invite.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["invites"]), 0)
        self.assertContains(response, "No pending invitations.")

    def test_does_not_show_other_users_invites(self):
        self.login_user()

        self.other_user = User.objects.create_user(
            username="other_user", password="testpass123"
        )

        TripInvite.objects.create(
            trip=self.trip,
            user=self.other_user,
            invited_by=self.owner,
            status="pending",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["invites"]), 0)
        self.assertContains(response, "No pending invitations.")

    def test_expired_invites_are_marked(self):
        self.login_user()

        self.pending_invite = TripInvite.objects.create(
            trip=self.trip, user=self.user, invited_by=self.owner, status="pending"
        )

        self.pending_invite.expires_at = timezone.now() - timedelta(days=1)
        self.pending_invite.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["invites"]), 0)
        self.assertContains(response, "No pending invitations.")

        self.pending_invite.refresh_from_db()

        self.assertEqual(self.pending_invite.status, "expired")
