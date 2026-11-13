"""Unit-тесты каждой стратегии: позитив + негатив."""
from datetime import date
from decimal import Decimal

from discount_engine import (
    PercentDiscount, FixedDiscount, ThreeForTwoDiscount,
    LoyaltyDiscount, FirstOrderDiscount, FreeDeliveryDiscount,
    PromoCodeDiscount, DiscountContext,
)
from discount_engine.money import money
from tests.conftest import make_order


def _ctx(order):
    goods = money(sum((i.product.base_price * i.quantity for i in order.items),
                      Decimal(0)))
    return DiscountContext(order=order, goods_total=goods,
                           delivery_cost=order.delivery_cost)


# ---------- Percent ----------

def test_percent_applies():
    ctx = _ctx(make_order([("p1", "A", 100, "Cat", 1)]))
    rec = PercentDiscount(name="10%", percent=10).apply(ctx)
    assert rec is not None
    assert rec.amount == Decimal("10.00")
    assert ctx.goods_total == Decimal("90.00")


def test_percent_min_total_not_met():
    ctx = _ctx(make_order([("p1", "A", 100, "Cat", 1)]))
    rec = PercentDiscount(name="10%", percent=10, min_total=200).apply(ctx)
    assert rec is None


# ---------- Fixed ----------

def test_fixed_applies_at_threshold():
    ctx = _ctx(make_order([("p1", "A", 500, "Cat", 1)]))
    rec = FixedDiscount(name="fixed", value=100, threshold=500).apply(ctx)
    assert rec.amount == Decimal("100.00")
    assert ctx.goods_total == Decimal("400.00")


def test_fixed_below_threshold_skips():
    ctx = _ctx(make_order([("p1", "A", 400, "Cat", 1)]))
    rec = FixedDiscount(name="fixed", value=100, threshold=500).apply(ctx)
    assert rec is None


def test_fixed_does_not_go_below_zero():
    ctx = _ctx(make_order([("p1", "A", 100, "Cat", 1)]))
    rec = FixedDiscount(name="fixed", value=500, threshold=0).apply(ctx)
    assert rec.amount == Decimal("100.00")
    assert ctx.goods_total == Decimal("0.00")


# ---------- 3-for-2 ----------

def test_three_for_two_applies():
    ctx = _ctx(make_order([("p1", "A", 100, "Books", 3)]))
    rec = ThreeForTwoDiscount(name="3for2", category="Books").apply(ctx)
    assert rec.amount == Decimal("100.00")
    assert ctx.goods_total == Decimal("200.00")


def test_three_for_two_cheapest_is_free():
    # Цены 1000, 500, 300 -> бесплатная = 300
    ctx = _ctx(make_order([
        ("p1", "A", 1000, "Books", 1),
        ("p2", "B", 500, "Books", 1),
        ("p3", "C", 300, "Books", 1),
    ]))
    rec = ThreeForTwoDiscount(name="3for2", category="Books").apply(ctx)
    assert rec.amount == Decimal("300.00")


def test_three_for_two_under_three_units():
    ctx = _ctx(make_order([("p1", "A", 100, "Books", 2)]))
    rec = ThreeForTwoDiscount(name="3for2", category="Books").apply(ctx)
    assert rec is None


def test_three_for_two_wrong_category():
    ctx = _ctx(make_order([("p1", "A", 100, "Toys", 3)]))
    rec = ThreeForTwoDiscount(name="3for2", category="Books").apply(ctx)
    assert rec is None


# ---------- Loyalty ----------

def test_loyalty_within_30_days_inclusive():
    ctx = _ctx(make_order(
        [("p1", "A", 1000, "Cat", 1)],
        last_purchase=date(2024, 5, 16),
        created_at=date(2024, 6, 15),
    ))
    rec = LoyaltyDiscount(name="loyalty").apply(ctx)
    assert rec is not None
    assert rec.amount == Decimal("50.00")


def test_loyalty_31_days_skips():
    ctx = _ctx(make_order(
        [("p1", "A", 1000, "Cat", 1)],
        last_purchase=date(2024, 5, 15),
        created_at=date(2024, 6, 15),
    ))
    assert LoyaltyDiscount(name="loyalty").apply(ctx) is None


def test_loyalty_future_date_skips():
    ctx = _ctx(make_order(
        [("p1", "A", 1000, "Cat", 1)],
        last_purchase=date(2024, 7, 1),
        created_at=date(2024, 6, 15),
    ))
    assert LoyaltyDiscount(name="loyalty").apply(ctx) is None


def test_loyalty_no_previous_purchase_skips():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], last_purchase=None))
    assert LoyaltyDiscount(name="loyalty").apply(ctx) is None


# ---------- First order ----------

def test_first_order_applies():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], is_first_order=True))
    rec = FirstOrderDiscount(name="first").apply(ctx)
    assert rec.amount == Decimal("100.00")


def test_first_order_false_skips():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], is_first_order=False))
    assert FirstOrderDiscount(name="first").apply(ctx) is None


# ---------- Free delivery ----------

def test_free_delivery_strictly_above():
    ctx = _ctx(make_order([("p1", "A", 5001, "Cat", 1)], delivery_cost=200))
    rec = FreeDeliveryDiscount(name="fd", threshold=5000).apply(ctx)
    assert rec.amount == Decimal("200.00")
    assert ctx.delivery_cost == Decimal("0.00")


def test_free_delivery_at_threshold_skips():
    ctx = _ctx(make_order([("p1", "A", 5000, "Cat", 1)], delivery_cost=200))
    assert FreeDeliveryDiscount(name="fd", threshold=5000).apply(ctx) is None


# ---------- Promo ----------

def test_promo_percent_applies():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], promo_code="SAVE10"))
    rec = PromoCodeDiscount(name="promo", code="SAVE10",
                            kind="percent", value=10).apply(ctx)
    assert rec.amount == Decimal("100.00")


def test_promo_fixed_applies():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], promo_code="SAVE200"))
    rec = PromoCodeDiscount(name="promo", code="SAVE200",
                            kind="fixed", value=200).apply(ctx)
    assert rec.amount == Decimal("200.00")


def test_promo_wrong_code_skips():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], promo_code="WRONG"))
    assert PromoCodeDiscount(name="promo", code="SAVE10",
                             kind="percent", value=10).apply(ctx) is None


def test_promo_expired_skips():
    ctx = _ctx(make_order(
        [("p1", "A", 1000, "Cat", 1)],
        promo_code="SAVE10",
        created_at=date(2024, 7, 1),
    ))
    assert PromoCodeDiscount(name="promo", code="SAVE10", kind="percent",
                             value=10,
                             expires=date(2024, 6, 30)).apply(ctx) is None


def test_promo_on_expiry_date_applies():
    ctx = _ctx(make_order(
        [("p1", "A", 1000, "Cat", 1)],
        promo_code="SAVE10",
        created_at=date(2024, 6, 30),
    ))
    assert PromoCodeDiscount(name="promo", code="SAVE10", kind="percent",
                             value=10,
                             expires=date(2024, 6, 30)).apply(ctx) is not None


def test_promo_inactive_skips():
    ctx = _ctx(make_order([("p1", "A", 1000, "Cat", 1)], promo_code="SAVE10"))
    assert PromoCodeDiscount(name="promo", code="SAVE10", kind="percent",
                             value=10, active=False).apply(ctx) is None