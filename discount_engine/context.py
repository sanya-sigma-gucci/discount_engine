from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Set
from .models import AppliedDiscount, Order
from .money import money

@dataclass
class DiscountContext:
    order: Order
    goods_total: Decimal
    delivery_cost: Decimal
    applied: List[AppliedDiscount] = field(default_factory=list)
    applied_names: Set[str] = field(default_factory=set)

    def apply_goods_discount(self, name: str, amount: Decimal, reason: str) -> AppliedDiscount:
        amount = money(min(amount, self.goods_total))
        self.goods_total = money(self.goods_total - amount)
        record = AppliedDiscount(name=name, amount=amount, reason=reason)
        self.applied.append(record)
        self.applied_names.add(name)
        return record

    def apply_delivery_discount(self, name: str, amount: Decimal, reason: str) -> AppliedDiscount:
        amount = money(min(amount, self.delivery_cost))
        self.delivery_cost = money(self.delivery_cost - amount)
        record = AppliedDiscount(name=name, amount=amount, reason=reason)
        self.applied.append(record)
        self.applied_names.add(name)
        return record