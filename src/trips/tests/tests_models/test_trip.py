from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember
from django.core.exceptions import ValidationError

User = get_user_model()


class TripModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="email@example.com", password="testpass123"
        )

    def test_create_trip(self):
        trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.user,
        )

        self.assertIsNotNone(trip.created_at)
        self.assertEqual(trip.title, "Trip")
        self.assertEqual(trip.destination, "Example")
        self.assertEqual(str(trip.start_date), "2026-07-01")
        self.assertEqual(str(trip.end_date), "2026-07-14")
        self.assertEqual(trip.owner, self.user)

    def test_end_date_before_start_date_raises_error(self):
        with self.assertRaises(ValidationError):
            Trip.objects.create(
                title="Trip",
                destination="Example",
                start_date="2026-07-14",
                end_date="2026-07-01",
                owner=self.user,
            )

    def test_same_start_and_end_date_is_valid(self):
        trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-01",
            owner=self.user,
        )

        self.assertEqual(trip.start_date, trip.end_date)

    def test_is_owner_returns_true(self):
        trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.user,
        )

        result = trip.is_owner(self.user)
        self.assertTrue(result)

    def test_is_owner_returns_false_for_invalid_user(self):
        trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.user,
        )

        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )

        result = trip.is_owner(other_user)
        self.assertFalse(result)

    def test_is_participant_returns_true_for_member(self):
        trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.user,
        )

        member_user = User.objects.create_user(
            username="memberuser", password="memberpass123"
        )

        TripMember.objects.create(trip=trip, user=member_user)
        result = trip.is_participant(member_user)

        self.assertTrue(result)

    def test_str_method(self):
        trip = Trip.objects.create(
            title="Trip",
            destination="Example",
            start_date="2026-07-01",
            end_date="2026-07-14",
            owner=self.user,
        )

        result = str(trip)
        self.assertEqual(result, "Trip - Example")
