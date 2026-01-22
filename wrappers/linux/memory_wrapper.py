#!/usr/bin/env python3

import json
import psutil
import socket
from datetime import datetime
import argparse

def get_memory_status(mem_percent: float):
    if mem_percent <= 70:
        return "OK", "Memory usage within normal limits"
    elif mem_percent <= 85:
        return "WARN", "Memory usage is moderately high"
    else:
        return "FAIL", "Memory usage is critically high"

def main():
    parser = argparse.ArgumentParser(description="Memory Health Check Wrapper")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    status, message = get_memory_status(mem_percent)

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
            "name": "Memory Health",
            "description": "System memory utilization health check"
        },
        "result": {
            "status": status,
            "summary": message,
            "metrics": {
                "memory_usage_percent": mem_percent,
                "total_mb": round(mem.total / 1024 / 1024, 2),
                "used_mb": round(mem.used / 1024 / 1024, 2),
                "available_mb": round(mem.available / 1024 / 1024, 2)
            }
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
