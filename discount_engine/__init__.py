from .models import Product, CartItem, Customer, Order, AppliedDiscount, PricingResult
from .context import DiscountContext
from .engine import PricingEngine
from .factory import DiscountFactory, DiscountRegistry, register_defaults
from .discounts import (
    Discount, Stage,
    PercentDiscount, FixedDiscount, ThreeForTwoDiscount,
    LoyaltyDiscount, FirstOrderDiscount, FreeDeliveryDiscount, PromoCodeDiscount,
)
register_defaults()
