from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from notifications.context_processors import count_unread_notifications
from .factories import UserFactory, NotificationFactory


class CountUnreadNotificationsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_zero_for_anonymous_user(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        context = count_unread_notifications(request)
        self.assertEqual(context["unread_notifications_count"], 0)

    def test_returns_correct_count_for_authenticated_user(self):
        user = UserFactory()
        NotificationFactory(recipient=user, is_read=False)
        NotificationFactory(recipient=user, is_read=False)
        NotificationFactory(recipient=user, is_read=True)
        request = self.factory.get("/")
        request.user = user
        context = count_unread_notifications(request)
        self.assertEqual(context["unread_notifications_count"], 2)

    def test_does_not_count_other_users_notifications(self):
        user = UserFactory()
        other = UserFactory()
        NotificationFactory(recipient=other, is_read=False)
        request = self.factory.get("/")
        request.user = user
        context = count_unread_notifications(request)
        self.assertEqual(context["unread_notifications_count"], 0)
