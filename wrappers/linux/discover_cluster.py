#!/usr/bin/env python3

import os
import sys
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
# Discover Applications (Services + Processes + Ports)
# =====================================================
def discover_apps():
    apps = []
    service_names = set()

    # -------------------------
    # SYSTEMD SERVICES
    # -------------------------
    services_output = run([
        "systemctl",
        "list-units",
        "--type=service",
        "--state=running",
        "--no-pager",
        "--no-legend"
    ])

    for line in services_output.splitlines():
        parts = line.split()
        if parts and parts[0].endswith(".service"):
            service_names.add(parts[0].replace(".service", "").lower())

    # -------------------------
    # PROCESS DISCOVERY (IMPORTANT)
    # -------------------------
    process_output = run(["ps", "-eo", "comm,args"])

    for line in process_output.splitlines():
        line = line.lower()

        if "mysqld" in line:
            service_names.add("mysql")

        if "nginx" in line:
            service_names.add("nginx")

        if "httpd" in line:
            service_names.add("apache")

        if "postgres" in line:
            service_names.add("postgres")

        if "mongod" in line:
            service_names.add("mongodb")

        if "redis" in line:
            service_names.add("redis")

    # -------------------------
    # PORT MAPPING
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
        proc = parts[-1].lower()

        try:
            port = int(addr.split(":")[-1])
        except Exception:
            continue

        for svc in service_names:
            if svc in proc:
                service_ports.setdefault(svc, set()).add(port)

    print("Debug Services:", service_names, file=sys.stderr)

    # -------------------------
    # FINAL APP LIST
    # -------------------------
    for svc in sorted(service_names):
        apps.append({
            "name": svc,
            "type": "service",
            "status": "running",
            "ports": sorted(service_ports.get(svc, [])),
        })

    return apps


# =====================================================
# Discover Mount Points
# =====================================================
def discover_mounts():
    mounts = []

    output = run(["lsblk", "-o", "NAME,MOUNTPOINT,FSTYPE"])

    for line in output.splitlines()[1:]:
        parts = line.split()

        if len(parts) < 3:
            continue

        name, mount, fstype = parts

        if not mount:
            continue

        if fstype in ["tmpfs", "devtmpfs"]:
            continue

        mounts.append({
            "mount": mount,
            "device": name,
            "fstype": fstype
        })

    # fallback if empty (WSL case)
    if not mounts:
        mounts.append({
            "mount": "/",
            "device": "root",
            "fstype": "unknown"
        })

    return mounts


# =====================================================
# Discover Processes with Paths (🔥 CORE)
# =====================================================
def discover_process_details():
    processes = []

    output = run(["ps", "-eo", "pid,comm,args"])

    for line in output.splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue

        pid, name, args = parts

        processes.append({
            "pid": pid,
            "name": name.lower(),
            "args": args.lower()
        })

    return processes


# =====================================================
# Extract paths from process args
# =====================================================
def extract_paths(proc):
    paths = []

    for token in proc["args"].split():
        if token.startswith("/"):
            paths.append(token)

    return paths


# =====================================================
# Map Applications to Mounts (🔥 FULLY DYNAMIC)
# =====================================================
def map_apps_to_mounts(mounts):
    mapping = []
    processes = discover_process_details()

    mount_points = [m["mount"] for m in mounts]

    def find_mount(path):
        for m in sorted(mount_points, key=len, reverse=True):
            if path.startswith(m):
                return m
        return "/"

    IGNORE = ["systemd", "bash", "sh", "ps", "login"]

    for proc in processes:
        name = proc["name"]

        if any(i in name for i in IGNORE):
            continue

        paths = extract_paths(proc)

        for path in paths:
            mapping.append({
                "mount": find_mount(path),
                "path": path,
                "application": name
            })

    return mapping


# =====================================================
# Cluster Discovery
# =====================================================
def discover_cluster():
    apps = discover_apps()
    mounts = discover_mounts()
    mapping = map_apps_to_mounts(mounts)

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
                "mounts": mounts,
                "app_mount_mapping": mapping
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
        "os": run(["uname", "-s"]) or "Linux",
        "host": {
            "hostname": HOSTNAME,
            "ip": IP_ADDRESS,
        },
        "cluster": discover_cluster(),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()