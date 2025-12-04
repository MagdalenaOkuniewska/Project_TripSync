from django.contrib import messages
from django.template.context_processors import request
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Trip
from .forms import TripForm


class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'
    ordering = ['-created_at']

    def get_queryset(self):
        """Trips where User is on Owner OR a Participant"""
        user = self.request.user
        return Trip.objects.filter(Q(owner=user) | Q(participants=user)).distinct()

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

    def form_valid(self, form):
        """Sets up logged-in User as an Owner adn saves it to db"""
        form.instance.owner = self.request.user
        messages.success(self.request, f'Your trip "{form.instance.title}"has been created.')
        return super().form_valid(form)

class TripUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_create.html'

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

    def test_func(self):
        trip = self.get_object()
        return trip.is_owner(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, 'Only the Trip Owner can delete this Trip.')

    def delete(self, request, *args, **kwargs):
        trip = self.get_object()
        messages.success(self.request, f'Trip "{trip.instance.title}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
