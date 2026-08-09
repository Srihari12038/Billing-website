from django.contrib import admin

from .models import Expense, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "expense_date", "amount", "payment_method", "user"]
    list_filter = ["category", "payment_method", "expense_date"]
    search_fields = ["title", "notes"]

# Register your models here.
