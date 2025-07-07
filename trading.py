import time
from init import MEXCClient

def get_trade_side(action):
    """
    Determines the correct trade side for MEXC Futures API.
    Mapping:
    - 1 → Buy (Open Long)
    - 2 → Sell (Open Short)
    - 3 → Close Short (BroughtSell)
    - 4 → Close Long (SoldBrought)
    """
    action = action.lower()
    if action == "buy":
        return 1  # Open Long
    elif action == "sell":
        return 3  # Open Short
    elif action == "broughtsell":
        return 4  # Close Short
    elif action == "soldbuy":
        return 2  # Close Long
    return None

async def place_order(uid, mtoken, htoken, action, symbol, vol, leverage, price, take_profit=None, stop_loss=None, testnet=True):
    """
    Places a futures order using MEXCClient.
    """
    start_time = time.time()
    
    print(f"Placing {action.upper()} order on {symbol} with volume {vol}, leverage {leverage}, price {price}")
    
    # Initialize client
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    print("Client initialized")

    # Get trade side
    side = get_trade_side(action)
    if side is None:
        raise ValueError("Invalid action. Use 'buy', 'sell', 'broughtsell', or 'soldbuy'.")

    # Create the order
    order = await client.create_order(
        symbol=symbol.upper(),
        side=side,
        order_type=2,  # Market order
        vol=vol,
        leverage=leverage,
        open_type=1,  # Isolated margin
        price=price,
        reduce_only=False,
        stop_loss_price=stop_loss,
        take_profit_price=take_profit,
        position_id=None,
        external_oid=None,
        position_mode=1  # Isolated margin mode
    )

    print("Order result:", order)
    print(f"Execution time: {time.time() - start_time:.2f} seconds")
    return order

async def cancel_all_orders(uid, mtoken, htoken, symbol=None, testnet=True):
    """
    Cancels all open orders on a given symbol (or all symbols if none given).
    """
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    print(f"Cancelling all orders for symbol: {symbol}")
    result = await client.cancel_all_orders(symbol=symbol)
    print("Cancel result:", result)
    return result
