from django.test import TestCase
from ..forms import TripForm


class TripFormTest(TestCase):

    def test_valid_data(self):
        form_data = {
            "title": "Trip",
            "destination": "Example",
            "start_date": "2026-07-01",
            "end_date": "2026-07-14",
        }
        form = TripForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_field_is_invalid(self):
        form_data = {
            "title": "",
            "destination": "Example",
            "start_date": "2026-07-01",
            "end_date": "2026-07-14",
        }
        form = TripForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
