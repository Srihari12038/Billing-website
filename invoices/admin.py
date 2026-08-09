from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["sale", "pdf_file", "shared_on_whatsapp", "whatsapp_message_id", "created_at"]
    search_fields = ["sale__invoice_number", "sale__customer__name"]
    list_filter = ["shared_on_whatsapp", "created_at"]

# Register your models here.
