#!/usr/bin/env python3

import os
import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ------------------------------------------------------------------
# Metadata (Injected by Ansible / Environment)
# ------------------------------------------------------------------
CLIENT_ID = os.getenv("CLIENT_ID", "unknown_client")
ENVIRONMENT = os.getenv("ENVIRONMENT", "unknown_env")
RUN_ID = os.getenv("RUN_ID", "manual_run")
SOURCE = "ansible"

HOSTNAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOSTNAME)
TIMESTAMP = datetime.now(timezone.utc).isoformat()

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def run(cmd):
    try:
        return subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return ""

# ------------------------------------------------------------------
# Discover FC HBAs (FCA IDs)
# ------------------------------------------------------------------
def discover_hbas():
    hbas = []
    fc_path = Path("/sys/class/fc_host")

    if not fc_path.exists():
        return hbas

    for host in fc_path.iterdir():
        hba = {
            "hba_id": host.name,
            "wwpn": run(["cat", str(host / "port_name")]),
            "wwnn": run(["cat", str(host / "node_name")]),
            "state": run(["cat", str(host / "port_state")]),
            "speed": run(["cat", str(host / "speed")]),
            "driver": run(
                ["basename", str((host / "device/driver").resolve())]
            ),
        }
        hbas.append(hba)

    return hbas

# ------------------------------------------------------------------
# Discover LUNs visible to host
# ------------------------------------------------------------------
def discover_luns():
    luns = []

    output = run(["lsblk", "-dn", "-o", "NAME,TYPE"])
    for line in output.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue

        name, dtype = parts
        if dtype != "disk":
            continue

        luns.append(name)

    return luns

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    hbas = discover_hbas()
    visible_luns = discover_luns()

    payload = {
        "client_id": CLIENT_ID,
        "environment": ENVIRONMENT,
        "run_id": RUN_ID,
        "source": SOURCE,
        "timestamp": TIMESTAMP,
        "os": run(["uname", "-s"]) or "Linux",
        "host": {
            "hostname": HOSTNAME,
            "ip": IP_ADDRESS,
        },
        "san": {
            "hbas": hbas,
            "visible_luns": visible_luns,
        },
    }

    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
