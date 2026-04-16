from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, View
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserUpdateForm, CustomPasswordResetForm
from .models import CustomUser
from trips.models import Trip, TripInvite
from packing_lists.models import PackingList
from notes.models import Note
from django.db.models import Q

from django.contrib.auth.tokens import default_token_generator  # generowanie tokenu
from django.utils.encoding import (
    force_bytes,
    force_str,
)  # force_bytes() zamienia cokolwiek (tu: liczbę) na bytes. 42 → b'42'
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail


class RegistrationView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # konto nieaktywne
        user.save()

        token = default_token_generator.make_token(user)  # generowanie tokenu
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # kodowanie ID usera do meila

        current_site = get_current_site(self.request)
        activation_link = f"http://{current_site.domain}/users/activate/{uid}/{token}/"
        email_subject = "Confirm Registration"

        send_mail(
            email_subject,
            message=f"Click the link to activate your account {activation_link}",
            from_email="noreply@tripsync.com",
            recipient_list=[user.email],
        )

        messages.info(self.request, "Check your email to activate your account.")

        return redirect(self.success_url)


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(
                urlsafe_base64_decode(uidb64)
            )  # dekoduje uid z Base64 z powrotem na id usera
            user = CustomUser.objects.get(pk=uid)  # pobiera usera
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(
            user, token
        ):  # czy token jest ważny
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated.")
            return redirect("login")
        else:
            messages.error(request, "The confirmation link is invalid or has expired.")
            return redirect("register")


class ProfileView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = "users/profile.html"
    context_object_name = "user_trips"

    def get_queryset(self):
        user = self.request.user
        return (
            Trip.objects.filter(Q(owner=user) | Q(members__user=user))
            .select_related("owner")
            .distinct()
            .order_by("start_date")
        )

    def get_context_data(self, **kwargs):
        """Passing 'response' to HTML template"""
        context = super().get_context_data(**kwargs)

        today = timezone.localtime(timezone.now()).date()
        user = self.request.user

        all_trips = self.get_queryset()

        # expired:
        TripInvite.objects.filter(
            user=user, status="pending", expires_at__lte=timezone.now()
        ).update(status="expired")

        all_invites = TripInvite.objects.filter(user=user, status="pending").order_by(
            "-created_at"
        )
        declined_invites = (
            TripInvite.objects.filter(user=user, status="declined")
            .select_related("trip")
            .order_by("-responded_at")
        )

        context["upcoming_trips"] = all_trips.filter(start_date__gte=today)
        context["past_trips"] = all_trips.filter(end_date__lt=today)
        context["declined_invites"] = declined_invites
        context["pending_invites"] = all_invites

        days_since_joined = (timezone.now() - user.date_joined).days + 1

        if user.last_login:
            days_since_last_login = (timezone.now() - user.last_login).days + 1
        else:
            days_since_last_login = 0

        context["days_since_joined"] = days_since_joined
        context["days_since_last_login"] = days_since_last_login

        upcoming_trips_with_notes = []
        for trip in context["upcoming_trips"]:
            private_notes_count = Note.objects.filter(
                trip=trip, user=user, note_type="private"
            ).count()
            upcoming_trips_with_notes.append(
                {"trip": trip, "private_notes_count": private_notes_count}
            )

        context["upcoming_trips_with_notes"] = upcoming_trips_with_notes

        upcoming_trips_with_packing_lists = []
        for trip in context["upcoming_trips"]:
            packing_list = PackingList.objects.filter(
                trip=trip, user=user, list_type="private"
            ).first()

            if packing_list:
                packing_items_count = packing_list.items.count()
                upcoming_trips_with_packing_lists.append(
                    {"trip": trip, "packing_items_count": packing_items_count}
                )

        context["upcoming_trips_with_packing_lists"] = upcoming_trips_with_packing_lists

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "users/edit_profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your account has been updated!")
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        messages.success(
            self.request,
            f'Password reset email was sent to "{email}". Please check your inbox and follow instructions.',
        )
        return super().form_valid(form)


class SearchUsersView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "users/search_users.html"
    context_object_name = "users"

    def get_queryset(self):
        query = self.request.GET.get("q")  # w navbar name="q"

        if not query:
            return CustomUser.objects.none()

        results = CustomUser.objects.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

        return results.exclude(pk=self.request.user.pk).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["my_trips"] = Trip.objects.filter(owner=self.request.user)
        return context
