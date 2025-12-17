from django.urls import path, include
from .views import TripListView,TripCreateView, TripDetailView, TripUpdateView, TripDeleteView, TripInviteCreateView, TripInviteListView, TripInviteCancelView, TripInviteSentList,TripInviteRespondView

urlpatterns = [
    path('', TripListView.as_view(), name='trip-list'),
    path('<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('create/', TripCreateView.as_view(), name='trip-create'),
    path('<int:pk>/update/', TripUpdateView.as_view(), name='trip-update'),
    path('<int:pk>/delete/', TripDeleteView.as_view(), name='trip-delete'),

    path('<int:trip_id>/invite/', TripInviteCreateView.as_view(), name='trip-invite-create'),
    path('invites/', TripInviteListView.as_view(), name='trip-invite-list'),
    path('invites/sent/', TripInviteSentList.as_view(), name='trip-invite-sent'),
    path('invites/<int:pk>/cancel/', TripInviteCancelView.as_view(), name='trip-invite-cancel'),
    path('invites/<int:pk>/<str:response>/', TripInviteRespondView.as_view(), name='trip-invite-respond'),

]