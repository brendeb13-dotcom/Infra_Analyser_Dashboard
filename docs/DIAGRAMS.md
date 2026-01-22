# System Diagrams and Visualizations

## 1. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         END USERS                                       │
│                  (System Administrators)                                │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                    ┌──────────▼─────────────┐
                    │   FRONTEND - React    │
                    │   http://localhost:3000│
                    │                       │
                    │ ┌─────────────────┐  │
                    │ │   Dashboard     │  │
                    │ │ ┌─────────────┐ │  │
                    │ │ │ Capability  │ │  │
                    │ │ │ Selector    │ │  │
                    │ │ └─────────────┘ │  │
                    │ │ ┌─────────────┐ │  │
                    │ │ │ Execution   │ │  │
                    │ │ │ Panel       │ │  │
                    │ │ └─────────────┘ │  │
                    │ │ ┌─────────────┐ │  │
                    │ │ │ Results     │ │  │
                    │ │ │ Charts      │ │  │
                    │ │ └─────────────┘ │  │
                    │ └─────────────────┘  │
                    └──────────────┬───────┘
                                   │ (Axios HTTP)
                    ┌──────────────▼───────────┐
                    │   API GATEWAY - Nginx    │
                    │   http://localhost/api   │
                    └──────────────┬───────────┘
                                   │
        ┌──────────────────────────┴──────────────────────────┐
        │                                                      │
┌───────▼──────────────────────────────────────────────────────▼────────┐
│                    BACKEND - FastAPI                                  │
│                  http://localhost:8000                                │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              API Layer (/api/v1)                              │  │
│  │ ┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐ │  │
│  │ │ Health Checks   │ │ Capabilities     │ │ Configurations  │ │  │
│  │ │ ┌─────────────┐ │ │ ┌──────────────┐ │ │ ┌─────────────┐ │  │
│  │ │ │ Execute     │ │ │ │ Get All      │ │ │ │ Get Config  │ │  │
│  │ │ │ Get Status  │ │ │ │ Get Details  │ │ │ │ Update      │ │  │
│  │ │ │ Get Results │ │ │ └──────────────┘ │ │ │ └─────────────┘ │  │
│  │ │ │ Get History │ │ │                  │ │ │                 │  │
│  │ │ └─────────────┘ │ │                  │ │ │                 │  │
│  │ └─────────────────┘ └──────────────────┘ └─────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                   │                                    │
│  ┌────────────────────────────────▼────────────────────────────────┐  │
│  │         Health Check Execution Engine                          │  │
│  │ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │  │
│  │ │ Windows Svr  │ │ Storage      │ │ Backup / Virtualization │ │  │
│  │ │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌────────────────────┐  │ │  │
│  │ │ │ CPU      │ │ │ │Capacity  │ │ │ │ Network / AD / Ex  │  │ │  │
│  │ │ │ Memory   │ │ │ │Performance│ │ │ │                    │  │ │  │
│  │ │ │ Disk     │ │ │ │Health    │ │ │ │                    │  │ │  │
│  │ │ │ Services │ │ │ │RAID      │ │ │ │                    │  │ │  │
│  │ │ │ Uptime   │ │ │ └──────────┘ │ │ │                    │  │ │  │
│  │ │ └──────────┘ │ │              │ │ │                    │  │ │  │
│  │ └──────────────┘ └──────────────┘ │ └────────────────────┘  │ │  │
│  └──────────────────────────────────┬──────────────────────────┘  │  │
│                                      │                             │  │
│  ┌───────────────────────────────────▼──────────────────────────┐  │  │
│  │         Remote Execution Layer                              │  │  │
│  │ ┌──────────────┐        ┌──────────────┐                   │  │  │
│  │ │ WinRM Handler│        │ SSH Handler  │                   │  │  │
│  │ │ ├─ Kerberos  │        │ ├─ Key Auth  │                   │  │  │
│  │ │ ├─ CredSSP   │        │ ├─ Password  │                   │  │  │
│  │ │ └─ NTLM      │        │ └─ Agent     │                   │  │  │
│  │ └──────────────┘        └──────────────┘                   │  │  │
│  └───────────────────────────────────┬──────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────┬──────────────────────────┘
                      │                    │
        ┌─────────────▼─────────┐  ┌────────▼─────────────┐
        │   PostgreSQL 15       │  │   Redis 7            │
        │   ┌─────────────────┐ │  │ ┌──────────────────┐ │
        │   │ Health Checks   │ │  │ │ Cache            │ │
        │   │ Results         │ │  │ │ Sessions         │ │
        │   │ Configurations  │ │  │ │ Task Queue       │ │
        │   │ Servers         │ │  │ │ Rate Limiting    │ │
        │   └─────────────────┘ │  │ └──────────────────┘ │
        └───────────────────────┘  └──────────────────────┘
                      │                    │
        ┌─────────────▼──────────┬─────────▼─────────────┐
        │                        │                       │
        │   ON-PREMISE SYSTEMS   │   CLOUD SYSTEMS       │
        │  ┌──────────────────┐  │  ┌─────────────────┐  │
        │  │ Windows Servers  │  │  │ AWS Systems     │  │
        │  │ Storage Arrays   │  │  │ Azure Systems   │  │
        │  │ Backup Systems   │  │  │ GCP Systems     │  │
        │  │ Hypervisors      │  │  │                 │  │
        │  │ Network Devices  │  │  │                 │  │
        │  │ AD Servers       │  │  │                 │  │
        │  │ Exchange Servers │  │  │                 │  │
        │  └──────────────────┘  │  └─────────────────┘  │
        │                        │                       │
        └────────────────────────┴───────────────────────┘
