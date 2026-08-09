from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from customers.models import Customer
from products.models import Product
from settings_app.models import CompanySettings


class Sale(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [(STATUS_DRAFT, "processing"), (STATUS_COMPLETED, "completed"), (STATUS_CANCELLED, "cancel")]
    PAYMENT_CASH = "cash"
    PAYMENT_UPI = "upi"
    PAYMENT_CARD = "card"
    PAYMENT_BANK = "bank"
    PAYMENT_CREDIT = "credit"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_UPI, "UPI"),
        (PAYMENT_CARD, "Card"),
        (PAYMENT_BANK, "Bank"),
        (PAYMENT_CREDIT, "Credit"),
    ]

    invoice_number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-invoice_date", "-id"]

    def __str__(self):
        return self.invoice_number or f"Sale #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            prefix = CompanySettings.load().invoice_prefix
            year = timezone.localdate().year
            last = Sale.objects.filter(invoice_number__startswith=f"{prefix}-{year}-").order_by("-id").first()
            number = (last.pk if last else 0) + 1
            self.invoice_number = f"{prefix}-{year}-{number:05d}"
        super().save(*args, **kwargs)

    def recalculate(self, commit=True):
        totals = self.items.aggregate(
            subtotal=models.Sum("line_subtotal"),
            discount=models.Sum("discount_amount"),
            gst=models.Sum("gst_amount"),
            total=models.Sum("line_total"),
        )
        self.subtotal = totals["subtotal"] or Decimal("0.00")
        self.discount_total = totals["discount"] or Decimal("0.00")
        self.gst_total = totals["gst"] or Decimal("0.00")
        self.grand_total = totals["total"] or Decimal("0.00")
        self.balance_due = self.grand_total - self.paid_amount
        if commit:
            self.save(update_fields=["subtotal", "discount_total", "gst_total", "grand_total", "balance_due", "updated_at"])

    def complete(self):
        from inventory.models import StockHistory

        with transaction.atomic():
            self.status = self.STATUS_COMPLETED
            self.recalculate(commit=False)
            self.save()
            for item in self.items.select_related("product"):
                product = item.product
                product.current_stock -= item.quantity
                product.save(update_fields=["current_stock", "updated_at"])
                StockHistory.objects.create(product=product, sale=self, movement_type=StockHistory.OUT, quantity=item.quantity, notes=f"Sale {self.invoice_number}")

    def get_absolute_url(self):
        return reverse("sale_detail", kwargs={"pk": self.pk})


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.line_subtotal = self.quantity * self.unit_price
        self.discount_amount = self.line_subtotal * self.discount_percent / Decimal("100")
        taxable = self.line_subtotal - self.discount_amount
        self.gst_amount = taxable * self.gst_rate / Decimal("100")
        self.line_total = taxable + self.gst_amount
        super().save(*args, **kwargs)
        self.sale.recalculate()

    def delete(self, *args, **kwargs):
        sale = self.sale
        super().delete(*args, **kwargs)
        sale.recalculate()

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=20, choices=Sale.PAYMENT_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sale.paid_amount = self.sale.payments.aggregate(models.Sum("amount")).get("amount__sum") or Decimal("0.00")
        self.sale.recalculate()

    def __str__(self):
        return f"{self.sale.invoice_number} - {self.amount}"

# Create your models here.
