from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripInvite
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()


class TripInviteCreateViewTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="testpass123")

        self.trip = Trip.objects.create(
            title="My Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.owner,
        )

        self.url = reverse("trip-invite-create", kwargs={"trip_id": self.trip.pk})

    def login_user(self):
        self.client.login(username="owner", password="testpass123")

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f"{reverse('login')}?next={self.url}"

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_owner_can_view_invite_page(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_invite_create.html")

    def test_owner_can_invite(self):
        self.login_user()

        self.invited_user = User.objects.create_user(
            username="invited", password="testpass123"
        )

        data = {"user": self.invited_user.pk}

        response = self.client.post(self.url, data)

        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )
        self.assertTrue(
            TripInvite.objects.filter(trip=self.trip, user=self.invited_user).exists()
        )

    def test_invite_has_correct_info(self):
        self.login_user()

        self.invited_user = User.objects.create_user(
            username="invited", password="testpass123"
        )

        data = {"user": self.invited_user.pk}
        self.client.post(self.url, data)

        invite = TripInvite.objects.get(trip=self.trip, user=self.invited_user)

        self.assertEqual(invite.trip, self.trip)
        self.assertEqual(invite.invited_by, self.owner)
        self.assertEqual(invite.user, self.invited_user)

    def test_shows_success_message_after_invite(self):
        self.login_user()

        self.invited_user = User.objects.create_user(
            username="invited", password="testpass123"
        )

        data = {"user": self.invited_user.pk}
        response = self.client.post(self.url, data)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Invitation sent", str(messages[0]))

    def test_non_owner_cannot_invite(self):
        self.other_user = User.objects.create_user(
            username="otheruser", password="otheruser"
        )
        self.client.login(username="otheruser", password="otheruser")

        self.invited_user = User.objects.create_user(
            username="invited", password="testpass123"
        )

        data = {"user": self.invited_user.pk}

        self.client.post(self.url, data)

        self.assertFalse(
            TripInvite.objects.filter(trip=self.trip, user=self.invited_user).exists()
        )

    def test_shows_unsuccessful_message_after_invite(self):
        self.other_user = User.objects.create_user(
            username="otheruser", password="otheruser"
        )
        self.client.login(username="otheruser", password="otheruser")

        response = self.client.get(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Only the Trip Owner", str(messages[0]))
