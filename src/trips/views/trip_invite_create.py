from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Trip, TripInvite


class TripInviteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TripInvite
    template_name = "trips/trip_invite_create.html"
    fields = ["user"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trip_id"] = self.kwargs["trip_id"]

        trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        context["trip"] = trip
        return context

    def test_func(self):
        self.trip = Trip.objects.get(
            id=self.kwargs["trip_id"]
        )  # self -> atrybut klasy użyty w innych metodach poniżej
        return self.trip.owner == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only the Trip Owner can invite to a Trip.")
        return redirect("trip-list")

    def form_valid(self, form):
        form.instance.trip = self.trip
        form.instance.invited_by = self.request.user
        messages.success(
            self.request, f"Invitation sent to {form.instance.user.username}."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("trip-detail", kwargs={"pk": self.trip.id})
