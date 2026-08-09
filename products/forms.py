from django import forms

from .models import Category, Product


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            if isinstance(field.widget, forms.Select):
                css = "form-select"
            field.widget.attrs["class"] = css


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]


class ProductForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "barcode", "category", "cost_price", "selling_price", "gst_rate", "hsn_code", "description", "image", "current_stock", "minimum_stock", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
        labels = {"sku": "Product Code"}
        help_texts = {"sku": "Leave blank to auto-generate a code like PRD-00001. Use this code in the invoice item row."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sku"].required = False
