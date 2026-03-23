from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from trips.models import TripMember
from notes.models import Note
from .factories import UserFactory, TripFactory, NoteFactory


class NoteListViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.note = NoteFactory(user=self.user, trip=self.trip)

        self.url = reverse("note-list", kwargs={"trip_id": self.trip.pk})
        self.client.force_login(self.user)

    def test_page_loads_for_member(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_list.html")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_is_redirected(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("trip-list"))

    def test_owner_sees_own_private_note(self):
        response = self.client.get(self.url)

        self.assertIn(self.note, response.context["private_notes"])

    def test_member_sees_shared_note(self):
        shared_note = NoteFactory(user=self.user, trip=self.trip, note_type="shared")
        member = UserFactory()

        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)

        response = self.client.get(self.url)

        self.assertIn(shared_note, response.context["shared_notes"])

    def test_member_cannot_see_private_note_of_other_user(self):
        member = UserFactory()
        TripMember.objects.create(trip=self.trip, user=member)
        self.client.force_login(member)

        response = self.client.get(self.url)

        self.assertNotIn(self.note, response.context["private_notes"])


class NoteCreateViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.url = reverse("note-create", kwargs={"trip_id": self.trip.pk})

        self.client.force_login(self.user)
        self.data = {"title": "New Note", "content": "Content", "note_type": "private"}

    def test_page_loads_for_member(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_create.html")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_member_is_redirected(self):
        other = UserFactory()
        self.client.force_login(other)

        response = self.client.post(self.url, self.data)

        self.assertRedirects(response, reverse("trip-list"))

    def test_note_created_successfully(self):
        self.client.post(self.url, self.data)

        self.assertTrue(Note.objects.filter(title="New Note", trip=self.trip).exists())

    def test_redirects_after_success(self):
        response = self.client.post(self.url, self.data)

        self.assertRedirects(
            response, reverse("note-list", kwargs={"trip_id": self.trip.id})
        )

    def test_user_set_as_note_owner(self):
        self.client.post(self.url, self.data)
        note = Note.objects.get(title="New Note")

        self.assertEqual(note.user, self.user)

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("created successfully", str(messages[0]))


class NoteDetailViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.note = NoteFactory(user=self.user, trip=self.trip, note_type="private")

        self.url = reverse("note-detail", kwargs={"pk": self.note.pk})
        self.client.force_login(self.user)

    def test_owner_can_view_private_note(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_details.html")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_owner_cannot_view_private_note(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("trip-list"))

    def test_participant_can_view_shared_note(self):
        shared_note = NoteFactory(user=self.user, trip=self.trip, note_type="shared")
        participant = UserFactory()

        TripMember.objects.create(trip=self.trip, user=participant)
        self.client.force_login(participant)
        response = self.client.get(
            reverse("note-detail", kwargs={"pk": shared_note.pk})
        )

        self.assertEqual(response.status_code, 200)


class NoteUpdateViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.note = NoteFactory(user=self.user, trip=self.trip)

        self.url = reverse("note-edit", kwargs={"pk": self.note.pk})
        self.client.force_login(self.user)
        self.data = {
            "title": "Updated",
            "content": "Updated content",
            "note_type": "private",
        }

    def test_owner_can_update_note(self):
        self.client.post(self.url, self.data)
        self.note.refresh_from_db()

        self.assertEqual(self.note.title, "Updated")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_owner_cannot_update(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url, self.data)

        self.assertRedirects(response, reverse("trip-list"))

    def test_redirects_after_success(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(
            response, reverse("note-list", kwargs={"trip_id": self.trip.pk})
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url, self.data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("updated successfully", str(messages[0]))


class NoteDeleteViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.note = NoteFactory(user=self.user, trip=self.trip)

        self.url = reverse("note-delete", kwargs={"pk": self.note.pk})
        self.client.force_login(self.user)

    def test_owner_can_delete_note(self):
        self.client.post(self.url)

        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_non_owner_cannot_delete(self):
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("trip-list"))
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_redirects_after_success(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response, reverse("note-list", kwargs={"trip_id": self.trip.pk})
        )

    def test_shows_success_message(self):
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertIn("deleted successfully", str(messages[0]))
