# Движок скидок «Штучки-Дрючки»

Расширяемый движок расчёта скидок на Python 3.10+.

## Структура
discount_engine/
money.py # Decimal + банковское округление (half-to-even)
models.py # Product, CartItem, Customer, Order, AppliedDiscount, PricingResult
context.py # DiscountContext — единственный мутируемый объект расчёта
discounts/
base.py # Абстракция Discount + enum Stage
percent.py # Процентная скидка
fixed.py # Фиксированная скидка
three_for_two.py # 3 по цене 2
loyalty.py # Лояльность 5% / 30 дней
first_order.py # Первый заказ 10%
free_delivery.py # Бесплатная доставка
promo_code.py # Промокод (процент или фикс)
factory.py # DiscountFactory + DiscountRegistry (Singleton)
engine.py # PricingEngine — оркестратор
tests/ # pytest
demo.py # демо


## Паттерны
| Паттерн | Где |
|---|---|
| **Стратегия** | Каждая скидка — подкласс `Discount` с методом `apply(ctx)` |
| **Фабрика** | `DiscountFactory.create(type, config)` |
| **Синглтон** | `DiscountRegistry` — реестр создателей; **не хранит состояние заказа** |
| **Полиморфизм** | `PricingEngine` вызывает `d.apply(ctx)` не проверяя класс |
| **Инкапсуляция** | Всё состояние расчёта — внутри `DiscountContext` |

## Порядок применения
1. **QUANTITY** — 3-по-цене-2.
2. **PERCENT** — процентные скидки + разрешение конфликта «обычная vs % промокод» (ничья → промокод), затем лояльность и первый заказ.
3. **FIXED** — фиксированные скидки и фикс-промокоды.
4. **DELIVERY** — бесплатная доставка.
Внутри стадии — порядок конфигурации. Каждая следующая скидка считается от уже уменьшенной суммы.

## Округление
Все денежные величины — `Decimal`. Округление — **half-to-even** (банковское) до копеек **после каждой операции** (при формировании `AppliedDiscount` и обновлении сумм).
`Decimal("10.005") -> 10.00`, `Decimal("10.015") -> 10.02`.

## Промокоды
- Сравнение кодов — **точное, регистрозависимое** (`ctx.order.promo_code == cfg.code`).
- Просроченный (created_at > expires) — не применяется.
- Дата окончания включительна (`created_at == expires` — ОК).
- `active=False` — не применяется.
- Один промокод применяется не более одного раза в расчёте.

## Границы
- `quantity > 0`, `basePrice ≥ 0`, `deliveryCost ≥ 0` — иначе `ValueError`.
- Лояльность: `0 ≤ delta ≤ 30` дней, будущее — некорректно, скидки нет.
- Бесплатная доставка: `goods_total > threshold` (строго).
- Скидка не превышает уменьшаемую часть; итог не уходит ниже 0.

## Запуск
```powershell
pip install -r requirements.txt
python demo.py
pytest -v