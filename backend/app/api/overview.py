from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Dict, Any

router = APIRouter(prefix="/api/v1", tags=["overview"])

# IMPORTANT: must be the SAME list used by /api/health
from app.api.health import HEALTH_EVENTS


STATUS_PRIORITY = {
    "FAIL": 3,
    "WARN": 2,
    "OK": 1,
    "UNKNOWN": 0,
}


def extract(event: Dict[str, Any], key: str):
    """
    Safely extract a top-level or meta field.
    """
    if key in event:
        return event.get(key)
    return event.get("meta", {}).get(key)


def normalize_check(event: Dict[str, Any]):
    """
    Normalize check field across all script styles.
    Supports:
    - check: "CPU"
    - check: { "name": "CPU", "category": "infra" }
    """
    check_obj = event.get("check")

    if isinstance(check_obj, dict):
        check_name = check_obj.get("name", "unknown")
        category = check_obj.get("category", "infra")
    else:
        check_name = str(check_obj) if check_obj else "unknown"
        category = "infra"

    return check_name, category


@router.get("/overview")
def get_overview(
    client_id: str = Query(...),
    environment: str = Query(...),
):
    # --- Safety: no events yet ---
    if not HEALTH_EVENTS:
        return {
            "client_id": client_id,
            "environment": environment,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "capabilities": [],
        }

    # --- Filter by client + environment ---
    relevant_events = [
        e for e in HEALTH_EVENTS
        if extract(e, "client_id") == client_id
        and extract(e, "environment") == environment
    ]

    if not relevant_events:
        return {
            "client_id": client_id,
            "environment": environment,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "capabilities": [],
        }

    # --- Keep latest event per (host, check) ---
    latest_by_host_check: Dict[tuple, Dict] = {}

    for event in relevant_events:
        host = event.get("host", {}).get("hostname", "unknown")
        check_name, _ = normalize_check(event)

        try:
            ts = datetime.fromisoformat(
                event["timestamp"].replace("Z", "+00:00")
            )
        except Exception:
            ts = datetime.now(timezone.utc)

        key = (host, check_name)

        if key not in latest_by_host_check or ts > latest_by_host_check[key]["_ts"]:
            event["_ts"] = ts
            latest_by_host_check[key] = event

    # --- Aggregate per capability (category) ---
    capabilities: Dict[str, Dict] = {}

    for event in latest_by_host_check.values():
        check_name, category = normalize_check(event)
        status = event.get("result", {}).get("status", "UNKNOWN")
        host = event.get("host", {}).get("hostname", "unknown")
        ts = event["_ts"]

        if category not in capabilities:
            capabilities[category] = {
                "category": category,
                "name": f"{category.capitalize()} Health",
                "status": status,
                "affected_hosts": set(),
                "last_run": ts,
            }

        cap = capabilities[category]

        # Worst status wins
        if STATUS_PRIORITY.get(status, 0) > STATUS_PRIORITY.get(cap["status"], 0):
            cap["status"] = status

        if status != "OK":
            cap["affected_hosts"].add(host)

        if ts > cap["last_run"]:
            cap["last_run"] = ts

    # --- Build response ---
    return {
        "client_id": client_id,
        "environment": environment,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": [
            {
                "category": cap["category"],
                "name": cap["name"],
                "status": cap["status"],
                "affected_hosts": len(cap["affected_hosts"]),
                "last_run": cap["last_run"].isoformat(),
            }
            for cap in capabilities.values()
        ],
    }
