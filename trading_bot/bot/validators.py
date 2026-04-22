from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize the trading symbol.

    Example:
        btcusdt -> BTCUSDT
    """

    if not symbol:
        raise ValidationError("Symbol is required.")

    symbol = symbol.strip().upper()

    if not symbol.endswith("USDT"):
        raise ValidationError("Only USDT-M symbols are supported. Example: BTCUSDT.")

    if len(symbol) < 6:
        raise ValidationError("Invalid symbol. Example format: BTCUSDT.")

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.

    Allowed values:
        BUY
        SELL
    """

    if not side:
        raise ValidationError("Side is required. Use BUY or SELL.")

    side = side.strip().upper()

    if side not in VALID_SIDES:
        raise ValidationError("Invalid side. Allowed values: BUY or SELL.")

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Allowed values:
        MARKET
        LIMIT
    """

    if not order_type:
        raise ValidationError("Order type is required. Use MARKET or LIMIT.")

    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError("Invalid order type. Allowed values: MARKET or LIMIT.")

    return order_type


def validate_positive_decimal(value: str, field_name: str) -> str:
    """
    Validate that a numeric input is a positive decimal.

    Returns the value as a string because Binance API expects string-like
    decimal values for quantity and price.
    """

    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{field_name} must be a valid number.")

    if decimal_value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")

    return format(decimal_value, "f")


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> dict:
    """
    Validate all order input values together.

    Price is required only for LIMIT orders.
    """

    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity = validate_positive_decimal(quantity, "Quantity")

    validated_price = None

    if validated_order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        validated_price = validate_positive_decimal(price, "Price")

    if validated_order_type == "MARKET" and price is not None:
        raise ValidationError("Price should not be provided for MARKET orders.")

    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_order_type,
        "quantity": validated_quantity,
        "price": validated_price,
    }