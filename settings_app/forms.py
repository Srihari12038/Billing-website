from django import forms

from products.forms import BootstrapFormMixin
from .models import CompanySettings


class CompanySettingsForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ["business_name", "logo", "address", "phone", "email", "website", "gst_number", "pan", "invoice_prefix", "invoice_footer", "bank_details", "upi_id", "upi_qr_code", "digital_signature", "terms_and_conditions"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "invoice_footer": forms.Textarea(attrs={"rows": 2}),
            "bank_details": forms.Textarea(attrs={"rows": 3}),
            "terms_and_conditions": forms.Textarea(attrs={"rows": 3}),
        }
