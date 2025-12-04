from django.urls import path
from .views import RegistrationView, ProfileView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', next_page = '/users/profile/' ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
