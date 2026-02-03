from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import DeleteView, DetailView, View, ListView
from ..models import PackingList
from trips.models import Trip


# Private list: każdy uczestnik tripu ma swoją
# Shared list: tylko JEDNA na trip, tworzy ją owner
# Lista NIE edytowalna (trip/user/type) => tylko itemy sie edytuje =  "Add Item" Na stronie Packing List Details (w HTML template)
# 1. user klika create new packing list lub use template packing list w trip details
# 2. nowa lista -> pusta -> dodaje items => TUTAJ CREATE
# 3. z template -> aplikuje do tripu => jakiś Apply View? w packing list template views
# Lista list (shared zrobiona przez ownera i prywatna) - w Trip detail => HTML


class PackingListDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PackingList
    template_name = "packing_lists/packing_list_details.html"
    context_object_name = "packing_list"

    def test_func(self):
        packing_list = self.get_object()

        if packing_list.list_type == "private":
            return packing_list.user == self.request.user
        else:
            return packing_list.trip.is_owner(
                self.request.user
            ) or packing_list.trip.is_participant(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot view this list.")
        return redirect("trip-list")


class PackingListCreateView(LoginRequiredMixin, View):
    """Creates an empty Packing List."""

    def post(self, request, *args, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])

        if not (trip.is_owner(request.user) or trip.is_participant(request.user)):
            messages.error(request, "You cannot create a packing list for this trip.")
            return redirect("trip-list")

        existing_private_list = PackingList.objects.filter(
            trip=trip, user=request.user, list_type="private"
        ).first()

        if existing_private_list:
            messages.warning(request, "You already have a packing list for this trip.")
            return redirect("packing-list-details", pk=existing_private_list.pk)

        packing_list = PackingList.objects.create(
            trip=trip,
            user=request.user,
            list_type="private",
        )

        messages.success(request, f'Packing list for "{trip.title}" created!')
        return redirect("packing-list-details", pk=packing_list.pk)


class PackingListsForTripView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Shows ALL packing lists for a trip (private + shared)"""

    model = PackingList
    template_name = "packing_lists/packing_lists_for_trip.html"
    context_object_name = "packing_lists"

    def test_func(self):
        self.trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        return self.trip.is_owner(self.request.user) or self.trip.is_participant(
            self.request.user
        )

    def get_queryset(self):
        return PackingList.objects.filter(
            Q(trip=self.trip, user=self.request.user, list_type="private")
            | Q(trip=self.trip, list_type="shared")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trip"] = self.trip
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot view lists for this trip.")
        return redirect("trip-list")


class PackingListDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PackingList
    template_name = "packing_lists/packing_list_delete.html"

    def test_func(self):
        packing_list = self.get_object()

        if packing_list.list_type == "private":
            return packing_list.user == self.request.user
        else:
            return packing_list.trip.is_owner(self.request.user)

    def delete(self, request, *args, **kwargs):
        self.trip_pk = self.get_object().trip.pk
        return super().delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(
            self.request, f'Packing list for "{self.object.trip.title}" deleted!'
        )
        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this packing list.")
        return redirect("trip-list")

    def get_success_url(self):
        return reverse_lazy("trip-detail", kwargs={"pk": self.trip_pk})
