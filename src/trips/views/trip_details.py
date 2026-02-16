from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Trip
from notes.models import Note
from shopping_list.models import ShoppingList


class TripDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Trip
    template_name = "trips/trip_details.html"
    context_object_name = "trip"

    def test_func(self):
        """Tests if User is either an Owner or a Participant"""
        trip = self.get_object()
        return trip.is_owner(self.request.user) or trip.is_participant(
            self.request.user
        )

    def handle_no_permission(self):
        """Handles no permission in case User is neither Owner/Patricipant"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You are not allowed to view this Trip.")
        return redirect("trip-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Notes
        context["private_notes_count"] = Note.objects.filter(
            trip=self.object, user=self.request.user, note_type="private"
        ).count()

        context["shared_notes_count"] = Note.objects.filter(
            trip=self.object, note_type="shared"
        ).count()

        # Packing Lists
        has_private_list = self.object.packing_lists.filter(
            user=self.request.user, list_type="private"
        ).exists()

        private_list = self.object.packing_lists.filter(
            user=self.request.user, list_type="private"
        ).first()

        shared_list = self.object.packing_lists.filter(list_type="shared").first()

        context["has_private_list"] = has_private_list
        context["private_list"] = private_list
        context["shared_list"] = shared_list

        # Shopping List
        try:
            context["shopping_list"] = self.object.shopping_list
            context["has_shopping_list"] = True
        except ShoppingList.DoesNotExist:
            context["shopping_list"] = None
            context["has_shopping_list"] = False

        return context
