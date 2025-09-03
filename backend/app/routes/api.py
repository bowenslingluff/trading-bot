# /trades route
# This file will contain all the API endpoints for the frontend
from fastapi import APIRouter
from alpaca_client import get_account, get_positions, get_trades, place_order, get_market_data

router = APIRouter()

@router.get("/account")
async def get_account():
    return get_account()

@router.get("/positions")
async def get_positions():
    return get_positions()

@router.get("/orders")
async def get_trades():
    return get_trades()

@router.post("/orders")
async def place_order(order: dict):
    return place_order(order)

@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    return get_market_data(symbol)

@router.get("/status")
async def get_bot_status():
    return get_bot_status()