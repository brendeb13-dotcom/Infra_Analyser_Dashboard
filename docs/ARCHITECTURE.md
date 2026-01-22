# System Architecture

## Overview

The Infrastructure Analyzer Dashboard is a modern, scalable web application designed to monitor and analyze on-premise infrastructure health across multiple capabilities. It uses a microservices architecture with a React frontend and Python/FastAPI backend.

## Architecture Layers

### 1. Presentation Layer (Frontend)

**Technology:** React 18, Material-UI, Redux  
**Location:** `frontend/`

**Components:**
- Dashboard - Main user interface
- Capability Selector - Choose monitoring capability
- Configuration Panel - Configure health checks
- Execution Panel - Trigger health checks
- Results Visualization - Display results with charts
- Health Status Indicators - Real-time status display

**Responsibilities:**
- User interaction and form handling
- State management with Redux
- API communication with axios
- Real-time updates with polling
- Data visualization with Recharts
- Responsive UI for all devices

**Key Libraries:**
- `react-router-dom`: Client-side routing
- `@mui/material`: UI components
- `recharts`: Data visualization
- `axios`: HTTP client
- `react-hot-toast`: Notifications

---

### 2. API Layer (Backend)

**Technology:** FastAPI (Python 3.11), async/await  
**Location:** `backend/app/api/`

**API Structure:**
```
/api/v1/
├── /health-checks          # Health check operations
├── /capabilities           # Available capabilities
├── /configurations         # Configuration management
├── /servers               # Server inventory
└── /reports               # Report generation
```

**Key Endpoints:**
- `POST /health-checks/execute` - Start health check
- `GET /health-checks/{id}` - Get check status
- `GET /health-checks/results/{id}` - Get results
- `GET /capabilities` - List capabilities
- `GET /capabilities/{name}` - Get capability details

**Features:**
- RESTful API design
- Async request handling
- Background task execution
- CORS support
- Comprehensive error handling
- Request validation with Pydantic

---

### 3. Business Logic Layer

**Location:** `backend/app/health_checks/`

**Health Check Classes:**
- `BaseHealthCheck` - Abstract base class
- `WindowsServerHealthCheck` - Windows server monitoring
- `StorageHealthCheck` - Storage array monitoring
- `BackupHealthCheck` - Backup system monitoring
- `VirtualizationHealthCheck` - Hypervisor monitoring
- `NetworkHealthCheck` - Network infrastructure
- `ActiveDirectoryHealthCheck` - Domain services
- `ExchangeHealthCheck` - Email system monitoring

**Execution Flow:**
1. Validate configuration
2. Connect to target systems
3. Execute health checks in parallel
4. Collect results
5. Generate summary and status
6. Store results in database
7. Return to API

**Error Handling:**
- Transient errors: Retry with exponential backoff
- Permanent errors: Fail and log
- Partial failures: Continue with available targets
- Timeout handling: Cancel operation after timeout

---

### 4. Data Access Layer

**Technology:** SQLAlchemy ORM  
**Location:** `backend/app/db/` and `backend/app/models/`

**Database Schema:**

```sql
-- Health Checks Table
CREATE TABLE health_checks (
  id UUID PRIMARY KEY,
  capability VARCHAR(100),
  account_name VARCHAR(100),
  status ENUM (pending, running, completed, failed),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  execution_result JSONB,
  error_message TEXT,
  created_at TIMESTAMP
);

-- Health Check Results Table
CREATE TABLE health_check_results (
  id UUID PRIMARY KEY,
  health_check_id UUID FK,
  server_name VARCHAR(255),
  check_type VARCHAR(100),
  status ENUM (healthy, warning, critical, unknown),
  details JSONB,
  created_at TIMESTAMP
);

-- Configurations Table
CREATE TABLE health_check_configurations (
  id UUID PRIMARY KEY,
  capability VARCHAR(100) UNIQUE,
  config_data JSONB,
  version INT,
  updated_at TIMESTAMP
);

-- Servers Table
CREATE TABLE servers (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  hostname VARCHAR(255),
  ip_address VARCHAR(15),
  server_type VARCHAR(50),
  port INT,
  auth_type VARCHAR(50),
  capabilities JSON,
  is_active BOOLEAN,
  created_at TIMESTAMP
);
```