```

---

## 2. Data Flow Diagram - Health Check Execution

```
┌─────────────┐
│ User        │
│ Selects     │
│ Capability  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│ Frontend: Dashboard                             │
│ - Loads capability details                      │
│ - Shows configuration form                      │
│ - User selects servers and checks               │
└──────┬──────────────────────────────────────────┘
       │
       │ POST /api/v1/health-checks/execute
       │ {
       │   capability: "windows_server",
       │   config: { servers: [...], checks: {...} }
       │ }
       ▼
┌─────────────────────────────────────────────────┐
│ Backend: API Layer                              │
│ - Validates request                             │
│ - Creates HealthCheck record (PENDING)          │
│ - Returns check_id                              │
│ - Queues background task                        │
└──────┬──────────────────────────────────────────┘
       │
       │ Response: { id: "uuid", status: "pending" }
       ▼
┌─────────────────────────────────────────────────┐
│ Frontend: Health Status Component               │
│ - Displays "Execution Started"                  │
│ - Starts polling /api/v1/health-checks/{id}     │
│ - Polls every 5 seconds                         │
└──────┬──────────────────────────────────────────┘
       │
       │ Background Task Executing (Parallel)
       ▼
┌─────────────────────────────────────────────────┐
│ Backend: Health Check Execution                 │
│ - Update status to RUNNING                      │
│ - For each server in parallel:                  │
│   ├─ Connect via WinRM/SSH                      │
│   ├─ Execute health checks                      │
│   │  ├─ Get disk info                           │
│   │  ├─ Get memory info                         │
│   │  ├─ Get CPU info                            │
│   │  ├─ Get service status                      │
│   │  └─ Analyze results                         │
│   ├─ Determine status (Healthy/Warning/Critical)│
│   └─ Store results in DB                        │
│ - Generate summary statistics                   │
│ - Update HealthCheck status to COMPLETED        │
└──────┬──────────────────────────────────────────┘
       │
       │ Poll Response Status: "completed"
       ▼
┌─────────────────────────────────────────────────┐
│ Frontend: Results Panel                         │
│ - GET /api/v1/health-checks/results/{id}        │
│ - Display summary cards                         │
│ - Show status distribution chart                │
│ - Display results table                         │
│ - Enable export options                         │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│ User Views  │
│ Results &   │
│ Exports     │
│ Report      │
└─────────────┘
```

---

## 3. Database Schema Diagram

```
┌─────────────────────────────┐
│    health_checks            │
├─────────────────────────────┤
│ id: UUID (PK)               │
│ capability: VARCHAR(100)    │◄──┐
│ account_name: VARCHAR(100)  │   │
│ status: ENUM                │   │
│ started_at: TIMESTAMP       │   │
│ completed_at: TIMESTAMP     │   │
│ execution_result: JSONB     │   │
│ error_message: TEXT         │   │
│ created_at: TIMESTAMP       │   │
└─────────────────────────────┘   │
         ▲ 1                       │
         │ has many               │
         │                        │
         │                        │
