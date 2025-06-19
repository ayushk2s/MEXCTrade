# func.py

import json, random, string, hashlib, time, re
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA 
from Crypto.Random import get_random_bytes
from base64 import b64encode
from typing import Optional, Dict, Any, List, Union


def get_data(fp_data: dict, info: dict, auth: str):
    """
    Constructs a data payload with encrypted and signed components.

    Parameters:
    - fp_data (dict): Contains 'mtoken' and 'mhash' for data construction.
    - info (dict): Additional information to include in the payload.
    - auth (str): Authentication key for signing the payload.

    Returns:
    - tuple: The data payload (dict), its signature (str), and the timestamp (str).
    """
    ts = str(int(time.time() * 1000))  # Current timestamp in milliseconds.

    # Generate a random chash (hexadecimal hash-like string of length 32).
    chash = ''.join(random.choice(string.hexdigits.lower()) for _ in range(32))
    key = get_random_bytes(32)  # Generate a random 32-byte AES key.
    p0 = get_p0(json.dumps(fp_data), key)  # Encrypt fp_data with the AES key.
    k0 = get_k0(key)  # Encrypt the AES key using RSA public key.

    # Construct the data payload.
    data = {
        **info,
        "p0": p0,  # Encrypted fp_data.
        "k0": k0,  # RSA-encrypted AES key.
        "chash": chash,
        "mtoken": fp_data['mtoken'],  # Token from fp_data.
        "ts": ts,  # Timestamp.
        "mhash": fp_data['mhash']  # Hash from fp_data.
    }

    # Generate a signature for the data payload.
    hash = get_sign(auth, json.dumps(data), ts)

    return data, hash, ts


def encrypt_aes_gcm_256(plaintext: str, key_hex: str) -> str:
    """
    Encrypts plaintext using AES-GCM-256.

    Parameters:
    - plaintext (str): Text to encrypt.
    - key_hex (str): Hexadecimal AES key.

    Returns:
    - str: Base64-encoded encrypted message (IV + ciphertext + auth tag).
    """
    key = bytes.fromhex(key_hex)  # Convert the hex key to bytes.
    iv = get_random_bytes(12)  # Generate a random 12-byte IV.
    cipher = AES.new(key, AES.MODE_GCM, iv)  # Initialize AES cipher in GCM mode.
    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))  # Encrypt and get authentication tag.
    encrypted_message = iv + ciphertext + auth_tag  # Concatenate IV, ciphertext, and auth tag.
    encrypted_message_base64 = b64encode(encrypted_message).decode('utf-8')  # Encode to Base64.
    return encrypted_message_base64


def get_p0(plaintext_object_str: str, key: bytes) -> str:
    """
    Encrypts the plaintext object string using AES-GCM-256.

    Parameters:
    - plaintext_object_str (str): JSON string to encrypt.
    - key (bytes): AES key.

    Returns:
    - str: Base64-encoded encrypted string.
    """
    return encrypt_aes_gcm_256(plaintext_object_str, key.hex())


def get_k0(aes_key: bytes) -> str:
    """
    Encrypts the AES key using RSA public key.

    Parameters:
    - aes_key (bytes): AES key to encrypt.

    Returns:
    - str: Base64-encoded RSA-encrypted AES key.
    """
    public_key_str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqqpMCeNv7qfsKe09xwE5o05ZCq/qJvTok6WbqYZOXA16UQqR+sHH0XXfnWxLSEvCviP9qjZjruHWdpMmC4i/yQJe7MJ66YoNloeNtmMgtqEIjOvSxRktmAxywul/eJolrhDnRPXYll4fA5+24t1g6L5fgo/p66yLtZRg4fC1s3rAF1WPe6dSJQx7jQ/xhy8Z0WojmzIeaoBa0m8qswx0DMIdzXfswH+gwMYCQGR3F/NAlxyvlWPMBlpFEuHZWkp9TXlTtbLf+YL8vYjV5HNqIdNjVzrIvg/Bis49ktfsWuQxT/RIyCsTEuHmZyZR6NJAMPZUE5DBnVWdLShb6KuyqwIDAQAB
