from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ...models import TripInvite
from ..factories import UserFactory, TripFactory


class TripInviteCreateViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.trip = TripFactory(owner=self.owner, title="My Trip")
        self.invited = UserFactory()
        self.url = reverse("trip-invite-create", kwargs={"trip_id": self.trip.pk})
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_owner_can_view_invite_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_invite_create.html")

    def test_owner_can_invite(self):
        self.client.post(self.url, {"user": self.invited.pk})
        self.assertTrue(
            TripInvite.objects.filter(trip=self.trip, user=self.invited).exists()
        )

    def test_invite_redirects_to_trip_detail(self):
        response = self.client.post(self.url, {"user": self.invited.pk})
        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )

    def test_invite_has_correct_info(self):
        self.client.post(self.url, {"user": self.invited.pk})
        invite = TripInvite.objects.get(trip=self.trip, user=self.invited)
        self.assertEqual(invite.invited_by, self.owner)

    def test_shows_success_message(self):
        response = self.client.post(self.url, {"user": self.invited.pk})
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Invitation sent", str(msgs[0]))

    def test_non_owner_cannot_invite(self):
        self.client.force_login(UserFactory())
        self.client.post(self.url, {"user": self.invited.pk})
        self.assertFalse(
            TripInvite.objects.filter(trip=self.trip, user=self.invited).exists()
        )

    def test_non_owner_sees_error_message(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Only the Trip Owner", str(msgs[0]))
