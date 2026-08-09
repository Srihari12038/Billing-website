from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from expenses.models import Expense
from products.models import Product
from sales.models import Sale, SaleItem


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "reports/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        completed = Sale.objects.filter(status=Sale.STATUS_COMPLETED)
        context.update({
            "daily_sales": completed.filter(invoice_date=today).aggregate(total=Sum("grand_total"))["total"] or 0,
            "monthly_sales": completed.filter(invoice_date__year=today.year, invoice_date__month=today.month).aggregate(total=Sum("grand_total"))["total"] or 0,
            "yearly_sales": completed.filter(invoice_date__year=today.year).aggregate(total=Sum("grand_total"))["total"] or 0,
            "expense_total": Expense.objects.aggregate(total=Sum("amount"))["total"] or 0,
            "inventory_value": sum(p.current_stock * p.cost_price for p in Product.objects.all()),
            "top_products": SaleItem.objects.values("product__name").annotate(quantity=Sum("quantity"), amount=Sum("line_total")).order_by("-quantity")[:20],
        })
        return context

# Create your views here.
