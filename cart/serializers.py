"""DRF serializers for the cart domain."""
from __future__ import annotations

from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product_sku", "name", "unit_price", "quantity"]


class AddItemSerializer(serializers.Serializer):
    product_sku = serializers.CharField(max_length=64)
    quantity = serializers.IntegerField(min_value=1, default=1)
