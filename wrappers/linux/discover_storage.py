#!/usr/bin/env python3

import os
import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# -------------------------
# Metadata (INPUT)
# -------------------------
CLIENT_ID = os.getenv("CLIENT_ID", "unknown_client")
ENVIRONMENT = os.getenv("ENVIRONMENT", "unknown_env")
RUN_ID = os.getenv("RUN_ID", "manual_run")
SOURCE = "ansible"

HOSTNAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOSTNAME)

TIMESTAMP = datetime.now(timezone.utc).isoformat()

# -------------------------
# Helpers
# -------------------------
def run(cmd):
    try:
        return subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return ""

# -------------------------
# Discover HBAs
# -------------------------
def discover_hbas():
    hbas = []
    fc_path = Path("/sys/class/fc_host")

    if not fc_path.exists():
        return hbas

    for host in fc_path.iterdir():
        hba = {
            "hba_id": host.name,
            "wwn": run(["cat", str(host / "port_name")]),
            "state": run(["cat", str(host / "port_state")]),
            "speed": run(["cat", str(host / "speed")]),
            "driver": run(["basename", str((host / "device/driver").resolve())]),
        }
        hbas.append(hba)

    return hbas

# -------------------------
# Discover LUNs
# -------------------------
def discover_luns():
    luns = []

    output = run(["lsblk", "-dn", "-o", "NAME,SIZE,TYPE"])
    for line in output.splitlines():
        name, size, dtype = line.split()
        if dtype != "disk":
            continue

        device = f"/dev/{name}"

        vendor = run(["udevadm", "info", "--query=property", f"--name={device}"])
        vendor_name = "unknown"
        for v in vendor.splitlines():
            if v.startswith("ID_VENDOR="):
                vendor_name = v.split("=", 1)[1]

        luns.append({
            "lun_id": name,
            "size": size,
            "device": device,
            "vendor": vendor_name,
        })

    return luns

# -------------------------
# Discover Multipath Mapping
# -------------------------
def discover_mappings(hbas):
    mappings = []

    mp_output = run(["multipath", "-ll"])
    if not mp_output:
        return mappings

    current_lun = None

    for line in mp_output.splitlines():
        if line and not line.startswith(" "):
            current_lun = line.split()[0]
        elif "active ready running" in line and current_lun:
            mappings.append({
                "lun_id": current_lun,
                "paths": mp_output.count(current_lun),
                "hba_wwns": [h["wwn"] for h in hbas if h["wwn"]],
                "status": "OK" if hbas else "FAIL",
            })

    return mappings

# -------------------------
# MAIN
# -------------------------
def main():
    hbas = discover_hbas()
    luns = discover_luns()
    mappings = discover_mappings(hbas)

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
        "storage": {
            "hbas": hbas,
            "luns": luns,
            "mappings": mappings,
        },
    }

    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
