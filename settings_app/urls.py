from django.urls import path

from .views import CompanySettingsUpdateView

urlpatterns = [path("company/", CompanySettingsUpdateView.as_view(), name="company_settings")]
