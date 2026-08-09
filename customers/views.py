from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import viewsets

from products.views import SearchListMixin
from .forms import CustomerForm
from .models import Customer
from .serializers import CustomerSerializer


class CustomerListView(SearchListMixin):
    model = Customer
    template_name = "customers/customer_list.html"
    search_fields = ["name", "phone", "email", "gst_number"]


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "customers/customer_detail.html"


class CustomerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "customers.add_customer"
    model = Customer
    form_class = CustomerForm
    template_name = "generic/form.html"
    extra_context = {"title": "Customer"}


class CustomerUpdateView(CustomerCreateView, UpdateView):
    permission_required = "customers.change_customer"


class CustomerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "customers.delete_customer"
    model = Customer
    template_name = "generic/confirm_delete.html"
    success_url = reverse_lazy("customer_list")


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

# Create your views here.
