from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ...models import TripInvite
from ..factories import UserFactory, TripFactory, TripInviteFactory


class TripInviteCancelViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.invited = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.invite = TripInviteFactory(
            trip=self.trip, user=self.invited, invited_by=self.owner
        )
        self.url = reverse("trip-invite-cancel", kwargs={"pk": self.invite.pk})
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_owner_can_view_cancel_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_invite_cancel.html")

    def test_owner_can_cancel_invite(self):
        self.client.post(self.url)
        self.assertFalse(TripInvite.objects.filter(pk=self.invite.pk).exists())

    def test_cancel_redirects_to_trip_detail(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )

    def test_cancel_shows_success_message(self):
        response = self.client.post(self.url)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Cancelled", str(msgs[0]))

    def test_other_user_cannot_cancel(self):
        self.client.force_login(UserFactory())
        self.client.post(self.url)
        self.assertTrue(TripInvite.objects.filter(pk=self.invite.pk).exists())

    def test_other_user_sees_error_message(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Only the trip owner", str(msgs[0]))
