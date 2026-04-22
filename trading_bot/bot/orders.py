from typing import Any

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging


class OrderService:
    """
    Handles order-related business logic.

    This class prepares order parameters and then uses
    BinanceFuturesClient to send them to Binance Futures Testnet.
    """

    def __init__(self, client: BinanceFuturesClient | None = None) -> None:
        self.client = client or BinanceFuturesClient()
        self.logger = setup_logging()

    def build_order_params(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
    ) -> dict[str, Any]:
        """
        Build Binance Futures order parameters.

        MARKET order requires:
            symbol, side, type, quantity

        LIMIT order requires:
            symbol, side, type, quantity, price, timeInForce
        """

        order_params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "newOrderRespType": "RESULT",
        }

        if order_type == "LIMIT":
            order_params["price"] = price
            order_params["timeInForce"] = "GTC"

        return order_params

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        Place an order or validate it using dry-run mode.
        """

        order_params = self.build_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        self.logger.info(
            "Order request summary | symbol=%s side=%s type=%s quantity=%s price=%s dry_run=%s",
            symbol,
            side,
            order_type,
            quantity,
            price,
            dry_run,
        )

        if dry_run:
            response = self.client.test_order(order_params)
        else:
            response = self.client.place_order(order_params)

        self.logger.info("Order completed successfully | response=%s", response)

        return response