"""Демо: заказ с несколькими скидками -> PricingResult."""
import json
from datetime import date
from decimal import Decimal

from discount_engine import (
    Product, CartItem, Customer, Order, PricingEngine, DiscountFactory,
)


def main():
    products = [
        Product(id="b1", name="Книга A", base_price=Decimal("800"), category="Книги"),
        Product(id="b2", name="Книга B", base_price=Decimal("600"), category="Книги"),
        Product(id="b3", name="Книга C", base_price=Decimal("400"), category="Книги"),
        Product(id="t1", name="Игрушка", base_price=Decimal("1500"), category="Игрушки"),
    ]
    items = [
        CartItem(product=products[0], quantity=1),
        CartItem(product=products[1], quantity=1),
        CartItem(product=products[2], quantity=1),
        CartItem(product=products[3], quantity=1),
    ]
    customer = Customer(
        id="cust-42",
        last_purchase_date=date(2024, 6, 1),
        is_first_order=False,
    )
    order = Order(
        id="ORD-2024-0001",
        customer=customer,
        items=items,
        created_at=date(2024, 6, 15),
        delivery_cost=Decimal("300"),
        promo_code="AUTUMN10",
    )

    configs = [
        {"type": "threeForTwo", "category": "Книги", "name": "3 по цене 2"},
        {"type": "percent", "value": 15, "name": "Осенняя распродажа 15%"},
        {"type": "promo", "name": "Промокод AUTUMN10",
         "code": "AUTUMN10", "kind": "percent", "value": 10,
         "expires": date(2024, 6, 30)},
        {"type": "loyalty", "percent": 5, "days": 30, "name": "Лояльность"},
        {"type": "fixed", "value": 200, "threshold": 1000,
         "name": "Фикс. 200 ₽ от 1000"},
        {"type": "freeDelivery", "threshold": 4000,
         "name": "Бесплатная доставка от 4000"},
    ]

    factory = DiscountFactory()
    discounts = factory.create_all(configs)

    engine = PricingEngine()
    result = engine.calculate(order, discounts)

    output = {
        "baseTotal": f"{result.base_total:.2f}",
        "appliedDiscounts": [
            {"name": d.name,
             "amount": f"{d.amount:.2f}",
             "reason": d.reason}
            for d in result.applied_discounts
        ],
        "finalTotal": f"{result.final_total:.2f}",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()