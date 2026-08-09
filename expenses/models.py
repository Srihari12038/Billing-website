from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name="expenses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    expense_date = models.DateField(default=timezone.localdate)
    title = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[("cash", "Cash"), ("upi", "UPI"), ("card", "Card"), ("bank", "Bank")], default="cash")
    receipt = models.FileField(upload_to="expenses/", blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-expense_date", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("expense_list")

# Create your models here.
