# Alpaca API wrapper
# This file will contain the Alpaca API client implementation for fetching account data, positions, and trade history 

from alpaca.trading.client import TradingClient
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
