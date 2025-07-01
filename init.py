# init.py

import random
import requests # type: ignore
from typing import Optional, Dict, Any, List, Union
from func import get_data, random_params, return_data, normalize_proxies
# from constants import constants as const
# Examples:
# const.OPEN_LONG
# const.ISOLATED
# const.PRICE_LIMITED_ORDER

class MEXCClient:
    def __init__(self, auth: str, mtoken: str, mhash: str, testnet: bool = False, proxy: Union[List[Union[str, dict]], str, None] = None):
        self.auth = auth
        self.mtoken = mtoken
        self.mhash = mhash
        
        # Initialize proxy list
        if proxy:
            self.proxy_list = proxy if isinstance(proxy, list) else [proxy]
        else:
            self.proxy_list = []  # Empty list if no proxies are provided
        
        self.language = random_params('languages', self)
        self.base_url = "https://futures.mexc.com" if testnet else 'https://futures.mexc.com'
        
        self.info = {
            "mtoken": self.mtoken,
            "mhash": self.mhash,
            **random_params('systems', self),
            **random_params('browsers', self),
            "language": self.language["language"],
            "kernel_name": "Blink",
            "kernel_ver": "",
            "display_resolution": "36",
            "color_depth": "24",
            "total_memory": "8",
            "pixel_ratio": 1.25,
            "time_zone": random_params('time_zones', self),
            "session_enable": "true",
            "storage_enable": "true",
            "indexeddb_enable": "true",
            "websql_enable": "false",
            "fonts": random_params('fonts', self),
            "audio_hash": "",
            "webgl_hash": "",
            "member_id": "",
            "env_info": "",
            "hostname": self.base_url,
            "sdk_v": "0.0.10",
            "product_type": 0,
            "platform_type": 3
        }

    
    async def make_request(self, endpoint: str, data: Optional[dict], method: str) -> Dict[str, Any]:
     """
     Generate and send a signed HTTP request to the MEXC API.
     """
     data, sign, ts = get_data(self.info, data, self.auth)
    
     # If no proxy list is provided, just skip the proxy logic
     proxies = None
     if self.proxy_list:
         proxy = random.choice(self.proxy_list)  # Pick a random proxy from the list
         proxy_url = f"{proxy['protocol']}://{proxy['host']}:{proxy['port']}"
         if 'username' in proxy and 'password' in proxy:
             proxy_url = f"{proxy['protocol']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
         proxies = {"http": proxy_url, "https": proxy_url}
     
     headers = {
         'User-Agent': random_params('user_agents', self),
         'Accept': '*/*',
         'Accept-Language': f'{self.language["language"]},{self.language["language"].split("-")[0]};q=0.5',
         'Accept-Encoding': 'gzip, deflate, br',
         'Content-Type': 'application/json',
         'Language': self.language["full_language"],
         'x-mxc-sign': sign,
         'x-mxc-nonce': ts,
         'Authorization': self.auth,
         'Pragma': 'akamai-x-cache-on',
         'Origin': self.base_url,
         'Connection': 'keep-alive',
         'Sec-Fetch-Dest': 'empty',
         'Sec-Fetch-Mode': 'cors',
         'Sec-Fetch-Site': 'same-origin',
         'TE': 'trailers',
     }
     
     headers = {k: str(v) for k, v in headers.items()}
     headers = {k: v.encode('ascii', 'ignore').decode('ascii') for k, v in headers.items()}
     
     try:
         if method.upper() == 'GET':
             response = requests.request(
                 method=method.upper(),
                 url=self.base_url + "/" + endpoint,
                 headers=headers,
                 params=data,
                 proxies=proxies
             )
         else:
             response = requests.request(
                 method=method.upper(),
                 url=self.base_url + "/" + endpoint,
                 headers=headers,
                 json=data,
                  proxies=proxies
            )
 
         response.raise_for_status()
         return response.json()
     except requests.exceptions.RequestException as e:
          if e.response:
             raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
          raise Exception(f"Network Error: {str(e)}")

      # Method to get the server time
   
    async def get_server_ping(self) -> Dict:
        """
        Fetch the list of open positions.
        - return the open positions data from the API.
        """
        endpoint = f'api/v1/contract/ping'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the contract information
    async def get_contract_info(self, symbol: str = None) -> Dict:
        """
        Fetch the contract information for a specific symbol.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the contract information data from the API.
        """
        endpoint = f'api/v1/contract/detail'
        data = return_data({ 'symbol': symbol })
        data['symbol'] = symbol
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the transferable currencies
    async def get_transferable_currencies(self) -> Dict:
        """
        Fetch the list of transferable currencies.
        - return the transferable currencies data from the API.
        """
        endpoint = f'api/v1/contract/support_currencies'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the contract‘s depth information
    async def get_contract_depth(self, symbol: str, limit: int = None) -> Dict:
        """
        Fetch the contract's depth information.
        - symbol: The trading pair (e.g., BTC_USDT).
        - limit: The number of depth levels to return (default: 100).
        - return the contract's depth information data from the API.
        """
        endpoint = f'api/v1/contract/depth/{symbol}'
        data = return_data({ 'limit': limit })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get a snapshot of the latest N depth information of the contract
    async def get_contract_snapshot(self, symbol: str, limit: int) -> Dict:
        """
        Fetch a snapshot of the latest N depth information of the contract.
        - symbol: The trading pair (e.g., BTC_USDT).
        - limit: The number of depth levels to return (default: 100).
        - return the snapshot of the latest N depth information of the contract data from the API.
        """
        endpoint = f'api/v1/contract/depth_commits/{symbol}/{limit}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract index price
    async def get_contract_index_price(self, symbol: str) -> Dict:
        """
        Fetch contract index price.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the contract index price data from the API.
        """
        endpoint = f'api/v1/contract/index_price/{symbol}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract fair price
    async def get_contract_fair_price(self, symbol: str) -> Dict:
        """
        Fetch contract fair price.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the contract fair price data from the API.
        """
        endpoint = f'api/v1/contract/fair_price/{symbol}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract funding rate
    async def get_contract_funding_rate(self, symbol: str) -> Dict:
        """
        Fetch contract funding rate.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the contract funding rate data from the API.
        """
        endpoint = f'api/v1/contract/funding_rate/{symbol}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get K-line data
    async def get_kline_data(self, symbol: str, interval: str = None, start: str = None, end: str = None) -> Dict:
        """
        Fetch K-line data.
        - symbol: The trading pair (e.g., BTC_USDT).
        - interval: The time interval of the K-line data (e.g., '1m', '5m', '15m', '30m', '1h', '4h', '1d').
        - start: The start time of the K-line data (start timestamp,seconds).
        - end: The end time of the K-line data (end timestamp,seconds).
        - return the K-line data from the API.
        """
        endpoint = f'api/v1/contract/kline/{symbol}'
        data = return_data({ 'interval': interval, 'start': start, 'end': end })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get K-line data of the index price
    async def get_index_kline_data(self, symbol: str, interval: str = None, start: str = None, end: str = None) -> Dict:
        """
        Fetch K-line data of the index price.
        - symbol: The trading pair (e.g., BTC_USDT).
        - interval: The time interval of the K-line data (e.g., '1m', '5m', '15m', '30m', '1h', '4h', '1d').
        - start: The start time of the K-line data (start timestamp,seconds).
        - end: The end time of the K-line data (end timestamp,seconds).
        - return the K-line data of the index price from the API.
        """
        endpoint = f'api/v1/contract/kline/index_price/{symbol}'
        data = return_data({ 'interval': interval, 'start': start, 'end': end })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get K-line data of the fair price
    async def get_fair_kline_data(self, symbol: str, interval: str = None, start: str = None, end: str = None) -> Dict:
        """
        Fetch K-line data of the fair price.
        - symbol: The trading pair (e.g., BTC_USDT).
        - interval: The time interval of the K-line data (e.g., '1m', '5m', '15m', '30m', '1h', '4h', '1d').
        - start: The start time of the K-line data (start timestamp,seconds).
        - end: The end time of the K-line data (end timestamp,seconds).
        - return the K-line data of the fair price from the API.
        """
        endpoint = f'api/v1/contract/kline/fair_price/{symbol}'
        data = return_data({ 'interval': interval, 'start': start, 'end': end })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract transaction data
    async def get_contract_transaction_data(self, symbol: str, limit: int = None) -> Dict:
        """
        Fetch contract transaction data.
        - symbol: The trading pair (e.g., BTC_USDT).
        - limit: The number of transactions to return (maximum is 100, default 100 without setting).
        - return the contract transaction data from the API.
        """
        endpoint = f'api/v1/contract/deals/{symbol}'
        data = return_data({ 'limit': limit })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract trend data
    async def get_contract_trend_data(self, symbol: str = None) -> Dict:
        """
        Fetch contract trend data.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the contract trend data from the API.
        """
        endpoint = f'api/v1/contract/ticker'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get all contract risk fund balance
    async def get_contract_risk_fund_balance(self) -> Dict:
        """
        Fetch all contract risk fund balance.
        - return the all contract risk fund balance from the API.
        """
        endpoint = f'api/v1/contract/risk_reverse'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract risk fund balance history
    async def get_contract_risk_fund_balance_history(self, symbol: str, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch contract risk fund balance history.
        - symbol: The trading pair (e.g., BTC_USDT).
        - page_num: The page number (default 1).
        - page_size: The page size (default 20).
        - return the contract risk fund balance history from the API.
        """
        endpoint = f'api/v1/contract/risk_reverse/history'
        data = return_data({ 'symbol': symbol, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get contract funding rate history
    async def get_contract_funding_rate_history(self, symbol: str, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch contract funding rate history.
        - symbol: The trading pair (e.g., BTC_USDT).
        - page_num: The page number (default 1).
        - page_size: The page size (default 20).
        - return the contract funding rate history from the API.
        """
        endpoint = f'api/v1/contract/funding_rate/history'
        data = return_data({ 'symbol': symbol, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get all informations of user's asset
    async def get_user_info(self) -> Dict:
        """
        Fetch all informations of user's asset.
        - return the all informations of user's asset from the API.
        """
        endpoint = f'api/v1/private/account/assets'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')

    # Method to get the user's single currency asset information
    async def get_single_currency_info(self, currency: str) -> Dict:
        """
        Fetch the user's single currency asset information.
        - currency: The currency (e.g., BTC).
        - return the user's single currency asset information from the API.
        """
        endpoint = f'api/v1/private/account/assets/{currency}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the user's asset transfer records
    async def get_asset_transfer_records(self, currency: str = None, state: str = None, get_type: str = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch the user's asset transfer records.
        - currency: The currency (e.g., BTC).
        - state: The state of the transfer (e.g., success).
        - type: The type of the transfer (e.g., deposit).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return the user's asset transfer records from the API.
        """
        endpoint = f'api/v1/private/account/transfer_record'
        data = return_data({ 'currency': currency, 'state': state, 'type': get_type, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')

    # Method to get the user’s history position information
    async def get_history_info(self, symbol: str = None, get_type: str = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch the user’s history position information.
        - symbol: The trading pair (e.g., BTC_USDT).
        - get_type: The type of the position (e.g., 1 for long, 2 for short).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return the user’s history position information from the API.
        """
        endpoint = f'api/v1/private/position/history_positions'
        data = return_data({ 'symbol': symbol, 'type': get_type, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the user's current holding position
    async def get_position_info(self, symbol: str = None) -> Dict:
        """
        Fetch the user’s history position information.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the user’s history position information from the API.
        """
        endpoint = f'api/v1/private/position/open_positions'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'GET')

    # Method to get details of user‘s funding rate
    async def get_funding_rate(self, symbol: str = None, position_id: int = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch details of user‘s funding rate.
        - symbol: The trading pair (e.g., BTC_USDT).
        - position_id: The position ID.
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return details of user‘s funding rate from the API.
        """
        endpoint = f'api/v1/private/position/funding_records'
        data = return_data({ 'symbol': symbol, 'position_id': position_id, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')

    # Method to get the user's current pending order
    async def get_current_pending_order(self, symbol: str = "", page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch the user's current pending order.
        - symbol: The trading pair (e.g., BTC_USDT).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return the user's current pending order from the API.
        """
        endpoint = f'api/v1/private/order/list/open_orders/{symbol}'
        data = return_data({ 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get all of the user's historical orders
    async def get_all_orders(self, symbol: str = None, states: str = None, category: str = None, start_time: int = None, end_time: int = None, side: int = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Fetch all of the user's historical orders.
        - symbol: The trading pair (e.g., BTC_USDT).
        - states: The order state The order state (1 uninformed, 2uncompleted, 3completed, 4cancelled, 5invalid; multiple separate by ',').
        - category: The order category  The order category (1limit order, 2 system take-over delegate, 3 close delegate 4 ADL reduction).
        - start_time: The start time of the order (e.g., 1609459200000).
        - end_time: The end time of the order (e.g., 1609459200000).
        - side: The order side (The order direction 1long,2close short,3open short 4 close long).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return all of the user's historical orders from the API.
        """
        endpoint = f'api/v1/private/order/list/history_orders'
        data = return_data({ 'symbol': symbol, 'states': states, 'category': category, 'start_time': start_time, 'end_time': end_time, 'side': side, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to query the order based on the external number
    async def query_order_by_external_id(self, symbol: str, external_id: str) -> Dict:
        """
        Query the order based on the external number.
        - symbol: The trading pair (e.g., BTC_USDT).
        - external_id: The external number.
        - return the order based on the external number from the API.
        """
        endpoint = f'api/v1/private/order/external/{symbol}/{external_id}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to query the order based on the order number
    async def query_order_by_order_id(self, order_id: int) -> Dict:
        """
        Query the order based on the order number.
        - order_id: The order number.
        - return the order based on the order number from the API.
        """
        endpoint = f'api/v1/private/order/get/{order_id}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to query the order in bulk based on the order number
    async def query_order_by_ids(self, order_ids: List[int]) -> Dict:
        """
        Query the order in bulk based on the order number.
        - order_ids: The order number.
        - return the order in bulk based on the order number from the API.
        """
        endpoint = f'api/v1/private/order/batch_query'
        data = return_data({ 'order_ids': ",".join(order_ids) })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get order transaction details based on the order ID
    async def get_order_transaction_details(self, order_id: int) -> Dict:
        """
        Get order transaction details based on the order ID.
        - order_id: The order ID.
        - return the order transaction details based on the order ID from the API.
        """
        endpoint = f'api/v1/private/order/deal_details/{order_id}'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get all transaction details of the user’s order
    async def get_all_order_transaction_details(self, symbol: str, start_time: int = None, end_time: int = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Get all transaction details of the user’s order.
        - symbol: The trading pair (e.g., BTC_USDT).
        - start_time: The start time of the order (e.g., 1609459200000).
        - end_time: The end time of the order (e.g., 1609459200000).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return all transaction details of the user’s order from
        """
        endpoint = f'api/v1/private/order/list/order_deals'
        data = return_data({ 'symbol': symbol, 'start_time': start_time, 'end_time': end_time, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the trigger order list
    async def get_trigger_order_list(self, symbol: str, states: str = None, start_time: int = None, end_time: int = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Get the trigger order list.
        - symbol: The trading pair (e.g., BTC_USDT).
        - states: The states of the order (1 uninformed, 2uncompleted,3completed,4cancelled, 5invalid; Multiple separate by ',').
        - start_time: The start time of the order (e.g., 1609459200000).
        - end_time: The end time of the order (e.g., 1609459200000).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return the trigger order list from the API.
        """
        endpoint = f'api/v1/private/planorder/list/orders'
        data = return_data({ 'symbol': symbol, 'start_time': start_time, 'end_time': end_time, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the Stop-Limit order list
    async def get_stop_limit_order_list(self, symbol: str, is_finished: str = None, start_time: int = None, end_time: int = None, page_num: int = 1, page_size: int = 20) -> Dict:
        """
        Get the Stop-Limit order list.
        - symbol: The trading pair (e.g., BTC_USDT).
        - is_finished: The status of the order (0: uncompleted, 1: completed).
        - start_time: The start time of the order (e.g., 1609459200000).
        - end_time: The end time of the order (e.g., 1609459200000).
        - page_num: The page number (default 1).
        - page_size: The page size (default is 20, maximum is 100).
        - return the Stop-Limit order list from the API.
        """
        endpoint = f'api/v1/private/stoporder/list/orders'
        data = return_data({ 'symbol': symbol, 'start_time': start_time, 'end_time': end_time, 'page_num': page_num, 'page_size': page_size })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get risk limits
    async def get_risk_limits(self, symbol: str = None) -> Dict:
        """
        Get risk limits.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return risk limits from the API.
        """
        endpoint = f'api/v1/private/account/risk_limit'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to get the user's current trading fee rate
    async def get_trading_fee_rate(self, symbol: str = None) -> Dict:
        """
        Get the user's current trading fee rate.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the user's current trading fee rate from the API.
        """
        endpoint = f'api/v1/private/account/tiered_fee_rate'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to Increase or decrease margin
    async def increase_or_decrease_margin(self, positionId: str, amount: int, order_type: str) -> Dict:
        """
        Increase or decrease margin.
        - positionId: The position ID.
        - amount: The amount of margin to increase or decrease.
        - type: The type of margin to increase or decrease (1: increase, 2: decrease).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/position/change_margin'
        data = return_data({ 'positionId': positionId, 'amount': amount, 'type': order_type })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to get leverage
    async def get_leverage(self, symbol: str = None) -> Dict:
        """
        Get the leverage for a specific symbol.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return leverage from the API.
        """
        endpoint = f'api/v1/private/position/leverage'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to switch leverage
    async def switch_leverage(self, positionId: int, leverage: int, open_type: int = None, symbol: str = None, positionType: int = None) -> Dict:
        """
        Switch leverage.
        - positionId: The position ID.
        - leverage: The leverage to switch to.
        - open_type: The type of order to open (1: isolated position, 2: full position).
        - symbol: The trading pair (e.g., BTC_USDT).
        - positionType: The type of position (required when there is no position, positionType: 1 Long 2:short).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/position/change_leverage'
        data = return_data({ 'positionId': positionId, 'leverage': leverage, 'open_type': open_type, 'symbol': symbol, 'positionType': positionType })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to get position mode
    async def get_position_mode(self) -> Dict:
        """
        Get the position mode.
        - return position mode from the API.
        """
        endpoint = f'api/v1/private/position/position_mode'
        data = return_data()
        return await self.make_request(endpoint, data, 'GET')
    
    # Method to change position mode
    async def change_position_mode(self, position_mode: str) -> Dict:
        """
        Change position mode.
        - position_mode: The position mode to change to (1: isolated position, 2: full position).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/position/change_position_mode'
        data = return_data({ 'position_mode': position_mode })
        return await self.make_request(endpoint, data, 'POST')
    
    # Methot to create order (Under maintenance)
    async def create_order(
        self,
        symbol: str,
        price: float,
        vol: int,
        side: int,
        order_type: int,
        open_type: int,
        leverage: int = None,
        position_id: int = None,
        external_oid: str = None,
        stop_loss_price: int = None,
        take_profit_price: int = None,
        position_mode: int = None,
        reduce_only: bool = None,
    ) -> Dict:
        """
        Create a new order on the platform.
        - symbol: The trading pair (e.g., BTC_USDT).
        - price: The price of the order.
        - vol: The volume of the order.
        - leverage: The leverage to use for the order.
        - side: The side of the order (1: buy, 2: sell).
        - type: The type of order (1: limit, 2: market).
        - openType: The type of order (1: isolated position, 2: full position).
        - position_id: The position ID.
        - external_oid: The external order ID.
        - stop_loss_price: The stop loss price.
        - take_profit_price: The take profit price.
        - position_mode: The position mode (1: isolated position, 2: full position).
        - reduce_only: Whether to reduce only.
        - return the result from the API.
        """
        # endpoint = f'api/v1/order/submit'
        endpoint = f'api/v1/private/order/submit'

        # endpoint = f'api/v1/private/order/create'
        data = return_data({ 'symbol': symbol, 'price': price, 'vol': vol, 'leverage': leverage, 'side': side, 'type': order_type, 'openType': open_type, 'positionId': position_id, 'externalOid': external_oid, 'stopLossPrice': stop_loss_price, 'takeProfitPrice': take_profit_price, 'positionMode': position_mode, 'reduceOnly': False, 'postOnly': False })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to create bulk order (Under maintenance)
    async def bulk_order(
        self,
        symbol: str,
        price: float,
        vol: int,
        side: int,
        order_type: int,
        open_type: int,
        leverage: int = None,
        position_id: int = None,
        external_oid: str = None,
        stop_loss_price: int = None,
        take_profit_price: int = None,
    ) -> Dict:
        """
        Create a new order on the platform.
        - symbol: The trading pair (e.g., BTC_USDT).
        - price: The price of the order.
        - vol: The volume of the order.
        - leverage: The leverage to use for the order.
        - side: The side of the order (1: buy, 2: sell).
        - type: The type of order (1: limit, 2: market).
        - openType: The type of order (1: isolated position, 2: full position).
        - position_id: The position ID.
        - external_oid: The external order ID.
        - stop_loss_price: The stop loss price.
        - take_profit_price: The take profit price.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/order/submit_batch'
        data = return_data({ 'symbol': symbol, 'price': price, 'vol': vol, 'leverage': leverage, 'side': side, 'type': order_type, 'openType': open_type, 'positionId': position_id, 'externalOid': external_oid, 'stopLossPrice': stop_loss_price, 'takeProfitPrice': take_profit_price })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel the order (Under maintenance)
    async def cancel_order(self, orderIds: List[int]) -> Dict:
        """
        Cancel the order on the platform.
        - orderIds: The order IDs to cancel (maximum is 50).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/order/cancel'
        data = return_data({ 'none': orderIds })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel the order according to the external order ID (Under maintenance)
    async def cancel_external_order(self, symbol: str, external_oid: str) -> Dict:
        """
        Cancel the order on the platform.
        - symbol: The trading pair (e.g., BTC_USDT).
        - external_oid: The external order ID.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/order/cancel_by_external_oid'
        data = return_data({ 'symbol': symbol, 'externalOid': external_oid })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel all orders under a contract (Under maintenance)
    async def cancel_all_orders(self, symbol: str = None) -> Dict:
        """
        Cancel all orders under a contract on the platform.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/order/cancel_all'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to switch the risk level
    async def switch_risk_level(self) -> Dict:
        """
        Switch the risk level on the platform.
        ## !!! Disabled The call returns the error code 8817
        ## !!! Prompt information: The risk restriction function has been upgraded. 
        ## !!! For details, please go to the web to view
        - return the result from the API.
        """
        endpoint = f'api/v1/private/account/change_risk_level'
        data = return_data()
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to trigger order (Under maintenance)
    async def trigger_order(
        self, 
        symbol: str, 
        vol: int, 
        side: int,  
        open_type: int, 
        trigger_price: int, 
        trigger_type: int, 
        execute_cycle: int, 
        order_type: int,
        trend: int,
        price: float = None, 
        leverage: int = None 
    ) -> Dict:
        """
        Trigger an order on the platform.
        - symbol: The trading pair (e.g., BTC_USDT).
        - vol: The volume of the order.
        - side: The side of the order (1: buy, 2: sell).
        - open_type: The type of order (1: isolated position, 2: full position).
        - triggerPrice: The trigger price.
        - triggerType: The trigger type (1: trigger by price, 2: trigger by time).
        - executeCycle: The execution cycle (1: execute immediately, 2: execute after the trigger).
        - order_type: The type of order (1: limit, 2: market).
        - trend: The trend of the order (1: up, 2: down).
        - price: The price of the order.
        - leverage: The leverage of the order.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/planorder/place'
        data = ({ 'symbol': symbol, 'price': price, 'leverage': leverage, 'vol': vol, 'side': side, 'openType': open_type, 'triggerPrice': trigger_price, 'triggerType': trigger_type, 'executeCycle': execute_cycle, 'orderType': order_type, 'trend': trend })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel the trigger order (Under maintenance)
    async def cancel_trigger_order(self, order_ids: List[int]) -> Dict:
        """
        Cancel the trigger order on the platform.
        - order_ids: The order IDs.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/planorder/cancel'
        data = return_data({ 'none': order_ids })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel all trigger orders (Under maintenance)
    async def cancel_all_trigger_orders(self, symbol: str = None) -> Dict:
        """
        Cancel all trigger orders on the platform.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/planorder/cancel_all'
        data = return_data({ 'symbol': symbol })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel the Stop-Limit trigger order (Under maintenance)
    async def cancel_stop_limit_trigger_order(self, order_ids: List[int]) -> Dict:
        """
        Cancel the Stop-Limit trigger order on the platform.
        - order_ids: The order IDs.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/stoporder/cancel'
        data = return_data({ 'none': order_ids })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to cancel all Stop-Limit price trigger orders (Under maintenance)
    async def cancel_all_stop_limit_trigger_orders(self, position_id: int = None, symbol: str = None) -> Dict:
        """
        Cancel all Stop-Limit price trigger orders on the platform.
        - position_id: The position ID.
        - symbol: The trading pair (e.g., BTC_USDT).
        - return the result from the API.
        """
        endpoint = f'api/v1/private/stoporder/cancel_all'
        data = return_data({ 'positionId': position_id, 'symbol': symbol })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to switch Stop-Limit limited order price
    async def switch_stop_limit_price(self, order_id: int, stop_loss_price: int = None, take_profit_price: int = None) -> Dict:
        """
        Switch Stop-Limit limited order price on the platform.
        - order_id: The order ID.
        - stop_loss_price: The stop loss price.
        - take_profit_price: The take profit price.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/stoporder/change_price'
        data = return_data({ 'orderId': order_id, 'stopLossPrice': stop_loss_price, 'takeProfitPrice': take_profit_price })
        return await self.make_request(endpoint, data, 'POST')
    
    # Method to switch the Stop-Limit price of trigger orders
    async def switch_stop_limit_trigger_order(self, stop_plan_order_id: int, stop_loss_price: int = None, take_profit_price: int = None) -> Dict:
        """
        Switch the Stop-Limit price of trigger orders on the platform.
        - stop_plan_order_id: The stop plan order ID.
        - stop_loss_price: The stop loss price.
        - take_profit_price: The take profit price.
        - return the result from the API.
        """
        endpoint = f'api/v1/private/stoporder/change_plan_price'
        data = return_data({ 'stopPlanOrderId': stop_plan_order_id, 'stopLossPrice': stop_loss_price, 'takeProfitPrice': take_profit_price })
        return await self.make_request(endpoint, data, 'POST')
