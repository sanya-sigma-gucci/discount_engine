from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import dec, money
from .base import Discount, Stage

class LoyaltyDiscount(Discount):
    def __init__(self, name: str, percent=5, days=30):
        super().__init__(name)
        self.percent = dec(percent)
        self.days = int(days)
    @property
    def stage(self) -> Stage:
        return Stage.PERCENT
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if self.name in ctx.applied_names: return None
        last = ctx.order.customer.last_purchase_date
        if last is None: return None
        delta = (ctx.order.created_at - last).days
        if delta < 0 or delta > self.days: return None
        amount = min(money(ctx.goods_total * self.percent / Decimal(100)), ctx.goods_total)
        if amount <= 0: return None
        return ctx.apply_goods_discount(self.name, amount, f"Последняя покупка {delta} дн. назад")