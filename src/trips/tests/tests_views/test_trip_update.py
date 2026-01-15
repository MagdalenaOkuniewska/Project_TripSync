from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()

class TripUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        self.trip = Trip.objects.create(
            title='Original Trip',
            destination='Example',
            start_date='2026-07-01',
            end_date='2026-07-14',
            owner=self.user
        )

        self.url = reverse('trip-update', kwargs={'pk': self.trip.pk})

    def login_user(self):
        self.client.login(username='user', password='testpass123')

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_owner_can_update_trip(self):
        self.login_user()

        data = {
            'title': 'My Trip',
            'destination': 'Example',
            'start_date': '2026-07-01',
            'end_date': '2026-07-14',
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('trip-detail', kwargs={'pk': self.trip.pk}))

        self.trip.refresh_from_db()
        self.assertEqual(self.trip.title, 'My Trip')
        self.assertEqual(self.trip.destination, 'Example')

    def test_shows_success_message_after_update(self):
        self.login_user()

        data = {
            'title': 'My Trip',
            'destination': 'New Example',
            'start_date': '2026-07-01',
            'end_date': '2026-07-14',
        }

        response = self.client.post(self.url, data)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('has been updated', str(messages[0]))

    def test_non_owner_cannot_update_trip(self):
        self.client.login(username='otheruser', password='testpass123')

        data = {
            'title': 'My Trip',
            'destination': 'New Example',
            'start_date': '2026-07-01',
            'end_date': '2026-07-14',
        }

        self.client.post(self.url, data)

        self.trip.refresh_from_db()
        self.assertEqual(self.trip.title, 'Original Trip')

    def test_non_owner_sees_error_message(self):
        self.client.login(username='otheruser', password='testpass123')

        response = self.client.get(self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Only the Trip Owner', str(messages[0]))

    def test_form_shows_current_trip_data(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertContains(response, 'Original Trip')
        self.assertContains(response, 'Example')
