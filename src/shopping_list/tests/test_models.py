from django.test import TestCase
from .factories import UserFactory, ShoppingListFactory, ShoppingItemFactory


class ShoppingListModelTest(TestCase):

    def setUp(self):
        self.shopping_list = ShoppingListFactory()

    def test_str_method(self):
        self.assertEqual(
            str(self.shopping_list), f" {self.shopping_list.trip.title} Shopping list"
        )


class ShoppingItemModelTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.item = ShoppingItemFactory(added_by=self.user)

    def test_str_method(self):
        self.assertEqual(
            str(self.item), f"{self.item.item_name} x{self.item.item_quantity}"
        )

    def test_default_is_not_purchased(self):
        self.assertFalse(self.item.is_purchased)

    def test_marked_as_purchased(self):
        self.item.marked_as_purchased(self.user)

        self.assertTrue(self.item.is_purchased)
        self.assertEqual(self.item.purchased_by, self.user)

    def test_marked_as_purchased_saves_to_db(self):
        self.item.marked_as_purchased(self.user)
        self.item.refresh_from_db()

        self.assertTrue(self.item.is_purchased)
        self.assertEqual(self.item.purchased_by, self.user)
