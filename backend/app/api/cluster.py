from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
from datetime import datetime, timezone

# =====================================================
# Routers
# =====================================================
ingest_router = APIRouter(prefix="/api/v1", tags=["cluster-ingest"])
read_router   = APIRouter(prefix="/api/v1", tags=["cluster-read"])

# =====================================================
# In-memory store
# =====================================================
CLUSTER_EVENTS: List[Dict] = []

# =====================================================
# Helpers
# =====================================================
def normalize_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)

# =====================================================
# INGEST
# =====================================================
@ingest_router.post("/cluster")
def ingest_cluster(payload: Dict):

    required_fields = [
        "client_id",
        "environment",
        "run_id",
        "host",
        "cluster",
        "timestamp",
    ]

    for field in required_fields:
        if field not in payload:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}",
            )

    payload["timestamp"] = normalize_ts(payload["timestamp"])
    CLUSTER_EVENTS.append(payload)

    return {
        "status": "accepted",
        "stored_events": len(CLUSTER_EVENTS),
    }

# =====================================================
# OVERVIEW
# =====================================================
@read_router.get("/cluster/overview")
def get_cluster_overview(
    client_id: str = Query(...),
    environment: str = Query(...),
):
    relevant = [
        e for e in CLUSTER_EVENTS
        if e["client_id"] == client_id
        and e["environment"] == environment
    ]

    if not relevant:
        return {
            "client_id": client_id,
            "environment": environment,
            "clusters": [],
        }

    clusters = {}

    for event in relevant:
        cluster = event["cluster"]
        name = cluster.get("name", "unknown")

        if name not in clusters:
            clusters[name] = {
                "name": name,
                "type": cluster.get("type", "unknown"),
                "nodes": {},
                "last_seen": event["timestamp"],
            }

        for node in cluster.get("nodes", []):
            hostname = node.get("hostname")
            if hostname:
                clusters[name]["nodes"][hostname] = node

        if event["timestamp"] > clusters[name]["last_seen"]:
            clusters[name]["last_seen"] = event["timestamp"]

    return {
        "client_id": client_id,
        "environment": environment,
        "clusters": [
            {
                "name": c["name"],
                "type": c["type"],
                "nodes": len(c["nodes"]),
                "last_seen": c["last_seen"].isoformat(),
            }
            for c in clusters.values()
        ],
    }

# =====================================================
# DETAILS (IMPORTANT FOR YOUR UI)
# =====================================================
@read_router.get("/cluster/{cluster_name}")
def get_cluster_details(
    cluster_name: str,
    client_id: str = Query(...),
    environment: str = Query(...),
):
    relevant = [
        e for e in CLUSTER_EVENTS
        if e["client_id"] == client_id
        and e["environment"] == environment
        and e["cluster"]["name"] == cluster_name
    ]

    if not relevant:
        raise HTTPException(status_code=404, detail="Cluster not found")

    cluster = {
        "name": cluster_name,
        "type": relevant[0]["cluster"].get("type", "unknown"),
        "nodes": {},
        "last_seen": None,
    }

    for event in relevant:
        ts = event["timestamp"]

        for node in event["cluster"].get("nodes", []):
            hostname = node.get("hostname")
            if hostname:
                cluster["nodes"][hostname] = node

        if not cluster["last_seen"] or ts > cluster["last_seen"]:
            cluster["last_seen"] = ts

    return {
        "client_id": client_id,
        "environment": environment,
        "cluster": {
            "name": cluster["name"],
            "type": cluster["type"],
            "nodes": list(cluster["nodes"].values()),
            "last_seen": cluster["last_seen"].isoformat(),
        },
    }

