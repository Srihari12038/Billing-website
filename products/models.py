from decimal import Decimal

from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_list")


class Product(models.Model):
    name = models.CharField(max_length=180)
    sku = models.CharField(max_length=80, unique=True, blank=True)
    barcode = models.CharField(max_length=120, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    hsn_code = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name", "sku", "barcode"])]

    @property
    def stock_alert(self):
        return self.current_stock <= self.minimum_stock

    @property
    def profit_margin(self):
        if not self.selling_price:
            return Decimal("0.00")
        return ((self.selling_price - self.cost_price) / self.selling_price) * 100

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.sku:
            last = Product.objects.exclude(sku="").order_by("-id").first()
            next_number = (last.id if last else 0) + 1
            candidate = f"PRD-{next_number:05d}"
            while Product.objects.filter(sku=candidate).exists():
                next_number += 1
                candidate = f"PRD-{next_number:05d}"
            self.sku = candidate
        self.sku = self.sku.strip().upper()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

# Create your models here.