**ORM Models:**
- `HealthCheck` - Health check execution record
- `HealthCheckResult` - Individual check result
- `HealthCheckConfiguration` - Configuration storage
- `Server` - Server inventory

---

### 5. Remote Execution Layer

**Location:** `backend/app/utils/remote_executor.py`

**Supported Protocols:**
- **WinRM** - Windows remote management
  - Uses Python pywinrm library
  - Supports Kerberos, CredSSP, Basic auth
  - Default port: 5985 (HTTP), 5986 (HTTPS)

- **SSH** - Linux/Unix remote access
  - Uses Paramiko library
  - Key-based authentication
  - Default port: 22

- **SNMP** - Network device monitoring
  - SNMP v2/v3 support
  - Community string or credentials

- **SOAP/REST APIs** - Direct API calls
  - Storage arrays, backup systems
  - Custom authentication

**Connection Management:**
- Connection pooling
- Session reuse
- Timeout handling
- Automatic retry logic
- Credential encryption

---

### 6. Infrastructure & Deployment

**Containerization:** Docker & Docker Compose

**Service Stack:**
1. **PostgreSQL** - Primary database
   - Data persistence
   - ACID transactions
   - Full-text search

2. **Redis** - Caching & task queue
   - Session cache
   - Result caching
   - Celery task queue

3. **FastAPI Backend** - API server
   - Uvicorn ASGI server
   - Multiple workers
   - Health checks

4. **React Frontend** - Web UI
   - Node.js development server
   - Production-ready build
   - Static file serving

5. **Nginx** - Reverse proxy
   - Load balancing
   - SSL/TLS termination
   - Static file caching

---

## Data Flow

### Health Check Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User initiates health check from React dashboard         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Frontend sends POST request to FastAPI backend           │
│    POST /api/v1/health-checks/execute                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. API creates HealthCheck record with PENDING status       │
│    Stores in PostgreSQL                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. API returns check_id to frontend                         │
│    Frontend starts polling for status                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Backend executes health check in background              │
│    - Validates configuration                                 │
│    - Updates status to RUNNING                              │
│    - Connects to target systems via WinRM/SSH               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Collects metrics from each server in parallel            │
│    - Disk capacity, memory, CPU                             │
│    - Service status, uptime                                 │
│    - Event logs, network config                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Evaluates results against thresholds                     │
│    - Determines status: HEALTHY, WARNING, CRITICAL          │
│    - Generates summary statistics                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Stores results in database                               │
│    - HealthCheckResults for each check                      │
│    - Summary in HealthCheck.execution_result                │
│    - Updates status to COMPLETED                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. Frontend polls and receives COMPLETED status             │
│    Fetches detailed results via GET /results/{id}           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Displays results in dashboard with visualizations       │
│     - Status indicators, charts, tables                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication & Authorization (v2.0)
- JWT token-based authentication
- Role-based access control (RBAC)
- User management system
- Session management

### Credential Management
- Encrypted credential storage
- Vault integration (Hashicorp Vault)
- Per-environment credentials
- Audit logging of credential access

### Network Security
- HTTPS/TLS encryption
- WinRM with Kerberos/CredSSP
- SSH key-based authentication
- VPN/firewall for on-premise access

### Data Security
- Database encryption at rest
- API request validation
- SQL injection prevention (SQLAlchemy)
- XSS protection
- CORS policy enforcement

---

## Scalability & Performance

### Horizontal Scaling
- Stateless API servers (multiple Uvicorn workers)
- Load balancing via Nginx
- Database connection pooling
- Redis for distributed caching

