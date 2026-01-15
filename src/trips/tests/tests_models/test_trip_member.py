from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember
from django.db import IntegrityError

User = get_user_model()

class TripMemberModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='email@example.com',
            password='testpass123'
        )

        self.trip = Trip.objects.create(
            title='Trip',
            destination='Example',
            start_date='2026-07-01',
            end_date='2026-07-14',
            owner=self.user
        )

    def test_str_method(self):
        member = TripMember.objects.create(trip=self.trip, user=self.user)
        result = str(member)

        self.assertEqual(result, 'testuser - Trip')

    def test_default_member_role(self):
        other_user = User.objects.create_user(
            username='memberuser',
            email='member@example.com',
            password='testpass123'
        )
        member = TripMember.objects.create(trip=self.trip, user=other_user)

        self.assertEqual(member.role, 'member')

    def test_trip_owner_has_owner_role(self):
        member = TripMember.objects.create(trip=self.trip, user=self.user)

        self.assertEqual(member.role, 'owner')

    def test_duplicates_raises_error(self):
        TripMember.objects.create(trip=self.trip, user=self.user)

        with self.assertRaises(IntegrityError):
            TripMember.objects.create(trip=self.trip, user=self.user)



