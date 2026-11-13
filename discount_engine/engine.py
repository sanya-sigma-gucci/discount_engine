from collections import defaultdict
from decimal import Decimal
from typing import Dict, List
from .context import DiscountContext
from .discounts import Discount, Stage
from .models import Order, PricingResult
from .money import money

class PricingEngine:
    def calculate(self, order: Order, discounts: List[Discount]) -> PricingResult:
        goods_total = money(sum((item.product.base_price * item.quantity for item in order.items), Decimal(0)))
        delivery_cost = money(order.delivery_cost)
        base_total = money(goods_total + delivery_cost)

        ctx = DiscountContext(order=order, goods_total=goods_total, delivery_cost=delivery_cost)

        by_stage: Dict[Stage, List[Discount]] = defaultdict(list)
        for d in discounts:
            by_stage[d.stage].append(d)

        for d in by_stage[Stage.QUANTITY]:
            d.apply(ctx)

        self._apply_percent_stage(by_stage[Stage.PERCENT], ctx)

        for d in by_stage[Stage.FIXED]:
            d.apply(ctx)

        for d in by_stage[Stage.DELIVERY]:
            d.apply(ctx)

        final_total = money(ctx.goods_total + ctx.delivery_cost)
        return PricingResult(base_total=base_total, applied_discounts=list(ctx.applied), final_total=final_total)

    def _apply_percent_stage(self, discounts: List[Discount], ctx: DiscountContext) -> None:
        regular = [d for d in discounts if not d.is_promo and d.conflicts_with_percent_promo]
        special = [d for d in discounts if not d.is_promo and not d.conflicts_with_percent_promo]
        promos = [d for d in discounts if d.is_promo]

        regular_savings = self._simulate(regular, ctx)
        best_promo = None
        best_promo_savings = Decimal(0)
        for p in promos:
            s = self._simulate([p], ctx)
            if s > best_promo_savings:
                best_promo_savings = s
                best_promo = p

        if best_promo is not None and best_promo_savings > 0 and best_promo_savings >= regular_savings:
            best_promo.apply(ctx)
        else:
            for d in regular:
                d.apply(ctx)

        for d in special:
            d.apply(ctx)

    def _simulate(self, discounts: List[Discount], ctx: DiscountContext) -> Decimal:
        if not discounts:
            return Decimal(0)
        saved_goods = ctx.goods_total
        saved_delivery = ctx.delivery_cost
        saved_len = len(ctx.applied)
        saved_names = set(ctx.applied_names)
        total = Decimal(0)
        try:
            for d in discounts:
                record = d.apply(ctx)
                if record is not None:
                    total += record.amount
        finally:
            ctx.goods_total = saved_goods
            ctx.delivery_cost = saved_delivery
            del ctx.applied[saved_len:]
            ctx.applied_names = saved_names
        return money(total)