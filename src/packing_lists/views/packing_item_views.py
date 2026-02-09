from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from ..models import PackingItem, PackingList


def user_can_access_packing_list(user, packing_list):
    """Checks if user can access this packing list"""
    if packing_list.list_type == "private":
        return packing_list.user == user
    else:
        return packing_list.trip.is_owner(user) or packing_list.trip.is_participant(
            user
        )


def user_can_edit_packing_item(user, packing_list):
    """Checks if user can edit items in this packing list"""
    if packing_list.list_type == "private":
        return packing_list.user == user
    else:
        return packing_list.trip.is_owner(user) or packing_list.trip.is_participant(
            user
        )


def user_can_delete_packing_item(user, packing_list):
    """Checks if user can delete items from this packing list"""
    if packing_list.list_type == "private":
        return packing_list.user == user
    else:
        return packing_list.trip.is_owner(user)


class PackingItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = PackingItem
    template_name = "packing_lists/packing_item_create.html"
    fields = ["item_name", "item_quantity"]

    def test_func(self):
        packing_list = get_object_or_404(PackingList, pk=self.kwargs["list_pk"])
        return user_can_access_packing_list(self.request.user, packing_list)

    def form_valid(self, form):
        packing_list = get_object_or_404(PackingList, pk=self.kwargs["list_pk"])
        form.instance.packing_list = packing_list
        form.instance.added_by = self.request.user

        messages.success(
            self.request,
            f'Item "{form.instance.item_name}" successfully added to the packing list.',
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-details", kwargs={"pk": self.kwargs["list_pk"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        packing_list = get_object_or_404(PackingList, pk=self.kwargs["list_pk"])
        context["packing_list"] = packing_list
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot add this item.")
        return redirect("trip-list")


class PackingItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PackingItem
    template_name = "packing_lists/packing_item_create.html"
    fields = ["item_name", "item_quantity"]

    def test_func(self):
        item = self.get_object()
        return user_can_edit_packing_item(self.request.user, item.packing_list)

    def form_valid(self, form):
        messages.success(self.request, f'Item "{form.instance.item_name}" updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-details", kwargs={"pk": self.object.packing_list.pk}
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot update this item.")
        return redirect("trip-list")


class PackingItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PackingItem
    template_name = "packing_lists/packing_item_delete.html"

    def test_func(self):
        item = self.get_object()
        return user_can_delete_packing_item(self.request.user, item.packing_list)

    def form_valid(self, form):
        self.list_pk = self.get_object().packing_list.pk

        messages.success(self.request, f'Item "{self.object.item_name}" deleted!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("packing-list-details", kwargs={"pk": self.list_pk})

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this item.")
        return redirect("trip-list")
