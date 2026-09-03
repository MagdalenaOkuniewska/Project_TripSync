from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from ..models import Trip


class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = "trips/trip_list.html"
    context_object_name = "trips"

    def get_queryset(self):
        """Trips where User is on Owner OR a Participant"""
        user = self.request.user
        return (
            Trip.objects.filter(Q(owner=user) | Q(members__user=user))
            .distinct()
            .order_by("-created_at")
        )
