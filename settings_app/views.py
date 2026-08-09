from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from rest_framework import viewsets

from .forms import CompanySettingsForm
from .models import CompanySettings
from .serializers import CompanySettingsSerializer


class CompanySettingsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "settings_app.change_companysettings"
    model = CompanySettings
    form_class = CompanySettingsForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("company_settings")
    extra_context = {"title": "Company Settings"}

    def get_object(self, queryset=None):
        return CompanySettings.load()


class CompanySettingsViewSet(viewsets.ModelViewSet):
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer

# Create your views here.
