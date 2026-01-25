from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import Dict, List

# -----------------------------
# Routers
# -----------------------------
ingest_router = APIRouter(prefix="/api", tags=["san-ingest"])
read_router = APIRouter(prefix="/api/v1", tags=["san"])

# -----------------------------
# In-memory store (B2 scope)
# -----------------------------
SAN_EVENTS: List[Dict] = []


# -----------------------------
# Helpers
# -----------------------------
def normalize_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


# -----------------------------
# INGEST SAN DISCOVERY
# -----------------------------
@ingest_router.post("/san")
def ingest_san(payload: Dict):
    required = [
        "client_id",
        "environment",
        "run_id",
        "host",
        "san",
        "timestamp",
    ]

    for field in required:
        if field not in payload:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}",
            )

    payload["timestamp"] = normalize_ts(payload["timestamp"])
    SAN_EVENTS.append(payload)

    return {
        "status": "accepted",
        "stored_events": len(SAN_EVENTS),
    }


# -----------------------------
# SAN OVERVIEW (Dashboard)
# -----------------------------
@read_router.get("/san/overview")
def san_overview(
    client_id: str = Query(...),
    environment: str = Query(...),
):
    relevant = [
        e for e in SAN_EVENTS
        if e["client_id"] == client_id
        and e["environment"] == environment
    ]

    hosts = []
    for e in relevant:
        hosts.append({
            "hostname": e["host"]["hostname"],
            "ip": e["host"]["ip"],
            "fcas": e["san"].get("fcas", []),
            "switches": e["san"].get("switches", []),
            "lun_mappings": e["san"].get("lun_mappings", []),
            "last_seen": e["timestamp"].isoformat(),
        })

    summary = {
        "hosts": len(hosts),
        "fcas": sum(len(h["fcas"]) for h in hosts),
        "switch_ports": sum(
            len(s.get("ports", []))
            for h in hosts for s in h["switches"]
        ),
        "luns": sum(len(h["lun_mappings"]) for h in hosts),
    }

    return {
        "client_id": client_id,
        "environment": environment,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "hosts": hosts,
    }
