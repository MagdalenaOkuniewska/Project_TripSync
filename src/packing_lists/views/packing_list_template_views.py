from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from ..models import PackingListTemplate
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)

# jaki view aby Apply taki template? PackingListTemplate.apply_to_trip
# template=getobjector404,trip tez,packing_list = template.apply_to_trip(trip, request.user)


class PackingListTemplateListView(LoginRequiredMixin, ListView):  # templates usera
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_lists.html"
    context_object_name = "list_templates"

    def get_queryset(self):
        return PackingListTemplate.objects.filter(user=self.request.user).order_by(
            "name"
        )


class PackingListTemplateCreateView(LoginRequiredMixin, CreateView):
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_create.html"
    fields = ["name"]

    def form_valid(self, form):
        form.instance.user = self.request.user

        messages.success(
            self.request, f'Template "{form.instance.name}" created successfully.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-template-details", kwargs={"pk": self.object.pk}
        )


class PackingListTemplateDetailView(
    LoginRequiredMixin, UserPassesTestMixin, DetailView
):
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_details.html"
    context_object_name = "packing_template"

    def test_func(self):
        template = self.get_object()
        return template.user == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot view this template.")
        return redirect("packing-list-template-list")


class PackingListTemplateUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_update.html"
    fields = ["name"]

    def test_func(self):
        template = self.get_object()
        return template.user == self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Template "{form.instance.name}" updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "packing-list-template-details", kwargs={"pk": self.object.pk}
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot update this template.")
        return redirect("packing-list-template-list")


class PackingListTemplateDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, DeleteView
):
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_delete.html"
    success_url = reverse_lazy("packing-list-template-list")

    def test_func(self):
        template = self.get_object()
        return template.user == self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Template "{self.object.name}" deleted!')
        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this template.")
        return redirect("packing-list-template-list")
