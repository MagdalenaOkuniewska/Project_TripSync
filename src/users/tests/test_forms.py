from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from ..forms import UserRegistrationForm, UserUpdateForm, CustomPasswordResetForm
from .factories import UserFactory

User = get_user_model()


class UserRegistrationFormTest(TestCase):

    def test_valid_data(self):
        form = UserRegistrationForm(
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "olduser321",
                "password2": "olduser321",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_email(self):
        form = UserRegistrationForm(
            data={
                "username": "newuser",
                "email": "",
                "password1": "olduser321",
                "password2": "olduser321",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class UserUpdateFormTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_valid_data(self):
        form = UserUpdateForm(
            data={
                "username": "updateduser",
                "email": self.user.email,
                "first_name": "Jan",
                "last_name": "Nowak",
            },
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, "Jan")

    def test_email_field_is_readonly(self):
        form = UserUpdateForm(instance=self.user)
        self.assertEqual(form.fields["email"].widget.attrs["readonly"], "readonly")

    def test_with_avatar(self):
        buffer = BytesIO()
        Image.new("RGB", (100, 100), color="red").save(buffer, "PNG")
        avatar = SimpleUploadedFile(
            "test_avatar.jpg", buffer.getvalue(), content_type="image/jpeg"
        )
        form = UserUpdateForm(
            data={
                "username": self.user.username,
                "email": self.user.email,
                "first_name": "",
                "last_name": "",
            },
            files={"avatar": avatar},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)


class CustomPasswordResetFormTest(TestCase):

    def setUp(self):
        self.user = UserFactory(email="existing@example.com")

    def test_valid_email(self):
        form = CustomPasswordResetForm(data={"email": "existing@example.com"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_nonexistent_email_raises_error(self):
        form = CustomPasswordResetForm(data={"email": "nobody@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"][0], "Email does not exist. Please try again."
        )
