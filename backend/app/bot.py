from alpaca.data import BarSet
from app.alpaca_client import market_order, bracket_order, get_15min_data
from app.strategy import llm_strategy

def run_bot(symbol="SPY", qty=1):
    # Get last 10 days of data
    df = get_15min_data(symbol)

    decision = llm_strategy(df, symbol, qty)

    if decision.get("decision") == "HOLD":
        print(f"No trade (HOLD): {decision.get("reason")}")
        return decision

    # Extract trade plan
    side = decision["side"]
    qty = decision.get("qty", qty)
    order_type = decision.get("order_type", "market")
    stop_loss = decision["stop_loss"]
    take_profit = decision["take_profit"]
    reasoning = decision.get("reasoning", "N/A")
    confidence = decision.get("confidence", 0.0)
    
    print(f"🚀 Placing {side.upper()} order for {qty} {symbol}")
    print(f"   Stop Loss: ${stop_loss:.2f}")
    print(f"   Take Profit: ${take_profit:.2f}")
    print(f"   Confidence: {confidence:.2f}")
    print(f"   Reasoning: {reasoning}")
    
    # order = bracket_order(
    #     symbol=symbol,
    #     qty=qty,
    #     side=side,
    #     stop_loss=stop_loss,
    #     take_profit=take_profit,
    #     order_type=order_type
    # )

    order = "test"

    return order
