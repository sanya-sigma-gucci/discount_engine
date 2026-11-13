from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Optional
from .money import dec, money

@dataclass
class Product:
    id: str
    name: str
    base_price: Decimal
    category: str

    def __post_init__(self):
        self.base_price = dec(self.base_price)
        if self.base_price < 0:
            raise ValueError("base_price must be >= 0")

@dataclass
class CartItem:
    product: Product
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")

@dataclass
class Customer:
    id: str
    last_purchase_date: Optional[date] = None
    is_first_order: bool = False

@dataclass
class Order:
    id: str
    customer: Customer
    items: List[CartItem]
    created_at: date
    delivery_cost: Decimal
    promo_code: Optional[str] = None

    def __post_init__(self):
        self.delivery_cost = dec(self.delivery_cost)
        if self.delivery_cost < 0:
            raise ValueError("delivery_cost must be >= 0")

@dataclass
class AppliedDiscount:
    name: str
    amount: Decimal
    reason: str

@dataclass
class PricingResult:
    base_total: Decimal
    applied_discounts: List[AppliedDiscount]
    final_total: Decimal