from fastapi import APIRouter

from app.models.schemas import LogsResponse
from app.utils.log_buffer import log_buffer

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=LogsResponse)
async def get_logs():
    return LogsResponse(entries=log_buffer.get_entries())


@router.post("/clear")
async def clear_logs():
    log_buffer.clear()
    return {"success": True}
