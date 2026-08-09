from django import forms

from products.forms import BootstrapFormMixin
from .models import StockHistory


class StockHistoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = StockHistory
        fields = ["product", "movement_type", "quantity", "movement_date", "notes"]
        widgets = {"movement_date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3})}
