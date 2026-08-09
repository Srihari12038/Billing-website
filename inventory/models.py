from django.conf import settings
from django.db import models
from django.utils import timezone

from products.models import Product


class StockHistory(models.Model):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
    MOVEMENT_CHOICES = [(IN, "Stock In"), (OUT, "Stock Out"), (ADJUSTMENT, "Adjustment")]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_history")
    sale = models.ForeignKey("sales.Sale", on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_movements")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    movement_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-movement_date", "-id"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.sale_id:
            if self.movement_type == self.IN:
                self.product.current_stock += self.quantity
            elif self.movement_type == self.OUT:
                self.product.current_stock -= self.quantity
            else:
                self.product.current_stock = self.quantity
            self.product.save(update_fields=["current_stock", "updated_at"])

    def __str__(self):
        return f"{self.product} {self.get_movement_type_display()} {self.quantity}"

# Create your models here.
