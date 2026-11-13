from decimal import Decimal
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount
from ..money import dec
from .base import Discount, Stage

class FreeDeliveryDiscount(Discount):
    def __init__(self, name: str, threshold):
        super().__init__(name)
        self.threshold = dec(threshold)
    @property
    def stage(self) -> Stage:
        return Stage.DELIVERY
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]:
        if self.name in ctx.applied_names: return None
        if ctx.goods_total <= self.threshold or ctx.delivery_cost <= 0: return None
        return ctx.apply_delivery_discount(self.name, ctx.delivery_cost, "Бесплатная доставка")