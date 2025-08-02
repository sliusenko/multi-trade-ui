from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_trades():
    return {"message": "Trades endpoint works"}
