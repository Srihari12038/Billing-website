from django.urls import path

from . import views

urlpatterns = [
    path("", views.SaleListView.as_view(), name="sale_list"),
    path("add/", views.SaleCreateView.as_view(), name="sale_add"),
    path("<int:pk>/", views.SaleDetailView.as_view(), name="sale_detail"),
    path("<int:pk>/edit/", views.SaleUpdateView.as_view(), name="sale_edit"),
    path("<int:pk>/delete/", views.SaleDeleteView.as_view(), name="sale_delete"),
    path("<int:pk>/complete/", views.sale_complete, name="sale_complete"),
    path("payments/add/", views.PaymentCreateView.as_view(), name="payment_add"),
    path("product-lookup/", views.product_lookup, name="product_lookup"),
]
