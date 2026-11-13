from typing import Callable, Dict, List
from .discounts import (
    Discount, PercentDiscount, FixedDiscount, ThreeForTwoDiscount,
    LoyaltyDiscount, FirstOrderDiscount, FreeDeliveryDiscount, PromoCodeDiscount,
)

class DiscountRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._creators: Dict[str, Callable] = {}
        return cls._instance
    def register(self, type_name: str, creator: Callable) -> None:
        self._creators[type_name] = creator
    def get(self, type_name: str) -> Callable:
        return self._creators.get(type_name)

def register_defaults(registry: DiscountRegistry = None) -> None:
    registry = registry or DiscountRegistry()
    registry.register("percent", lambda cfg: PercentDiscount(name=cfg["name"], percent=cfg["value"]))
    registry.register("fixed", lambda cfg: FixedDiscount(name=cfg["name"], value=cfg["value"], threshold=cfg.get("threshold", 0)))
    registry.register("threeForTwo", lambda cfg: ThreeForTwoDiscount(name=cfg["name"], category=cfg["category"]))
    registry.register("loyalty", lambda cfg: LoyaltyDiscount(name=cfg["name"], percent=cfg.get("percent", 5), days=cfg.get("days", 30)))
    registry.register("firstOrder", lambda cfg: FirstOrderDiscount(name=cfg["name"], percent=cfg.get("percent", 10)))
    registry.register("freeDelivery", lambda cfg: FreeDeliveryDiscount(name=cfg["name"], threshold=cfg["threshold"]))
    registry.register("promo", lambda cfg: PromoCodeDiscount(
        name=cfg["name"], code=cfg["code"], kind=cfg["kind"], value=cfg["value"],
        expires=cfg.get("expires"), active=cfg.get("active", True)
    ))

class DiscountFactory:
    def __init__(self, registry: DiscountRegistry = None):
        self._registry = registry or DiscountRegistry()
    def create(self, type_name: str, config: dict) -> Discount:
        creator = self._registry.get(type_name)
        if creator is None:
            raise ValueError(f"Unknown discount type: {type_name!r}")
        return creator(config)
    def create_all(self, configs: List[dict]) -> List[Discount]:
        return [self.create(cfg["type"], cfg) for cfg in configs]