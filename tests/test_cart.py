import pytest

from cart import views
from cart.catalog_client import ProductNotFound
from cart.models import CartItem

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_catalog(monkeypatch):
    """Stub the REST call to catalog-service."""
    products = {
        "SKU-1": {"sku": "SKU-1", "name": "Thing", "price": "9.99", "stock": 10},
    }

    def fake_get_product(sku):
        if sku not in products:
            raise ProductNotFound(sku)
        return products[sku]

    monkeypatch.setattr(views, "get_product", fake_get_product)
    return products


def test_add_item_checks_catalog_and_snapshots(api, auth_headers, mock_catalog):
    resp = api.post("/items/", {"product_sku": "SKU-1", "quantity": 2}, format="json", **auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"][0]["name"] == "Thing"
    assert body["total"] == "19.98"
    assert CartItem.objects.filter(user_id="user-123", product_sku="SKU-1").exists()


def test_add_unknown_product_rejected(api, auth_headers, mock_catalog):
    resp = api.post("/items/", {"product_sku": "NOPE", "quantity": 1}, format="json", **auth_headers)
    assert resp.status_code == 400


def test_add_insufficient_stock_rejected(api, auth_headers, mock_catalog):
    resp = api.post("/items/", {"product_sku": "SKU-1", "quantity": 999}, format="json", **auth_headers)
    assert resp.status_code == 400


def test_cart_requires_auth(api):
    assert api.get("/").status_code == 401


def test_get_and_clear_cart(api, auth_headers, mock_catalog):
    api.post("/items/", {"product_sku": "SKU-1", "quantity": 1}, format="json", **auth_headers)
    assert len(api.get("/", **auth_headers).json()["items"]) == 1
    api.post("/clear/", **auth_headers)
    assert api.get("/", **auth_headers).json()["items"] == []
