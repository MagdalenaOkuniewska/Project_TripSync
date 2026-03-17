from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Trip, TripMember


class TripMemberLeaveView(LoginRequiredMixin, View):

    def get(self, request, trip_id):
        trip = get_object_or_404(Trip, pk=trip_id)
        member = get_object_or_404(TripMember, trip=trip, user=request.user)
        return render(
            request, "trips/trip_member_leave.html", {"trip": trip, "member": member}
        )

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, pk=trip_id)
        member = get_object_or_404(TripMember, trip=trip, user=request.user)
        try:
            member.leave()
            messages.success(request, f'You have left "{trip.title}".')
            return redirect("trip-list")
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("trip-detail", pk=trip_id)
