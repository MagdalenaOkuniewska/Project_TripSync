from django.urls import path
from .views import (
    RegistrationView,
    ProfileView,
    ProfileEditView,
    CustomPasswordResetView,
    SearchUsersView,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="edit_profile"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="users/login.html", next_page="/users/profile/"
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("search/", SearchUsersView.as_view(), name="search-users"),
]