┌─────────────────────────────┐   │
│health_check_results         │   │
├─────────────────────────────┤   │
│ id: UUID (PK)               │   │
│ health_check_id: UUID (FK)◄─┘   │
│ server_name: VARCHAR(255)   │   │
│ check_type: VARCHAR(100)    │   │
│ status: ENUM                │   │
│ details: JSONB              │   │
│ created_at: TIMESTAMP       │   │
└─────────────────────────────┘   │
                                  │
                                  │
┌──────────────────────────────┐  │
│health_check_configurations   │  │
├──────────────────────────────┤  │
│ id: UUID (PK)                │  │
│ capability: VARCHAR(100) (UX)├──┘
│ config_data: JSONB           │
│ version: INT                 │
│ updated_at: TIMESTAMP        │
│ created_at: TIMESTAMP        │
└──────────────────────────────┘

┌──────────────────────────────┐
│ servers                      │
├──────────────────────────────┤
│ id: UUID (PK)                │
│ name: VARCHAR(255) (UX)      │
│ hostname: VARCHAR(255)       │
│ ip_address: VARCHAR(15)      │
│ server_type: VARCHAR(50)     │
│ port: INT                    │
│ username: VARCHAR(255)       │
│ auth_type: VARCHAR(50)       │
│ capabilities: JSON           │
│ is_active: BOOLEAN           │
│ connection_details: JSON     │
│ created_at: TIMESTAMP        │
└──────────────────────────────┘
```

---

## 4. API Endpoints Structure

```
/api
└── /v1
    ├── /health-checks
    │   ├── POST /execute
    │   │   ├── Request: { capability, config }
    │   │   └── Response: { id, status, created_at }
    │   │
    │   ├── GET /{check_id}
    │   │   └── Response: { id, status, timestamps, results }
    │   │
    │   ├── GET /results/{check_id}
    │   │   └── Response: { id, execution_result, details [...] }
    │   │
    │   └── GET /history
    │       ├── Query: ?capability=&limit=&offset=
    │       └── Response: { total, data [...] }
    │
    ├── /capabilities
    │   ├── GET /
    │   │   └── Response: [ { id, name, version, description } ]
    │   │
    │   └── GET /{capability_name}
    │       └── Response: { id, name, checks, schema }
    │
    ├── /configurations
    │   ├── GET /{capability}
    │   ├── PUT /{capability}
    │   └── GET /{capability}/validate
    │
    └── /servers
        ├── GET /
        ├── POST /
        ├── PUT /{server_id}
        └── DELETE /{server_id}
```

---

## 5. Component Hierarchy - React

```
App
├── Header
│   ├── Logo
│   ├── Title
│   └── Settings Button
│
└── Dashboard
    ├── Container
    │   ├── Grid (Left: Capability Selection)
    │   │   └── Paper
    │   │       └── CapabilitySelector
    │   │           └── List
    │   │               └── ListItemButton[] (for each capability)
    │   │
    │   └── Grid (Right: Execution & Results)
    │       ├── Paper
    │       │   └── Capability Details
    │       │       └── ExecutionPanel
    │       │           ├── TextField (Account Name)
    │       │           ├── TextField (Servers)
    │       │           ├── Checkboxes (Checks to run)
    │       │           └── Button (Execute)
    │       │
    │       ├── Paper (Conditional)
    │       │   └── HealthStatus
    │       │       ├── Status Chip
    │       │       ├── Details Grid
    │       │       └── LinearProgress (if running)
    │       │
    │       └── Paper (Conditional)
    │           └── ResultsPanel
    │               ├── Summary Cards
    │               │   ├── Card (Total)
    │               │   ├── Card (Healthy)
    │               │   ├── Card (Warning)
    │               │   └── Card (Critical)
    │               ├── Chart
    │               │   └── PieChart / BarChart
    │               └── Table
    │                   └── TableRow[] (results)
    │
    └── Toaster (Notifications)
