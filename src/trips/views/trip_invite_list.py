from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import TripInvite


class TripInviteListView(LoginRequiredMixin, ListView):
    model = TripInvite
    template_name = 'trips/trip_invite_list.html'
    context_object_name = 'invites'
    ordering = ['-created_at']

    def get_queryset(self):
        """Pendning invites"""
        invites = TripInvite.objects.filter(user=self.request.user, status='pending')

        for invite in invites:
            invite.mark_expired()

        return TripInvite.objects.filter(user=self.request.user, status='pending').distinct()