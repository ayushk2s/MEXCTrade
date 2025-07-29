from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
import logging
from contextlib import asynccontextmanager
from init import MEXCClient, close_http_client
from trading import get_trade_side, place_order, cancel_all_order
from cache import init_cache, close_cache, get_cache_stats, clear_cache
try:
    import orjson as json_lib
except ImportError:
    import ujson as json_lib
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance metrics
request_count = 0
total_request_time = 0.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting MEXC Trading API...")
    await init_cache()
    logger.info("Cache system initialized")

    yield

    # Shutdown
    logger.info("Shutting down MEXC Trading API...")
    await close_cache()
    await close_http_client()
    logger.info("Cleanup completed")

# Create FastAPI app with optimizations
app = FastAPI(
    title="MEXC Trading API - Optimized",
    description="High-performance MEXC trading API with caching and connection pooling",
    version="2.0.0",
    lifespan=lifespan
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware to track request performance"""
    global request_count, total_request_time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    request_count += 1
    total_request_time += process_time

    # Add performance headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-Count"] = str(request_count)

    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")

    return response

# ──────── Request Models ────────

class TradeRequest(BaseModel):
    uid: str
    mtoken: str
    htoken: str
    symbol: str
    action: str
    order_type: int
    vol: float
    leverage: int
    price: float
    take_profit: float | None = None
    stop_loss: float | None = None
    testnet: bool = True

class CancelRequest(BaseModel):
    uid: str
    mtoken: str
    htoken: str
    # symbol: str
    testnet: bool = True

# ──────── Trade Endpoint ────────

@app.post("/trade")
async def trade(request: TradeRequest):
    """
    Optimized trade endpoint with performance monitoring and error handling
    """
    start_time = time.time()

    try:
        # Validate trade side
        side = get_trade_side(request.action)
        if side is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid trade side/action: {request.action}. Use 'buy', 'sell', 'broughtsell', or 'soldbuy'"
            )

        logger.info(f"Processing {request.action.upper()} order for {request.symbol}")

        # Execute the trade with optimized client
        result = await place_order(
            uid=request.uid,
            mtoken=request.mtoken,
            htoken=request.htoken,
            symbol=request.symbol,
            action=request.action,
            order_type=request.order_type,
            vol=request.vol,
            leverage=request.leverage,
            price=request.price,
            take_profit=request.take_profit,
            stop_loss=request.stop_loss,
            testnet=request.testnet
        )

        execution_time = time.time() - start_time
        logger.info(f"Trade completed in {execution_time:.3f}s")

        return {
            "status": "success",
            "result": result,
            "execution_time": execution_time,
            "timestamp": time.time()
        }

    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Trade failed after {execution_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
        )

# ──────── Cancel All Orders Endpoint ────────

@app.post("/cancel")
async def cancel_all(request: CancelRequest):
    """
    Optimized cancel all orders endpoint
    """
    start_time = time.time()

    try:
        logger.info("Processing cancel all orders request")

        result = await cancel_all_order(
            uid=request.uid,
            mtoken=request.mtoken,
            htoken=request.htoken,
            testnet=request.testnet
        )

        execution_time = time.time() - start_time
        logger.info(f"Cancel all orders completed in {execution_time:.3f}s")

        return {
            "status": "success",
            "result": result,
            "execution_time": execution_time,
            "timestamp": time.time()
        }

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Cancel all orders failed after {execution_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
        )

# ──────── Monitoring and Health Check Endpoints ────────

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    }

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    global request_count, total_request_time

    avg_response_time = total_request_time / request_count if request_count > 0 else 0
    cache_stats = await get_cache_stats()

    return {
        "requests": {
            "total_count": request_count,
            "total_time": total_request_time,
            "average_response_time": avg_response_time
        },
        "cache": cache_stats,
        "timestamp": time.time()
    }

@app.post("/cache/clear")
async def clear_api_cache(pattern: str = "*"):
    """Clear cache entries"""
    cleared_count = await clear_cache(pattern)
    return {
        "status": "success",
        "cleared_entries": cleared_count,
        "pattern": pattern,
        "timestamp": time.time()
    }

