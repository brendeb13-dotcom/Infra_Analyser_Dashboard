# Storage Health Check - Complete System Guide

## 📋 Overview

This is a **complete, production-ready solution** for discovering servers in your network, collecting storage health information, storing results in a database, and displaying them in the React dashboard.

### Key Components

| Component | Purpose | Files |
|-----------|---------|-------|
| **Network Discovery** | Scan network and identify servers | `network_scanner.py` |
| **Storage Health Check** | Collect storage info from servers | `storage.py` |
| **Ansible Automation** | Deploy and execute on multiple servers | `storage_health_check.yml` |
| **Inventory Management** | Generate Ansible inventory | `generate_inventory.py` |
| **Results Processing** | Store and manage results in DB | `storage_results.py` |
| **REST API** | Backend endpoints for dashboard | `storage.py` (API) |
| **React Dashboard** | Visual display of results | `StorageHealthCheck.jsx` |
| **Orchestration** | Master script for automation | `orchestrate_storage_checks.py` |

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install pywinrm paramiko psutil requests pyyaml ansible
ansible-galaxy collection install community.general community.windows
```

### 2. Configure Credentials

```bash
ansible-vault create ansible/vault.yml
# Add Windows admin password and SSH key path
```

### 3. Run Complete Workflow

```bash
python orchestrate_storage_checks.py --network-range 192.168.1.0/24
```

### 4. View Results

```bash
# In dashboard
open http://localhost:3000
# Go to Storage Health Check tab

# Or via API
curl http://localhost:8000/api/v1/storage/results
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│       React Dashboard                    │
│  Storage Health Check Component          │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴─────────┬──────────────┐
    │                  │              │
    ▼                  ▼              ▼
┌────────────┐  ┌────────────┐  ┌──────────┐
│ Discovery  │  │ Health     │  │ Results  │
│ API        │  │ Check API  │  │ API      │
└────┬───────┘  └──────┬─────┘  └────┬─────┘
     │                 │             │
     │      FastAPI Backend          │
     │                 │             │
  ┌──┴──────────────┬──┴──────┬──────┴───┐
  │                 │         │          │
  ▼                 ▼         ▼          ▼
Network          Storage    Results   Database
Scanner         Health     Processor   (SQLite)
                Check
  │                 │
  │     Ansible      │
  └──────────┬───────┘
             │
    ┌────────┴───────────┬──────────────┐
    │                    │              │
    ▼                    ▼              ▼
Windows Server      Linux Server   Storage Array
(WinRM)            (SSH)          (REST/SNMP)
```

---

## 📁 File Structure

```
infra-analyzer-dashboard/
├── backend/
│   ├── app/
│   │   ├── discovery/
│   │   │   └── network_scanner.py      # Network discovery
│   │   ├── health_checks/
│   │   │   └── storage.py              # Storage checks
│   │   ├── processors/
│   │   │   └── storage_results.py      # Results processing
│   │   ├── api/
│   │   │   └── storage.py              # REST API endpoints
│   │   └── db/
│   │       └── __init__.py             # Database setup
│   ├── requirements.txt
│   └── app/main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── StorageHealthCheck.jsx  # React component
│   │   ├── services/
│   │   │   └── api.js                  # API client
│   │   └── App.jsx
│   └── package.json
├── ansible/
│   ├── storage_health_check.yml        # Main playbook
│   ├── generate_inventory.py           # Inventory generator
│   └── vault.yml                       # Credentials vault
├── orchestrate_storage_checks.py       # Master orchestration
├── STORAGE_QUICK_START.md              # Quick start guide
├── STORAGE_DEPLOYMENT_GUIDE.md         # Detailed guide
└── docker-compose.yml
```

---

## 🔄 Complete Workflow

### Step 1: Network Discovery

**Purpose:** Find all servers in your network

```python
from app.discovery.network_scanner import NetworkScanner

scanner = NetworkScanner(timeout=2, threads=20)
servers = scanner.scan_network('192.168.1.0/24')
scanner.save_to_json('discovered_servers.json')
```

**Output:** JSON/CSV file with server IPs, hostnames, OS types

**Time:** 5-10 minutes for typical network

### Step 2: Generate Inventory

**Purpose:** Convert discovered servers to Ansible format

```bash
python ansible/generate_inventory.py \
  --input discovered_servers.json \
  --output inventory.ini \
  --format ini
```

**Output:** INI file with Windows and Linux groups

**Time:** < 1 minute

### Step 3: Deploy & Execute

**Purpose:** Deploy scripts and run health checks on all servers

```bash
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  --vault-password-file vault_pass.txt
```

**What happens:**
1. Clone scripts from GitHub
2. Install dependencies
3. Execute health check script
4. Collect results

**Time:** 2-10 minutes depending on server count

### Step 4: Process Results

**Purpose:** Import results into database

```python
from app.processors.storage_results import StorageResultsProcessor

