from django.db import IntegrityError
from django.test import TestCase

from ...models import TripMember
from ..factories import TripFactory, TripMemberFactory, UserFactory


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
