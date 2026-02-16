from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    DeleteView,
    DetailView,
    View,
)
from ..models import ShoppingList, ShoppingItem
from trips.models import Trip

# List nie ponieważ jeden Trip => 1 grupowy shopping list , brak private/shared itd => bedzie przycisk See Shopping List itd


def user_can_access_trip(user, trip):
    """Checks if user is owner or participant of trip"""
    return trip.is_owner(user) or trip.is_participant(user)


class ShoppingListCreateView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        return trip.is_owner(self.request.user)

    def post(self, request, *args, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])

        try:
            shopping_list = trip.shopping_list
            messages.warning(request, "Shopping list already exists for this trip.")
            return redirect("shopping-list-detail", pk=shopping_list.pk)
        except ShoppingList.DoesNotExist:
            shopping_list = ShoppingList.objects.create(trip=trip)
            messages.success(request, f'Shopping list for "{trip.title}" created!')
            return redirect("shopping-list-detail", pk=shopping_list.pk)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only trip owner can create a shopping list.")
        return redirect("trip-list")


class ShoppingListDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ShoppingList
    template_name = "shopping_list/shopping_list_details.html"
    context_object_name = "shopping_list"

    def test_func(self):
        shopping_list = self.get_object()
        return user_can_access_trip(self.request.user, shopping_list.trip)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot view this shopping list.")
        return redirect("trip-list")


class ShoppingListDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ShoppingList
    template_name = "shopping_list/shopping_list_delete.html"

    def test_func(self):
        shopping_list = self.get_object()
        return shopping_list.trip.is_owner(self.request.user)

    def form_valid(self, form):
        self.trip_pk = self.get_object().trip.pk

        messages.success(
            self.request, f'Shopping list for "{self.object.trip.title}" deleted!'
        )
        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this shopping list.")
        return redirect("trip-list")

    def get_success_url(self):
        return reverse_lazy("trip-detail", kwargs={"pk": self.trip_pk})


@login_required
@require_POST
def toggle_item_purchased(request, item_id):
    try:
        item = ShoppingItem.objects.get(pk=item_id)

        if not user_can_access_trip(request.user, item.shopping_list.trip):
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        data = json.loads(request.body)
        is_purchased = data.get("is_purchased", False)

        # Toggle packed status
        if is_purchased:
            item.marked_as_purchased(request.user)
        else:
            item.is_purchased = False
            item.purchased_by = None
            item.save()

        return JsonResponse(
            {
                "success": True,
                "is_purchased": item.is_purchased,
                "purchased_by": (
                    item.purchased_by.username if item.purchased_by else None
                ),
            }
        )

    except ShoppingItem.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
