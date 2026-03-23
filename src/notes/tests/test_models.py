from django.test import TestCase
from trips.models import TripMember
from .factories import UserFactory, TripFactory, NoteFactory


class NoteModelTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trip = TripFactory(owner=self.user)
        self.note = NoteFactory(user=self.user, trip=self.trip, note_type="private")

    # is_owner

    def test_is_owner_returns_true(self):
        self.assertTrue(self.note.is_owner(self.user))

    def test_is_owner_returns_false_for_other_user(self):
        other = UserFactory()
        self.assertFalse(self.note.is_owner(other))

    # can_edit / can_delete

    def test_can_edit_as_owner(self):
        self.assertTrue(self.note.can_edit(self.user))

    def test_can_edit_as_other_user(self):
        other = UserFactory()
        self.assertFalse(self.note.can_edit(other))

    def test_can_delete_as_owner(self):
        self.assertTrue(self.note.can_delete(self.user))

    def test_can_delete_as_other_user(self):
        other = UserFactory()
        self.assertFalse(self.note.can_delete(other))

    # can_view (private note)

    def test_can_view_private_note_as_owner(self):
        self.assertTrue(self.note.can_view(self.user))

    def test_can_view_private_note_as_other_user(self):
        other = UserFactory()
        self.assertFalse(self.note.can_view(other))

    # can_view (shared note)

    def test_can_view_shared_note_as_trip_participant(self):
        shared_note = NoteFactory(user=self.user, trip=self.trip, note_type="shared")
        participant = UserFactory()
        TripMember.objects.create(trip=self.trip, user=participant)
        self.assertTrue(shared_note.can_view(participant))

    def test_can_view_shared_note_as_non_participant(self):
        shared_note = NoteFactory(user=self.user, trip=self.trip, note_type="shared")
        outsider = UserFactory()
        self.assertFalse(shared_note.can_view(outsider))

    # __str__

    def test_str_method(self):
        self.assertEqual(
            str(self.note), f" Note: {self.note.title} - Trip: {self.trip.title}"
        )
