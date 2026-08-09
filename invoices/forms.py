from django import forms

from products.forms import BootstrapFormMixin
from .models import Invoice


class InvoiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["sale", "pdf_file", "shared_on_whatsapp", "whatsapp_message_id"]
