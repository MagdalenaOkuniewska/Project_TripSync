from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import TripInvite


class TripInviteCancelView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TripInvite
    template_name = "trips/trip_invite_cancel.html"

    def test_func(self):
        invite = self.get_object()
        return invite.trip.owner == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only the trip owner can cancel invitations.")
        return redirect("trip-list")

    def form_valid(self, form):
        invite = self.get_object()

        try:
            username = invite.user.username
            trip_id = invite.trip.id
            invite.cancel()
            messages.success(
                self.request, f'Invitation to "{username}" has been Cancelled.'
            )
            return redirect("trip-detail", pk=trip_id)

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect("trip-detail", pk=invite.trip.id)

    def get_success_url(self):
        return reverse_lazy("trip-detail", kwargs={"pk": self.object.trip.id})
