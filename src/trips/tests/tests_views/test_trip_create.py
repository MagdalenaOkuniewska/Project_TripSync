from django.test import TestCase
from django.contrib.auth import get_user_model
from ...forms import TripForm
from ...models import Trip, TripMember
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()

class TripCreateViewTest(TestCase):
    def setUp(self):
        self.url = reverse('trip-create')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def login_user(self):
        self.client.login(username='testuser', password='testpass123')


    def test_page_loads_correctly(self):
        self.login_user()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_create.html')
        self.assertIsInstance(response.context['form'], TripForm)

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_trip_created_successfully(self):
        self.login_user()

        data = {
            'title': 'TestTrip',
            'destination': 'Example',
            'start_date': '2026-07-01',
            'end_date':'2026-07-14'
        }

        response = self.client.post(self.url, data)

        self.assertTrue(Trip.objects.filter(title='TestTrip', destination = 'Example').exists())

        trip = Trip.objects.get(title='TestTrip')
        self.assertRedirects(response, reverse('trip-detail', kwargs={'pk': trip.pk}))

    def test_logged_user_is_set_as_owner(self):
        self.login_user()

        data = {
            'title': 'TestTrip',
            'destination': 'Example',
            'start_date': '2026-07-01',
            'end_date': '2026-07-14'
        }
        self.client.post(self.url, data)
        trip = Trip.objects.get(title='TestTrip', destination = 'Example')

        self.assertEqual(trip.owner, self.user)

    def test_trip_member_created_for_owner(self):
        self.login_user()

        data = {
            'title': 'TestTrip',
            'destination': 'Example',
            'start_date': '2026-07-01',
            'end_date': '2026-07-14'
        }
        self.client.post(self.url, data)

        trip = Trip.objects.get(title='TestTrip', destination = 'Example')

        self.assertTrue(TripMember.objects.filter(trip=trip, user=self.user).exists())

    def test_shows_success_message(self):
        self.login_user()

        data = {
            'title': 'TestTrip',
            'destination': 'Example',
            'start_date': '2026-07-01',
            'end_date': '2026-07-14'
        }
        response = self.client.post(self.url, data)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('has been created', str(messages[0]))

