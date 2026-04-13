from django.test import TestCase
from django.utils import timezone
from .factories import UserFactory, NotificationFactory


class NotificationModelTest(TestCase):

    def setUp(self):
        self.recipient = UserFactory()
        self.sender = UserFactory()
        self.notification = NotificationFactory(
            recipient=self.recipient, sender=self.sender
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.notification),
            f"{self.notification.notification_type} - {self.recipient.username}",
        )

    def test_default_is_read_false(self):
        self.assertFalse(self.notification.is_read)

    def test_default_read_at_is_none(self):
        self.assertIsNone(self.notification.read_at)

    def test_mark_as_read(self):
        self.notification.mark_as_read()
        self.notification.refresh_from_db()

        self.assertTrue(self.notification.is_read)
        self.assertIsNotNone(self.notification.read_at)

    def test_mark_as_read_sets_read_at_timestamp(self):
        before = timezone.now()
        self.notification.mark_as_read()
        self.notification.refresh_from_db()

        self.assertGreaterEqual(self.notification.read_at, before)

    def test_mark_as_read_idempotent(self):
        self.notification.mark_as_read()
        first_read_at = self.notification.read_at

        self.notification.mark_as_read()
        self.assertEqual(self.notification.read_at, first_read_at)

    def test_mark_as_unread(self):
        self.notification.mark_as_read()
        self.notification.mark_as_unread()
        self.notification.refresh_from_db()

        self.assertFalse(self.notification.is_read)
        self.assertIsNone(self.notification.read_at)

    def test_mark_as_unread_idempotent(self):
        self.notification.mark_as_unread()

        self.assertFalse(self.notification.is_read)
