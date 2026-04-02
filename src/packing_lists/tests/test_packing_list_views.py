from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from trips.models import TripMember
from packing_lists.models import PackingList
from .factories import UserFactory, TripFactory, PackingListFactory


class PackingListCreateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.url = reverse("packing-list-create", kwargs={"trip_pk": self.trip.pk})
        self.client.force_login(self.user)

    def test_owner_can_create_packing_list(self):
        self.client.post(self.url)
        self.assertTrue(
            PackingList.objects.filter(trip=self.trip, user=self.user).exists()
        )

    def test_participant_can_create_packing_list(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        self.client.post(self.url)
        self.assertTrue(
            PackingList.objects.filter(trip=self.trip, user=member).exists()
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_cannot_create(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("trip-list"))

    def test_redirects_to_packing_list_detail(self):
        response = self.client.post(self.url)
        packing_list = PackingList.objects.get(trip=self.trip, user=self.user)
        self.assertRedirects(
            response, reverse("packing-list-details", kwargs={"pk": packing_list.pk})
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("created", str(messages[0]))

    def test_duplicate_shows_warning(self):
        PackingListFactory(trip=self.trip, user=self.user, list_type="private")
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("already have", str(messages[0]))


class PackingListCreateSharedViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.url = reverse(
            "packing-list-create-shared", kwargs={"trip_pk": self.trip.pk}
        )
        self.client.force_login(self.user)

    def test_owner_can_create_shared_list(self):
        self.client.post(self.url)
        self.assertTrue(
            PackingList.objects.filter(trip=self.trip, list_type="shared").exists()
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_owner_cannot_create_shared_list(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("trip-list"))

    def test_duplicate_shared_list_shows_error(self):
        PackingListFactory(trip=self.trip, user=None, list_type="shared")
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("already exists", str(messages[0]))


class PackingListDetailViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.packing_list = PackingListFactory(
            trip=self.trip, user=self.user, list_type="private"
        )
        self.url = reverse("packing-list-details", kwargs={"pk": self.packing_list.pk})
        self.client.force_login(self.user)

    def test_owner_can_view_private_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "packing_lists/packing_list_details.html")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_view_private_list(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("trip-list"))

    def test_participant_can_view_shared_list(self):
        shared_list = PackingListFactory(trip=self.trip, user=None, list_type="shared")
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)
        response = self.client.get(
            reverse("packing-list-details", kwargs={"pk": shared_list.pk})
        )
        self.assertEqual(response.status_code, 200)


class PackingListDeleteViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.packing_list = PackingListFactory(
            trip=self.trip, user=self.user, list_type="private"
        )
        self.url = reverse("packing-list-delete", kwargs={"pk": self.packing_list.pk})
        self.client.force_login(self.user)

    def test_owner_can_delete_private_list(self):
        self.client.post(self.url)
        self.assertFalse(PackingList.objects.filter(pk=self.packing_list.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_other_user_cannot_delete_private_list(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("trip-list"))
        self.assertTrue(PackingList.objects.filter(pk=self.packing_list.pk).exists())

    def test_trip_owner_can_delete_shared_list(self):
        shared_list = PackingListFactory(trip=self.trip, user=None, list_type="shared")
        self.client.post(reverse("packing-list-delete", kwargs={"pk": shared_list.pk}))
        self.assertFalse(PackingList.objects.filter(pk=shared_list.pk).exists())

    def test_redirects_to_trip_detail_after_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response, reverse("trip-detail", kwargs={"pk": self.trip.pk})
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("deleted", str(messages[0]))


class PackingListsForTripViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.url = reverse("packing-lists-for-trip", kwargs={"trip_pk": self.trip.pk})
        self.client.force_login(self.user)

    def test_member_can_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "packing_lists/packing_lists_for_trip.html")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_is_redirected(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("trip-list"))
