from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from ..factories import UserFactory, TripFactory, TripMemberFactory


class TripMemberListViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.participant = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        TripMemberFactory(trip=self.trip, user=self.participant)
        self.url = reverse("trip-member-list", kwargs={"trip_id": self.trip.pk})
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_owner_can_view_members(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trips/trip_member_list.html")

    def test_participant_can_view_members(self):
        self.client.force_login(self.participant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_random_user_cannot_view_members(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("trip-list"))

    def test_random_user_sees_error_message(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        msgs = list(get_messages(response.wsgi_request))
        self.assertIn("only members and owners", str(msgs[0]))

    def test_displays_trip_members(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.participant.username)

    def test_trip_in_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["trip"], self.trip)
