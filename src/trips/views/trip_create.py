from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Trip, TripMember
from ..forms import TripForm


class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripForm
    template_name = "trips/trip_create.html"

    def get_success_url(self):
        """Redirect to details of created trip"""
        return reverse_lazy("trip-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Sets up logged-in User as an Owner adn saves it to db"""
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        TripMember.objects.create(
            trip=self.object,
            user=self.request.user,
            role="owner",
        )

        messages.success(
            self.request, f'Your trip "{form.instance.title}" has been created.'
        )
        return response
