from django.test import TestCase
from django.urls import reverse
from trips.models import TripMember
from .factories import UserFactory, TripFactory, AuditLogFactory


class TripAuditLogViewTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.url = reverse("trip-audit-log", kwargs={"trip_id": self.trip.pk})
        self.client.force_login(self.owner)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_owner_can_view_log(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "logs/trip_audit_log.html")

    def test_participant_can_view_log(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_non_member_is_redirected(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("trip-list"))

    def test_shows_only_logs_for_this_trip(self):
        other_trip = TripFactory(owner=self.owner)
        AuditLogFactory(content_object=self.trip, action="member_added")
        AuditLogFactory(content_object=other_trip, action="invite_sent")
        response = self.client.get(self.url)

        self.assertEqual(len(response.context["logs"]), 1)

    def test_context_contains_trip(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context["trip"], self.trip)
