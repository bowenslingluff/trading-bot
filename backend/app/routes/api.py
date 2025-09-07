# /trades route
# This file will contain all the API endpoints for the frontend
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.alpaca_client import (
    get_account, get_positions, get_orders, get_market_data,
    market_order, limit_order, bracket_order, stop_loss, take_profit,
    cancel_order_by_id, get_order_status
)

router = APIRouter()

# Simple in-memory cache
cache = {}
CACHE_TTL = 60

def cached_call(key: str, fetch_fn):
    """Check cache, otherwise call function and store result"""
    now = time.time()
    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < CACHE_TTL:
            return data
    # Refresh
    data = fetch_fn()
    cache[key] = (data, now)
    return data

# Pydantic models for request validation
class MarketOrderRequest(BaseModel):
    symbol: str
    qty: int
    side: str  # "buy" or "sell"

class LimitOrderRequest(BaseModel):
    symbol: str
    qty: int
    side: str
    limit_price: float

class BracketOrderRequest(BaseModel):
    symbol: str
    qty: int
    side: str
    stop_loss: float
    take_profit: float
    order_type: str = "market"  # "market" or "limit"
    limit_price: float = None

class StopLossRequest(BaseModel):
    symbol: str
    qty: int
    stop_price: float

class TakeProfitRequest(BaseModel):
    symbol: str
    qty: int
    limit_price: float

@router.get("/account")
async def account():
    return cached_call("account", get_account)

@router.get("/positions")
async def positions():
    return get_positions()

@router.get("/orders")
async def orders():
    return get_orders()

@router.get("/market-data/{symbol}")
async def market_data(symbol: str):
    return get_market_data(symbol)

# Order Endpoints
@router.post("/orders/market")
async def place_market_order(order: MarketOrderRequest):
    try:
        return market_order(order.symbol, order.qty, order.side)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/limit")
async def place_limit_order(order: LimitOrderRequest):
    try:
        return limit_order(order.symbol, order.qty, order.side, order.limit_price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/bracket")
async def place_bracket_order(order: BracketOrderRequest):
    try:
        return bracket_order(
            order.symbol, order.qty, order.side, 
            order.stop_loss, order.take_profit, 
            order.order_type, order.limit_price
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/stop-loss")
async def place_stop_loss_order(order: StopLossRequest):
    try:
        return stop_loss(order.symbol, order.qty, order.stop_price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/take-profit")
async def place_take_profit_order(order: TakeProfitRequest):
    try:
        return take_profit(order.symbol, order.qty, order.limit_price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Order Management
@router.delete("/orders/{order_id}")
async def cancel_order_endpoint(order_id: str):
    try:
        return cancel_order_by_id(order_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_id}/status")
async def get_order_status_endpoint(order_id: str):
    try:
        status = get_order_status(order_id)
        return {"order_id": order_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Bot Status (placeholder for future)
@router.get("/status")
async def get_bot_status():
    return {
        "status": "running",
        "last_update": time.time(),
        "account": cached_call("account", get_account)
    }