from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember, TripInvite
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class TripInviteModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="email@example.com", password="testpass123"
        )

        self.trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.owner,
        )

        self.invited_user = User.objects.create_user(
            username="inviteduser", email="other@example.com", password="testpass123"
        )

    def test_default_status_is_pending(self):
        invite = TripInvite.objects.create(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )

        self.assertEqual(invite.status, "pending")

    def test_str_method(self):
        invite = TripInvite.objects.create(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )
        result = str(invite)

        self.assertEqual(result, "inviteduser invited to Trip - pending")

    def test_duplicates_raises_error(self):
        TripInvite.objects.create(
            trip=self.trip, user=self.invited_user, invited_by=self.owner
        )

        with self.assertRaises(IntegrityError):
            TripInvite.objects.create(
                trip=self.trip, user=self.invited_user, invited_by=self.owner
            )

    def test_is_expired_returns_false_before_expires_at(self):
        tomorrow = timezone.now() + timedelta(days=1)
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=tomorrow,
        )

        self.assertEqual(invite.is_expired(), False)

    def test_is_expired_returns_true_while_pending_and_expired(self):
        expired_date = timezone.now() - timedelta(days=1)
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=expired_date,
            status="pending",
        )

        self.assertEqual(invite.is_expired(), True)

    def test_is_expired_returns_false_while_accepted_and_expired(self):
        expired_date = timezone.now() - timedelta(days=1)
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=expired_date,
            status="accepted",
        )

        self.assertEqual(invite.is_expired(), False)

    def test_accept_method_changes_status(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=1),
            status="pending",
        )

        invite.accept()
        self.assertEqual(invite.status, "accepted")

    def test_accept_raises_error_when_not_pending(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=1),
            status="accepted",
        )

        with self.assertRaises(ValidationError):
            invite.accept()

    def test_accept_raises_error_when_expired(self):
        expired_date = timezone.now() - timedelta(days=1)
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=expired_date,
            status="pending",
        )

        with self.assertRaises(ValidationError):
            invite.accept()

    def test_accept_sets_responded_at(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
        )

        invite.accept()
        self.assertIsNotNone(invite.responded_at)

    def test_accept_creates_trip_member(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
        )

        invite.accept()
        self.assertTrue(
            TripMember.objects.filter(trip=self.trip, user=self.invited_user).exists()
        )

    def test_decline_raises_error_when_not_pending(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=1),
            status="accepted",
        )

        with self.assertRaises(ValidationError):
            invite.decline()

    def test_decline_method_changes_status(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=1),
            status="pending",
        )

        invite.decline()
        self.assertEqual(invite.status, "declined")

    def test_decline_sets_responded_at(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
        )

        invite.decline()
        self.assertIsNotNone(invite.responded_at)

    def test_mark_expired_returns_true_and_changes_status(self):
        expired_date = timezone.now() - timedelta(days=1)
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            expires_at=expired_date,
            status="pending",
        )

        result = invite.mark_expired()

        self.assertTrue(result)
        self.assertEqual(invite.status, "expired")

    def test_cancel_raises_error_when_not_pending(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status="accepted",
        )

        with self.assertRaises(ValidationError):
            invite.cancel()

    def test_cancel_deletes_invite(self):
        invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status="pending",
        )

        invite.cancel()

        self.assertFalse(
            TripMember.objects.filter(trip=self.trip, user=self.invited_user).exists()
        )
