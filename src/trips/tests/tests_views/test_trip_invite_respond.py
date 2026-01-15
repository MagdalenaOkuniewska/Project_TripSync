from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember, TripInvite
from django.contrib.messages import get_messages
from django.urls import reverse
User = get_user_model()


class TripInviteRespondViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='testpass123'
        )

        self.invited_user = User.objects.create_user(
            username='invited',
            password='testpass123'
        )

        self.trip = Trip.objects.create(
            title='Test Trip',
            destination='Example',
            start_date='2026-07-01',
            end_date='2026-07-14',
            owner=self.owner
        )

        self.invite = TripInvite.objects.create(
            trip=self.trip,
            user=self.invited_user,
            invited_by=self.owner,
            status='pending'
        )

        self.url = reverse('trip-invite-respond', kwargs={'pk': self.invite.pk})

    def login_user(self):
        self.client.login(username='invited', password='testpass123')

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_invited_user_can_view_page(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_invite_confirm.html')

    def test_other_user_cannot_view_page(self):
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )
        self.client.login(username='other', password='testpass123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/invites/', response.url)

    def test_other_user_sees_error_message(self):
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )
        self.client.login(username='other', password='testpass123')

        response = self.client.get(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('not yours', str(messages[0]))

    def test_accept_changes_status(self):
        self.login_user()

        self.client.post(self.url, {'response': 'accept'})

        self.invite.refresh_from_db()
        self.assertEqual(self.invite.status, 'accepted')

    def test_accept_creates_trip_member(self):
        self.login_user()

        self.client.post(self.url, {'response': 'accept'})

        self.assertTrue(TripMember.objects.filter(trip=self.trip, user=self.invited_user).exists())

    def test_accept_redirects_to_trip_detail(self):
        self.login_user()

        response = self.client.post(self.url, {'response': 'accept'})

        self.assertRedirects(response, reverse('trip-detail', kwargs={'pk': self.invite.pk}))

    def test_accept_shows_success_message(self):
        self.login_user()

        response = self.client.post(self.url, {'response': 'accept'})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Accepted', str(messages[0]))

    def test_decline_changes_status(self):
        self.login_user()

        self.client.post(self.url, {'response': 'decline'})

        self.invite.refresh_from_db()
        self.assertEqual(self.invite.status, 'declined')

    def test_decline_does_not_create_trip_member(self):
        self.login_user()

        self.client.post(self.url, {'response': 'decline'})

        self.assertFalse(TripMember.objects.filter(trip=self.trip, user=self.invited_user).exists())

    def test_decline_redirects_to_invite_list(self):
        self.login_user()

        response = self.client.post(self.url, {'response': 'decline'})

        self.assertRedirects(response, reverse('trip-invite-list'))

    def test_decline_shows_success_message(self):
        self.login_user()

        response = self.client.post(self.url, {'response': 'decline'})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Declined', str(messages[0]))

    def test_response_in_context_default_accept(self):
        self.login_user()

        response = self.client.get(self.url)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['response'], 'accept')

    def test_response_in_context_decline(self):
        self.login_user()

        response = self.client.get(self.url, {'response': 'decline'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['response'], 'decline')
