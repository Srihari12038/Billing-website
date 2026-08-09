from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from customers.models import Customer
from expenses.models import Expense
from products.models import Product
from sales.models import Sale, SaleItem


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        month_start = today.replace(day=1)
        completed = Sale.objects.filter(status=Sale.STATUS_COMPLETED)
        active_sales = Sale.objects.exclude(status=Sale.STATUS_CANCELLED)
        stock_value = ExpressionWrapper(F("current_stock") * F("cost_price"), output_field=DecimalField(max_digits=14, decimal_places=2))
        retail_stock_value = ExpressionWrapper(F("current_stock") * F("selling_price"), output_field=DecimalField(max_digits=14, decimal_places=2))
        item_cost = ExpressionWrapper(F("quantity") * F("product__cost_price"), output_field=DecimalField(max_digits=14, decimal_places=2))

        today_items = SaleItem.objects.filter(sale__invoice_date=today).exclude(sale__status=Sale.STATUS_CANCELLED)
        month_items = SaleItem.objects.filter(sale__invoice_date__gte=month_start).exclude(sale__status=Sale.STATUS_CANCELLED)

        today_sales = today_items.aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")
        today_expense = Expense.objects.filter(expense_date=today).aggregate(total=Sum("amount"))["total"] or 0
        today_cogs = today_items.aggregate(total=Sum(item_cost))["total"] or Decimal("0.00")
        today_gross_profit = today_sales - today_cogs
        today_net_profit = today_gross_profit - today_expense
        today_cash_in = active_sales.filter(invoice_date=today).aggregate(total=Sum("paid_amount"))["total"] or 0
        today_cashflow = today_cash_in - today_expense
        total_expense = Expense.objects.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        monthly_sales = month_items.aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")
        monthly_expense = Expense.objects.filter(expense_date__gte=month_start).aggregate(total=Sum("amount"))["total"] or 0
        monthly_cogs = month_items.aggregate(total=Sum(item_cost))["total"] or Decimal("0.00")
        monthly_gross_profit = monthly_sales - monthly_cogs
        monthly_net_profit = monthly_expense - monthly_sales
        monthly_cash_in = active_sales.filter(invoice_date__gte=month_start).aggregate(total=Sum("paid_amount"))["total"] or 0
        monthly_cashflow = monthly_cash_in - monthly_expense
        labels, sales_data, expense_data = [], [], []
        for day in range(6, -1, -1):
            date = today - timezone.timedelta(days=day)
            labels.append(date.strftime("%d %b"))
            day_items = SaleItem.objects.filter(sale__invoice_date=date).exclude(sale__status=Sale.STATUS_CANCELLED)
            sales_data.append(float(day_items.aggregate(total=Sum("line_total"))["total"] or 0))
            expense_data.append(float(Expense.objects.filter(expense_date=date).aggregate(total=Sum("amount"))["total"] or 0))
        context.update({
            "today_sales": today_sales,
            "today_expense": today_expense,
            "today_cogs": today_cogs,
            "today_gross_profit": today_gross_profit,
            "today_profit": today_net_profit,
            "today_profit_amount": abs(today_net_profit),
            "today_profit_label": "Profit" if today_net_profit >= 0 else "Loss",
            "total_expense": total_expense,
            "today_cash_in": today_cash_in,
            "today_cashflow": today_cashflow,
            "today_cashflow_amount": abs(today_cashflow),
            "today_cashflow_label": "Net Cash In" if today_cashflow >= 0 else "Net Cash Out",
            "monthly_sales": monthly_sales,
            "monthly_expense": monthly_expense,
            "monthly_cogs": monthly_cogs,
            "monthly_gross_profit": monthly_gross_profit,
            "monthly_profit": monthly_net_profit,
            "monthly_profit_amount": abs(monthly_net_profit),
            "monthly_profit_label": "Profit" if monthly_net_profit >= 0 else "Loss",
            "monthly_cash_in": monthly_cash_in,
            "monthly_cashflow": monthly_cashflow,
            "invoice_count": active_sales.count(),
            "total_sale_qty": SaleItem.objects.exclude(sale__status=Sale.STATUS_CANCELLED).aggregate(total=Sum("quantity"))["total"] or 0,
            "customer_count": Customer.objects.count(),
            "product_count": Product.objects.filter(is_active=True).count(),
            "total_stock": Product.objects.filter(is_active=True).aggregate(total=Sum("current_stock"))["total"] or 0,
            "inventory_cost_value": Product.objects.filter(is_active=True).aggregate(total=Sum(stock_value))["total"] or 0,
            "inventory_retail_value": Product.objects.filter(is_active=True).aggregate(total=Sum(retail_stock_value))["total"] or 0,
            "low_stock_count": Product.objects.filter(is_active=True, current_stock__lte=F("minimum_stock")).count(),
            "pending_payments": active_sales.filter(balance_due__gt=0).aggregate(total=Sum("balance_due"))["total"] or 0,
            "latest_orders": completed.select_related("customer")[:8],
            "top_products": SaleItem.objects.filter(sale__status=Sale.STATUS_COMPLETED).values("product__name").annotate(quantity=Sum("quantity")).order_by("-quantity")[:5],
            "recent_customers": Customer.objects.order_by("-created_at")[:5],
            "chart_labels": labels,
            "sales_data": sales_data,
            "expense_data": expense_data,
        })
        return context

# Create your views here.
