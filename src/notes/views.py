from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from trips.models import Trip
from .models import Note
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)


class NoteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Note
    template_name = "notes/note_create.html"
    fields = ["title", "content", "note_type"]

    def test_func(self):
        self.trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        return self.trip.is_owner(self.request.user) or self.trip.is_participant(
            self.request.user
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.trip = self.trip

        messages.success(
            self.request, f'Note "{form.instance.title}" created successfully.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("note-list", kwargs={"trip_id": self.trip.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trip"] = self.trip
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You are not a member of this Trip.")
        return redirect("trip-list")


class NoteListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Note
    template_name = "notes/note_list.html"
    context_object_name = "notes"
    ordering = ["-created_at"]

    def test_func(self):
        self.trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        return self.trip.is_owner(self.request.user) or self.trip.is_participant(
            self.request.user
        )

    def get_queryset(self):
        user = self.request.user
        self.trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])

        private_notes = Note.objects.filter(
            trip=self.trip, note_type="private", user=user
        )
        shared_notes = Note.objects.filter(trip=self.trip, note_type="shared")

        all_notes = (
            (private_notes | shared_notes)
            .select_related("user", "trip")
            .order_by("-created_at")
        )

        return all_notes

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You are not a member of this Trip.")
        return redirect("trip-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_notes = self.get_queryset()

        context["trip"] = self.trip
        context["private_notes"] = all_notes.filter(note_type="private")
        context["shared_notes"] = all_notes.filter(note_type="shared")

        return context


class NoteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Note
    template_name = "notes/note_details.html"
    context_object_name = "note"

    def test_func(self):
        note = self.get_object()
        return note.can_view(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You are not a member of this Trip.")
        return redirect("trip-list")


class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    template_name = "notes/note_create.html"
    fields = ["title", "content", "note_type"]

    def test_func(self):
        note = self.get_object()
        return note.can_edit(self.request.user)

    def form_valid(self, form):
        messages.success(
            self.request, f'Note "{form.instance.title}" updated successfully.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("note-list", kwargs={"trip_id": self.object.trip.id})

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You are not a member of this Trip.")
        return redirect("trip-list")


class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = "notes/note_delete.html"

    def test_func(self):
        note = self.get_object()
        return note.can_delete(self.request.user)

    def get_success_url(self):
        return reverse_lazy("note-list", kwargs={"trip_id": self.trip_id})

    def form_valid(self, form):
        note = self.get_object()

        self.trip_id = note.trip.id
        note_title = note.title

        messages.success(self.request, f'Note "{note_title}" deleted successfully.')

        return super().form_valid(form)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only the note creator can delete this note.")
        return redirect("trip-list")
