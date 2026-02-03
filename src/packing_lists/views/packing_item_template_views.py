from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from ..models import PackingItemTemplate, PackingListTemplate


class PackingItemTemplateCreateView(
    LoginRequiredMixin, UserPassesTestMixin, CreateView
):
    model = PackingItemTemplate
    template_name = "packing_lists/packing_item_template_create.html"
    fields = ["name", "quantity"]

    def test_func(self):
        self.packing_template = get_object_or_404(
            PackingListTemplate, pk=self.kwargs["template_pk"]
        )  # TODO WSTAWIĆ DO URLS
        return self.packing_template.user == self.request.user

    def form_valid(self, form):  # nie ma pola user
        form.instance.template = self.packing_template

        messages.success(
            self.request,
            f'Packing Item "{form.instance.name}" added to Packing Template',
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-template-details", kwargs={"pk": self.packing_template.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["packing_template"] = self.packing_template
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot add this item.")
        return redirect("packing-list-template-list")


class PackingItemTemplateUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = PackingItemTemplate
    template_name = "packing_lists/packing_item_template_update.html"
    fields = ["name", "quantity"]

    def test_func(self):
        template_item = self.get_object()
        return self.request.user == template_item.template.user

    def form_valid(self, form):
        messages.success(self.request, f'Template-item "{form.instance.name}" updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-template-details", kwargs={"pk": self.object.template.pk}
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot update this item.")
        return redirect("packing-list-template-list")


class PackingItemTemplateDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, DeleteView
):
    model = PackingItemTemplate
    template_name = "packing_lists/packing_item_template_delete.html"

    def test_func(self):
        template_item = self.get_object()
        return self.request.user == template_item.template.user

    def delete(
        self, request, *args, **kwargs
    ):  # zapis template pk przed usunięciem obiektu (success url)
        self.template_pk = self.get_object().template.pk
        return super().delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Template-item "{self.object.name}" deleted!')
        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this item.")
        return redirect("packing-list-template-list")

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-template-details", kwargs={"pk": self.template_pk}
        )
