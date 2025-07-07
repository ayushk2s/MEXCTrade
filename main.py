from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from trading import get_trade_side, place_order, cancel_all_order  # Your core functions

app = FastAPI()

# ──────── Request Models ────────
class TradeRequest(BaseModel):
    uid: str
    mtoken: str
    htoken: str
    symbol: str
    action: str     # ✅ should be 'buy', 'sell', 'broughtsell', or 'soldbuy'
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
    testnet: bool = True

# ──────── Trade Endpoint ────────
@app.post("/trade")
async def trade(request: TradeRequest):
    try:
        # Validate the action
        side = get_trade_side(request.action)
        if side is None:
            raise HTTPException(status_code=400, detail="Invalid trade action. Must be 'buy', 'sell', 'broughtsell', or 'soldbuy'.")

        # Call the actual order placement function
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


# ──────── Cancel All Orders Endpoint ────────
@app.post("/cancel")
async def cancel_all(request: CancelRequest):
    try:
        result = await cancel_all_order(
            uid=request.uid,
            mtoken=request.mtoken,
            htoken=request.htoken,
            testnet=request.testnet
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
