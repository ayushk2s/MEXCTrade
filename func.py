# optimized_func.py

import json, random, string, hashlib, time, re
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA 
from Crypto.Random import get_random_bytes
from base64 import b64encode
from typing import Optional, Dict, Any, List, Union
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ──────── Global Thread Pool for CPU-bound operations ────────
crypto_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="crypto")

# ──────── Cached RSA Key ────────
@lru_cache(maxsize=1)
def get_rsa_public_key():
    """Cache the RSA public key to avoid repeated imports"""
    public_key_str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqqpMCeNv7qfsKe09xwE5o05ZCq/qJvTok6WbqYZOXA16UQqR+sHH0XXfnWxLSEvCviP9qjZjruHWdpMmC4i/yQJe7MJ66YoNloeNtmMgtqEIjOvSxRktmAxywul/eJolrhDnRPXYll4fA5+24t1g6L5fgo/p66yLtZRg4fC1s3rAF1WPe6dSJQx7jQ/xhy8Z0WojmzIeaoBa0m8qswx0DMIdzXfswH+gwMYCQGR3F/NAlxyvlWPMBlpFEuHZWkp9TXlTtbLf+YL8vYjV5HNqIdNjVzrIvg/Bis49ktfsWuQxT/RIyCsTEuHmZyZR6NJAMPZUE5DBnVWdLShb6KuyqwIDAQAB
