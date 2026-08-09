from django.urls import path

from . import views

urlpatterns = [
    path("", views.InvoiceListView.as_view(), name="invoice_list"),
    path("<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
    path("<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("<int:pk>/whatsapp/", views.invoice_whatsapp, name="invoice_whatsapp"),
]
