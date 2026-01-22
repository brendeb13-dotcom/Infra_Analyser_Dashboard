"""
Capabilities API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/capabilities", tags=["capabilities"])

# Define available capabilities
CAPABILITIES = {
    "windows_server": {
        "name": "Windows Server",
        "description": "Windows Server health checks",
        "version": "1.2",
        "checks": {
            "availability": "Server connectivity and availability",
            "disk_capacity": "Disk usage and capacity",
            "memory": "Memory utilization",
            "cpu": "CPU usage",
            "services": "Critical services status",
            "uptime": "Server uptime",
            "event_log": "Event log analysis",
        },
        "configuration_schema": {
            "servers": {"type": "array", "items": {"type": "string"}},
            "account_name": {"type": "string"},
            "checks": {
                "type": "object",
                "properties": {
                    "availability": {"type": "boolean"},
                    "disk_capacity": {"type": "boolean"},
                    "disk_threshold_percent": {"type": "number"},
                    "memory": {"type": "boolean"},
                    "cpu": {"type": "boolean"},
                    "services": {"type": "boolean"},
                    "critical_services": {"type": "array"},
                    "uptime": {"type": "boolean"},
                    "min_uptime_days": {"type": "number"},
                }
            },
        }
    },
    "storage": {
        "name": "Storage Systems",
        "description": "Storage health checks (EMC, 3PAR)",
        "version": "1.0",
        "checks": {
            "capacity": "Storage capacity monitoring",
            "performance": "Performance metrics",
            "health": "Array health status",
            "raid": "RAID status",
            "snapshot": "Snapshot management",
        },
        "configuration_schema": {}
    },
    "backup": {
        "name": "Backup Systems",
        "description": "Backup health checks (NetBackup, BackupExec)",
        "version": "1.0",
        "checks": {
            "job_status": "Backup job status",
            "capacity": "Backup capacity monitoring",
            "devices": "Backup device health",
            "database": "Backup database health",
        },
        "configuration_schema": {}
    },
    "virtualization": {
        "name": "Virtualization",
        "description": "Virtualization health checks (HyperV, VMware)",
        "version": "1.0",
        "checks": {
            "hosts": "Host status",
            "vms": "Virtual machine status",
            "resources": "Resource utilization",
            "cluster": "Cluster status",
        },
        "configuration_schema": {}
    },
    "network": {
        "name": "Network",
        "description": "Network infrastructure health checks",
        "version": "1.0",
        "checks": {
            "connectivity": "Network connectivity",
            "interfaces": "Network interfaces",
            "performance": "Network performance",
        },
        "configuration_schema": {}
    },
    "active_directory": {
        "name": "Active Directory",
        "description": "Active Directory health checks",
        "version": "1.0",
        "checks": {
            "replication": "Domain controller replication",
            "schema": "Schema status",
            "forest_health": "Forest functional level",
        },
        "configuration_schema": {}
    },
    "exchange": {
        "name": "Exchange Server",
        "description": "Exchange Server health checks",
        "version": "1.0",
        "checks": {
            "dag": "Database Availability Groups",
            "databases": "Database health",
            "services": "Exchange services",
            "disk_space": "Disk space monitoring",
        },
        "configuration_schema": {}
    },
}


@router.get("")
async def get_capabilities() -> List[Dict[str, Any]]:
    """
    Get list of all available capabilities
    
    Returns:
        List of capabilities
    """
    return [
        {
            "id": key,
            "name": cap["name"],
            "description": cap["description"],
            "version": cap["version"],
        }
        for key, cap in CAPABILITIES.items()
    ]


@router.get("/{capability_name}")
async def get_capability_details(capability_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a capability
    
    Args:
        capability_name: Capability ID/name
    
    Returns:
        Capability details including schema and checks
    """
    if capability_name not in CAPABILITIES:
        raise HTTPException(status_code=404, detail="Capability not found")
    
    capability = CAPABILITIES[capability_name]
    return {
        "id": capability_name,
        "name": capability["name"],
        "description": capability["description"],
        "version": capability["version"],
        "checks": capability["checks"],
        "configuration_schema": capability["configuration_schema"],
    }
