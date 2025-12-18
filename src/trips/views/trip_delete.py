from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Trip


class TripDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Trip
    template_name = 'trips/trip_delete.html'
    success_url = reverse_lazy('trip-list')

    def get_success_url(self):
        messages.success(self.request, 'Trip has been deleted successfully.')
        return super().get_success_url()

    def test_func(self):
        trip = self.get_object()
        return trip.is_owner(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, 'Only the Trip Owner can delete this Trip.')
        return redirect('trip-list')
