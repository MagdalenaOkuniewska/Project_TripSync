from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from ..models import Trip, TripInvite


class TripJoinByLinkView(LoginRequiredMixin, View):
    def get(self, request, token):
        trip = get_object_or_404(Trip, invite_token=token)

        if trip.is_owner(request.user):
            messages.info(request, "You are the owner of this trip.")
            return redirect("trip-detail", pk=trip.pk)

        if trip.is_participant(request.user):
            messages.info(
                request, f"You already are the participant of this trip: {trip.title}"
            )
            return redirect("trip-detail", pk=trip.pk)

        invite, _created = TripInvite.objects.get_or_create(
            trip=trip,
            user=request.user,
            defaults={"invited_by": trip.owner, "status": "pending"},
        )

        return redirect("trip-invite-respond", pk=invite.pk)
