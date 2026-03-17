from django.urls import path
from .views import TripAuditLogView

urlpatterns = [
    path("<int:trip_id>/activity/", TripAuditLogView.as_view(), name="trip-audit-log"),
]
