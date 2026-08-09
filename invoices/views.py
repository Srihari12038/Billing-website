from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from rest_framework import viewsets

from products.views import SearchListMixin
from .models import Invoice
from .serializers import InvoiceSerializer
from .services import generate_invoice_pdf, send_whatsapp_document


class InvoiceListView(SearchListMixin):
    model = Invoice
    template_name = "invoices/invoice_list.html"
    search_fields = ["sale__invoice_number", "sale__customer__name", "sale__customer__phone"]

    def get_queryset(self):
        return super().get_queryset().select_related("sale", "sale__customer")


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "invoices/invoice_detail.html"

    def get_queryset(self):
        return Invoice.objects.select_related("sale", "sale__customer").prefetch_related("sale__items__product")


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("sale"), pk=pk)
    invoice = generate_invoice_pdf(invoice.sale)
    return FileResponse(invoice.pdf_file.open("rb"), as_attachment=False, filename=f"{invoice.sale.invoice_number}.pdf")


@login_required
def invoice_whatsapp(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("sale", "sale__customer"), pk=pk)
    if not invoice.pdf_file:
        invoice = generate_invoice_pdf(invoice.sale)
    result = send_whatsapp_document(invoice)
    if result.get("configured"):
        messages.success(request, "Invoice sent through WhatsApp Cloud API.")
        return redirect(invoice)
    return redirect(result["fallback_url"])


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("sale").all()
    serializer_class = InvoiceSerializer

# Create your views here.
