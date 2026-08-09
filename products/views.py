from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import viewsets

from .forms import CategoryForm, ProductForm
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .services import export_products_workbook, import_products_workbook


class SearchListMixin(LoginRequiredMixin, ListView):
    paginate_by = 10
    search_fields = []

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            from django.db.models import Q
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(condition)
        return queryset


class CategoryListView(SearchListMixin):
    model = Category
    template_name = "generic/list.html"
    search_fields = ["name", "description"]
    extra_context = {"title": "Categories", "add_url": "category_add", "columns": ["name", "is_active"]}


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "products.add_category"
    model = Category
    form_class = CategoryForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("category_list")
    extra_context = {"title": "Category"}


class CategoryUpdateView(CategoryCreateView, UpdateView):
    permission_required = "products.change_category"


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "products.delete_category"
    model = Category
    template_name = "generic/confirm_delete.html"
    success_url = reverse_lazy("category_list")


class ProductListView(SearchListMixin):
    model = Product
    template_name = "products/product_list.html"
    search_fields = ["name", "sku", "barcode", "category__name"]


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "products/product_detail.html"


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "products.add_product"
    model = Product
    form_class = ProductForm
    template_name = "generic/form.html"
    extra_context = {"title": "Product"}


class ProductUpdateView(ProductCreateView, UpdateView):
    permission_required = "products.change_product"


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "products.delete_product"
    model = Product
    template_name = "generic/confirm_delete.html"
    success_url = reverse_lazy("product_list")


@login_required
def product_export(request):
    output = BytesIO()
    export_products_workbook().save(output)
    response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="products.xlsx"'
    return response


@login_required
def product_import(request):
    if request.method == "POST" and request.FILES.get("file"):
        count = import_products_workbook(request.FILES["file"])
        messages.success(request, f"Imported {count} products.")
        return redirect("product_list")
    return render(request, "products/product_import.html")


@login_required
def product_bulk_delete(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        deleted, _ = Product.objects.filter(id__in=ids).delete()
        messages.success(request, f"Deleted {deleted} selected products.")
    return redirect("product_list")


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer

# Create your views here.
