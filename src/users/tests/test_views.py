from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from ..forms import UserRegistrationForm, UserUpdateForm, CustomPasswordResetForm
from .factories import UserFactory, TripFactory

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.dummy.EmailBackend")
class RegistrationViewTest(TestCase):

    def setUp(self):
        self.url = reverse("register")
        self.valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "olduser321",
            "password2": "olduser321",
        }

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertIsInstance(response.context["form"], UserRegistrationForm)

    def test_registration_creates_inactive_user(self):
        self.client.post(self.url, self.valid_data)
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_active)

    def test_registration_redirects_after_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse("login"))

    def test_registration_shows_check_email_message(self):
        response = self.client.post(self.url, self.valid_data)
        msgs = list(get_messages(response.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertIn("email", str(msgs[0]).lower())

    def test_registration_fails_with_taken_username(self):
        UserFactory(username="takenuser")
        data = {
            "username": "takenuser",
            "email": "other@example.com",
            "password1": "olduser321",
            "password2": "olduser321",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="takenuser").count(), 1)
        self.assertIn("username", response.context["form"].errors)


class ProfileViewTest(TestCase):

    def setUp(self):
        self.url = reverse("profile")
        self.user = UserFactory()
        self.trip1 = TripFactory(owner=self.user)
        self.trip2 = TripFactory(owner=self.user)
        self.client.force_login(self.user)

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

    def test_shows_user_trips(self):
        response = self.client.get(self.url)
        self.assertIn(self.trip1, response.context["user_trips"])
        self.assertIn(self.trip2, response.context["user_trips"])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class ProfileEditViewTest(TestCase):

    def setUp(self):
        self.url = reverse("edit_profile")
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.update_data = {
            "username": self.user.username,
            "email": self.user.email,
            "first_name": "Jan",
            "last_name": "Nowak",
        }

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/edit_profile.html")
        self.assertIsInstance(response.context["form"], UserUpdateForm)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_update_success(self):
        response = self.client.post(self.url, self.update_data)
        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jan")

    def test_update_shows_success_message(self):
        response = self.client.post(self.url, self.update_data)
        msgs = list(get_messages(response.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertEqual(str(msgs[0]), "Your account has been updated!")


class CustomPasswordResetViewTest(TestCase):

    def setUp(self):
        self.url = reverse("password_reset")
        self.user = UserFactory(email="existing@example.com")

    def test_page_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_reset.html")
        self.assertIsInstance(response.context["form"], CustomPasswordResetForm)

    def test_valid_email_redirects(self):
        response = self.client.post(self.url, {"email": "existing@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))

    def test_valid_email_shows_message(self):
        response = self.client.post(self.url, {"email": "existing@example.com"})
        msgs = list(get_messages(response.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertIn("existing@example.com", str(msgs[0]))

    def test_nonexistent_email_shows_error(self):
        response = self.client.post(self.url, {"email": "nobody@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)


class SearchUsersViewTest(TestCase):

    def setUp(self):
        self.url = reverse("search-users")
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_empty_query_returns_no_results(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["users"]), 0)

    def test_search_by_username(self):
        target = UserFactory(username="findme")
        response = self.client.get(self.url + "?q=findme")
        self.assertIn(target, response.context["users"])

    def test_search_excludes_current_user(self):
        response = self.client.get(self.url + f"?q={self.user.username}")
        self.assertNotIn(self.user, response.context["users"])

    def test_context_contains_my_trips(self):
        TripFactory(owner=self.user)
        response = self.client.get(self.url)
        self.assertIn("my_trips", response.context)
