from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "gst_number", "outstanding_balance", "created_at"]
    search_fields = ["name", "phone", "email", "gst_number"]

# Register your models here.
