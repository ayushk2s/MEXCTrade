from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from init import MEXCClient  # from your existing file
from trading import get_trade_side, place_order, cancel_all_orders


app = FastAPI()

class TradeRequest(BaseModel):
    uid: str
    mtoken: str
    htoken: str
    symbol: str
    action: str
    vol: float
    leverage: int
    price: float
    take_profit: float | None = None
    stop_loss: float | None = None
    testnet: bool = True

@app.post("/trade")
async def trade(request: TradeRequest):
    try:
        # Optional validation
        if get_trade_side(request.action) is None:
            raise HTTPException(status_code=400, detail="Invalid trade side/action")

        result = await place_order(
            uid=request.uid,
            mtoken=request.mtoken,
            htoken=request.htoken,
            action=request.action,  # ✅ pass action, not side
            symbol=request.symbol,
            vol=request.vol,
            leverage=request.leverage,
            price=request.price,
            take_profit=request.take_profit,
            stop_loss=request.stop_loss,
            testnet=request.testnet
        )
        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel_all_orders")
async def cancel_all_orders_route(request: CancelOrdersRequest):
    try:
        result = await cancel_all_orders(
            uid=request.uid,
            mtoken=request.mtoken,
            htoken=request.htoken,
            symbol=request.symbol,
            testnet=request.testnet
        )
        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


