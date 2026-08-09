from django.db import models


class CompanySettings(models.Model):
    business_name = models.CharField(max_length=180, default="My Business")
    logo = models.ImageField(upload_to="company/", blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    gst_number = models.CharField(max_length=30, blank=True)
    pan = models.CharField(max_length=20, blank=True)
    invoice_prefix = models.CharField(max_length=12, default="INV")
    invoice_footer = models.TextField(default="Thank you for your business.")
    bank_details = models.TextField(blank=True)
    upi_id = models.CharField(max_length=120, blank=True)
    upi_qr_code = models.ImageField(upload_to="company/", blank=True)
    digital_signature = models.ImageField(upload_to="company/", blank=True)
    terms_and_conditions = models.TextField(default="Goods once sold will not be taken back. Payment is due as per invoice terms.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"

    def __str__(self):
        return self.business_name

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

# Create your models here.
