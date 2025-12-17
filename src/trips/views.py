from django.contrib import messages
from django.core.exceptions import ValidationError
from django.template.context_processors import request
from django.shortcuts import redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Trip, TripInvite, TripMember
from .forms import TripForm


class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'
    ordering = ['-created_at']

    def get_queryset(self):
        """Trips where User is on Owner OR a Participant"""
        user = self.request.user
        return Trip.objects.filter(Q(owner=user) | Q(members__user=user)).distinct()

class TripDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Trip
    template_name = 'trips/trip_details.html'
    context_object_name = 'trip'

    def test_func(self):
        """Tests if User is either an Owner or a Participant"""
        trip = self.get_object()
        return  trip.is_owner(self.request.user) or trip.is_participant(self.request.user)

    def handle_no_permission(self):
        """Handles no permission in case User is neither Owner/Patricipant"""
        messages.error(self.request, 'You are not allowed to view this Trip.')
        return redirect('trip-list')

class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_create.html'

    def get_success_url(self):
        """Redirect to details of created trip"""
        return reverse_lazy('trip-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Sets up logged-in User as an Owner adn saves it to db"""
        form.instance.owner = self.request.user
        messages.success(self.request, f'Your trip "{form.instance.title}" has been created.')
        return super().form_valid(form)

class TripUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_create.html'

    def get_success_url(self):
        """Redirect to details of created trip"""
        return reverse_lazy('trip-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f'Your trip "{form.instance.title}"has been updated.')
        return super().form_valid(form)

    def test_func(self):
        trip = self.get_object()
        return trip.is_owner(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, 'Only the Trip Owner can edit this Trip.')
        return redirect('trip-list')


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



class TripInviteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TripInvite
    template_name = 'trips/trip_invite_create.html'
    fields = ['user']

    def test_func(self):
        self.trip = Trip.objects.get(id=self.kwargs['trip_id'])
        return self.trip.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Only the Trip Owner can invite to a Trip.')
        return redirect('trip-list')

    def form_valid(self, form):
        form.instance.trip = self.trip
        form.instance.invited_by = self.request.user
        messages.success(self.request, f'Invitation sent to {form.instance.user.username}.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trip-detail', kwargs={'pk': self.trip.id})


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

class TripInviteRespondView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TripInvite
    template_name = 'trips/trip_invite_confirm.html'
    fields = []

    def test_func(self):
        invite = self.get_object()
        return invite.user == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'You cannot access this invitation as it is not yours.')
        return redirect('trip-invite-list')

    def get_context_data(self, **kwargs):
        """Passing 'response' to HTML template"""
        context = super().get_context_data(**kwargs)
        context['response'] = self.kwargs.get('response')  # 'accept' lub 'decline'
        return context

    def form_valid(self, form):
        invite = self.get_object()
        response = self.kwargs.get('response') #from URL .../<str:response>/

        try:
            if response == 'accept':
                invite.accept()
                messages.success(self.request, f'Invitation to "{invite.trip.title}" Accepted.')
                return redirect('trip-detail', pk=invite.trip.id)

            elif response == 'decline':
                invite.decline()
                messages.success(self.request, f'Invitation to "{invite.trip.title}" Declined.')
                return redirect('trip-invite-list')

        except ValidationError as e:
            messages.error(self.request,str(e))
            return redirect('trip-invite-list')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trip-detail', kwargs={'pk': self.object.trip.id})


class TripInviteCancelView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = TripInvite
    template_name = 'trips/trip_invite_cancel.html'

    def test_func(self):
        invite = self.get_object()
        return invite.trip.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Only the trip owner can cancel invitations.')
        return redirect('trip-list')

    def form_valid(self, form):
        invite = self.get_object()

        try:
            username = invite.user.username
            trip_id = invite.trip.id
            invite.cancel()
            messages.success(self.request, f'Invitation to "{username}" has been Cancelled.')
            return redirect('trip-detail', pk=trip_id)

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect('trip-detail', pk=invite.trip.id)

    def get_success_url(self):
        return reverse_lazy('trip-detail', kwargs={'pk': self.object.trip.id})


