from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from logs.models import AuditLog
from logs.utils import log_action
from .factories import UserFactory, TripFactory, AuditLogFactory


class AuditLogModelTest(TestCase):

    def setUp(self):
        self.performer = UserFactory()
        self.affected = UserFactory()
        self.trip = TripFactory(owner=self.performer)

        self.log = AuditLogFactory(
            content_object=self.trip,
            action="member_added",
            performed_by=self.performer,
            affected_user=self.affected,
        )

    def test_log_is_created(self):
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_content_type_is_trip(self):
        expected_ct = ContentType.objects.get_for_model(self.trip)

        self.assertEqual(self.log.content_type, expected_ct)

    def test_object_id_matches_trip(self):
        self.assertEqual(self.log.object_id, self.trip.pk)

    def test_content_object_is_trip(self):
        self.assertEqual(self.log.content_object, self.trip)

    def test_ordering_newest_first(self):
        second = AuditLogFactory(content_object=self.trip, action="member_left")
        logs = list(AuditLog.objects.all())

        self.assertEqual(logs[0], second)
        self.assertEqual(logs[1], self.log)


class LogActionUtilTest(TestCase):

    def setUp(self):
        self.performer = UserFactory()
        self.affected = UserFactory()
        self.trip = TripFactory(owner=self.performer)

    def test_creates_audit_log(self):
        log_action("invite_sent", self.trip, self.performer, self.affected)

        self.assertEqual(AuditLog.objects.count(), 1)

    def test_log_has_correct_action(self):
        log_action("invite_sent", self.trip, self.performer, self.affected)
        log = AuditLog.objects.first()

        self.assertEqual(log.action, "invite_sent")

    def test_log_has_correct_performed_by(self):
        log_action("member_removed", self.trip, self.performer, self.affected)
        log = AuditLog.objects.first()

        self.assertEqual(log.performed_by, self.performer)

    def test_log_has_correct_affected_user(self):
        log_action("member_removed", self.trip, self.performer, self.affected)
        log = AuditLog.objects.first()

        self.assertEqual(log.affected_user, self.affected)

    def test_extra_data_defaults_to_empty_dict(self):
        log_action("member_left", self.trip, self.performer)
        log = AuditLog.objects.first()

        self.assertEqual(log.extra_data, {})

    def test_extra_data_is_saved(self):
        log_action(
            "invite_sent", self.trip, self.performer, extra_data={"note": "test"}
        )
        log = AuditLog.objects.first()

        self.assertEqual(log.extra_data, {"note": "test"})
