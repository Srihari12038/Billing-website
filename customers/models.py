from django.db import models
from django.urls import reverse


class Customer(models.Model):
    name = models.CharField(max_length=180)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gst_number = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def outstanding_balance(self):
        total = self.sales.aggregate(models.Sum("balance_due")).get("balance_due__sum")
        return self.opening_balance + (total or 0)

    def get_absolute_url(self):
        return reverse("customer_detail", kwargs={"pk": self.pk})

# Create your models here.
