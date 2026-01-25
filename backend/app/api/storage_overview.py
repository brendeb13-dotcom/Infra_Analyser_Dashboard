from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Dict, List

from app.api.storage import STORAGE_EVENTS

router = APIRouter(prefix="/api/v1", tags=["storage-overview"])


@router.get("/storage/overview")
def storage_overview(
    client_id: str = Query(...),
    environment: str = Query(...),
):
    relevant = [
        e for e in STORAGE_EVENTS
        if e["client_id"] == client_id
        and e["environment"] == environment
    ]

    if not relevant:
        return {
            "client_id": client_id,
            "environment": environment,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "hosts": 0,
                "hbas": 0,
                "luns": 0,
                "mappings": 0,
            },
            "hosts": [],
        }

    hosts = {}
    total_hbas = total_luns = total_mappings = 0

    for event in relevant:
        host = event["host"]["hostname"]
        storage = event["storage"]

        hosts.setdefault(host, {
            "hostname": host,
            "ip": event["host"]["ip"],
            "hbas": [],
            "luns": [],
            "mappings": [],
            "last_seen": event["timestamp"],
        })

        hosts[host]["hbas"].extend(storage.get("hbas", []))
        hosts[host]["luns"].extend(storage.get("luns", []))
        hosts[host]["mappings"].extend(storage.get("mappings", []))

        total_hbas += len(storage.get("hbas", []))
        total_luns += len(storage.get("luns", []))
        total_mappings += len(storage.get("mappings", []))

    return {
        "client_id": client_id,
        "environment": environment,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "hosts": len(hosts),
            "hbas": total_hbas,
            "luns": total_luns,
            "mappings": total_mappings,
        },
        "hosts": list(hosts.values()),
    }
