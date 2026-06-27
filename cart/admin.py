from django.contrib import admin

from .models import CartItem, OutboxEvent


@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "status", "attempts", "created_at", "published_at")
    list_filter = ("status", "topic")
    search_fields = ("id", "topic", "correlation_id")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user_id", "product_sku", "quantity", "unit_price")
    search_fields = ("user_id", "product_sku")
