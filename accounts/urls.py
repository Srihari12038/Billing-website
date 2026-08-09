from django.contrib.auth import views as auth_views
from django.urls import path

from .views import ProfileUpdateView

urlpatterns = [
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("change-password/", auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html", success_url="/"), name="password_change"),
]
