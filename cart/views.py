"""Cart API. All endpoints operate on the gateway-verified user (request.user_id).

Adding an item does a synchronous REST stock-check against catalog-service —
the canonical "sync over ClusterIP DNS" path.
"""
from __future__ import annotations

from decimal import Decimal

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .catalog_client import ProductNotFound, get_product
from .models import CartItem
from .serializers import AddItemSerializer, CartItemSerializer


def _cart_response(user_id: str) -> Response:
    items = CartItem.objects.filter(user_id=user_id)
    total = sum((i.unit_price * i.quantity for i in items), Decimal("0.00"))
    return Response({"items": CartItemSerializer(items, many=True).data, "total": str(total)})


@api_view(["GET"])
def get_cart(request: Request) -> Response:
    return _cart_response(request.user.id)


@api_view(["POST"])
def add_item(request: Request) -> Response:
    req = AddItemSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    sku = req.validated_data["product_sku"]
    qty = req.validated_data["quantity"]

    try:
        product = get_product(sku)
    except ProductNotFound:
        return Response({"detail": f"unknown product {sku}"}, status=400)
    if product["stock"] < qty:
        return Response({"detail": "insufficient stock"}, status=400)

    CartItem.objects.update_or_create(
        user_id=request.user.id,
        product_sku=sku,
        defaults={
            "name": product["name"],
            "unit_price": Decimal(str(product["price"])),
            "quantity": qty,
        },
    )
    return _cart_response(request.user.id)


@api_view(["DELETE"])
def remove_item(request: Request, sku: str) -> Response:
    CartItem.objects.filter(user_id=request.user.id, product_sku=sku).delete()
    return _cart_response(request.user.id)


@api_view(["POST"])
def clear_cart(request: Request) -> Response:
    CartItem.objects.filter(user_id=request.user.id).delete()
    return _cart_response(request.user.id)
