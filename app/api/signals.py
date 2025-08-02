from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

SIGNAL_LOG = []

@router.post("/")
async def record_signal(signal: dict):
    signal["timestamp"] = datetime.now().isoformat()
    SIGNAL_LOG.append(signal)
    return {"status": "ok"}

@router.get("/")
async def get_signals():
    return SIGNAL_LOG[-50:]  # останні 50
