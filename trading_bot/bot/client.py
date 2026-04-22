import hashlib
import hmac
import json
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from bot.logging_config import setup_logging


class BinanceAPIError(Exception):
    """Raised when Binance returns an API error response."""


class BinanceNetworkError(Exception):
    """Raised when a network error occurs while calling Binance API."""


class BinanceFuturesClient:
    """
    Small Binance Futures Testnet client.

    This class is responsible for:
    - loading API credentials
    - signing requests
    - sending requests to Binance Futures Testnet
    - logging API requests, responses, and errors
    """

    def __init__(self) -> None:
        load_dotenv()

        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.base_url = os.getenv(
            "BINANCE_FUTURES_BASE_URL",
            "https://testnet.binancefuture.com",
        ).rstrip("/")

        self.logger = setup_logging()

        if not self.api_key:
            raise ValueError("BINANCE_API_KEY is missing. Please add it to your .env file.")

        if not self.api_secret:
            raise ValueError("BINANCE_API_SECRET is missing. Please add it to your .env file.")

    def _generate_signature(self, params: dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature required by Binance signed endpoints.
        """

        query_string = urlencode(params)

        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _redact_sensitive_data(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Hide sensitive values before writing data to log file.
        """

        safe_params = params.copy()

        if "signature" in safe_params:
            safe_params["signature"] = "<redacted>"

        return safe_params

    def _send_signed_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send a signed request to Binance Futures API.
        """

        url = f"{self.base_url}{endpoint}"

        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        params["signature"] = self._generate_signature(params)

        headers = {
            "X-MBX-APIKEY": self.api_key,
        }

        safe_params = self._redact_sensitive_data(params)

        self.logger.info(
            "API request | method=%s url=%s params=%s",
            method,
            url,
            json.dumps(safe_params, sort_keys=True),
        )

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=10,
            )
        except requests.RequestException as exc:
            self.logger.error("Network error | %s", str(exc))
            raise BinanceNetworkError(f"Network error: {exc}") from exc

        self.logger.info(
            "API response | status_code=%s body=%s",
            response.status_code,
            response.text,
        )

        try:
            response_data = response.json()
        except ValueError:
            response_data = {
                "raw_response": response.text,
            }

        if response.status_code >= 400:
            error_message = response_data.get("msg", "Unknown Binance API error")
            self.logger.error(
                "Binance API error | %s | payload=%s",
                error_message,
                response_data,
            )
            raise BinanceAPIError(error_message)

        return response_data

    def place_order(self, order_params: dict[str, Any]) -> dict[str, Any]:
        """
        Place a real order on Binance Futures Testnet.
        """

        return self._send_signed_request(
            method="POST",
            endpoint="/fapi/v1/order",
            params=order_params,
        )

    def test_order(self, order_params: dict[str, Any]) -> dict[str, Any]:
        """
        Validate an order using Binance test order endpoint.

        This does not create a real order.
        It only checks whether the order request is valid.
        """

        return self._send_signed_request(
            method="POST",
            endpoint="/fapi/v1/order/test",
            params=order_params,
        )