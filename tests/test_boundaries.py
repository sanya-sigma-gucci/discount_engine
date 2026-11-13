"""Границы, ошибки и расширяемость."""
from decimal import Decimal

import pytest

from discount_engine import (
    Product, CartItem, DiscountFactory, DiscountRegistry,
)
from discount_engine.discounts import Discount, Stage


def test_negative_quantity_raises():
    p = Product(id="1", name="A", base_price=Decimal("10"), category="C")
    with pytest.raises(ValueError):
        CartItem(product=p, quantity=0)


def test_negative_price_raises():
    with pytest.raises(ValueError):
        Product(id="1", name="A", base_price=Decimal("-1"), category="C")


def test_unknown_discount_type_raises():
    factory = DiscountFactory()
    with pytest.raises(ValueError):
        factory.create("unknown_type_xyz", {"name": "x"})


def test_extensibility_new_discount_registered():
    """Расширяемость: новый класс + регистрация в реестре."""

    class ZeroDiscount(Discount):
        @property
        def stage(self) -> Stage:
            return Stage.PERCENT

        def apply(self, ctx):
            return None

    registry = DiscountRegistry()  # синглтон
    original = dict(registry._creators)
    try:
        registry.register("zero", lambda cfg: ZeroDiscount(name=cfg["name"]))
        factory = DiscountFactory(registry)
        d = factory.create("zero", {"name": "z"})
        assert d.name == "z"
    finally:
        registry._creators = original