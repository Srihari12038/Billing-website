from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework import viewsets

from products.views import SearchListMixin
from .forms import StockHistoryForm
from .models import StockHistory
from .serializers import StockHistorySerializer


class StockHistoryListView(SearchListMixin):
    model = StockHistory
    template_name = "inventory/stock_history_list.html"
    search_fields = ["product__name", "product__sku", "notes"]

    def get_queryset(self):
        return super().get_queryset().select_related("product")


class StockHistoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "inventory.add_stockhistory"
    model = StockHistory
    form_class = StockHistoryForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("stock_history_list")
    extra_context = {"title": "Stock Movement"}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StockHistoryViewSet(viewsets.ModelViewSet):
    queryset = StockHistory.objects.select_related("product").all()
    serializer_class = StockHistorySerializer

# Create your views here.
