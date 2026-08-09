from django.urls import path

from .views import CustomerCreateView, CustomerDeleteView, CustomerDetailView, CustomerListView, CustomerUpdateView

urlpatterns = [
    path("", CustomerListView.as_view(), name="customer_list"),
    path("add/", CustomerCreateView.as_view(), name="customer_add"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
    path("<int:pk>/edit/", CustomerUpdateView.as_view(), name="customer_edit"),
    path("<int:pk>/delete/", CustomerDeleteView.as_view(), name="customer_delete"),
]
