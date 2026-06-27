from django.apps import AppConfig


class CartConfig(AppConfig):
    name = "cart"
    # Distinct label so a service named after a Django builtin (e.g. "auth")
    # doesn't collide with django.contrib.* app labels.
    label = "cart_app"
