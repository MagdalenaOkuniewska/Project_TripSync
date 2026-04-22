from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ...models import TripMember
from ..factories import UserFactory, TripFactory, TripInviteFactory


class TripInviteRespondViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.invited = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.invite = TripInviteFactory(
            trip=self.trip, user=self.invited, invited_by=self.owner
        )
        self.url = reverse("trip-invite-respond", kwargs={"pk": self.invite.pk})
        self.client.force_login(self.invited)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_invited_user_can_view_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_invite_confirm.html")

    def test_other_user_cannot_view_page(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/invites/", response.url)

    def test_other_user_sees_error_message(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("not yours", str(msgs[0]))

    def test_accept_changes_status(self):
        self.client.post(self.url, {"response": "accept"})
        self.invite.refresh_from_db()
        self.assertEqual(self.invite.status, "accepted")

    def test_accept_creates_trip_member(self):
        self.client.post(self.url, {"response": "accept"})
        self.assertTrue(
            TripMember.objects.filter(trip=self.trip, user=self.invited).exists()
        )

    def test_accept_redirects_to_trip_detail(self):
        response = self.client.post(self.url, {"response": "accept"})
        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )

    def test_accept_shows_success_message(self):
        response = self.client.post(self.url, {"response": "accept"})
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Accepted", str(msgs[0]))

    def test_decline_changes_status(self):
        self.client.post(self.url, {"response": "decline"})
        self.invite.refresh_from_db()
        self.assertEqual(self.invite.status, "declined")

    def test_decline_does_not_create_trip_member(self):
        self.client.post(self.url, {"response": "decline"})
        self.assertFalse(
            TripMember.objects.filter(trip=self.trip, user=self.invited).exists()
        )

    def test_decline_redirects_to_invite_list(self):
        response = self.client.post(self.url, {"response": "decline"})
        self.assertRedirects(response, reverse("trip-invite-list"))

    def test_decline_shows_success_message(self):
        response = self.client.post(self.url, {"response": "decline"})
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("Declined", str(msgs[0]))

    def test_response_context_default_accept(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["response"], "accept")

    def test_response_context_decline(self):
        response = self.client.get(self.url, {"response": "decline"})
        self.assertEqual(response.context["response"], "decline")
