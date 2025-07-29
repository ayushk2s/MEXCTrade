import time
import asyncio
import sys
import logging
from init import MEXCClient
from cache import cached_api_call

logger = logging.getLogger(__name__)

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

async def place_order(uid, mtoken, htoken, symbol, action, order_type, vol, leverage, price, take_profit=None, stop_loss=None, testnet=True):
    """
    Places a futures order using optimized MEXCClient with performance monitoring.
    """
    start_time = time.time()

    logger.info(f"Placing {action.upper()} order on {symbol} - Vol: {vol}, Leverage: {leverage}, Price: {price}")

    try:
        # Create optimized client
        client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
        logger.debug("MEXC client initialized")

        # Validate trade side
        side = get_trade_side(action)
        if side is None:
            raise ValueError(f"Invalid action '{action}'. Use 'buy', 'sell', 'broughtsell', or 'soldbuy'.")

        # Execute order with error handling and retries
        order = await client.create_order(
            symbol=symbol.upper(),
            side=side,
            order_type=order_type,   # 1=Limit, 5=Market, 6=Market-to-Limit, 2=Post Order
            vol=vol,
            leverage=leverage,
            open_type=1,  # Isolated margin
            price=price,
            reduce_only=False,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
            position_id=None,
            external_oid=None,
            position_mode=1
        )

        execution_time = time.time() - start_time
        logger.info(f"Order placed successfully in {execution_time:.3f}s - Order: {order}")

        return {
            **order,
            "execution_time": execution_time,
            "client_info": {
                "symbol": symbol.upper(),
                "action": action,
                "side": side,
                "volume": vol,
                "leverage": leverage,
                "price": price
            }
        }

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Order placement failed after {execution_time:.3f}s: {str(e)}")
        raise

async def cancel_all_order(uid, mtoken, htoken, testnet=True):
    """
    Cancels all active futures orders for the given user with optimized performance.
    """
    start_time = time.time()

    try:
        client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
        logger.info("Canceling all orders...")

        result = await client.cancel_all_orders()

        execution_time = time.time() - start_time
        logger.info(f"All orders canceled successfully in {execution_time:.3f}s - Result: {result}")

        return {
            **result,
            "execution_time": execution_time,
            "timestamp": time.time()
        }

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Cancel all orders failed after {execution_time:.3f}s: {str(e)}")
        raise

# ──────── Cached API Functions for Better Performance ────────

@cached_api_call(ttl=60, key_prefix="contract_info")
async def get_cached_contract_info(uid, mtoken, htoken, symbol, testnet=True):
    """Get contract information with caching"""
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    return await client.get_contract_info(symbol)

@cached_api_call(ttl=30, key_prefix="user_positions")
async def get_cached_user_positions(uid, mtoken, htoken, symbol=None, testnet=True):
    """Get user positions with caching"""
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    return await client.get_position_info(symbol)

@cached_api_call(ttl=10, key_prefix="market_data")
async def get_cached_market_data(uid, mtoken, htoken, symbol, testnet=True):
    """Get market data with short-term caching"""
    client = MEXCClient(uid, mtoken, htoken, testnet=testnet)
    return await client.get_contract_trend_data(symbol)

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
