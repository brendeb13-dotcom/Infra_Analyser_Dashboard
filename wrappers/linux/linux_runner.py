#!/usr/bin/env python3

import subprocess
import json
import sys
import socket
import requests
from datetime import datetime, timezone
from pathlib import Path

# Base directory of wrappers
BASE_DIR = Path(__file__).parent.resolve()

# Backend ingestion endpoint
BACKEND_URL = "http://localhost:8000/api/health"

# Wrapper scripts to execute
WRAPPERS = [
    "cpu_wrapper.py",
    "memory_wrapper.py",
    "uptime_wrapper.py"
]

def run_wrapper(wrapper, args):
    wrapper_path = BASE_DIR / wrapper

    try:
        completed = subprocess.run(
            ["python3", str(wrapper_path)] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            env={"PYTHONWARNINGS": "ignore"}
        )

        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip())

        return json.loads(completed.stdout.strip())

    except Exception as e:
        return {
            "run_id": None,
            "client_id": None,
            "environment": None,
            "source": "ansible",
            "host": {
                "hostname": socket.gethostname(),
                "ip": "127.0.0.1",
                "os": "linux",
                "role": "infrastructure"
            },
            "check": {
                "category": "infra",
                "name": wrapper.replace("_wrapper.py", "").replace("_", " ").title()
            },
            "result": {
                "status": "FAIL",
                "summary": f"Wrapper execution failed: {str(e)}"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def send_to_backend(event):
    try:
        resp = requests.post(
            BACKEND_URL,
            json=event,
            timeout=5
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to send event to backend: {e}", file=sys.stderr)

def main():
    args = sys.argv[1:]
    results = []

    for wrapper in WRAPPERS:
        event = run_wrapper(wrapper, args)
        results.append(event)

        # 🔑 SEND EVENT TO BACKEND (THIS WAS MISSING)
        send_to_backend(event)

    # Still print JSON for logs / debugging
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
