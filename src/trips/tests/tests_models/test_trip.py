from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ..factories import UserFactory, TripFactory, TripMemberFactory
from ...models import Trip, TripMember


class TripModelTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)

    def test_str_method(self):
        self.assertEqual(str(self.trip), f"{self.trip.title} - {self.trip.destination}")

    def test_created_at_is_set(self):
        self.assertIsNotNone(self.trip.created_at)

    def test_end_date_before_start_date_raises_error(self):
        with self.assertRaises(ValidationError):
            TripFactory(owner=self.user, start_date="2026-07-14", end_date="2026-07-01")

    def test_same_start_and_end_date_is_valid(self):
        trip = TripFactory(
            owner=self.user, start_date="2026-07-01", end_date="2026-07-01"
        )
        self.assertEqual(trip.start_date, trip.end_date)

    def test_is_owner_returns_true(self):
        self.assertTrue(self.trip.is_owner(self.user))

    def test_is_owner_returns_false_for_other_user(self):
        other = UserFactory()
        self.assertFalse(self.trip.is_owner(other))

    def test_is_participant_returns_true_for_member(self):
        member = UserFactory()
        TripMemberFactory(trip=self.trip, user=member)
        self.assertTrue(self.trip.is_participant(member))

    def test_owner_tripmember_created_on_save(self):
        self.assertTrue(
            TripMember.objects.filter(trip=self.trip, user=self.user).exists()
        )


class TripMemberModelTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.trip = TripFactory(owner=self.owner)

    def test_str_method(self):
        member = TripMember.objects.get(trip=self.trip, user=self.owner)
        self.assertEqual(str(member), f"{self.owner.username} - {self.trip.title}")

    def test_owner_has_owner_role(self):
        member = TripMember.objects.get(trip=self.trip, user=self.owner)
        self.assertEqual(member.role, "owner")

    def test_default_member_role(self):
        other = UserFactory()
        member = TripMemberFactory(trip=self.trip, user=other)
        self.assertEqual(member.role, "member")

    def test_duplicates_raises_error(self):
        other = UserFactory()
        TripMemberFactory(trip=self.trip, user=other)
        with self.assertRaises(IntegrityError):
            TripMemberFactory(trip=self.trip, user=other)
