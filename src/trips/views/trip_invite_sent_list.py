from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import TripInvite


class TripInviteSentListView(LoginRequiredMixin, ListView):
    model = TripInvite
    template_name = "trips/trip_invite_sent_list.html"
    context_object_name = "sent_invites"

    def get_queryset(self):
        """Invites sent by logged in user"""
        return TripInvite.objects.filter(trip__owner=self.request.user).order_by(
            "-created_at"
        )
