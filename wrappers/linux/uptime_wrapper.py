#!/usr/bin/env python3

import json
import psutil
import socket
from datetime import datetime, timedelta
import argparse

def get_uptime_status(uptime_hours: float):
    if uptime_hours >= 24:
        return "OK", "System uptime is stable"
    elif uptime_hours >= 4:
        return "WARN", "System was restarted within the last 24 hours"
    else:
        return "FAIL", "System was restarted very recently"

def main():
    parser = argparse.ArgumentParser(description="Uptime Health Check Wrapper")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.utcnow()
    uptime_delta = now - boot_time
    uptime_hours = round(uptime_delta.total_seconds() / 3600, 2)

    status, message = get_uptime_status(uptime_hours)

    hostname = socket.gethostname()

    result = {
        "run_id": args.run_id,
        "client_id": args.client_id,
        "environment": args.environment,
        "source": "ansible",
        "host": {
            "hostname": hostname,
            "ip": socket.gethostbyname(hostname),
            "os": "linux",
            "role": "infrastructure"
        },
        "check": {
            "category": "infra",
            "name": "Uptime Health",
            "description": "System uptime stability check"
        },
        "result": {
            "status": status,
            "summary": message,
            "metrics": {
                "uptime_hours": uptime_hours,
                "boot_time_utc": boot_time.isoformat() + "Z"
            }
        },
        "timestamp": now.isoformat() + "Z"
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
