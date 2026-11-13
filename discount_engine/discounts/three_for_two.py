from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import money
from .base import Discount, Stage

class ThreeForTwoDiscount(Discount):
    def __init__(self, name: str, category: str):
        super().__init__(name)
        self.category = category
    @property
    def stage(self) -> Stage:
        return Stage.QUANTITY
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if self.name in ctx.applied_names: return None
        prices = []
        for item in ctx.order.items:
            if item.product.category == self.category:
                prices.extend([item.product.base_price] * item.quantity)
        n = len(prices)
        free_count = n // 3
        if free_count == 0: return None
        prices.sort(reverse=True)
        free_prices = [prices[i * 3 + 2] for i in range(free_count)]
        amount = money(sum(free_prices, Decimal(0)))
        if amount <= 0: return None
        return ctx.apply_goods_discount(self.name, amount, f"Категория {self.category}: {free_count} бесплатно")