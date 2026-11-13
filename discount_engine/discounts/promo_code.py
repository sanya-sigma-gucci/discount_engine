from datetime import date
from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import dec, money
from .base import Discount, Stage

class PromoCodeDiscount(Discount):
    def __init__(self, name: str, code: str, kind: str, value, expires: Optional[date] = None, active: bool = True):
        super().__init__(name)
        self.code = code
        self.kind = kind
        self.value = dec(value)
        self.expires = expires
        self.active = active
    @property
    def stage(self) -> Stage:
        return Stage.PERCENT if self.kind == "percent" else Stage.FIXED
    @property
    def is_promo(self) -> bool:
        return True
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if not self.active or ctx.order.promo_code != self.code: return None
        if self.expires is not None and ctx.order.created_at > self.expires: return None
        if self.name in ctx.applied_names: return None
        amount = money(ctx.goods_total * self.value / Decimal(100)) if self.kind == "percent" else money(self.value)
        amount = min(amount, ctx.goods_total)
        if amount <= 0: return None
        return ctx.apply_goods_discount(self.name, amount, f"Промокод {self.code}")