from django.db import models

from sales.models import Sale


class Invoice(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name="invoice")
    pdf_file = models.FileField(upload_to="invoices/", blank=True)
    shared_on_whatsapp = models.BooleanField(default=False)
    whatsapp_message_id = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.sale.invoice_number

# Create your models here.
