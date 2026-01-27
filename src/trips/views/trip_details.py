from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Trip


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
