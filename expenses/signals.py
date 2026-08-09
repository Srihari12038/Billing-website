from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_expense_categories(sender, **kwargs):
    if sender.name != "expenses":
        return
    from .models import ExpenseCategory

    for name in ["Rent", "Electricity", "Salary", "Internet", "Marketing", "Travel", "Transport", "Office Expense", "Miscellaneous"]:
        ExpenseCategory.objects.get_or_create(name=name)
