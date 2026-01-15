from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from ..models import TripInvite


class TripInviteListView(LoginRequiredMixin, ListView):
    model = TripInvite
    template_name = 'trips/trip_invite_list.html'
    context_object_name = 'invites'
    ordering = ['-created_at']

    def get_queryset(self): # TODO in the future -> Periodic Celery Task.
        """Pendning invites"""
        user  = self.request.user

        TripInvite.objects.filter(
            user=user,
            status='pending',
            expires_at__lte=timezone.now()
        ).update(status='expired')


        # invites = TripInvite.objects.filter(user=self.request.user, status='pending')

        # for invite in invites:
            # invite.mark_expired()

        return TripInvite.objects.filter(user=self.request.user, status='pending').select_related('trip', 'invited_by')