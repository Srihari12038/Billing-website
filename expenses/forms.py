from django import forms

from products.forms import BootstrapFormMixin
from .models import Expense, ExpenseCategory


class ExpenseCategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name", "description", "is_active"]


class ExpenseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "expense_date", "title", "amount", "payment_method", "receipt", "notes"]
        widgets = {"expense_date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3})}