processor = StorageResultsProcessor('storage_results.db')
processor.process_json_result('server1', 'server1_storage_check.json')
summary = processor.get_summary()
processor.close()
```

**Output:** SQLite database with normalized results

**Time:** < 1 minute

### Step 5: View & Export

**Purpose:** Display results and generate reports

```bash
# View in dashboard
open http://localhost:3000

# Export to CSV
curl -X POST http://localhost:8000/api/v1/storage/export
```

---

## 📊 API Endpoints

### Discovery

```http
POST /api/v1/storage/discover
{
  "network_range": "192.168.1.0/24",
  "ports": [22, 3389, 5985, 445]
}

GET /api/v1/storage/discovery/{discovery_id}
```

### Health Check

```http
POST /api/v1/storage/health-check
{
  "servers": ["192.168.1.10", "192.168.1.20"],
  "check_types": ["disk", "config", "health"]
}

GET /api/v1/storage/health-check/{check_id}
```

### Results

```http
GET /api/v1/storage/results
GET /api/v1/storage/results?status_filter=CRITICAL
GET /api/v1/storage/summary
POST /api/v1/storage/export
```

---

## 🗄️ Database Schema

```sql
-- Servers table
servers (id, hostname, ip_address, os_type, check_timestamp)

-- Disk information
disk_info (
  id, server_id, device_name, device_path, size_gb, used_gb,
  available_gb, used_percent, filesystem, mount_point, status
)

-- Storage configuration
storage_config (
  id, server_id, device_name, device_path, size_gb, status,
  vendor, model, serial_number
)

-- Health check results
health_check_results (
  id, server_id, check_status, total_disks, total_capacity_gb,
  total_used_gb, issues
)
```

---

## 🎯 Usage Examples

### Via Command Line

```bash
# One-command complete workflow
python orchestrate_storage_checks.py --network-range 192.168.1.0/24

# Discover only
python orchestrate_storage_checks.py --skip inventory playbook processing export

# Dry run
python orchestrate_storage_checks.py --dry-run

# Custom config
python orchestrate_storage_checks.py --config custom_config.json
```

### Via REST API

```bash
# Discover servers
curl -X POST http://localhost:8000/api/v1/storage/discover \
  -d '{"network_range": "192.168.1.0/24"}'

# Execute health checks
curl -X POST http://localhost:8000/api/v1/storage/health-check \
  -d '{"servers": ["192.168.1.10"], "check_types": ["disk"]}'

# Get results
curl http://localhost:8000/api/v1/storage/results
curl http://localhost:8000/api/v1/storage/summary
```

### Via React Dashboard

1. Open http://localhost:3000
2. Go to "Storage Health Check" tab
3. Enter network range
4. Click "Discover Servers"
5. Click "Execute Health Check"
6. View results in charts and tables

### Via Python Script

```python
from app.discovery.network_scanner import NetworkScanner
from app.health_checks.storage import StorageHealthCheck
from app.processors.storage_results import StorageResultsProcessor

# Discover
scanner = NetworkScanner()
servers = scanner.scan_network('192.168.1.0/24')

# Check
checker = StorageHealthCheck()
results = checker.check_disk_health()

# Process
processor = StorageResultsProcessor()
processor.export_to_csv('results.csv')
```

---

## 🔐 Security

### Credentials Management

1. **Ansible Vault**
   ```bash
   ansible-vault create ansible/vault.yml
   ```

2. **Environment Variables**
   ```bash
   export ANSIBLE_VAULT_PASSWORD_FILE=vault_pass.txt
   ```

3. **SSH Keys**
   - Store securely outside code
   - Use key-based authentication
   - Restrict file permissions (600)

### Network Security

- Restrict Ansible execution to trusted networks
- Use VPN/bastion hosts if needed
- Validate SSL certificates
- Use WinRM over HTTPS (port 5986)

### API Security

- Implement authentication (JWT tokens)
- Use HTTPS in production
- Restrict API access by IP
- Rate limiting on endpoints
- Audit logging

---

## 🛠️ Configuration

### Backend Configuration

```python
# backend/app/core/config.py
STORAGE_DB_PATH = "storage_results.db"
NETWORK_SCANNER_TIMEOUT = 2
NETWORK_SCANNER_THREADS = 20
STORAGE_SCRIPT_REPO = "https://github.com/your-org/scripts.git"
```

### Ansible Configuration

```bash
# ansible.cfg
[defaults]
inventory = inventory.ini
vault_password_file = vault_pass.txt
host_key_checking = False
parallel_execution = 10
```

### Frontend Configuration

```javascript
// frontend/.env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
REACT_APP_POLLING_INTERVAL=5000
```

---

## 📈 Performance

### Network Scanning

- **Single Subnet (256 hosts):** 5-10 minutes
- **Threads:** Adjust based on network speed
- **Timeout:** Lower on reliable networks

```python
scanner = NetworkScanner(timeout=1, threads=50)  # Faster
```

### Ansible Execution

- **10 Servers:** 2-5 minutes
- **100 Servers:** 10-15 minutes
- **Parallel Forks:** Increase for more servers

```bash
ansible-playbook playbook.yml -f 20  # 20 parallel forks
```

### Database

- Create indexes for queries:
  ```sql
  CREATE INDEX idx_server_id ON disk_info(server_id);
  CREATE INDEX idx_status ON health_check_results(check_status);
  ```

---

## 🐛 Troubleshooting

### Network Discovery

```bash
# Test ping
python -c "from app.discovery.network_scanner import NetworkScanner; \
  print(NetworkScanner().ping_host('192.168.1.10'))"

