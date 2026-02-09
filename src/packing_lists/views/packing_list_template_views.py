from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from ..models import PackingListTemplate, PackingList
from trips.models import Trip
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    View,
)


def user_owns_template(user, template):
    """Checks if user owns this packing list template"""
    return template.user == user


def user_can_apply_template_to_trip(user, trip):
    """Checks if user can apply template to trip (owner or participant)"""
    return trip.is_owner(user) or trip.is_participant(user)


def user_already_has_packing_list(user, trip):
    """Check if user already has a packing list for this trip"""
    return PackingList.objects.filter(trip=trip, user=user).exists()


class PackingListTemplateListView(LoginRequiredMixin, ListView):  # templates usera
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_list.html"
    context_object_name = "list_templates"

    def get_queryset(self):
        return PackingListTemplate.objects.filter(user=self.request.user).order_by(
            "name"
        )


class PackingListTemplateCreateView(LoginRequiredMixin, CreateView):
    """Creates an empty packing list template"""

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


class ApplyPackingListTemplateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Applies Packing List Template to the Trip - copies items"""

    def test_func(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])

        if not user_can_apply_template_to_trip(self.request.user, trip):
            return False

        if user_already_has_packing_list(self.request.user, trip):
            return False

        return True

    def post(self, request, *args, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        packing_list_template = get_object_or_404(
            PackingListTemplate, pk=self.kwargs["template_pk"]
        )

        packing_list = packing_list_template.apply_to_trip(trip=trip, user=request.user)

        messages.success(
            request,
            f'Template "{packing_list_template.name}" applied to "{trip.title}".',
        )

        return redirect("packing-list-details", pk=packing_list.pk)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot apply this template.")
        return redirect("trip-list")


class SelectTemplateForTripView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Shows list of user's templates to apply to a trip"""

    model = PackingListTemplate
    template_name = "packing_lists/select_template_for_trip.html"
    context_object_name = "templates"

    def test_func(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        return user_can_apply_template_to_trip(self.request.user, trip)

    def get_queryset(self):
        return PackingListTemplate.objects.filter(user=self.request.user).order_by(
            "name"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"])
        context["trip"] = trip
        return context


class PackingListTemplateDetailView(
    LoginRequiredMixin, UserPassesTestMixin, DetailView
):
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_details.html"
    context_object_name = "packing_template"

    def test_func(self):
        template = self.get_object()
        return user_owns_template(self.request.user, template)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot view this template.")
        return redirect("packing-list-template-list")


class PackingListTemplateUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = PackingListTemplate
    template_name = "packing_lists/packing_list_template_create.html"
    fields = ["name"]

    def test_func(self):
        template = self.get_object()
        return user_owns_template(self.request.user, template)

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
        return user_owns_template(self.request.user, template)

    def form_valid(self, form):
        messages.success(self.request, f'Template "{self.object.name}" deleted!')
        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You cannot delete this template.")
        return redirect("packing-list-template-list")
