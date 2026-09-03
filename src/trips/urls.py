from django.urls import path

from .views import (
    TripCreateView,
    TripDeleteView,
    TripDetailView,
    TripInviteCancelView,
    TripInviteCreateView,
    TripInviteListView,
    TripInviteRespondView,
    TripInviteSentListView,
    TripJoinByLinkView,
    TripListView,
    TripMemberLeaveView,
    TripMemberListView,
    TripMemberRemoveView,
    TripUpdateView,
)

urlpatterns = [
    path("", TripListView.as_view(), name="trip-list"),
    path("<int:pk>/", TripDetailView.as_view(), name="trip-detail"),
    path("create/", TripCreateView.as_view(), name="trip-create"),
    path("<int:pk>/update/", TripUpdateView.as_view(), name="trip-update"),
    path("<int:pk>/delete/", TripDeleteView.as_view(), name="trip-delete"),
    path(
        "<int:trip_id>/invite/",
        TripInviteCreateView.as_view(),
        name="trip-invite-create",
    ),
    path("join/<uuid:token>/", TripJoinByLinkView.as_view(), name="trip-join-by-link"),
    path(
        "<int:trip_id>/members/", TripMemberListView.as_view(), name="trip-member-list"
    ),
    path("invites/", TripInviteListView.as_view(), name="trip-invite-list"),
    path(
        "<int:trip_id>/leave/", TripMemberLeaveView.as_view(), name="trip-member-leave"
    ),
    path(
        "members/<int:member_id>/remove/",
        TripMemberRemoveView.as_view(),
        name="trip-member-remove",
    ),
    path("invites/sent/", TripInviteSentListView.as_view(), name="trip-invite-sent"),
    path(
        "invites/<int:pk>/cancel/",
        TripInviteCancelView.as_view(),
        name="trip-invite-cancel",
    ),
    path(
        "invites/<int:pk>/", TripInviteRespondView.as_view(), name="trip-invite-respond"
    ),
]
