from fastapi import APIRouter

from app.models.schemas import QuotesResponse
from app.services.quotes import quotes_service

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("", response_model=QuotesResponse)
async def get_quotes():
    return await quotes_service.get_quotes()
