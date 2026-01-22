# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently no authentication required. In production, implement JWT token-based authentication.

## Response Format
All responses return JSON with standard format:

### Success Response
```json
{
  "data": {},
  "status": "success",
  "timestamp": "2024-01-19T10:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status": "error",
  "timestamp": "2024-01-19T10:00:00Z"
}
```

## Endpoints

### Health Checks

#### Execute Health Check
**POST** `/health-checks/execute`

Execute a health check for a specific capability.

**Request Body:**
```json
{
  "capability": "windows_server",
  "account_name": "PRODUCTION",
  "config": {
    "servers": ["SERVER1", "SERVER2"],
    "checks": {
      "availability": true,
      "disk_capacity": true,
      "disk_threshold_percent": 80,
      "memory": true,
      "cpu": true,
      "services": true,
      "uptime": true,
      "min_uptime_days": 7
    }
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "capability": "windows_server",
  "account_name": "PRODUCTION",
  "status": "pending",
  "created_at": "2024-01-19T10:00:00"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request
- 500: Server error

---

#### Get Health Check Status
**GET** `/health-checks/{check_id}`

Get the current status of a health check execution.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "capability": "windows_server",
  "account_name": "PRODUCTION",
  "status": "running",
  "started_at": "2024-01-19T10:00:00",
  "completed_at": null,
  "created_at": "2024-01-19T10:00:00"
}
```

---

#### Get Health Check Results
**GET** `/health-checks/results/{check_id}`

Get detailed results of a completed health check.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "capability": "windows_server",
  "account_name": "PRODUCTION",
  "status": "completed",
  "execution_result": {
    "overall_status": "warning",
    "total_checks": 12,
    "healthy": 10,
    "warning": 2,
    "critical": 0,
    "unknown": 0,
    "results": [
      {
        "server": "SERVER1",
        "check_type": "disk_capacity",
        "status": "warning",
        "details": {
          "C:": 82.5,
          "D:": 65.3,
          "threshold": 80
        },
        "timestamp": "2024-01-19T10:05:00"
      }
    ]
  },
  "detailed_results": []
}
```

---

#### Get Health Check History
**GET** `/health-checks/history`

Get execution history with pagination and filtering.

**Query Parameters:**
- `capability` (optional): Filter by capability name
- `limit` (optional, default: 10): Number of records per page
- `offset` (optional, default: 0): Pagination offset

**Request:**
```
GET /health-checks/history?capability=windows_server&limit=20&offset=0
```

**Response:**
```json
{
  "total": 45,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "capability": "windows_server",
      "status": "completed",
      "created_at": "2024-01-19T10:00:00"
    }
  ]
}
```

---

### Capabilities

#### Get All Capabilities
**GET** `/capabilities`

List all available health check capabilities.

**Response:**
```json
[
  {
    "id": "windows_server",
    "name": "Windows Server",
    "description": "Windows Server health checks",
    "version": "1.2"
  },
  {
    "id": "storage",
    "name": "Storage Systems",
    "description": "Storage health checks (EMC, 3PAR)",
    "version": "1.0"
  },
  {
    "id": "backup",
    "name": "Backup Systems",
    "description": "Backup health checks (NetBackup, BackupExec)",
    "version": "1.0"
  }
]
```

---

#### Get Capability Details
**GET** `/capabilities/{capability_name}`

Get detailed information about a specific capability.

**Response:**
```json
{
  "id": "windows_server",
  "name": "Windows Server",
  "description": "Windows Server health checks",
  "version": "1.2",
  "checks": {
    "availability": "Server connectivity and availability",
    "disk_capacity": "Disk usage and capacity",
    "memory": "Memory utilization",
    "cpu": "CPU usage",
    "services": "Critical services status",
    "uptime": "Server uptime"
  },
  "configuration_schema": {
    "servers": {
      "type": "array",
      "items": { "type": "string" }
    },
    "account_name": {
      "type": "string"
    }
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request - Invalid input |
| 404 | Not found - Resource doesn't exist |
| 500 | Server error - Internal error |
| 503 | Service unavailable - Database or Redis down |

## Rate Limiting
Not implemented in v1.0. Will be added in future versions.

## WebSocket Support
Real-time updates for health check progress coming in v2.0.

## Examples

### Example: Windows Server Health Check

```bash
# Start health check
curl -X POST http://localhost:8000/api/v1/health-checks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "windows_server",
    "account_name": "PRODUCTION",
    "config": {
      "servers": ["SERVER1", "SERVER2"],
      "checks": {
        "availability": true,
        "disk_capacity": true,
        "disk_threshold_percent": 80
      }
    }
  }'

# Response:
# {"id":"550e8400-e29b-41d4-a716-446655440000","status":"pending"}

# Check status (poll every 5 seconds)
curl http://localhost:8000/api/v1/health-checks/550e8400-e29b-41d4-a716-446655440000

# Get results when completed
curl http://localhost:8000/api/v1/health-checks/results/550e8400-e29b-41d4-a716-446655440000
```

### Example: Storage System Health Check

```bash
curl -X POST http://localhost:8000/api/v1/health-checks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "storage",
    "account_name": "PRODUCTION",
    "config": {
      "storage_arrays": ["ARRAY1", "ARRAY2"],
      "checks": {
        "capacity": true,
        "performance": true,
        "health": true
      }
    }
  }'
```

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## SDKs

Python SDK coming in v1.1. Check back for updates.

## Webhooks

Webhook support for health check notifications coming in v2.0.
