from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip, TripMember
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()

class TripDetailViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='testpass123'
        )

        self.participant = User.objects.create_user(
            username='participant',
            password='testpass123'
        )

        self.trip = Trip.objects.create(
            title='Test Trip',
            destination='Example',
            start_date='2026-07-01',
            end_date='2026-07-14',
            owner=self.owner
        )

        self.url = reverse('trip-detail', kwargs={'pk': self.trip.pk})

        TripMember.objects.create(
            trip=self.trip,
            user=self.participant
        )


    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_owner_can_view_trip(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_details.html')

    def test_participant_can_view_trip(self):
        self.client.login(username='participant', password='testpass123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_details.html')

    def test_random_user_cannot_view_trip(self):
        self.random_user = User.objects.create_user(
            username='random_user',
            password='testpass123'
        )
        self.client.login(username='random_user',
            password='testpass123')

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('trip-list'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('not allowed', str(messages[0]))


    def test_displays_correct_trip_data(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.get(self.url)

        self.assertContains(response, 'Test Trip')
        self.assertContains(response, 'Example')
