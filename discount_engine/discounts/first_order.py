from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import dec, money
from .base import Discount, Stage

class FirstOrderDiscount(Discount):
    def __init__(self, name: str, percent=10):
        super().__init__(name)
        self.percent = dec(percent)
    @property
    def stage(self) -> Stage:
        return Stage.PERCENT
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if self.name in ctx.applied_names: return None
        if not ctx.order.customer.is_first_order: return None
        amount = min(money(ctx.goods_total * self.percent / Decimal(100)), ctx.goods_total)
        if amount <= 0: return None
        return ctx.apply_goods_discount(self.name, amount, "Первый заказ")