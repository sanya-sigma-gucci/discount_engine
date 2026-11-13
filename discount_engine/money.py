from decimal import Decimal, ROUND_HALF_EVEN

MONEY_QUANT = Decimal("0.01")

def dec(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))

def money(value) -> Decimal:
    return dec(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_EVEN)