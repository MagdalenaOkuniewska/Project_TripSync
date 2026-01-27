from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Trip
from ..forms import TripForm


class TripUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Trip
    form_class = TripForm
    template_name = "trips/trip_create.html"

    def get_success_url(self):
        """Redirect to details of created trip"""
        return reverse_lazy("trip-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(
            self.request, f'Your trip "{form.instance.title}"has been updated.'
        )
        return super().form_valid(form)

    def test_func(self):
        trip = self.get_object()
        return trip.is_owner(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only the Trip Owner can edit this Trip.")
        return redirect("trip-list")
