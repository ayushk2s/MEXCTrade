# config.py - Configuration settings for optimized MEXC Trading API

import os
from typing import Optional

class Config:
    """Configuration class for the MEXC Trading API"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))  # Single worker for local hosting
    
    # Performance Settings
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", "100"))
    MAX_KEEPALIVE_CONNECTIONS: int = int(os.getenv("MAX_KEEPALIVE_CONNECTIONS", "20"))
    KEEPALIVE_EXPIRY: float = float(os.getenv("KEEPALIVE_EXPIRY", "30.0"))
    
    # Timeout Settings (in seconds)
    CONNECT_TIMEOUT: float = float(os.getenv("CONNECT_TIMEOUT", "5.0"))
    READ_TIMEOUT: float = float(os.getenv("READ_TIMEOUT", "10.0"))
    WRITE_TIMEOUT: float = float(os.getenv("WRITE_TIMEOUT", "5.0"))
    POOL_TIMEOUT: float = float(os.getenv("POOL_TIMEOUT", "10.0"))
    
    # Cache Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "300"))  # 5 minutes
    CACHE_CONTRACT_INFO_TTL: int = int(os.getenv("CACHE_CONTRACT_INFO_TTL", "60"))  # 1 minute
    CACHE_USER_POSITIONS_TTL: int = int(os.getenv("CACHE_USER_POSITIONS_TTL", "30"))  # 30 seconds
    CACHE_MARKET_DATA_TTL: int = int(os.getenv("CACHE_MARKET_DATA_TTL", "10"))  # 10 seconds
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # MEXC API Configuration
    MEXC_BASE_URL: str = os.getenv("MEXC_BASE_URL", "https://futures.mexc.com")
    MEXC_TESTNET_URL: str = os.getenv("MEXC_TESTNET_URL", "https://futures.mexc.com")
    
    # Security Settings
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Compression Settings
    ENABLE_GZIP: bool = os.getenv("ENABLE_GZIP", "true").lower() == "true"
    GZIP_MINIMUM_SIZE: int = int(os.getenv("GZIP_MINIMUM_SIZE", "1000"))
    
    # Rate Limiting (requests per minute)
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PATH: str = os.getenv("METRICS_PATH", "/metrics")
    
    # Development Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    @classmethod
    def get_uvicorn_config(cls) -> dict:
        """Get uvicorn server configuration"""
        config = {
            "host": cls.HOST,
            "port": cls.PORT,
            "workers": cls.WORKERS,
            "log_level": cls.LOG_LEVEL.lower(),
            "access_log": True,
            "use_colors": True,
        }
        
        if cls.DEBUG:
            config.update({
                "reload": cls.RELOAD,
                "reload_dirs": ["."],
                "reload_includes": ["*.py"]
            })
        
        # Use uvloop for better performance on Linux/Mac
        try:
            import uvloop
            config["loop"] = "uvloop"
        except ImportError:
            pass
        
        return config
    
    @classmethod
    def get_httpx_config(cls) -> dict:
        """Get httpx client configuration"""
        return {
            "limits": {
                "max_keepalive_connections": cls.MAX_KEEPALIVE_CONNECTIONS,
                "max_connections": cls.MAX_CONNECTIONS,
                "keepalive_expiry": cls.KEEPALIVE_EXPIRY
            },
            "timeout": {
                "connect": cls.CONNECT_TIMEOUT,
                "read": cls.READ_TIMEOUT,
                "write": cls.WRITE_TIMEOUT,
                "pool": cls.POOL_TIMEOUT
            },
            "http2": True,
            "follow_redirects": True
        }
    
    @classmethod
    def get_cache_config(cls) -> dict:
        """Get cache configuration"""
        return {
            "redis_url": cls.REDIS_URL,
            "default_ttl": cls.CACHE_DEFAULT_TTL,
            "contract_info_ttl": cls.CACHE_CONTRACT_INFO_TTL,
            "user_positions_ttl": cls.CACHE_USER_POSITIONS_TTL,
            "market_data_ttl": cls.CACHE_MARKET_DATA_TTL
        }

# Global config instance
config = Config()
