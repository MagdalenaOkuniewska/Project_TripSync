from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import TripMember


class TripMemberRemoveView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        member = get_object_or_404(TripMember, pk=self.kwargs["member_id"])
        return member.trip.is_owner(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Only the trip owner can remove members.")
        return redirect("trip-list")

    def get(self, request, member_id):
        member = get_object_or_404(TripMember, pk=member_id)
        return render(request, "trips/trip_member_remove.html", {"member": member})

    def post(self, request, member_id):
        member = get_object_or_404(TripMember, pk=member_id)
        trip_id = member.trip.pk
        try:
            member.remove(performed_by=request.user)
            messages.success(request, "Member has been removed.")
            return redirect("trip-member-list", trip_id=trip_id)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("trip-member-list", trip_id=trip_id)
