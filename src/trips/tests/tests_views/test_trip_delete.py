from django.test import TestCase
from django.contrib.auth import get_user_model
from ...models import Trip
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()

class TripDeleteViewTest(TestCase):
    def setUp(self):

        self.owner = User.objects.create_user(
            username='owner',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )

        self.trip = Trip.objects.create(
            title='Test Trip',
            destination='Example',
            start_date='2026-07-01',
            end_date='2026-07-14',
            owner=self.owner
        )
        self.url = reverse('trip-delete',  kwargs={'pk': self.trip.pk})

    def test_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_owner_can_view_delete_page(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trip_delete.html')

    def test_owner_can_delete_trip(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('trip-list'))
        self.assertFalse(Trip.objects.filter(pk=self.trip.pk).exists())

    def test_shows_success_message_after_delete(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.post(self.url, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('deleted successfully', str(messages[0]))

    def test_non_owner_cannot_delete_trip(self):
        self.client.login(username='other', password='testpass123')

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Trip.objects.filter(pk=self.trip.pk).exists())

    def test_non_owner_sees_error_message(self):
        self.client.login(username='other', password='testpass123')

        response = self.client.post(self.url, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Only the Trip Owner', str(messages[0]))


