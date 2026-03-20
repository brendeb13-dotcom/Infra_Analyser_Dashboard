from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
from datetime import datetime, timezone

# -----------------------------
# Routers
# -----------------------------
ingest_router = APIRouter(prefix="/api", tags=["storage"])
read_router = APIRouter(prefix="/api/v1", tags=["storage"])

# -----------------------------
# In-memory store (B2 scope)
# -----------------------------
STORAGE_EVENTS: List[Dict] = []

# -----------------------------
# Helpers
# -----------------------------
def normalize_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def parse_size_to_gb(size_str: str) -> float:
    """Convert size like 10G / 1T / 500M → GB"""
    try:
        size_str = size_str.upper()

        if "T" in size_str:
            return float(size_str.replace("T", "")) * 1024
        elif "G" in size_str:
            return float(size_str.replace("G", ""))
        elif "M" in size_str:
            return float(size_str.replace("M", "")) / 1024
        else:
            return 0.0
    except Exception:
        return 0.0


# -----------------------------
# INGEST STORAGE DISCOVERY
# -----------------------------
@ingest_router.post("/storage")
def ingest_storage(payload: Dict):
    print("Debug Payload:", payload)

    required_fields = [
        "client_id",
        "environment",
        "run_id",
        "host",
        "os",
        "storage",
        "timestamp",
    ]

    for field in required_fields:
        if field not in payload:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}",
            )

    payload["timestamp"] = normalize_ts(payload["timestamp"])
    STORAGE_EVENTS.append(payload)

    return {
        "status": "accepted",
        "stored_events": len(STORAGE_EVENTS),
    }


# -----------------------------
# STORAGE OVERVIEW (Dashboard)
# -----------------------------
@read_router.get("/storage/overview")
def storage_overview(
    client_id: str = Query(...),
    environment: str = Query(...),
):
    relevant = [
        e for e in STORAGE_EVENTS
        if e["client_id"] == client_id
        and e["environment"] == environment
    ]

    hosts = []

    for e in relevant:
        hbas = e["storage"].get("hbas", [])
        luns = e["storage"].get("luns", [])
        mappings = e["storage"].get("mappings", [])

        hosts.append({
            "hostname": e["host"]["hostname"],
            "ip": e["host"]["ip"],

            # ✅ FIXED OS (top-level)
            "os": e.get("os", "N/A"),

            # raw data
            "hbas": hbas,
            "luns": luns,
            "mappings": mappings,

            # 🔥 ENRICHED DATA
            "hba_drivers": list(set(
                h.get("driver") for h in hbas if h.get("driver")
            )),

            "lun_vendors": list(set(
                l.get("vendor") for l in luns if l.get("vendor")
            )),

            "total_capacity_gb": round(sum(
                parse_size_to_gb(l.get("size", "0"))
                for l in luns
            ), 2),

            "last_seen": e["timestamp"].isoformat(),
        })

    # -----------------------------
    # SUMMARY
    # -----------------------------
    summary = {
        "hosts": len(hosts),
        "os": len(set(h["os"] for h in hosts)),

        "hbas": sum(len(h["hbas"]) for h in hosts),
        "luns": sum(len(h["luns"]) for h in hosts),
        "mappings": sum(len(h["mappings"]) for h in hosts),

        # 🔥 NEW INSIGHTS
        "unique_hba_drivers": list(set(
            d for h in hosts for d in h["hba_drivers"]
        )),

        "unique_storage_vendors": list(set(
            v for h in hosts for v in h["lun_vendors"]
        )),

        "total_capacity_gb": round(sum(
            h["total_capacity_gb"] for h in hosts
        ), 2),
    }

    return {
        "client_id": client_id,
        "environment": environment,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "hosts": hosts,

        # OS breakdown
        "os_breakdown": {
            os: len([h for h in hosts if h["os"] == os])
            for os in set(h["os"] for h in hosts)
        },
    }


# -----------------------------
# STORAGE DETAILS (DEEP VIEW)
# -----------------------------
@read_router.get("/storage/details")
def storage_details(
    client_id: str = Query(...),
    environment: str = Query(...),
):
    relevant = [
        e for e in STORAGE_EVENTS
        if e["client_id"] == client_id
        and e["environment"] == environment
    ]

    return {
        "client_id": client_id,
        "environment": environment,
        "hosts": [
            {
                "hostname": e["host"]["hostname"],
                "ip": e["host"]["ip"],
                "os": e.get("os", "N/A"),
                "storage": e["storage"],  # full raw detail
                "timestamp": e["timestamp"].isoformat(),
            }
            for e in relevant
        ]
    }