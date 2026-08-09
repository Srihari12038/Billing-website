from django.contrib import admin

from .models import CompanySettings


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ["business_name", "phone", "email", "gst_number", "invoice_prefix", "updated_at"]

# Register your models here.
