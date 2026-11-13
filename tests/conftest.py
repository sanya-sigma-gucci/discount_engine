"""Общие фикстуры и хелперы для тестов."""
from datetime import date
from decimal import Decimal

import pytest

from discount_engine import (
    Product, CartItem, Customer, Order, PricingEngine, DiscountFactory,
)


@pytest.fixture
def engine():
    return PricingEngine()


@pytest.fixture
def factory():
    return DiscountFactory()


def make_order(items_spec, delivery_cost=0, promo_code=None,
               is_first_order=False, last_purchase=None,
               created_at=date(2024, 6, 15), order_id="O-1"):
    """items_spec: список кортежей (product_id, name, price, category, qty)."""
    items = []
    for pid, name, price, cat, qty in items_spec:
        product = Product(
            id=pid, name=name,
            base_price=Decimal(str(price)), category=cat,
        )
        items.append(CartItem(product=product, quantity=qty))
    customer = Customer(
        id="C-1",
        last_purchase_date=last_purchase,
        is_first_order=is_first_order,
    )
    return Order(
        id=order_id,
        customer=customer,
        items=items,
        created_at=created_at,
        delivery_cost=Decimal(str(delivery_cost)),
        promo_code=promo_code,
    )