# Test port
python -c "from app.discovery.network_scanner import NetworkScanner; \
  print(NetworkScanner().check_port('192.168.1.10', 22))"
```

### Ansible

```bash
# Validate
ansible-playbook playbook.yml --syntax-check

# Test connectivity
ansible all -i inventory.ini -m ping

# Verbose
ansible-playbook playbook.yml -vvv
```

### Database

```bash
# Check records
sqlite3 storage_results.db "SELECT COUNT(*) FROM servers;"

# View data
sqlite3 storage_results.db "SELECT * FROM health_check_results;"

# Reset
rm storage_results.db
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `STORAGE_QUICK_START.md` | 5-minute quick start guide |
| `STORAGE_DEPLOYMENT_GUIDE.md` | Detailed deployment & integration |
| `README.md` | Project overview (this file) |
| API Docs | `http://localhost:8000/docs` |

---

## 🔄 Scheduling

### Via Cron (Linux)

```bash
# Run every day at 2 AM
0 2 * * * /path/to/orchestrate_storage_checks.py --network-range 192.168.1.0/24

# Run every hour
0 * * * * /path/to/orchestrate_storage_checks.py
```

### Via Windows Task Scheduler

```cmd
# Create scheduled task
schtasks /create /tn "StorageHealthCheck" /tr "python orchestrate_storage_checks.py" /sc hourly
```

### Via APScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(orchestrate, 'cron', hour=2, minute=0)
scheduler.start()
```

---

## 📦 Deployment

### Docker

```bash
# Build and run
docker-compose up -d

# Access dashboard
open http://localhost:3000
```

### Manual

```bash
# Backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend
npm install
npm start
```

### Kubernetes

- Use provided Helm charts
- Configure ingress/service
- Set up persistent volumes for database

---

## 🤝 Contributing

To extend the system:

1. **Add New Health Check Type**
   - Extend `BaseHealthCheck` class
   - Implement check methods
   - Add API endpoints

2. **Enhance Dashboard**
   - Create new React components
   - Add visualization charts
   - Implement filters

3. **Improve Automation**
   - Enhance Ansible playbooks
   - Add error handling
   - Implement retry logic

---

## 📞 Support

- **API Documentation:** http://localhost:8000/docs
- **Logs:** Check `logs/` directory
- **Database:** Inspect `storage_results.db`
- **Issues:** Review troubleshooting section

---

## ✅ Verification Checklist

Before production deployment:

- [ ] Network discovery tested on sample subnet
- [ ] Ansible playbook syntax validated
- [ ] Credentials configured in vault
- [ ] Database initialized and tested
- [ ] API endpoints responding correctly
- [ ] Dashboard displaying results
- [ ] Results exporting to CSV
- [ ] Error handling working
- [ ] Logging configured
- [ ] Security review completed
- [ ] Performance tested
- [ ] Backup strategy defined

---

## 🎓 Key Features

✅ **Automated Discovery** - Find servers without manual inventory  
✅ **Cross-Platform** - Windows, Linux, Storage Arrays  
✅ **Scalable** - Handles 100+ servers efficiently  
✅ **Database-Backed** - Persistent storage of results  
✅ **REST API** - Easy integration with other systems  
✅ **Beautiful Dashboard** - Real-time visualization  
✅ **Playbook-Based** - Leverages Ansible for reliability  
✅ **Comprehensive Reporting** - CSV, JSON, database exports  
✅ **Production-Ready** - Error handling, logging, security  
✅ **Well-Documented** - Complete guides and examples  

---

**Ready to get started?** See `STORAGE_QUICK_START.md` for a 5-minute setup!

