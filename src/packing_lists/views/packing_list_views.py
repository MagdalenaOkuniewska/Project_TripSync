from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import DeleteView, DetailView, View, ListView
from ..models import PackingList, PackingListTemplate, PackingItemTemplate, PackingItem
from trips.models import Trip


def user_can_access_trip(user, trip):
    """Checks if user is owner or participant of trip"""
    return trip.is_owner(user) or trip.is_participant(user)


def user_can_access_packing_list(user, packing_list):
    """Checks if user can access this packing list"""
    if packing_list.list_type == "private":
        return packing_list.user == user
    else:
        return user_can_access_trip(user, packing_list.trip)


class PackingListDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PackingList
    template_name = "packing_lists/packing_list_details.html"
    context_object_name = "packing_list"

    def test_func(self):
        packing_list = self.get_object()
        return user_can_access_packing_list(self.request.user, packing_list)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot view this list.")
        return redirect("trip-list")


class PackingListCreateView(LoginRequiredMixin, View):
    """Creates an empty Packing List."""

    def post(self, request, *args, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])

        if not user_can_access_trip(request.user, trip):
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


class PackingListCreateSharedView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Creates shared packing list for trip (only trip owner)"""

    def test_func(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        return trip.is_owner(self.request.user)

    def post(self, request, *args, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])

        # Check if shared list already exists
        if PackingList.objects.filter(trip=trip, list_type="shared").exists():
            messages.error(request, "Team packing list already exists for this trip.")
            return redirect("trip-detail", pk=trip.pk)

        # Create shared list
        packing_list = PackingList.objects.create(
            trip=trip, list_type="shared", user=None  # Shared list has no specific user
        )

        messages.success(request, f'Team packing list created for "{trip.title}"!')
        return redirect("packing-list-details", pk=packing_list.pk)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only trip owner can create team packing list.")
        return redirect("trip-list")


class PackingListsForTripView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Shows ALL packing lists for a trip (private + shared)"""

    model = PackingList
    template_name = "packing_lists/packing_lists_for_trip.html"
    context_object_name = "packing_lists"

    def test_func(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        return user_can_access_trip(self.request.user, trip)

    def get_queryset(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        return PackingList.objects.filter(
            Q(trip=trip, user=self.request.user, list_type="private")
            | Q(trip=trip, list_type="shared")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        context["trip"] = trip
        context["has_shared_list"] = PackingList.objects.filter(
            trip=trip, list_type="shared"
        ).exists()
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

    def form_valid(self, form):
        self.trip_pk = self.get_object().trip.pk

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


class SavePackingListAsTemplateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Saves a private Packing List as a template"""

    def test_func(self):
        packing_list = get_object_or_404(PackingList, pk=self.kwargs["pk"])
        return (
            packing_list.list_type == "private"
            and packing_list.user == self.request.user
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot save this list as template.")
        return redirect("trip-list")

    def post(self, request, *args, **kwargs):
        packing_list = get_object_or_404(PackingList, pk=self.kwargs["pk"])
        template_name = request.POST.get("template_name", "").strip()

        if not template_name:
            messages.error(request, "You must provide a template name.")
            return redirect("packing-list-details", pk=packing_list.pk)

        # Creating template
        template = PackingListTemplate.objects.create(
            name=template_name,
            user=request.user,
        )

        # Copying items
        item_count = 0
        for item in packing_list.items.all():
            PackingItemTemplate.objects.create(
                template=template,
                name=item.item_name,  # ✅ POPRAWIONE!
                quantity=item.item_quantity,  # ✅ POPRAWIONE!
            )
            item_count += 1

        messages.success(
            request,
            f'Packing list saved as template "{template_name}"! {item_count} items copied.',
        )

        return redirect("packing-list-template-details", pk=template.pk)


@login_required
@require_POST
def toggle_item_packed(request, item_id):
    try:
        item = PackingItem.objects.get(pk=item_id)

        if not user_can_access_packing_list(request.user, item.packing_list):
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        data = json.loads(request.body)
        is_packed = data.get("is_packed", False)

        # Toggle packed status
        if is_packed:
            item.marked_as_packed(request.user)
        else:
            item.is_packed = False
            item.packed_by = None
            item.save()

        return JsonResponse(
            {
                "success": True,
                "is_packed": item.is_packed,
                "packed_by": item.packed_by.username if item.packed_by else None,
            }
        )

    except PackingItem.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
