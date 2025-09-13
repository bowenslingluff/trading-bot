# strategies.py
from openai import OpenAI
import json
import os
import pandas as pd
import numpy as np

# Create client once
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    return pd.Series(prices).rolling(window=period, min_periods=period).mean()

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    prices = pd.Series(prices)
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = pd.Series(prices).ewm(span=fast).mean()
    ema_slow = pd.Series(prices).ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def detect_sma_crossover(prices, sma_20, sma_50):
    """Detect SMA(20) crossing above SMA(50)"""
    if len(prices) < 2:
        return False
    
    # Check if current bar has crossover
    current_sma20 = sma_20.iloc[-1]
    current_sma50 = sma_50.iloc[-1]
    prev_sma20 = sma_20.iloc[-2]
    prev_sma50 = sma_50.iloc[-2]
    
    # SMA(20) crosses above SMA(50)
    return (prev_sma20 <= prev_sma50) and (current_sma20 > current_sma50)

def check_trend_reversal(sma_20, sma_50):
    """Check if SMA(20) crosses below SMA(50)"""
    if len(sma_20) < 2:
        return False
    
    current_sma20 = sma_20.iloc[-1]
    current_sma50 = sma_50.iloc[-1]
    prev_sma20 = sma_20.iloc[-2]
    prev_sma50 = sma_50.iloc[-2]
    
    # SMA(20) crosses below SMA(50)
    return (prev_sma20 >= prev_sma50) and (current_sma20 < current_sma50)

def llm_strategy(df, symbol: str, qty: int):
    """
    Send technical analysis data to LLM for decision making
    """
    if len(df) < 70:
        return {"decision": "HOLD", "reason": "Insufficient data"}
    
    # Extract OHLCV data
    closes = df['close'].values
    volumes = df['volume'].values
    
    # Calculate technical indicators
    sma_20 = calculate_sma(closes, 20)
    sma_50 = calculate_sma(closes, 50)
    rsi_9 = calculate_rsi(closes, 9)
    macd_line, signal_line, histogram = calculate_macd(closes)

    
    # Get current and recent values
    current_price = closes[-1]
    current_sma20 = sma_20.iloc[-1]
    current_sma50 = sma_50.iloc[-1]
    current_rsi = rsi_9.iloc[-1]
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    
    # Get recent price action (last 10 bars)
    recent_closes = closes[-10:]
    recent_volumes = volumes[-10:]
    
    # Check for trend reversal
    trend_reversal = check_trend_reversal(sma_20, sma_50)
    
    # Prepare comprehensive data for LLM
    technical_data = {
        "symbol": symbol,
        "current_price": current_price,
        "sma_20": current_sma20,
        "sma_50": current_sma50,
        "rsi_9": current_rsi,
        "macd": current_macd,
        "signal": current_signal,
        "recent_closes": recent_closes,
        "recent_volumes": recent_volumes,
        "sma_20_trend": "above" if current_sma20 > current_sma50 else "below",
        "rsi_zone": get_rsi_zone(current_rsi),
        "price_vs_sma20": ((current_price - current_sma20) / current_sma20) * 100,
        "price_vs_sma50": ((current_price - current_sma50) / current_sma50) * 100,
        "volume_trend": get_volume_trend(recent_volumes),
        "crossover_detected": detect_sma_crossover(closes, sma_20, sma_50),
        "trend_reversal": trend_reversal
    }
    
    # Create LLM prompt with technical data
    prompt = create_prompt(technical_data, symbol, qty)
    print(len(prompt))
    print(prompt)
    # Get LLM response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response)
    decision = response.choices[0].message.content.strip()
    CONFIDENCE_THRESHOLD = 0.75
    if decision.upper() == "HOLD":
        return {"decision": "HOLD", "reason": "LLM recommended HOLD"}
    if trade_plan["confidence"] < CONFIDENCE_THRESHOLD:
        return {"decision": "HOLD", "reason": "Confidence below threshold"}
    
    try:
        trade_plan = json.loads(decision)
        # Add technical context to the trade plan
        trade_plan["technical_context"] = {
            "sma20": current_sma20,
            "sma50": current_sma50,
            "rsi": current_rsi,
            "crossover_detected": technical_data["crossover_detected"]
        }
        return trade_plan
    except Exception:
        return {"decision": "HOLD", "reason": "Invalid LLM response"}

def get_rsi_zone(rsi):
    """Categorize RSI into zones"""
    if rsi < 30:
        return "oversold"
    elif rsi < 40:
        return "weak_oversold"
    elif rsi < 60:
        return "neutral"
    elif rsi < 70:
        return "weak_overbought"
    else:
        return "overbought"

def get_volume_trend(volumes):
    """Analyze volume trend"""
    if len(volumes) < 5:
        return "insufficient_data"
    
    recent_avg = sum(volumes[-3:]) / 3
    earlier_avg = sum(volumes[-6:-3]) / 3
    
    if recent_avg > earlier_avg * 1.2:
        return "increasing"
    elif recent_avg < earlier_avg * 0.8:
        return "decreasing"
    else:
        return "stable"

def create_prompt(technical_data, symbol, qty):
    """Create comprehensive prompt with technical data"""
    return f"""
    You are an expert day trader analyzing {symbol} using technical analysis.
    
    CURRENT MARKET DATA:
    - Symbol: {technical_data['symbol']}
    - Current Price: ${technical_data['current_price']:.4f}
    - SMA(20): ${technical_data['sma_20']:.4f}
    - SMA(50): ${technical_data['sma_50']:.4f}
    - RSI(9): {technical_data['rsi_9']:.4f}
    - MACD: {technical_data['macd']:.2f}
    - MACD Signal: {technical_data['signal']:.2f}
    - Recent Closes: {technical_data['recent_closes']}
    - Recent volumes: {technical_data['recent_volumes']}
    - Price vs SMA(20): {technical_data['price_vs_sma20']:.4f}%
    - Price vs SMA(50): {technical_data['price_vs_sma50']:.4f}%
    - RSI Zone: {technical_data['rsi_zone']}
    - Volume Trend: {technical_data['volume_trend']}
    - SMA Crossover Detected: {technical_data['crossover_detected']}
    - Trend Reversal: {technical_data['trend_reversal']}
    
    RECENT PRICE ACTION (Last 10 bars):
    - Closes: {technical_data['recent_closes']}
    - Volumes: {technical_data['recent_volumes']}
    
    RULES:
    - Long only, 1% Stop Loss, 2+% Take Profit
    - Risk/reward > 1.5
    
    ANALYSIS REQUIRED:
    1. Assess the current trend (bullish/bearish/neutral)
    2. Evaluate momentum
    3. Check for entry signals
    4. Consider volume confirmation
    5. Assess risk/reward ratio
    
    DECISION FORMAT:
    DECISION FORMAT:
- If no trade: respond with exactly HOLD (no extra text).
- If trade: respond with JSON only. Do not include code fences, or markdown. Return ONLY the JSON object in the following format:
    {{
        "side": "buy",
        "qty": {qty},
        "order_type": "market",
        "stop_loss": 435.5,
        "take_profit": 450.0,
        "reasoning": "Detailed explanation of your analysis",
        "confidence": 0.85,
        "risk_reward": 2.0
    }}
    """