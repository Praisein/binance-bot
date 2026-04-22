import argparse
import json
import sys

from bot.client import BinanceAPIError, BinanceNetworkError
from bot.logging_config import setup_logging
from bot.orders import OrderService
from bot.validators import ValidationError, validate_order_inputs


def create_parser() -> argparse.ArgumentParser:
    """
    Create CLI argument parser.
    """

    parser = argparse.ArgumentParser(
        description="Simplified Binance Futures Testnet Trading Bot"
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, for example BTCUSDT",
    )

    parser.add_argument(
        "--side",
        required=True,
        help="Order side: BUY or SELL",
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT",
    )

    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity, for example 0.001",
    )

    parser.add_argument(
        "--price",
        required=False,
        help="Order price. Required for LIMIT orders.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the order without actually placing it.",
    )

    return parser


def print_order_summary(order_data: dict, dry_run: bool) -> None:
    """
    Print a clear order request summary before sending the request.
    """

    print("\nOrder Request Summary")
    print("---------------------")
    print(f"Symbol     : {order_data['symbol']}")
    print(f"Side       : {order_data['side']}")
    print(f"Order Type : {order_data['order_type']}")
    print(f"Quantity   : {order_data['quantity']}")
    print(f"Price      : {order_data['price'] if order_data['price'] else 'N/A'}")
    print(f"Dry Run    : {'Yes' if dry_run else 'No'}")


def print_order_response(response: dict) -> None:
    """
    Print important details from Binance order response.
    """

    print("\nOrder Response Details")
    print("----------------------")

    if not response:
        print("No response body returned.")
        print("This usually happens when using Binance test order endpoint.")
        return

    print(f"Order ID     : {response.get('orderId', 'N/A')}")
    print(f"Status       : {response.get('status', 'N/A')}")
    print(f"Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"Average Price: {response.get('avgPrice', 'N/A')}")

    print("\nFull Response")
    print("-------------")
    print(json.dumps(response, indent=4))


def main() -> int:
    """
    CLI entry point.
    """

    logger = setup_logging()
    parser = create_parser()
    args = parser.parse_args()

    try:
        validated_order = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
        )

        print_order_summary(validated_order, args.dry_run)

        order_service = OrderService()

        response = order_service.place_order(
            symbol=validated_order["symbol"],
            side=validated_order["side"],
            order_type=validated_order["order_type"],
            quantity=validated_order["quantity"],
            price=validated_order["price"],
            dry_run=args.dry_run,
        )

        print_order_response(response)

        if args.dry_run:
            print("\nSuccess: Order request is valid. No real order was placed.")
        else:
            print("\nSuccess: Order placed successfully on Binance Futures Testnet.")

        return 0

    except ValidationError as exc:
        logger.error("Validation error: %s", str(exc))
        print(f"\nValidation Error: {exc}")
        return 1

    except BinanceAPIError as exc:
        logger.error("Binance API error: %s", str(exc))
        print(f"\nBinance API Error: {exc}")
        return 1

    except BinanceNetworkError as exc:
        logger.error("Network error: %s", str(exc))
        print(f"\nNetwork Error: {exc}")
        return 1

    except Exception as exc:
        logger.exception("Unexpected error")
        print(f"\nUnexpected Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())