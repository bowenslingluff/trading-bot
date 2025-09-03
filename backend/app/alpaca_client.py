# Alpaca API wrapper
# This file will contain the Alpaca API client implementation for fetching account data, positions, and trade history 

from alpaca.trading.client import TradingClient
from alpaca.data import StockHistoricalDataClient
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

#Utility functions
def get_trading_client():
    api_key = os.getenv('APCA-API-KEY-ID')
    secret_key = os.getenv('APCA-API-SECRET-KEY')
    
    if not api_key or not secret_key:
        raise ValueError("Missing Alpaca API credentials")
    
    return TradingClient(api_key, secret_key, paper=True)

def get_data_client():
    api_key = os.getenv('APCA-API-KEY-ID')
    secret_key = os.getenv('APCA-API-SECRET-KEY')
    
    if not api_key or not secret_key:
        raise ValueError("Missing Alpaca API credentials")
    
    return StockHistoricalDataClient(api_key, secret_key)

# Account
def get_account():
    trading_client = get_trading_client()
    account = trading_client.get_account()

    info = {
        "buying_power": account.buying_power,
        "cash": account.cash,
        "portfolio_value": account.portfolio_value,
        "last_trade_date": account.last_trade_date,
    }

    return info

def get_positions():
    trading_client = get_trading_client()
    positions = trading_client.get_all_positions()

    return positions

def get_orders(): 
    trading_client = get_trading_client()
    orders = trading_client.get_orders()

    return orders

#Place Orders
def market_order(symbol: str, qty: int, side: str):
    order_data = MarketOrderRequest(
        symbol=symbol.upper(),
        qty=qty,
        side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )
    return submit_order(order_data)

def limit_order(symbol: str, qty: int, side: str, limit_price: float):
    if not limit_price or limit_price <= 0:
        raise ValueError("Limit price must be positive")
    
    order_data = LimitOrderRequest(
        symbol=symbol.upper(),
        qty=qty,
        side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
        limit_price=limit_price,
        time_in_force=TimeInForce.DAY
    )

    return submit_order(order_data)

def bracket_order(symbol: str, qty: int, side: str, 
                       stop_loss: float, take_profit: float, 
                       order_type: str = "market", limit_price: float = None):
    # Build the main order first
    if order_type == "market":
        main_order = MarketOrderRequest(
            symbol=symbol.upper(),
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
    elif order_type == "limit":
        main_order = LimitOrderRequest(
            symbol=symbol.upper(),
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            limit_price=limit_price,
            time_in_force=TimeInForce.DAY
        )
    else:
        raise ValueError("Order type must be 'market' or 'limit'")
    
    # Add bracket components
    stop_loss_request = StopLossRequest(stop_price=stop_loss)
    take_profit_request = TakeProfitRequest(limit_price=take_profit)
    
    # Update main order with bracket properties
    main_order.order_class = OrderClass.BRACKET
    main_order.stop_loss = stop_loss_request
    main_order.take_profit = take_profit_request
    
    return submit_order(main_order)


def stop_loss(symbol: str, qty: int, stop_price: float):
    order_data = StopLossRequest(
        symbol=symbol.upper(),
        qty=qty,
        side=OrderSide.SELL,
        stop_price=stop_price,
        time_in_force=TimeInForce.DAY
    )
    return submit_order(order_data)

def take_profit(symbol: str, qty: int, limit_price: float):
    order_data = TakeProfitRequest(
        symbol=symbol.upper(),
        qty=qty,
        side=OrderSide.SELL,
        limit_price=limit_price,
        time_in_force=TimeInForce.DAY
    )

    return submit_order(order_data)

#Order Management
def submit_order(order_data):
    client = get_trading_client()
    order = client.submit_order(order_data)
    
    # Print order details for debugging
    for property_name, value in order:
        print(f'"{property_name}": {value}')
    
    return order

def cancel_order(order_id: str):
    # Cancel a pending order
    client = get_trading_client()
    client.cancel_order(order_id)

def get_order_status(order_id: str):
    # Check order status
    client = get_trading_client()
    order = client.get_order(order_id)
    return order.status

#Market Data
def get_market_data(symbol: str, timeframe: TimeFrame = TimeFrame.Day):

    client = get_data_client()
    
    bars_request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start=datetime.now() - timedelta(days=15)
    )
    
    bars = client.get_stock_bars(bars_request)
    return bars

