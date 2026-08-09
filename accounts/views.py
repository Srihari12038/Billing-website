from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileForm
from .models import Profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("dashboard")
    extra_context = {"title": "Profile"}

    def get_object(self, queryset=None):
        return self.request.user.profile

# Create your views here.
