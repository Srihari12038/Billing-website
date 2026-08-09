from django import forms
from django.forms import inlineformset_factory
from django.db.models import Q

from customers.models import Customer
from products.models import Product
from products.forms import BootstrapFormMixin
from .models import Payment, Sale, SaleItem


class SaleForm(BootstrapFormMixin, forms.ModelForm):
    customer_name = forms.CharField(max_length=180)
    customer_phone = forms.CharField(max_length=20)
    customer_email = forms.EmailField(required=False)
    customer_gst_number = forms.CharField(max_length=30, required=False)
    customer_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Sale
        fields = ["invoice_date", "status", "payment_method", "paid_amount", "notes"]
        widgets = {"invoice_date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.customer_id:
            customer = self.instance.customer
            self.fields["customer_name"].initial = customer.name
            self.fields["customer_phone"].initial = customer.phone
            self.fields["customer_email"].initial = customer.email
            self.fields["customer_gst_number"].initial = customer.gst_number
            self.fields["customer_address"].initial = customer.address

    def save_customer(self):
        phone = self.cleaned_data["customer_phone"].strip()
        customer, _ = Customer.objects.update_or_create(
            phone=phone,
            defaults={
                "name": self.cleaned_data["customer_name"].strip(),
                "email": self.cleaned_data.get("customer_email", ""),
                "gst_number": self.cleaned_data.get("customer_gst_number", ""),
                "address": self.cleaned_data.get("customer_address", ""),
            },
        )
        return customer


class SaleItemForm(BootstrapFormMixin, forms.ModelForm):
    product_code = forms.CharField(max_length=120, required=False, label="Product Code", help_text="Enter product code or barcode")

    class Meta:
        model = SaleItem
        fields = ["product", "quantity", "unit_price", "discount_percent", "gst_rate"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)
        self.fields["product"].required = False
        self.fields["product"].widget = forms.HiddenInput()
        self.fields["unit_price"].required = False
        self.fields["gst_rate"].required = False
        if self.instance and self.instance.pk:
            self.fields["product_code"].initial = self.instance.product.sku

    def clean(self):
        cleaned = super().clean()
        if self.cleaned_data.get("DELETE"):
            return cleaned
        if self.empty_permitted and not self.has_changed():
            return cleaned
        product = cleaned.get("product")
        code = (cleaned.get("product_code") or "").strip()
        if code:
            product = Product.objects.filter(Q(sku__iexact=code) | Q(barcode__iexact=code), is_active=True).first()
            if not product:
                raise forms.ValidationError(f"No active product found for code '{code}'.")
            cleaned["product"] = product
            self.instance.product = product
            if not cleaned.get("unit_price"):
                cleaned["unit_price"] = product.selling_price
                self.instance.unit_price = product.selling_price
            if not cleaned.get("gst_rate"):
                cleaned["gst_rate"] = product.gst_rate
                self.instance.gst_rate = product.gst_rate
        if not cleaned.get("product"):
            raise forms.ValidationError("Enter a valid product code.")
        return cleaned


SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)


class PaymentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["sale", "payment_date", "method", "amount", "reference", "notes"]
        widgets = {"payment_date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 2})}
