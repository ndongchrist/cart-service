from django.urls import path

from . import views

# Kong routes /cart/* here with strip_path, so paths are relative to the cart root.
urlpatterns = [
    path("", views.get_cart, name="cart"),
    path("items/", views.add_item, name="cart-add"),
    path("items/<str:sku>/", views.remove_item, name="cart-remove"),
    path("clear/", views.clear_cart, name="cart-clear"),
]
