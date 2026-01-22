from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List

router = APIRouter()

class HealthPayload(BaseModel):
    run_id: str
    source: str
    environment: str
    host: dict
    check: dict
    result: dict
    timestamp: datetime

HEALTH_EVENTS: List[Dict] = []



@router.post("/health")
def ingest_health(payload: Dict):
    """
    Ingest health event and store in memory.
    """
    HEALTH_EVENTS.append(payload)
    return {
        "status": "stored",
        "total_events": len(HEALTH_EVENTS)
    }

@router.get("/_debug/events")
def debug_events():
    return {
        "count": len(HEALTH_EVENTS),
        "events": HEALTH_EVENTS
    }

