from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from .models import Notification

# lista wszystkich powiadomień
# lista unread
# oznacz jako przeczytane
# oznacz wszystkie jako przeczytane
# usuń powiadomienie


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_count"] = Notification.objects.filter(
            recipient=self.request.user, is_read=False
        ).count()
        return context


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_as_read()
        return redirect("notification-list")


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True
        )
        messages.success(request, "All notifications marked as read.")
        return redirect("notification-list")


class NotificationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.delete()
        messages.success(request, "Notification deleted.")
        return redirect("notification-list")
