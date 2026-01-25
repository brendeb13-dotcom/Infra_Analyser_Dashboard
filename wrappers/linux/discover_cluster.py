#!/usr/bin/env python3

import os
import json
import socket
import subprocess
from datetime import datetime, timezone

# =====================================================
# Metadata (INPUT)
# =====================================================
CLIENT_ID = os.getenv("CLIENT_ID", "unknown_client")
ENVIRONMENT = os.getenv("ENVIRONMENT", "unknown_env")
RUN_ID = os.getenv("RUN_ID", "manual_run")
SOURCE = "ansible"

HOSTNAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOSTNAME)
TIMESTAMP = datetime.now(timezone.utc).isoformat()

# =====================================================
# Helpers
# =====================================================
def run(cmd):
    try:
        return subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return ""

# =====================================================
# Discover Applications (Services + Ports)
# =====================================================
def discover_apps():
    apps = []

    # -------------------------
    # Running systemd services
    # -------------------------
    services_output = run([
        "systemctl",
        "list-units",
        "--type=service",
        "--state=running",
        "--no-pager",
        "--no-legend"
    ])

    services = []
    for line in services_output.splitlines():
        name = line.split()[0]
        if name.endswith(".service"):
            services.append(name.replace(".service", ""))

    # -------------------------
    # Listening TCP ports
    # -------------------------
    ports_output = run(["ss", "-lntp"])
    service_ports = {}

    for line in ports_output.splitlines():
        if "LISTEN" not in line:
            continue

        parts = line.split()
        if len(parts) < 6:
            continue

        addr = parts[3]
        proc = parts[-1]

        try:
            port = int(addr.split(":")[-1])
        except Exception:
            continue

        for svc in services:
            if f'"{svc}"' in proc or f",{svc}," in proc:
                service_ports.setdefault(svc, set()).add(port)

    # -------------------------
    # Build app objects
    # -------------------------
    for svc in sorted(services):
        apps.append({
            "name": svc,
            "type": "service",
            "status": "running",
            "ports": sorted(service_ports.get(svc, [])),
        })

    return apps

# =====================================================
# Cluster Discovery
# =====================================================
def discover_cluster():
    apps = discover_apps()

    return {
        "name": "standalone",
        "type": "standalone",
        "version": "",
        "nodes": [
            {
                "hostname": HOSTNAME,
                "ip": IP_ADDRESS,
                "role": "standalone",
                "apps": apps,
            }
        ],
    }

# =====================================================
# MAIN
# =====================================================
def main():
    payload = {
        "client_id": CLIENT_ID,
        "environment": ENVIRONMENT,
        "run_id": RUN_ID,
        "source": SOURCE,
        "timestamp": TIMESTAMP,
        "host": {
            "hostname": HOSTNAME,
            "ip": IP_ADDRESS,
            "os": "linux",
        },
        "cluster": discover_cluster(),
    }

    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
