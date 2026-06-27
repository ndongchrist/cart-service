"""Thin REST client for catalog-service over ClusterIP DNS.

The base URL is the Kubernetes Service name (the contract), injected via the
ConfigMap as CATALOG_URL. The correlation id is propagated as a header so a
request can be traced across services.
"""
from __future__ import annotations

import os

import requests

from config.middleware import get_correlation_id

CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog-service")
TIMEOUT = float(os.environ.get("CATALOG_TIMEOUT", "3"))


class ProductNotFound(Exception):
    pass


def get_product(sku: str) -> dict:
    """Return the catalog product dict, or raise ProductNotFound."""
    resp = requests.get(
        f"{CATALOG_URL}/products/{sku}/",
        headers={"X-Correlation-Id": get_correlation_id()},
        timeout=TIMEOUT,
    )
    if resp.status_code == 404:
        raise ProductNotFound(sku)
    resp.raise_for_status()
    return resp.json()
