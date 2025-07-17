import time
import asyncio
import sys
from init import MEXCClient

def get_trade_side(action):
    """
    Determines the correct trade side for MEXC Futures API.
    Mapping:
    - buy         → 1 (Open Long)
    - sell        → 3 (Open Short)
    - broughtsell → 4 (Close Short)
    - soldbuy     → 2 (Close Long)
    """
    action = action.lower()
    if action == "buy":
        return 1
    elif action == "sell":
        return 3
    elif action == "broughtsell":
        return 4
    elif action == "soldbuy":
        return 2
    return None

async def place_order(uid, mtoken, htoken, action, symbol, order_type, vol, leverage, price, take_profit=None, stop_loss=None, testnet=True):
    """
    Places a futures order using MEXCClient.
    """
    start_time = time.time()
    
    print(f"Placing {action.upper()} order on {symbol} with volume {vol}, leverage {leverage}, price {price}")
    
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    print("Client initialized")

    side = get_trade_side(action)
    if side is None:
        raise ValueError("Invalid action. Use 'buy', 'sell', 'broughtsell', or 'soldbuy'.")

    order = await client.create_order(
        symbol=symbol.upper(),
        side=side,
        order_type=order_type,   #'1' (Limit), '5' (Market), '6' (Market-to-Limit), '2' (Post Order)
        vol=vol,
        leverage=leverage,
        open_type=1,
        price=price,
        reduce_only=False,
        stop_loss_price=stop_loss,
        take_profit_price=take_profit,
        position_id=None,
        external_oid=None,
        position_mode=1
    )

    print("Order result:", order)
    print(f"Execution time: {time.time() - start_time:.2f} seconds")
    return order

async def cancel_all_order(uid, mtoken, htoken, testnet=True):
    """
    Cancels all active futures orders for the given user.
    """
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    print("Canceling all orders...")
    result = await client.cancel_all_orders()
    print("Cancel result:", result)
    return result

# ──────────────────────────────
# Allow running from file path
# ──────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1]  # 'place' or 'cancel'
    uid = sys.argv[2]
    mtoken = sys.argv[3]
    htoken = sys.argv[4]
    testnet = sys.argv[5].lower() == "true"

    if mode == "place":
        action = sys.argv[6]          # buy, sell, etc.
        symbol = sys.argv[7]
        vol = float(sys.argv[8])
        leverage = int(sys.argv[9])
        price = float(sys.argv[10])
        take_profit = float(sys.argv[11]) if len(sys.argv) > 11 and sys.argv[11] != "None" else None
        stop_loss = float(sys.argv[12]) if len(sys.argv) > 12 and sys.argv[12] != "None" else None

        asyncio.run(place_order(uid, mtoken, htoken, action, symbol, vol, leverage, price, take_profit, stop_loss, testnet))

    elif mode == "cancel":
        asyncio.run(cancel_all_order(uid, mtoken, htoken, testnet))
    else:
        print("Invalid mode. Use 'place' or 'cancel'.")
