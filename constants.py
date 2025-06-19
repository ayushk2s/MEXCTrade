# constants.py

BASE_URL = 'https://futures.mexc.com'
BASE_URL_TESTNET = 'https://futures.mexc.com'

# Constants representing trade actions
# Examples:
# OPEN_LONG: Used to open a long position
# OPEN_SHORT: Used to open a short position
# CLOSE_LONG: Used to close an existing long position
# CLOSE_SHORT: Used to close an existing short position
OPEN_LONG = 1  # Example: A user wants to open a long position for BTC/USDT
OPEN_SHORT = 3  # Example: A user wants to open a short position for ETH/USDT
CLOSE_LONG = 4  # Example: Closing a long position for ADA/USDT
CLOSE_SHORT = 2  # Example: Closing a short position for XRP/USDT

# Margin types
# ISOLATED: Isolated margin mode
# CROSS: Cross margin mode
# Examples:
# ISOLATED: Used when the user wants to limit the risk to only the initial margin of the position
# CROSS: Used when the user wants to share the margin across all positions
ISOLATED = 1  # Example: Opening a BTC/USDT trade with isolated margin
CROSS = 2  # Example: Opening an ETH/USDT trade with cross margin

# Order types
# Examples of order types:
# PRICE_LIMITED_ORDER: A limit order with a specific price
# POST_ONLY_MAKER: Ensures the order enters the order book as a maker order
# TRANSACT_OR_CANCEL_INSTANTLY: Fill as much as possible immediately, cancel the rest
# TRANSACT_COMPLETELY_OR_CANCEL_COMPLETELY: Fill the full amount, or cancel entirely
# MARKET_ORDERS: Execute the order at the best available market price
PRICE_LIMITED_ORDER = "1"  # Example: Set a limit order to buy BTC/USDT at $62,800
POST_ONLY_MAKER = "2"  # Example: Place a maker order that doesn't remove liquidity
TRANSACT_OR_CANCEL_INSTANTLY = "3"  # Example: Place an order that fills partially immediately
TRANSACT_COMPLETELY_OR_CANCEL_COMPLETELY = "4"  # Example: Cancel order if not fully filled
MARKET_ORDERS = "5"  # Example: Place an order to buy BTC/USDT at the current market price
CONVERT_MARKET_PRICE_TO_CURRENT_PRICE = "6"  # Example: Adjust order price to the current market price