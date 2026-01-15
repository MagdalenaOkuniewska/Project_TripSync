from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import UserRegistrationForm, UserUpdateForm, CustomPasswordResetForm
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()

class UserFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='<Password>'
        )

    def test_registration_form_valid_data(self):
        """ Tests if from is correct for valid data"""

        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'olduser321',
            'password2': 'olduser321'
        }

        form = UserRegistrationForm(data=form_data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_registration_form_missing_email(self):
        form_data = {
            'username': 'newuser',
            'email': '',
            'password1': 'olduser321',
            'password2': 'olduser321'
        }

        form = UserRegistrationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_update_form_valid_data(self):
        form_data = {
            'username': 'olduser',
            'email': 'newuser@example.com',
            'first_name': 'Jan',
            'last_name': 'Nowak'
        }

        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertEqual(user.first_name, 'Jan')
        self.assertEqual(user.username, 'olduser')


    def test_update_form_email_widget_attrs(self):
        form = UserUpdateForm(instance=self.user)

        self.assertEqual(
            form.fields['email'].widget.attrs['readonly'], 'readonly'
        )

    def test_update_form_with_avatar(self):
        buffer = BytesIO()

        img = Image.new('RGB', (100, 100), color='red')

        img.save(buffer, 'PNG')

        image_file = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=buffer.getvalue(),
            content_type='image/jpeg',
        )

        form_data = {
            'username': 'olduser',
            'email': 'newuser@example.com',
            'first_name': 'Jan',
            'last_name': 'Nowak'
        }
        form_files = {'avatar': image_file}

        form = UserUpdateForm(data=form_data, instance=self.user, files=form_files)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertIsNotNone(user.avatar)
        self.assertTrue(user.avatar.name.endswith('.jpg'), user.avatar.name)

    def test_password_reset_with_valid_email(self):
        form_data = {'email': 'test@example.com'}
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_reset_invalid_email(self):
        form_data = {
            'email': 'invalid_email@example.com',
        }

        form = CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(
            form.errors['email'][0], 'Email does not exist. Please try again.'
        )