### Performance Optimization
- Async/await for concurrent operations
- Connection reuse and pooling
- Result caching in Redis
- Database query optimization
- Frontend code splitting and lazy loading

### Monitoring & Metrics
- Application logging (file + console)
- Performance metrics collection
- Health check endpoints
- Error rate tracking
- Response time monitoring

---

## High Availability

### Fault Tolerance
- Database replication
- Redis persistence
- Automatic retry logic
- Circuit breaker pattern
- Graceful degradation

### Backup & Recovery
- Daily database backups
- Point-in-time recovery
- Data archival to cold storage
- Disaster recovery procedures
- RTO: 4 hours, RPO: 1 hour

---

## Integration Points

### External Systems
- **Windows Servers**: WinRM + PowerShell
- **Linux/Unix**: SSH + shell scripts
- **Storage Arrays**: Vendor APIs, CLI tools
- **Backup Systems**: Vendor APIs, CLI tools
- **Email/Notifications**: SMTP
- **Logging**: Syslog, ELK Stack (optional)

---

## Technology Decisions

### Why FastAPI?
- Modern async framework
- High performance
- Auto-generated API docs
- Built-in validation
- Easy WebSocket support for v2.0

### Why React?
- Component-based architecture
- Rich ecosystem
- Developer experience
- Strong community
- SEO-friendly options (SSR)

### Why PostgreSQL?
- Reliable ACID transactions
- JSONB for flexible data storage
- Full-text search support
- Excellent replication
- Open source

### Why Docker?
- Consistent environments
- Easy deployment
- Service isolation
- Horizontal scaling
- Industry standard

---

## Future Enhancements

### v2.0 Roadmap
- WebSocket support for real-time updates
- User authentication & authorization
- Advanced scheduling & automation
- Machine learning for anomaly detection
- Mobile app (React Native)
- Database federation for multi-site
- Webhook notifications
- Custom health check builders

### Performance Improvements
- GraphQL API
- Event streaming (Kafka)
- Time-series database (InfluxDB/TimescaleDB)
- Advanced caching strategies
- CDN for static assets

### Infrastructure
- Kubernetes deployment
- Helm charts
- Terraform IaC
- CI/CD pipeline (GitLab/GitHub Actions)
- APM integration (DataDog, New Relic)

---

## Deployment Architectures

### Development
```
Local machine
├── Docker Compose
├── PostgreSQL
├── Redis
├── FastAPI (uvicorn)
└── React (webpack-dev-server)
```

### Production - Docker Compose
```
Single server or VM
├── Nginx (reverse proxy)
├── FastAPI (multiple workers)
├── PostgreSQL (primary)
├── Redis
└── React static files
```

### Production - Kubernetes
```
Kubernetes cluster
├── Ingress (Nginx/Istio)
├── FastAPI pods (autoscaling)
├── PostgreSQL (StatefulSet)
├── Redis (StatefulSet)
├── PersistentVolumes
└── ConfigMaps & Secrets
```

---

## Monitoring & Observability

### Application Metrics
- Request count & latency
- Error rate
- Active connections
- Queue depth
- Cache hit rate

### Infrastructure Metrics
- CPU, memory, disk usage
- Network I/O
- Database connections
- Container resources

### Logging
- Application logs (JSON format)
- Access logs
- Error logs
- Audit logs
- Debug logs (development only)

### Health Checks
- API health endpoint: `/health`
- Database connectivity
- Redis connectivity
- Backend service availability
- Frontend availability

---

## Configuration Management

### Environment-Based Config
- Development: `.env.development`
- Staging: `.env.staging`
- Production: `.env.production` (secrets vault)

### Configuration Sources
- Environment variables
- Config files (.env)
- Secret vault (Hashicorp Vault)
- Database (ConfigMap in K8s)

---

## API Versioning Strategy

- URI-based versioning: `/api/v1/`, `/api/v2/`
- Backward compatibility maintained for 2 versions
- Deprecation warnings in responses
- Migration guides for major versions

