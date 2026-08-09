from django.urls import path

from .views import StockHistoryCreateView, StockHistoryListView

urlpatterns = [
    path("", StockHistoryListView.as_view(), name="stock_history_list"),
    path("stock/add/", StockHistoryCreateView.as_view(), name="stock_history_add"),
]
