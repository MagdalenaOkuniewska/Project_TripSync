from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import TripInvite


class TripInviteRespondView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TripInvite
    template_name = "trips/trip_invite_confirm.html"
    fields = []

    def test_func(self):
        invite = self.get_object()
        return invite.user == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request, "You cannot access this invitation as it is not yours."
        )
        return redirect("trip-invite-list")

    def get_context_data(self, **kwargs):
        """Passing 'response' to HTML template"""
        context = super().get_context_data(**kwargs)
        context["response"] = self.request.GET.get("response", "accept")
        return context

    def post(self, request, *args, **kwargs):
        invite = self.get_object()
        response = request.POST.get("response")

        try:
            if response == "accept":
                invite.accept()
                messages.success(
                    self.request, f'Invitation to "{invite.trip.title}" Accepted.'
                )
                return redirect("trip-detail", pk=invite.trip.id)
            elif response == "decline":
                invite.decline()
                messages.success(
                    self.request, f'Invitation to "{invite.trip.title}" Declined.'
                )
                return redirect("trip-invite-list")

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect("trip-invite-list")

        return redirect("trip-invite-list")

    def get_success_url(self):
        return reverse_lazy("trip-detail", kwargs={"pk": self.object.trip.id})
