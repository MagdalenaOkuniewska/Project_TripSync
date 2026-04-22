from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from ..factories import UserFactory, TripFactory, TripInviteFactory
from ...models import TripMember, TripInvite


class TripInviteModelTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.trip = TripFactory(owner=self.owner)
        self.invited_user = UserFactory()

    def test_default_status_is_pending(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        self.assertEqual(invite.status, "pending")

    def test_str_method(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        self.assertEqual(
            str(invite),
            f"{self.invited_user.username} invited to {self.trip.title} - pending",
        )

    def test_duplicates_raises_error(self):
        TripInviteFactory(trip=self.trip, user=self.invited_user, invited_by=self.owner)
        with self.assertRaises(IntegrityError):
            TripInviteFactory(
                trip=self.trip, user=self.invited_user, invited_by=self.owner
            )

    def test_is_expired_returns_false_before_expires_at(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(invite.is_expired())

    def test_is_expired_returns_true_when_pending_and_past_expires_at(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(days=1),
            status="pending",
        )
        self.assertTrue(invite.is_expired())

    def test_is_expired_returns_false_when_accepted(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(days=1),
            status="accepted",
        )
        self.assertFalse(invite.is_expired())

    def test_accept_changes_status(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        invite.accept()
        self.assertEqual(invite.status, "accepted")

    def test_accept_raises_error_when_not_pending(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status="accepted",
        )
        with self.assertRaises(ValidationError):
            invite.accept()

    def test_accept_raises_error_when_expired(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(days=1),
            status="pending",
        )
        with self.assertRaises(ValidationError):
            invite.accept()

    def test_accept_sets_responded_at(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        invite.accept()
        self.assertIsNotNone(invite.responded_at)

    def test_accept_creates_trip_member(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        invite.accept()
        self.assertTrue(
            TripMember.objects.filter(trip=self.trip, user=self.invited_user).exists()
        )

    def test_decline_changes_status(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        invite.decline()
        self.assertEqual(invite.status, "declined")

    def test_decline_raises_error_when_not_pending(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status="accepted",
        )
        with self.assertRaises(ValidationError):
            invite.decline()

    def test_decline_sets_responded_at(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        invite.decline()
        self.assertIsNotNone(invite.responded_at)

    def test_mark_expired_returns_true_and_changes_status(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(days=1),
            status="pending",
        )
        self.assertTrue(invite.mark_expired())
        self.assertEqual(invite.status, "expired")

    def test_cancel_raises_error_when_not_pending(self):
        invite = TripInviteFactory(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status="accepted",
        )
        with self.assertRaises(ValidationError):
            invite.cancel()

    def test_cancel_deletes_invite(self):
        invite = TripInviteFactory(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        invite.cancel()
        self.assertFalse(TripInvite.objects.filter(pk=invite.pk).exists())
