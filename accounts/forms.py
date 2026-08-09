from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff", "is_active"]


class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff", "is_active", "groups", "user_permissions"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "phone", "avatar", "remember_me"]
