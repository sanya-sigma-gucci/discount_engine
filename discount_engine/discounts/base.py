from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from ..context import DiscountContext
from ..models import AppliedDiscount

class Stage(Enum):
    QUANTITY = "quantity"
    PERCENT = "percent"
    FIXED = "fixed"
    DELIVERY = "delivery"

class Discount(ABC):
    def __init__(self, name: str):
        self._name = name
    @property
    def name(self) -> str:
        return self._name
    @property
    @abstractmethod
    def stage(self) -> Stage: ...
    @property
    def is_promo(self) -> bool:
        return False
    @property
    def conflicts_with_percent_promo(self) -> bool:
        return False
    @abstractmethod
    def apply(self, ctx: DiscountContext) -> Optional[AppliedDiscount]: ...