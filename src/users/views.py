from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserUpdateForm, CustomPasswordResetForm
from .models import CustomUser
from django.db.models import Q
from trips.models import Trip

class RegistrationView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}')
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, ListView ):
    model = Trip
    template_name = 'users/profile.html'
    context_object_name = 'user_trips'

    def get_queryset(self):
        user = self.request.user
        return Trip.objects.filter(Q(owner=user) | Q(members__user=user)).distinct().order_by('start_date')

    def get_context_data(self, **kwargs):
        """Passing 'response' to HTML template"""
        context = super().get_context_data(**kwargs)

        today = timezone.localtime(timezone.now()).date()

        all_trips = self.get_queryset()

        context['upcoming_trips'] = all_trips.filter(start_date__gte=today)
        context['past_trips'] = all_trips.filter(end_date__lt=today)

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Your account has been updated!')
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        messages.success(self.request, f'Password reset email was sent to "{email}". Please check your inbox and follow instructions.')
        return super().form_valid(form)


