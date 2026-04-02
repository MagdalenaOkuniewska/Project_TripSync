from django.test import TestCase
from .factories import (
    UserFactory,
    TripFactory,
    PackingListFactory,
    PackingItemFactory,
    PackingListTemplateFactory,
    PackingItemTemplateFactory,
)


class PackingListModelTest(TestCase):

    def test_str_private_list(self):
        user = UserFactory()
        trip = TripFactory(owner=user)
        packing_list = PackingListFactory(trip=trip, user=user, list_type="private")
        self.assertEqual(str(packing_list), f"{user.username} {trip.title} list")

    def test_str_shared_list(self):
        user = UserFactory()
        trip = TripFactory(owner=user)
        packing_list = PackingListFactory(trip=trip, user=None, list_type="shared")
        self.assertEqual(str(packing_list), f"Shared {trip.title} list")


class PackingItemModelTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.packing_list = PackingListFactory(trip=self.trip, user=self.user)
        self.item = PackingItemFactory(
            packing_list=self.packing_list, added_by=self.user
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.item), f"{self.item.item_name} x{self.item.item_quantity}"
        )

    def test_default_is_not_packed(self):
        self.assertFalse(self.item.is_packed)

    def test_marked_as_packed_private_list(self):
        self.item.marked_as_packed(self.user)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_packed)
        # private list — packed_by not set
        self.assertIsNone(self.item.packed_by)

    def test_marked_as_packed_shared_list(self):
        shared_list = PackingListFactory(trip=self.trip, user=None, list_type="shared")
        item = PackingItemFactory(packing_list=shared_list, added_by=self.user)
        item.marked_as_packed(self.user)
        item.refresh_from_db()
        self.assertTrue(item.is_packed)
        self.assertEqual(item.packed_by, self.user)


class PackingListTemplateModelTest(TestCase):

    def test_str_method(self):
        template = PackingListTemplateFactory(name="Summer Trip")
        self.assertEqual(str(template), "Summer Trip")

    def test_apply_to_trip_creates_packing_list(self):
        user = UserFactory()
        trip = TripFactory(owner=user)
        template = PackingListTemplateFactory(user=user)
        PackingItemTemplateFactory(template=template, name="Sunscreen", quantity=1)
        PackingItemTemplateFactory(template=template, name="Towel", quantity=2)

        packing_list = template.apply_to_trip(trip=trip, user=user)

        self.assertEqual(packing_list.trip, trip)
        self.assertEqual(packing_list.user, user)
        self.assertEqual(packing_list.items.count(), 2)


class PackingItemTemplateModelTest(TestCase):

    def test_str_method(self):
        item = PackingItemTemplateFactory(name="Sunscreen", quantity=2)
        self.assertEqual(str(item), "Sunscreen: x2")
