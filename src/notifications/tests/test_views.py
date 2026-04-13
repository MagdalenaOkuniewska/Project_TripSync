from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from notifications.models import Notification
from .factories import UserFactory, NotificationFactory


class NotificationListViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse("notification-list")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_shows_user_notifications(self):
        NotificationFactory(recipient=self.user)
        NotificationFactory(recipient=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["notifications"]), 2)

    def test_does_not_show_other_users_notifications(self):
        other = UserFactory()
        NotificationFactory(recipient=other)
        response = self.client.get(self.url)

        self.assertEqual(len(response.context["notifications"]), 0)

    def test_filter_unread(self):
        NotificationFactory(recipient=self.user, is_read=False)
        NotificationFactory(recipient=self.user, is_read=True)
        response = self.client.get(self.url + "?unread=1")

        self.assertEqual(len(response.context["notifications"]), 1)

    def test_context_contains_unread_count(self):
        NotificationFactory(recipient=self.user, is_read=False)
        NotificationFactory(recipient=self.user, is_read=True)
        response = self.client.get(self.url)

        self.assertEqual(response.context["unread_notifications_count"], 1)


class NotificationMarkReadViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.notification = NotificationFactory(recipient=self.user, is_read=False)
        self.url = reverse(
            "notification-mark-read", kwargs={"pk": self.notification.pk}
        )
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_marks_notification_as_read(self):
        self.client.post(self.url)
        self.notification.refresh_from_db()

        self.assertTrue(self.notification.is_read)

    def test_redirects_to_notification_list(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("notification-list"))

    def test_cannot_mark_other_users_notification(self):
        other = UserFactory()
        notification = NotificationFactory(recipient=other, is_read=False)
        response = self.client.post(
            reverse("notification-mark-read", kwargs={"pk": notification.pk})
        )
        self.assertEqual(response.status_code, 404)
        notification.refresh_from_db()

        self.assertFalse(notification.is_read)


class NotificationMarkAllReadViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse("notification-mark-all-read")
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_marks_all_unread_as_read(self):
        NotificationFactory(recipient=self.user, is_read=False)
        NotificationFactory(recipient=self.user, is_read=False)
        self.client.post(self.url)
        unread_count = Notification.objects.filter(
            recipient=self.user, is_read=False
        ).count()

        self.assertEqual(unread_count, 0)

    def test_does_not_affect_other_users(self):
        other = UserFactory()
        NotificationFactory(recipient=other, is_read=False)
        self.client.post(self.url)

        self.assertTrue(
            Notification.objects.filter(recipient=other, is_read=False).exists()
        )

    def test_redirects_to_notification_list(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("notification-list"))

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("marked as read", str(messages[0]))


class NotificationDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.notification = NotificationFactory(recipient=self.user)
        self.url = reverse("notification-delete", kwargs={"pk": self.notification.pk})
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_deletes_notification(self):
        self.client.post(self.url)

        self.assertFalse(Notification.objects.filter(pk=self.notification.pk).exists())

    def test_cannot_delete_other_users_notification(self):
        other = UserFactory()
        notification = NotificationFactory(recipient=other)
        response = self.client.post(
            reverse("notification-delete", kwargs={"pk": notification.pk})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Notification.objects.filter(pk=notification.pk).exists())

    def test_redirects_to_notification_list(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("notification-list"))

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))
