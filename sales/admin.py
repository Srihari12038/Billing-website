from django.contrib import admin

from .models import Payment, Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ["line_subtotal", "discount_amount", "gst_amount", "line_total"]


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "customer", "invoice_date", "status", "payment_method", "grand_total", "paid_amount", "balance_due"]
    list_filter = ["status", "payment_method", "invoice_date"]
    search_fields = ["invoice_number", "customer__name", "customer__phone"]
    inlines = [SaleItemInline, PaymentInline]
    readonly_fields = ["subtotal", "discount_total", "gst_total", "grand_total", "balance_due"]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ["sale", "product", "quantity", "unit_price", "line_total"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["sale", "payment_date", "method", "amount", "reference"]
    search_fields = ["sale__invoice_number", "reference"]

# Register your models here.
