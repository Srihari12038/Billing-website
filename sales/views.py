from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import viewsets

from invoices.services import generate_invoice_pdf
from products.models import Product
from products.views import SearchListMixin
from .forms import PaymentForm, SaleForm, SaleItemFormSet
from .models import Payment, Sale, SaleItem
from .serializers import PaymentSerializer, SaleItemSerializer, SaleSerializer


class SaleListView(SearchListMixin):
    model = Sale
    template_name = "sales/sale_list.html"
    search_fields = ["invoice_number", "customer__name", "customer__phone"]

    def get_queryset(self):
        return super().get_queryset().select_related("customer")


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "sales/sale_detail.html"

    def get_queryset(self):
        return Sale.objects.select_related("customer").prefetch_related("items__product", "payments")


class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "sales.add_sale"
    model = Sale
    form_class = SaleForm
    template_name = "sales/sale_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = kwargs.get("formset") or SaleItemFormSet(instance=self.object)
        return context

    def form_valid(self, form, formset):
        form.instance.user = self.request.user
        was_completed = False
        if form.instance.pk:
            was_completed = Sale.objects.filter(pk=form.instance.pk, status=Sale.STATUS_COMPLETED).exists()
        with transaction.atomic():
            form.instance.customer = form.save_customer()
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            if self.object.status == Sale.STATUS_COMPLETED and not was_completed:
                self.object.complete()
                generate_invoice_pdf(self.object)
        messages.success(self.request, "Invoice saved.")
        return redirect(self.object)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = SaleItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class SaleUpdateView(SaleCreateView, UpdateView):
    permission_required = "sales.change_sale"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = kwargs.get("formset") or SaleItemFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = SaleItemFormSet(request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class SaleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "sales.delete_sale"
    model = Sale
    template_name = "generic/confirm_delete.html"
    success_url = reverse_lazy("sale_list")


@login_required
def sale_complete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale.complete()
    generate_invoice_pdf(sale)
    messages.success(request, f"{sale.invoice_number} completed.")
    return redirect(sale)


class PaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "sales.add_payment"
    model = Payment
    form_class = PaymentForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("sale_list")
    extra_context = {"title": "Payment"}


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related("customer").all()
    serializer_class = SaleSerializer


class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.select_related("sale", "product").all()
    serializer_class = SaleItemSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("sale").all()
    serializer_class = PaymentSerializer


@login_required
def product_lookup(request):
    code = request.GET.get("code", "").strip()
    product = Product.objects.filter(Q(sku__iexact=code) | Q(barcode__iexact=code), is_active=True).select_related("category").first()
    if not product:
        return JsonResponse({"found": False}, status=404)
    return JsonResponse({
        "found": True,
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "unit_price": str(product.selling_price),
        "gst_rate": str(product.gst_rate),
        "stock": str(product.current_stock),
    })

# Create your views here.
