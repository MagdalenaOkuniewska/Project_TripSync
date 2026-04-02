from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from packing_lists.models import PackingListTemplate, PackingList
from .factories import (
    UserFactory,
    TripFactory,
    PackingListTemplateFactory,
    PackingItemTemplateFactory,
)


class PackingListTemplateListViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse("packing-list-template-list")
        self.client.force_login(self.user)

    def test_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "packing_lists/packing_list_template_list.html"
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_only_shows_own_templates(self):
        own = PackingListTemplateFactory(user=self.user)
        other = PackingListTemplateFactory()  # different user
        response = self.client.get(self.url)
        self.assertIn(own, response.context["list_templates"])
        self.assertNotIn(other, response.context["list_templates"])


class PackingListTemplateCreateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse("packing-list-template-create")
        self.client.force_login(self.user)

    def test_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_template_created_with_current_user(self):
        self.client.post(self.url, {"name": "My Template"})
        template = PackingListTemplate.objects.get(name="My Template")
        self.assertEqual(template.user, self.user)

    def test_redirects_to_template_detail(self):
        response = self.client.post(self.url, {"name": "My Template"})
        template = PackingListTemplate.objects.get(name="My Template")
        self.assertRedirects(
            response,
            reverse("packing-list-template-details", kwargs={"pk": template.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, {"name": "My Template"})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("created successfully", str(messages[0]))


class PackingListTemplateDetailViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.template = PackingListTemplateFactory(user=self.user)
        self.url = reverse(
            "packing-list-template-details", kwargs={"pk": self.template.pk}
        )
        self.client.force_login(self.user)

    def test_owner_can_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "packing_lists/packing_list_template_details.html"
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_view(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("packing-list-template-list"))


class PackingListTemplateUpdateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.template = PackingListTemplateFactory(user=self.user)
        self.url = reverse(
            "packing-list-template-update", kwargs={"pk": self.template.pk}
        )
        self.client.force_login(self.user)

    def test_owner_can_update(self):
        self.client.post(self.url, {"name": "Updated Name"})
        self.template.refresh_from_db()
        self.assertEqual(self.template.name, "Updated Name")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_update(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, {"name": "Hacked"})
        self.assertRedirects(response, reverse("packing-list-template-list"))

    def test_shows_success_message(self):
        response = self.client.post(self.url, {"name": "Updated Name"})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("updated", str(messages[0]))


class PackingListTemplateDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.template = PackingListTemplateFactory(user=self.user)
        self.url = reverse(
            "packing-list-template-delete", kwargs={"pk": self.template.pk}
        )
        self.client.force_login(self.user)

    def test_owner_can_delete(self):
        self.client.post(self.url)
        self.assertFalse(
            PackingListTemplate.objects.filter(pk=self.template.pk).exists()
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_delete(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("packing-list-template-list"))
        self.assertTrue(
            PackingListTemplate.objects.filter(pk=self.template.pk).exists()
        )

    def test_redirects_to_template_list_after_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("packing-list-template-list"))

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))


class ApplyPackingListTemplateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.template = PackingListTemplateFactory(user=self.user)
        PackingItemTemplateFactory(template=self.template, name="Towel", quantity=1)
        self.url = reverse(
            "apply-template-to-trip",
            kwargs={"template_pk": self.template.pk, "trip_pk": self.trip.pk},
        )
        self.client.force_login(self.user)

    def test_member_can_apply_template(self):
        self.client.post(self.url)
        self.assertTrue(
            PackingList.objects.filter(trip=self.trip, user=self.user).exists()
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_cannot_apply(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("trip-list"))

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("applied", str(messages[0]))
