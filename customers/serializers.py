from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Customer
        fields = "__all__"
