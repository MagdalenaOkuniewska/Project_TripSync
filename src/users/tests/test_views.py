from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import UserRegistrationForm, UserUpdateForm, CustomPasswordResetForm
from trips.models import Trip
from django.utils import timezone
from django.contrib.messages import get_messages
from django.urls import reverse
User = get_user_model()

class RegistrationViewTest(TestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_registration_page_load_correctly(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

    def test_registration_success(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'olduser321',
            'password2': 'olduser321'
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Account created for newuser')

    def test_registration_fails_with_invalid_data(self):
        User.objects.create_user(
            username='takenuser',
            email='test@example.com',
            password='<Password>'
        )
        data = {
            'username': 'takenuser',
            'email': 'newuser@example.com',
            'password1': 'olduser321',
            'password2': 'olduser321'
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.filter(username='takenuser').count(), 1
        )

        form = response.context['form']

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class ProfileViewTest(TestCase):
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.create_user(
            username='testuser',
            email='email@example.com',
            password='custompassword123'
        )

        self.trip1 = Trip.objects.create(
            title="Trip 1",
            destination="Destination 1",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            owner=self.user
        )
        self.trip2 = Trip.objects.create(
            title="Trip 2",
            destination="Destination 2",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            owner=self.user
        )

    def test_profile_page_load_correctly(self):
        self.client.login(username='testuser', password='custompassword123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

        self.assertIn('user_trips', response.context)
        self.assertIn(self.trip1, response.context['user_trips'])
        self.assertIn(self.trip2, response.context['user_trips'])

    def test_profile_requires_login(self):
        response = self.client.get(self.url)
        expected_url = f'{reverse("login")}?next={self.url}'
        self.assertRedirects(response, expected_url)


class ProfileEditViewTest(TestCase):
    def setUp(self):
        self.url = reverse('edit_profile')
        self.user = User.objects.create_user(
            username='testuser',
            email='email@example.com',
            password='custompassword123'
        )

    def test_profile_page_load_correctly(self):
        self.client.login(username='testuser',
            password='custompassword123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/edit_profile.html')
        self.assertIsInstance(response.context['form'], UserUpdateForm)

    def test_profile_requires_login(self):
        """Tests if not logged-in user is redirected to login page"""
        response = self.client.get(self.url)
        expected_url = f'{reverse('login')}?next={self.url}'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)

    def test_profile_update_success(self):
        self.client.login(username='testuser',
                          password='custompassword123')

        data = {
            'username':'testuser',
            'email':'email@example.com',
            'first_name':'Jan',
            'last_name':'testlast',}

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('profile'))

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jan')

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your account has been updated!')


class CustomPasswordResetViewTest(TestCase):
    def setUp(self):
        self.url = reverse('password_reset')
        self.user = User.objects.create_user(
            username='testuser',
            email='existingemail@example.com',
            password='custompassword123'
        )

    def test_password_reset_page_load_correctly(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset.html')
        self.assertIsInstance(response.context['form'], CustomPasswordResetForm)

    def test_password_reset_with_valid_email(self):
        data = {
            'email': 'existingemail@example.com'}

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('password_reset_done'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Password reset email was sent to "{data["email"]}". Please check your inbox and follow instructions.')

    def test_password_reset_with_nonexistent_email(self):
        data = {'email': 'nonexistent@example.com'}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)






