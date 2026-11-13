from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import dec, money
from .base import Discount, Stage

class PercentDiscount(Discount):
    def __init__(self, name: str, percent, min_total=None):
        super().__init__(name)
        self.percent = dec(percent)
        self.min_total = dec(min_total) if min_total is not None else None
    @property
    def stage(self) -> Stage:
        return Stage.PERCENT
    @property
    def conflicts_with_percent_promo(self) -> bool:
        return True
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if self.name in ctx.applied_names: return None
        if ctx.goods_total <= 0: return None
        if self.min_total is not None and ctx.goods_total < self.min_total: return None
        amount = min(money(ctx.goods_total * self.percent / Decimal(100)), ctx.goods_total)
        if amount <= 0: return None
        return ctx.apply_goods_discount(self.name, amount, f"Скидка {self.percent}%")