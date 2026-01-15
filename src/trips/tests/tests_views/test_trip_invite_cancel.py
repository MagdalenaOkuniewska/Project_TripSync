from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripInvite
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()

class TripInviteCancelViewTest(TestCase):
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

        self.url = reverse('trip-invite-cancel', kwargs={'pk': self.invite.pk})

    def login_user(self):
        self.client.login(username='owner', password='testpass123')

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_owner_can_view_cancel_page(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_invite_cancel.html')

    def test_owner_can_cancel_invite(self):
        self.login_user()

        self.client.post(self.url)

        self.assertFalse(TripInvite.objects.filter(pk=self.invite.pk).exists())

    def test_other_user_cannot_cancel(self):
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )
        self.client.login(username='other', password='testpass123')

        self.client.post(self.url)

        self.assertTrue(TripInvite.objects.filter(pk=self.invite.pk).exists())

    def test_cancel_redirects_to_trip_detail(self):
        self.login_user()

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('trip-detail', kwargs={'pk': self.trip.pk}))

    def test_cancel_shows_success_message(self):
        self.login_user()

        response = self.client.post(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Cancelled', str(messages[0]))

    def test_other_user_sees_error_message(self):
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )
        self.client.login(username='other', password='testpass123')

        response = self.client.get(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Only the trip owner', str(messages[0]))




