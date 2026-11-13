from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import dec, money
from .base import Discount, Stage

class FixedDiscount(Discount):
    def __init__(self, name: str, value, threshold=0):
        super().__init__(name)
        self.value = dec(value)
        self.threshold = dec(threshold)
    @property
    def stage(self) -> Stage:
        return Stage.FIXED
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if self.name in ctx.applied_names: return None
        if ctx.goods_total < self.threshold: return None
        amount = money(min(self.value, ctx.goods_total))
        if amount <= 0: return None
        return ctx.apply_goods_discount(self.name, amount, f"Фикс. скидка {self.value} руб.")