```

---

## 6. Deployment Architecture

### Development Environment
```
Local Machine
├── Docker Compose
│   ├── postgres (volume: postgres_data)
│   ├── redis (volume: redis_data)
│   ├── backend (port 8000, volume: ./backend)
│   ├── frontend (port 3000, volume: ./frontend)
│   └── nginx (port 80, 443)
│
├── Hot Reload Enabled
├── Debug Logging
└── Database Console Access
```

### Production Environment (Docker Compose)
```
Server/VM
├── Docker Engine
│   ├── PostgreSQL Container (persistent volume)
│   ├── Redis Container (persistent volume)
│   ├── FastAPI Container (3 workers)
│   ├── React Container (static serve)
│   └── Nginx Container (reverse proxy)
│
├── SSL/TLS Certificates
├── Environment Secrets
├── Backup Scripts
└── Monitoring & Logging
```

### Production Environment (Kubernetes)
```
Kubernetes Cluster
├── Namespace: infra-analyzer
│
├── Pods
│   ├── FastAPI (Deployment, 3+ replicas)
│   ├── PostgreSQL (StatefulSet, 1 primary + replicas)
│   ├── Redis (StatefulSet, 1 master + slaves)
│   └── Nginx Ingress (Deployment)
│
├── Services
│   ├── backend-service (ClusterIP)
│   ├── database-service (ClusterIP)
│   ├── cache-service (ClusterIP)
│   └── api-ingress (LoadBalancer)
│
├── Storage
│   ├── PersistentVolume (Database)
│   ├── PersistentVolume (Cache)
│   └── PersistentVolumeClaim (Backup)
│
├── ConfigMaps
│   ├── api-config
│   └── logging-config
│
└── Secrets
    ├── db-credentials
    ├── jwt-secret
    └── credentials
```

---

## 7. Health Check Execution Sequence

```
Timeline
├─ T+0s   : User clicks "Execute Health Check"
│           └─ Frontend sends POST request
│
├─ T+0.5s : Backend receives request
│           ├─ Creates HealthCheck (PENDING)
│           ├─ Returns check_id
│           └─ Frontend receives response
│
├─ T+1s   : Frontend starts polling /health-checks/{id}
│
├─ T+1.5s : Backend background task starts
│           ├─ Updates status to RUNNING
│           └─ Begins server connections
│
├─ T+2-10s: Parallel execution on each server
│           ├─ WinRM/SSH connection established
│           ├─ Disk info retrieved (~1s)
│           ├─ Memory info retrieved (~1s)
│           ├─ CPU info retrieved (~1s)
│           ├─ Service status retrieved (~1s)
│           └─ Results evaluated
│
├─ T+10s+ : Results accumulated and stored
│
├─ T+15s  : Backend finishes, updates status to COMPLETED
│
├─ T+20s  : Frontend poll receives COMPLETED status
│           └─ Fetches detailed results
│
└─ T+25s  : Frontend displays results to user
```

---

## 8. Integration Points

```
Internet/Users
     │
     ▼
┌──────────────┐
│ React App    │ (localhost:3000)
│ - Browser    │
└──────┬───────┘
       │ REST API (Axios)
       ▼
┌──────────────┐
│ Nginx Proxy  │ (reverse proxy, port 80/443)
│ - Load Bal   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ FastAPI Backend  │ (localhost:8000)
│ - REST API       │
└──────┬───────────┘
       │
       ├──────────────────────┬──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
    ┌──────┐            ┌──────────┐          ┌─────────┐
    │ Psql │            │  Redis   │          │ Monitor │
    │  DB  │            │  Cache   │          │ Logs    │
    └──────┘            └──────────┘          └─────────┘
       │                                           │
       └─────────────────────────────────┬─────────┘
                                         │
       ┌─────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Target Infrastructure Systems        │
│ ├─ Windows Servers (WinRM)           │
│ ├─ Storage Arrays (API/CLI)          │
│ ├─ Backup Systems (API/CLI)          │
│ ├─ Virtualization (WinRM/SSH)        │
│ ├─ Network Devices (SNMP/SSH)        │
│ ├─ Active Directory (LDAP)           │
│ └─ Exchange Servers (EWS API)        │
└──────────────────────────────────────┘
```

---

## 9. Feature Timeline

```
v1.0 (Current - Design Phase)
├─ Core API ✓
├─ Dashboard UI ✓
├─ Windows Server Checks ✓
├─ Basic Capabilities ✓
└─ Docker Deployment ✓

v1.1 (Next - Initial Release)
├─ Complete all health checks
├─ Advanced filtering
├─ Export reports
├─ User authentication
└─ Performance optimization

v2.0 (Future)
├─ WebSocket real-time updates
├─ Advanced scheduling
├─ Email notifications
├─ Machine learning anomalies
├─ Mobile app
└─ Kubernetes native

v3.0 (Future)
├─ Multi-cloud support
├─ Custom health checks
├─ Advanced analytics
├─ Predictive insights
└─ API SDKs
```

---

This visual guide complements the documentation and provides quick reference for understanding the system architecture and data flows.
