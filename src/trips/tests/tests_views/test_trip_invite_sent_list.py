from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripInvite

from django.urls import reverse

User = get_user_model()

class TripInviteSentListViewTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='testpass123'
        )

        self.trip = Trip.objects.create(
            title='Test Trip',
            destination='Example',
            start_date='2026-07-01',
            end_date='2026-07-14',
            owner=self.owner
        )

        self.url = reverse('trip-invite-sent')

    def login_user(self):
        self.client.login(username='owner', password='testpass123')

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_page_loads_correctly(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_invite_sent_list.html')

    def test_shows_sent_invites(self):
        self.login_user()

        self.invited_user = User.objects.create_user(
            username='invited',
            password='testpass123'
        )
        self.invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status='pending'
        )

        response = self.client.get(self.url)

        self.assertContains(response, 'invited')