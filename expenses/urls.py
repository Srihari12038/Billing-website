from django.urls import path

from . import views

urlpatterns = [
    path("", views.ExpenseListView.as_view(), name="expense_list"),
    path("add/", views.ExpenseCreateView.as_view(), name="expense_add"),
    path("<int:pk>/edit/", views.ExpenseUpdateView.as_view(), name="expense_edit"),
    path("<int:pk>/delete/", views.ExpenseDeleteView.as_view(), name="expense_delete"),
    path("categories/", views.ExpenseCategoryListView.as_view(), name="expense_category_list"),
    path("categories/add/", views.ExpenseCategoryCreateView.as_view(), name="expense_category_add"),
]
