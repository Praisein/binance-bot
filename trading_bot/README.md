# Simplified Binance Futures Testnet Trading Bot

This is a small Python command-line application for placing MARKET and LIMIT orders on Binance Futures Testnet.

The project was created for the Python Developer application task. It focuses on clean structure, input validation, logging, and error handling.

## Features

- Place MARKET orders
- Place LIMIT orders
- Supports BUY and SELL sides
- Accepts user input using CLI arguments
- Validates user input before sending API requests
- Uses Binance Futures Testnet base URL
- Logs API requests, responses, and errors
- Handles validation errors, Binance API errors, and network errors
- Supports dry-run mode using Binance test order endpoint

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  cli.py
  README.md
  requirements.txt