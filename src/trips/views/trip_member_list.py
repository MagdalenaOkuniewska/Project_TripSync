from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Trip, TripMember


class TripMemberListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = TripMember
    template_name = "trips/trip_member_list.html"
    context_object_name = "members"

    def test_func(self):
        self.trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        return self.trip.is_owner(self.request.user) or self.trip.is_participant(
            self.request.user
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            "You cannot view members of this Trip - only members and owners have access.",
        )
        return redirect("trip-list")

    def get_queryset(self):
        return self.trip.members.all().order_by("-role", "-joined_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trip"] = self.trip
        return context
