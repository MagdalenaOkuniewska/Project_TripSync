from django.urls import path
from .views import (
    NoteListView,
    NoteCreateView,
    NoteDetailView,
    NoteUpdateView,
    NoteDeleteView,
)

urlpatterns = [
    path("<int:trip_id>/notes/", NoteListView.as_view(), name="note-list"),
    path("<int:trip_id>/notes/create/", NoteCreateView.as_view(), name="note-create"),
    path("notes/<int:pk>/", NoteDetailView.as_view(), name="note-detail"),
    path("notes/<int:pk>/edit/", NoteUpdateView.as_view(), name="note-edit"),
    path("notes/<int:pk>/delete/", NoteDeleteView.as_view(), name="note-delete"),
]
