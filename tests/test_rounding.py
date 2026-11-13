"""Округление half-to-even."""
from decimal import Decimal

from discount_engine import PercentDiscount, DiscountContext
from discount_engine.money import money
from tests.conftest import make_order


def test_money_half_to_even_down():
    # 10.005 -> 10.00 (последняя цифра 0 — чётная, вниз)
    assert money(Decimal("10.005")) == Decimal("10.00")


def test_money_half_to_even_up():
    # 10.015 -> 10.02 (последняя цифра 1 — нечётная, вверх)
    assert money(Decimal("10.015")) == Decimal("10.02")


def test_percent_rounding_half_to_even_down():
    order = make_order([("p1", "A", 100.05, "Cat", 1)])
    ctx = DiscountContext(order=order,
                          goods_total=Decimal("100.05"),
                          delivery_cost=Decimal("0"))
    rec = PercentDiscount(name="10%", percent=10).apply(ctx)
    assert rec.amount == Decimal("10.00")


def test_percent_rounding_half_to_even_up():
    order = make_order([("p1", "A", 100.15, "Cat", 1)])
    ctx = DiscountContext(order=order,
                          goods_total=Decimal("100.15"),
                          delivery_cost=Decimal("0"))
    rec = PercentDiscount(name="10%", percent=10).apply(ctx)
    assert rec.amount == Decimal("10.02")