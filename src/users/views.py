from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserUpdateForm
from .models import CustomUser

class RegistrationView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}')
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Your account has been updated!')
        return super().form_valid(form)



