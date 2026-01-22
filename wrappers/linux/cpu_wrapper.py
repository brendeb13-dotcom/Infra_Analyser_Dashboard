#!/usr/bin/env python3

import json
import psutil
import socket
from datetime import datetime
import argparse

def get_cpu_status(cpu_percent: float):
    if cpu_percent <= 70:
        return "OK", "CPU usage within normal limits"
    elif cpu_percent <= 85:
        return "WARN", "CPU usage is moderately high"
    else:
        return "FAIL", "CPU usage is critically high"

def main():
    parser = argparse.ArgumentParser(description="CPU Health Check Wrapper")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    cpu_percent = psutil.cpu_percent(interval=1)
    status, message = get_cpu_status(cpu_percent)

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
            "name": "CPU Health",
            "description": "CPU utilization health check"
        },
        "result": {
            "status": status,
            "summary": message,
            "metrics": {
                "cpu_usage_percent": cpu_percent
            }
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
