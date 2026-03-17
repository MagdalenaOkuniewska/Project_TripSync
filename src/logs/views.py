from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.contenttypes.models import ContentType

from trips.models import Trip
from .models import AuditLog


class TripAuditLogView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AuditLog
    template_name = "logs/trip_audit_log.html"
    context_object_name = "logs"

    def test_func(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        return trip.is_owner(self.request.user) or trip.is_participant(
            self.request.user
        )

    def handle_no_permission(self):
        messages.error(
            self.request, "You do not have access to this trip activity log."
        )
        return redirect("trip-list")

    def get_queryset(self):
        self.trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        content_type = ContentType.objects.get_for_model(Trip)

        return AuditLog.objects.filter(
            content_type=content_type, object_id=self.trip.pk
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trip"] = self.trip
        return context
