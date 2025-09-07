# strategies.py
from openai import OpenAI
import json
import os

# Create client once
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_strategy(prices: list[float], symbol: str, qty: int):
    """
    Send recent prices to an OpenAI model and get a trade decision.
    """
    prompt = f"""
    Act as an experienced day trader. 
    Your objective is to analyze the price and volume patterns of {symbol}
    to identify potential buying or selling opportunities. Utilize advanced charting tools 
    and technical indicators to scrutinize both short-term and long-term patterns, 
    taking into account historical data and recent market movements. 
    Assess the correlation between price and volume to gauge the strength 
    or weakness of a particular price trend. Based on your comprehensive analysis 
    of current market conditions, historical data, and emerging trends, 
    decide on optimal entry, stop-loss, and target points for a specified trading asset. 
    Thoroughly review recent price action, key technical indicators, 
    and relevant news that might influence the asset's direction. Here are some recent prices
    for {symbol} to help your analysis: {prices}

    If no trade, respond with: HOLD.

    If a trade, respond with JSON containing:
    - "side": "buy" or "sell"
    - "qty": number of shares (integer, default 1 if unsure)
    - "order_type": order type (market or limit)
    - "stop_loss": stop loss price (float)
    - "take_profit": take profit price (float)

    Example response:
    {{
      "side": "buy",
      "qty": 1,
      "order_type": "market",
      "stop_loss": 435.5,
      "take_profit": 450.0
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # use a free/cheap model to start
        messages=[{"role": "user", "content": prompt}]
    )

    decision = response.choices[0].message.content.strip().upper()
    if decision.upper() == "HOLD":
        return {"decision": "HOLD"}

    try:
        trade_plan = json.loads(decision)
        return trade_plan
    except Exception:
        return {"decision": "HOLD"} 
