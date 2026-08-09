from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework import viewsets

from products.views import SearchListMixin
from .forms import ExpenseCategoryForm, ExpenseForm
from .models import Expense, ExpenseCategory
from .serializers import ExpenseCategorySerializer, ExpenseSerializer


class ExpenseListView(SearchListMixin):
    model = Expense
    template_name = "expenses/expense_list.html"
    search_fields = ["title", "category__name", "notes"]

    def get_queryset(self):
        return super().get_queryset().select_related("category")


class ExpenseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "expenses.add_expense"
    model = Expense
    form_class = ExpenseForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("expense_list")
    extra_context = {"title": "Expense"}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(ExpenseCreateView, UpdateView):
    permission_required = "expenses.change_expense"


class ExpenseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "expenses.delete_expense"
    model = Expense
    template_name = "generic/confirm_delete.html"
    success_url = reverse_lazy("expense_list")


class ExpenseCategoryListView(SearchListMixin):
    model = ExpenseCategory
    template_name = "generic/list.html"
    search_fields = ["name"]
    extra_context = {"title": "Expense Categories", "add_url": "expense_category_add", "columns": ["name", "is_active"]}


class ExpenseCategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "expenses.add_expensecategory"
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = "generic/form.html"
    success_url = reverse_lazy("expense_category_list")
    extra_context = {"title": "Expense Category"}


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related("category").all()
    serializer_class = ExpenseSerializer

# Create your views here.