-----END PUBLIC KEY-----"""
    return RSA.import_key(public_key_str)

# ──────── Optimized Async Functions ────────
async def get_data_async(fp_data: dict, info: dict, auth: str):
    """
    Async version of get_data with parallel crypto operations
    """
    ts = str(int(time.time() * 1000))
    
    # Generate chash (fast operation)
    chash = ''.join(random.choice(string.hexdigits.lower()) for _ in range(32))
    
    # Generate AES key
    key = get_random_bytes(32)
    
    # Run expensive crypto operations in parallel
    fp_data_json = json.dumps(fp_data)
    
    # Execute crypto operations in thread pool
    loop = asyncio.get_event_loop()
    p0_task = loop.run_in_executor(crypto_executor, encrypt_aes_gcm_256, fp_data_json, key.hex())
    k0_task = loop.run_in_executor(crypto_executor, get_k0_sync, key)
    
    # Wait for both operations to complete
    p0, k0 = await asyncio.gather(p0_task, k0_task)
    
    # Construct the data payload
    data = {
        **info,
        "p0": p0,
        "k0": k0,
        "chash": chash,
        "mtoken": fp_data['mtoken'],
        "ts": ts,
        "mhash": fp_data['mhash']
    }
    
    # Generate signature (also CPU-bound, so use executor)
    hash_task = loop.run_in_executor(crypto_executor, get_sign, auth, json.dumps(data), ts)
    hash_result = await hash_task
    
    return data, hash_result, ts

def get_k0_sync(aes_key: bytes) -> str:
    """Synchronous version for thread pool execution"""
    public_key = get_rsa_public_key()  # Uses cached key
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted = cipher_rsa.encrypt(aes_key)
    return b64encode(encrypted).decode('utf-8')

# ──────── Optimized Crypto Functions ────────
def encrypt_aes_gcm_256_optimized(plaintext: str, key_hex: str) -> str:
    """
    Optimized AES-GCM encryption with reduced allocations
    """
    key = bytes.fromhex(key_hex)
    iv = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, iv)
    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    
    # Single concatenation instead of multiple
    encrypted_message = iv + ciphertext + auth_tag
    return b64encode(encrypted_message).decode('utf-8')

# Keep original function for backward compatibility
encrypt_aes_gcm_256 = encrypt_aes_gcm_256_optimized

@lru_cache(maxsize=1000)
def get_md5_cached(string: str) -> str:
    """Cached MD5 for repeated strings"""
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def get_md5(string: str) -> str:
    """Use cached version for better performance"""
    return get_md5_cached(string)

def get_g_optimized(auth: str, ts: str) -> tuple:
    """Optimized version using cached MD5"""
    md5_hash = get_md5_cached(auth + ts)
    return md5_hash[7:], ts

def get_sign_optimized(auth: str, formdata: str, ts: str) -> str:
    """Optimized signature generation"""
    g, current_ts = get_g_optimized(auth, ts)
    return get_md5_cached(current_ts + formdata + g)

# Use optimized versions
get_g = get_g_optimized
get_sign = get_sign_optimized

# ──────── Optimized Random Parameter Functions ────────
class OptimizedRandomParams:
    """Class to cache expensive random selections"""
    
    def __init__(self):
        # Pre-generate commonly used data
        self.fonts = [
            "Agency FB", "Calibri", "Century", "Century Gothic", "Franklin Gothic",
            "Haettenschweiler", "Leelawadee", "Lucida Bright", "Lucida Sans", "MS Outlook",
            "MS Reference Specialty", "MS UI Gothic", "MT Extra", "Marlett", "Microsoft Uighur",
            "Monotype Corsiva", "Pristina", "Segoe UI Light"
        ]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        ]
        
        self.timezones = [f"Etc/GMT{'+' if offset > 0 else ''}{offset}" for offset in range(-12, 13)]
        
        self.systems = {
            "Windows": ["NT 10.0", "NT 6.1", "NT 6.3"],
            "Linux": ["Ubuntu 22.04", "Debian 11", "Fedora 36"],
            "macOS": ["13.0 Ventura", "12.0 Monterey", "11.0 Big Sur"]
        }
        
        self.languages = [
            "en-US", "en-GB", "ru-RU", "fr-FR", "de-DE", "es-ES", "it-IT", "pt-BR",
            "zh-CN", "ja-JP", "ko-KR", "ar-SA", "hi-IN", "tr-TR", "vi-VN", "th-TH"
        ]
        
        self.language_map = {
            "en-US": "English", "en-GB": "English", "ru-RU": "Русский", "fr-FR": "Français",
            "de-DE": "Deutsch", "es-ES": "Español", "it-IT": "Italiano", "pt-BR": "Português",
            "zh-CN": "简体中文", "ja-JP": "日本語", "ko-KR": "한국어", "ar-SA": "العربية",
            "hi-IN": "हिन्दी", "tr-TR": "Türkçe", "vi-VN": "Tiếng Việt", "th-TH": "ไทย"
        }
        
        self.browsers = {
            "Chrome": ["119.0.0.0", "118.0.0.1", "117.0.0.0"],
            "Firefox": ["118.0", "117.0", "116.0"],
            "Safari": ["17.0", "16.5", "16.0"],
            "Edge": ["115.0.1901.203", "114.0.1823.67", "113.0.1774.50"],
            "Opera": ["103.0", "102.0", "101.5"]
        }
    
    def get_random_param(self, param_type: str, proxy_list=None):
        """Optimized random parameter generation"""
        if param_type == 'fonts':
            return self.fonts[:random.randint(1, len(self.fonts))]
        
        elif param_type == 'user_agents':
            return random.choice(self.user_agents)
        
        elif param_type == 'time_zones':
            return random.choice(self.timezones)
        
        elif param_type == 'systems':
            sys = random.choice(list(self.systems.keys()))
            sys_ver = random.choice(self.systems[sys])
            
            device_map = {"Windows": "Win32", "Linux": "Linux", "macOS": "MacIntel"}
            e_device = device_map.get(sys)
            
            return {"sys": sys, "sys_ver": sys_ver, "e_devices": e_device}
        
        elif param_type == 'languages':
            chosen_language = random.choice(self.languages)
            full_language_name = self.language_map.get(chosen_language, "Unknown")
            return {"language": chosen_language, "full_language": full_language_name}
        
        elif param_type == 'browsers':
            browser_name = random.choice(list(self.browsers.keys()))
            browser_ver = random.choice(self.browsers[browser_name])
            return {"browser_name": browser_name, "browser_ver": browser_ver}
        
        elif param_type == 'proxies':
            return random.choice(proxy_list) if proxy_list else None
        
        return None

# Global instance for reuse
_random_params_instance = OptimizedRandomParams()

def random_params(param_type: str, self=None) -> dict:
    """Optimized random_params function using cached instance"""
    proxy_list = getattr(self, 'proxy_list', None) if self else None
    return _random_params_instance.get_random_param(param_type, proxy_list)

# ──────── Batch Processing Functions ────────
async def batch_encrypt(data_list: List[dict], keys: List[bytes]) -> List[str]:
    """Batch encrypt multiple data items concurrently"""
    loop = asyncio.get_event_loop()
    tasks = []
    
    for data, key in zip(data_list, keys):
        json_str = json.dumps(data)
        task = loop.run_in_executor(crypto_executor, encrypt_aes_gcm_256, json_str, key.hex())
        tasks.append(task)
    
    return await asyncio.gather(*tasks)

# ──────── Memory Pool for AES Keys ────────
class AESKeyPool:
    """Pool of pre-generated AES keys for better performance"""
    
    def __init__(self, pool_size: int = 100):
        self.pool_size = pool_size
        self.keys = []
        self._fill_pool()
    
    def _fill_pool(self):
        """Fill the pool with pre-generated keys"""
        while len(self.keys) < self.pool_size:
            self.keys.append(get_random_bytes(32))
    
    def get_key(self) -> bytes:
        """Get a key from the pool, refill if needed"""
        if not self.keys:
            self._fill_pool()
        
        key = self.keys.pop()
        
        # Async refill when pool gets low
        if len(self.keys) < self.pool_size // 4:
            asyncio.create_task(self._async_refill())
        
        return key
    
    async def _async_refill(self):
        """Asynchronously refill the pool"""
        loop = asyncio.get_event_loop()
        new_keys = await loop.run_in_executor(
            crypto_executor, 
            lambda: [get_random_bytes(32) for _ in range(self.pool_size - len(self.keys))]
        )
        self.keys.extend(new_keys)

# Global key pool
aes_key_pool = AESKeyPool()

def get_pooled_aes_key() -> bytes:
    """Get an AES key from the pool for better performance"""
    return aes_key_pool.get_key()

# ──────── Backward Compatibility ────────
def get_data(fp_data: dict, info: dict, auth: str):
    """
    Synchronous version for backward compatibility
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_data_async(fp_data, info, auth))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(get_data_async(fp_data, info, auth))

def get_p0(plaintext_object_str: str, key: bytes) -> str:
    return encrypt_aes_gcm_256(plaintext_object_str, key.hex())

def get_k0(aes_key: bytes) -> str:
    return get_k0_sync(aes_key)

def return_data(variables: Optional[dict] = None) -> dict:
    if variables is None:
        variables = {}
    return {key: value for key, value in variables.items() if value is not None}

def normalize_proxies(proxy: Union[List[Union[str, dict]], str, None]) -> List[Dict[str, Any]]:
    if not proxy:
        return []
    if isinstance(proxy, str):
        proxy = [proxy]
    
    parsed_proxies = []
    for p in proxy:
        if isinstance(p, str):
            parsed = parse_proxy_string(p)
            if parsed:
                parsed_proxies.append(parsed)
        elif isinstance(p, dict):
            parsed_proxies.append(p)
    return parsed_proxies

def parse_proxy_string(proxy_string: str) -> Optional[Dict[str, Any]]:
    match = re.match(r'(https?|socks5)://([^:]+):([^@]+)@([^:]+):(\\d+)', proxy_string)
    return {'protocol': match.group(1), 'username': match.group(2), 'password': match.group(3), 'host': match.group(4), 'port': int(match.group(5))} if match else None