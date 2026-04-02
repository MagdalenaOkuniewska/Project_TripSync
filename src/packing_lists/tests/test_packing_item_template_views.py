from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from packing_lists.models import PackingItemTemplate
from .factories import (
    UserFactory,
    PackingListTemplateFactory,
    PackingItemTemplateFactory,
)


class PackingItemTemplateCreateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.template = PackingListTemplateFactory(user=self.user)
        self.url = reverse(
            "packing-item-template-create", kwargs={"template_pk": self.template.pk}
        )
        self.client.force_login(self.user)
        self.data = {"name": "Sunscreen", "quantity": 2}

    def test_owner_can_create_item(self):
        self.client.post(self.url, self.data)
        self.assertTrue(
            PackingItemTemplate.objects.filter(
                name="Sunscreen", template=self.template
            ).exists()
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_add_item(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("packing-list-template-list"))

    def test_redirects_to_template_detail(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(
            response,
            reverse("packing-list-template-details", kwargs={"pk": self.template.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("added", str(messages[0]))


class PackingItemTemplateUpdateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.template = PackingListTemplateFactory(user=self.user)
        self.item = PackingItemTemplateFactory(
            template=self.template, name="Old Name", quantity=1
        )
        self.url = reverse("packing-item-template-update", kwargs={"pk": self.item.pk})
        self.client.force_login(self.user)
        self.data = {"name": "New Name", "quantity": 3}

    def test_owner_can_update_item(self):
        self.client.post(self.url, self.data)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "New Name")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_update(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("packing-list-template-list"))

    def test_redirects_to_template_detail(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(
            response,
            reverse("packing-list-template-details", kwargs={"pk": self.template.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("updated", str(messages[0]))


class PackingItemTemplateDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.template = PackingListTemplateFactory(user=self.user)
        self.item = PackingItemTemplateFactory(template=self.template)
        self.url = reverse("packing-item-template-delete", kwargs={"pk": self.item.pk})
        self.client.force_login(self.user)

    def test_owner_can_delete_item(self):
        self.client.post(self.url)
        self.assertFalse(PackingItemTemplate.objects.filter(pk=self.item.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_delete(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("packing-list-template-list"))
        self.assertTrue(PackingItemTemplate.objects.filter(pk=self.item.pk).exists())

    def test_redirects_to_template_detail(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("packing-list-template-details", kwargs={"pk": self.template.pk}),
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))
