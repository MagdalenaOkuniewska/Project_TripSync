from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from ..models import ShoppingItem, ShoppingList
from .shopping_list_views import user_can_access_trip


def user_can_manage_shopping_item(user, shopping_list):
    """Checks if user can add/edit/delete items in shopping list"""
    return user_can_access_trip(user, shopping_list.trip)


class ShoppingItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ShoppingItem
    template_name = "shopping_list/shopping_item_create.html"
    fields = ["item_name", "item_quantity"]

    def test_func(self):
        shopping_list = get_object_or_404(
            ShoppingList, pk=self.kwargs["shopping_list_pk"]
        )
        return user_can_manage_shopping_item(self.request.user, shopping_list)

    def form_valid(self, form):
        shopping_list = get_object_or_404(
            ShoppingList, pk=self.kwargs["shopping_list_pk"]
        )
        form.instance.shopping_list = shopping_list
        form.instance.added_by = self.request.user

        messages.success(
            self.request,
            f'Item "{form.instance.item_name}" successfully added to the shopping list.',
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "shopping-list-details", kwargs={"pk": self.kwargs["shopping_list_pk"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shopping_list = get_object_or_404(
            ShoppingList, pk=self.kwargs["shopping_list_pk"]
        )
        context["shopping_list"] = shopping_list
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot add this item.")
        return redirect("trip-list")


class ShoppingItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ShoppingItem
    template_name = "shopping_list/shopping_item_create.html"
    fields = ["item_name", "item_quantity"]

    def test_func(self):
        item = self.get_object()
        return user_can_manage_shopping_item(self.request.user, item.shopping_list)

    def form_valid(self, form):
        messages.success(self.request, f'Item "{form.instance.item_name}" updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "shopping-list-details", kwargs={"pk": self.object.shopping_list.pk}
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot update this item.")
        return redirect("trip-list")


class ShoppingItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ShoppingItem
    template_name = "shopping_list/shopping_item_delete.html"

    def test_func(self):
        item = self.get_object()
        return user_can_manage_shopping_item(self.request.user, item.shopping_list)

    def form_valid(self, form):
        self.shopping_list_pk = self.get_object().shopping_list.pk

        messages.success(self.request, f'Item "{self.object.item_name}" deleted!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "shopping-list-details", kwargs={"pk": self.shopping_list_pk}
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this item.")
        return redirect("trip-list")
