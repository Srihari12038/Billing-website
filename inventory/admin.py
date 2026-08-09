from django.contrib import admin

from .models import StockHistory


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ["product", "movement_type", "quantity", "movement_date", "sale", "user"]
    list_filter = ["movement_type", "movement_date"]
    search_fields = ["product__name", "product__sku", "notes"]

# Register your models here.
