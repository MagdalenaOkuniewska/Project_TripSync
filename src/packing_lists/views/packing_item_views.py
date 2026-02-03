from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from ..models import PackingItem, PackingList


# jak zrobic checkbox? toggle? (nie znam/nie wiem)


class PackingItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = PackingItem
    template_name = "packing_lists/packing_item_create.html"
    fields = ["item_name", "item_quantity"]

    def test_func(self):
        self.packing_list = get_object_or_404(PackingList, pk=self.kwargs["list_pk"])

        if self.packing_list.list_type == "private":
            return self.packing_list.user == self.request.user
        else:
            return self.packing_list.trip.is_participant(self.request.user)

    def form_valid(self, form):
        form.instance.packing_list = self.packing_list
        form.instance.added_by = self.request.user

        messages.success(
            self.request,
            f'Item "{form.instance.item_name}" successfully added to the packing list.',
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("packing-list-details", kwargs={"pk": self.packing_list.pk})

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot add this item.")
        return redirect("trip-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["packing_list"] = self.packing_list
        return context


class PackingItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PackingItem
    template_name = "packing_lists/packing_item_create.html"
    fields = ["item_name", "item_quantity"]

    def test_func(self):
        item = self.get_object()
        packing_list = item.packing_list

        if packing_list.list_type == "private":
            return packing_list.user == self.request.user
        else:
            return packing_list.trip.is_participant(self.request.user)

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
        packing_list = item.packing_list

        if packing_list.list_type == "private":
            return packing_list.user == self.request.user
        else:
            return packing_list.trip.is_owner(self.request.user)

    def delete(self, request, *args, **kwargs):
        self.list_pk = self.get_object().packing_list.pk
        return super().delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Item "{self.object.item_name}" deleted!')
        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this item.")
        return redirect("trip-list")

    def get_success_url(self):
        return reverse_lazy("packing-list-details", kwargs={"pk": self.list_pk})
