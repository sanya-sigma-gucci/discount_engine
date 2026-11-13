"""Интеграционные тесты комбинаций и порядка применения."""
from datetime import date
from decimal import Decimal

from tests.conftest import make_order


def test_three_for_two_before_percent(engine, factory):
    order = make_order([("p1", "A", 100, "Books", 3)])
    discounts = factory.create_all([
        {"type": "threeForTwo", "category": "Books", "name": "3for2"},
        {"type": "percent", "value": 10, "name": "10%"},
    ])
    result = engine.calculate(order, discounts)

    assert result.applied_discounts[0].name == "3for2"
    assert result.applied_discounts[0].amount == Decimal("100.00")
    assert result.applied_discounts[1].name == "10%"
    assert result.applied_discounts[1].amount == Decimal("20.00")
    assert result.final_total == Decimal("180.00")


def test_promo_beats_regular_percent(engine, factory):
    order = make_order([("p1", "A", 1000, "Cat", 1)], promo_code="BIG")
    discounts = factory.create_all([
        {"type": "percent", "value": 10, "name": "regular"},
        {"type": "promo", "name": "promo", "code": "BIG",
         "kind": "percent", "value": 15},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert "promo" in names and "regular" not in names
    assert result.final_total == Decimal("850.00")


def test_regular_beats_weak_promo(engine, factory):
    order = make_order([("p1", "A", 1000, "Cat", 1)], promo_code="WEAK")
    discounts = factory.create_all([
        {"type": "percent", "value": 20, "name": "regular"},
        {"type": "promo", "name": "promo", "code": "WEAK",
         "kind": "percent", "value": 5},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert "regular" in names and "promo" not in names
    assert result.final_total == Decimal("800.00")


def test_tie_goes_to_promo(engine, factory):
    order = make_order([("p1", "A", 1000, "Cat", 1)], promo_code="TIE")
    discounts = factory.create_all([
        {"type": "percent", "value": 10, "name": "regular"},
        {"type": "promo", "name": "promo", "code": "TIE",
         "kind": "percent", "value": 10},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert "promo" in names and "regular" not in names


def test_fixed_promo_coexists_with_percent(engine, factory):
    order = make_order([("p1", "A", 1000, "Cat", 1)], promo_code="FIX")
    discounts = factory.create_all([
        {"type": "percent", "value": 10, "name": "regular"},
        {"type": "promo", "name": "promo", "code": "FIX",
         "kind": "fixed", "value": 200},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert "regular" in names and "promo" in names
    assert result.final_total == Decimal("700.00")


def test_loyalty_and_first_order_stack_with_winner(engine, factory):
    order = make_order(
        [("p1", "A", 1000, "Cat", 1)],
        is_first_order=True,
        last_purchase=date(2024, 6, 10),
        created_at=date(2024, 6, 15),
        promo_code="BIG",
    )
    discounts = factory.create_all([
        {"type": "percent", "value": 10, "name": "regular"},
        {"type": "promo", "name": "promo", "code": "BIG",
         "kind": "percent", "value": 20},
        {"type": "loyalty", "name": "loyalty"},
        {"type": "firstOrder", "name": "first"},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert "promo" in names and "regular" not in names
    assert "loyalty" in names and "first" in names
    assert result.final_total == Decimal("684.00")


def test_free_delivery_checked_after_discounts(engine, factory):
    # 5200 > 5000, но после 10% goods=4680 < 5000 -> доставка не бесплатна
    order = make_order([("p1", "A", 5200, "Cat", 1)], delivery_cost=200)
    discounts = factory.create_all([
        {"type": "percent", "value": 10, "name": "regular"},
        {"type": "freeDelivery", "name": "fd", "threshold": 5000},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert "fd" not in names
    assert result.final_total == Decimal("4880.00")


def test_breakdown_order_matches_calculation(engine, factory):
    order = make_order([("p1", "A", 100, "Books", 3)], delivery_cost=100)
    discounts = factory.create_all([
        {"type": "threeForTwo", "category": "Books", "name": "3for2"},
        {"type": "percent", "value": 10, "name": "10%"},
        {"type": "fixed", "name": "fixed", "value": 20, "threshold": 0},
        {"type": "freeDelivery", "name": "fd", "threshold": 100},
    ])
    result = engine.calculate(order, discounts)
    names = [d.name for d in result.applied_discounts]
    assert names == ["3for2", "10%", "fixed", "fd"]
    assert result.base_total == Decimal("400.00")
    assert result.final_total == Decimal("160.00")


def test_empty_cart(engine, factory):
    order = make_order([])
    discounts = factory.create_all([
        {"type": "percent", "value": 10, "name": "10%"},
    ])
    result = engine.calculate(order, discounts)
    assert result.final_total == Decimal("0.00")
    assert result.applied_discounts == []