-----END PUBLIC KEY-----"""
    public_key = RSA.import_key(public_key_str)  # Import RSA public key.
    cipher_rsa = PKCS1_OAEP.new(public_key)  # Initialize RSA cipher with OAEP padding.
    encrypted = cipher_rsa.encrypt(aes_key)  # Encrypt the AES key.
    return b64encode(encrypted).decode('utf-8')  # Encode the encrypted key to Base64.


def get_md5(string: str) -> str:
    """
    Generates an MD5 hash of the input string.

    Parameters:
    - string (str): Input string.

    Returns:
    - str: MD5 hash in hexadecimal format.
    """
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def get_g(auth: str, ts: str) -> tuple:
    """
    Generates a derived hash (g) from the auth key and timestamp.

    Parameters:
    - auth (str): Authentication key.
    - ts (str): Timestamp.

    Returns:
    - tuple: Derived hash (g, str) and the current timestamp (str).
    """
    md5_hash = get_md5(auth + ts)  # MD5 hash of auth and timestamp concatenated.
    return md5_hash[7:], ts  # Return a portion of the hash (starting from the 7th character) and timestamp.


def get_sign(auth: str, formdata: str, ts: str) -> str:
    """
    Generates a signature for the given data.

    Parameters:
    - auth (str): Authentication key.
    - formdata (str): JSON string of the data payload.
    - ts (str): Timestamp.

    Returns:
    - str: MD5 signature.
    """
    g, current_ts = get_g(auth, ts)  # Derive g from auth and timestamp.
    return get_md5(current_ts + formdata + g)  # MD5 hash of timestamp, data, and g concatenated.


def random_params(param_type: str, self) -> dict:
    if param_type == 'fonts':
        # List of font families
        fonts = [
            "Agency FB", "Calibri", "Century", "Century Gothic", "Franklin Gothic",
            "Haettenschweiler", "Leelawadee", "Lucida Bright", "Lucida Sans", "MS Outlook",
            "MS Reference Specialty", "MS UI Gothic", "MT Extra", "Marlett", "Microsoft Uighur",
            "Monotype Corsiva", "Pristina", "Segoe UI Light"
        ]

        return fonts[:random.randint(1, len(fonts))]
    
    if param_type == 'user_agents':
        user_agents = [
            # Desktop browsers
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",

            # Mobile browsers
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",

            # Search engine crawlers
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "DuckDuckBot/1.1 (+http://duckduckgo.com/duckduckbot.html)",

            # Smart TV
            "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/1.0 Safari/537.36",

            # Game consoles
            "Mozilla/5.0 (PlayStation 5 3.0) AppleWebKit/537.36 (KHTML, like Gecko)",

            # Random legacy browsers
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
        ]

        return random.choice(user_agents)

    if param_type == 'time_zones':
        # List of time zones in Etc/GMT format
        timezones = [f"Etc/GMT{'+' if offset > 0 else ''}{offset}" for offset in range(-12, 13)]
        
        return random.choice(timezones)

    if param_type == 'systems':
        """
        Generating a random OS, corresponding version, and device type.
        """
        systems = {
            "Windows": ["NT 10.0", "NT 6.1", "NT 6.3"],
            "Linux": ["Ubuntu 22.04", "Debian 11", "Fedora 36"],
            "macOS": ["13.0 Ventura", "12.0 Monterey", "11.0 Big Sur"]
        }

        sys = random.choice(list(systems.keys()))
        sys_ver = random.choice(systems[sys])

        e_device = None # Ensure e_device is initialized
        if sys == "Windows":
            e_device = "Win32"
        elif sys == "Linux":
            e_device = "Linux"
        elif sys == "macOS":
            e_device = "MacIntel"

        return {"sys": sys, "sys_ver": sys_ver, "e_devices": e_device}
    
    if param_type == 'languages':
        # List of languages
        languages = [
            "en-US", "en-GB", "ru-RU", "fr-FR", "de-DE", "es-ES", "it-IT", "pt-BR",
            "zh-CN", "ja-JP", "ko-KR", "ar-SA", "hi-IN", "tr-TR", "vi-VN", "th-TH",
            "id-ID", "ms-MY", "bn-BD", "ta-IN", "te-IN"
        ]
        chosen_language = random.choice(languages)

        # Dictionary for converting language codes into full names
        language_map = {
            "en-US": "English", "en-GB": "English", "ru-RU": "Русский", "fr-FR": "Français",
            "de-DE": "Deutsch", "es-ES": "Español", "it-IT": "Italiano", "pt-BR": "Português",
            "zh-CN": "简体中文", "ja-JP": "日本語", "ko-KR": "한국어", "ar-SA": "العربية",
            "hi-IN": "हिन्दी", "tr-TR": "Türkçe", "vi-VN": "Tiếng Việt", "th-TH": "ไทย",
            "id-ID": "Bahasa Indonesia", "ms-MY": "Bahasa Melayu", "bn-BD": "বাংলা",
            "ta-IN": "தமிழ்", "te-IN": "తెలుగు"
        }
        
        # Get the full name of the language
        full_language_name = language_map.get(chosen_language, "Unknown")

        return {"language": chosen_language, "full_language": full_language_name}
    
    if param_type == 'browsers':
        """
        Generating a random browser and corresponding version
        """
        browsers = {
            "Chrome": ["119.0.0.0", "118.0.0.1", "117.0.0.0"],
            "Firefox": ["118.0", "117.0", "116.0"],
            "Safari": ["17.0", "16.5", "16.0"],
            "Edge": ["115.0.1901.203", "114.0.1823.67", "113.0.1774.50"],
            "Opera": ["103.0", "102.0", "101.5"]
        }
        browser_name = random.choice(list(browsers.keys()))
        browser_ver = random.choice(browsers[browser_name])
        
        return {"browser_name": browser_name, "browser_ver": browser_ver}
    
    if param_type == 'proxies':
        """
        Retrieve a random proxy from the list
        """
        return random.choice(self.proxy_list) if self.proxy_list else None
    
    return None


def return_data(variables: Optional[dict] = None) -> dict:
    """
    :param variables: dict, optional
    :return: dict
    """
    if variables is None:
        variables = {}
    return {key: value for key, value in variables.items() if value is not None}


def normalize_proxies(proxy: Union[List[Union[str, dict]], str, None]) -> List[Dict[str, Any]]:
    """
    Normalize proxy input to a list of proxy dictionaries
    """
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
    """
    Parse proxy string into a dictionary
    """
    match = re.match(r'(https?|socks5)://([^:]+):([^@]+)@([^:]+):(\\d+)', proxy_string)
    return {'protocol': match.group(1), 'username': match.group(2), 'password': match.group(3), 'host': match.group(4), 'port': int(match.group(5))} if match else None
