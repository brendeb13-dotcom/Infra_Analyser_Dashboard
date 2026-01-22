# Storage Health Check - Quick Start Guide

## Overview

This guide provides a quick start for deploying and using the storage health check system with Ansible and the Infrastructure Analyzer Dashboard.

## 5-Minute Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install pywinrm paramiko psutil requests pyyaml ansible

# Install Ansible collections
ansible-galaxy collection install community.general community.windows
```

### 2. Configure Network Range

```bash
# Edit orchestration config
cat > storage_config.json << 'EOF'
{
  "network_range": "192.168.1.0/24",
  "scanner_threads": 20,
  "discovery_timeout": 120,
  "ansible_vault_file": "ansible/vault.yml",
  "results_db": "storage_results.db",
  "export_format": "csv"
}
EOF
```

### 3. Create Ansible Vault for Credentials

```bash
# Create vault file with passwords
ansible-vault create ansible/vault.yml

# Add these contents:
---
vault_password: "YourWindowsAdminPassword"
vault_ssh_key: "/path/to/ssh/private/key"

# Then save and exit editor
```

### 4. Run Complete Workflow

```bash
# Execute orchestration script
python orchestrate_storage_checks.py --config storage_config.json

# Or with inline options
python orchestrate_storage_checks.py \
  --network-range 192.168.1.0/24 \
  --vault-file ansible/vault.yml
```

## Detailed Workflow Steps

### Step 1: Network Discovery (5-10 minutes)

Discovers all servers in the network and identifies their OS types.

```bash
# Using the orchestrator
python orchestrate_storage_checks.py --skip inventory playbook processing export

# Or directly
python -c "
from app.discovery.network_scanner import NetworkScanner

scanner = NetworkScanner(timeout=2, threads=20)
servers = scanner.scan_network('192.168.1.0/24')
scanner.save_to_json('discovered_servers.json')
scanner.save_to_csv('discovered_servers.csv')

print(f'Found {len(servers)} servers')
for server in servers:
    print(f'  {server.hostname} ({server.ip_address}) - {server.os_type}')
"
```

**Output:**
- `discovered_servers.json` - Full server details
- `discovered_servers.csv` - Server list in CSV format

### Step 2: Generate Ansible Inventory

Converts discovered servers into Ansible inventory format.

```bash
# Generate inventory
python ansible/generate_inventory.py \
  --input discovered_servers.json \
  --output inventory.ini \
  --format ini

# Verify inventory
ansible-inventory -i inventory.ini --list
ansible all -i inventory.ini -m ping
```

**Output:**
- `inventory.ini` - Ansible inventory with Windows and Linux groups

### Step 3: Deploy and Execute Playbook

Deploys scripts to servers and executes health checks.

```bash
# Run playbook
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  --vault-password-file ansible/vault_pass.txt

# Or with prompt
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  --ask-vault-pass
```

**What it does:**
1. Clones scripts from GitHub
2. Installs Python dependencies
3. Executes storage health checks
4. Collects results from each server

### Step 4: Process Results

Imports results into database and generates reports.

```bash
# Process results
python -c "
from app.processors.storage_results import StorageResultsProcessor

processor = StorageResultsProcessor('storage_results.db')

# Get summary
summary = processor.get_summary()
print('Storage Health Summary:')
print(f'  Total Servers: {summary[\"total_servers\"]}')
print(f'  Total Capacity: {summary[\"total_capacity_gb\"]} GB')
print(f'  Total Used: {summary[\"total_used_gb\"]} GB')
print(f'  Usage: {summary[\"usage_percent\"]}%')
print(f'  Critical Issues: {summary[\"critical_issues_count\"]}')

# Export to CSV
processor.export_to_csv('storage_results.csv')
processor.close()
"
```

**Output:**
- `storage_results.db` - SQLite database with all results
- `storage_results.csv` - CSV export of results

### Step 5: View in Dashboard

```bash
# Access the dashboard
open http://localhost:3000
# Navigate to Storage Health Check tab
# View servers, capacity, usage, and issues
```

## API Usage Examples

### Via cURL

```bash
# 1. Discover servers
curl -X POST http://localhost:8000/api/v1/storage/discover \
  -H "Content-Type: application/json" \
  -d '{
    "network_range": "192.168.1.0/24",
    "ports": [22, 3389, 5985, 445]
  }'

# Check discovery status
curl http://localhost:8000/api/v1/storage/discovery/{discovery_id}

# 2. Execute health checks
curl -X POST http://localhost:8000/api/v1/storage/health-check \
  -H "Content-Type: application/json" \
  -d '{
    "servers": ["192.168.1.10", "192.168.1.20"],
    "check_types": ["disk", "config", "health"]
  }'

# Check health check status
curl http://localhost:8000/api/v1/storage/health-check/{check_id}

# 3. Get results
curl http://localhost:8000/api/v1/storage/results

# Get results with status filter
curl "http://localhost:8000/api/v1/storage/results?status_filter=CRITICAL"

# 4. Get summary
curl http://localhost:8000/api/v1/storage/summary

# 5. Export results
curl -X POST http://localhost:8000/api/v1/storage/export \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}' \
  -o storage_results.csv
```

### Via Python

```python
from app.discovery.network_scanner import NetworkScanner
from app.health_checks.storage import StorageHealthCheck
from app.processors.storage_results import StorageResultsProcessor

# 1. Discover
scanner = NetworkScanner()
servers = scanner.scan_network('192.168.1.0/24')

# 2. Check (on local system)
checker = StorageHealthCheck()
results = checker.check_disk_health()
print(results['status'])

# 3. Process and store
processor = StorageResultsProcessor()
for server in servers:
    processor.process_json_result(server.hostname, f'{server.hostname}_results.json')

# 4. Get summary
summary = processor.get_summary()
print(f"Total: {summary['total_servers']} servers")
```

## Using the Orchestration Script

### One-Command Complete Workflow

```bash
# Run all steps
python orchestrate_storage_checks.py

# Run all steps with custom network
python orchestrate_storage_checks.py --network-range 10.0.0.0/16

# Dry run (no actual changes)
python orchestrate_storage_checks.py --dry-run

# Skip certain steps
python orchestrate_storage_checks.py --skip playbook export

# Use custom config
python orchestrate_storage_checks.py --config custom_config.json
```

### Custom Configuration

```json
{
  "network_range": "192.168.1.0/24",
  "discovery_timeout": 120,
  "scanner_threads": 20,
  "ansible_vault_file": "ansible/vault.yml",
  "results_db": "storage_results.db",
  "export_format": "csv",
  "dry_run": false,
  "parallel_execution": true
}
```

## Dashboard Integration

### View in React Dashboard

1. Start the dashboard:
   ```bash
   cd frontend && npm start
   ```

2. Navigate to **Storage Health Check** tab

3. Features:
   - Discover servers in network
   - Execute health checks on discovered servers
   - View real-time status with progress
   - See detailed results in tables and charts
   - Export results to CSV

### API Integration Example

```javascript
// React component example
import React, { useState } from 'react';
import { storageAPI } from '../services/api';

export function StorageCheck() {
  const [results, setResults] = useState(null);

  const handleDiscover = async () => {
    const response = await storageAPI.discover({
      network_range: '192.168.1.0/24'
    });
    console.log(response);
  };

  const handleHealthCheck = async () => {
    const response = await storageAPI.executeHealthCheck({
      servers: ['192.168.1.10', '192.168.1.20'],
      check_types: ['disk', 'config', 'health']
    });
    console.log(response);
  };

  const handleGetResults = async () => {
    const data = await storageAPI.getResults();
    setResults(data);
  };

  return (
    <div>
      <button onClick={handleDiscover}>Discover</button>
      <button onClick={handleHealthCheck}>Health Check</button>
      <button onClick={handleGetResults}>Get Results</button>
      {results && <pre>{JSON.stringify(results, null, 2)}</pre>}
    </div>
  );
}
```

## Troubleshooting

### Network Discovery Issues

```bash
# Test ping
python -c "
from app.discovery.network_scanner import NetworkScanner
scanner = NetworkScanner()
print(scanner.ping_host('192.168.1.10'))
"

# Test SSH
python -c "
from app.discovery.network_scanner import NetworkScanner
scanner = NetworkScanner()
print(scanner.check_port('192.168.1.10', 22))
"

# Test WinRM
python -c "
from app.discovery.network_scanner import NetworkScanner
scanner = NetworkScanner()
print(scanner.check_port('192.168.1.10', 5985))
"
```

### Ansible Playbook Issues

```bash
# Validate playbook
ansible-playbook ansible/storage_health_check.yml --syntax-check

# Test connectivity
ansible all -i inventory.ini -m ping

# Run with verbose output
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  -vvv --vault-password-file ansible/vault_pass.txt
```

### Database Issues

```bash
# Check records
sqlite3 storage_results.db "SELECT COUNT(*) FROM servers;"

# View servers
sqlite3 storage_results.db "SELECT hostname, ip_address FROM servers;"

# Clear database
rm storage_results.db
```

## Performance Tips

1. **Network Scanning**
   - Increase `scanner_threads` for faster scanning
   - Reduce `timeout` if network is reliable
   ```python
   scanner = NetworkScanner(timeout=1, threads=50)
   ```

2. **Ansible Execution**
   - Use parallel forks for faster execution
   ```bash
   ansible-playbook -i inventory.ini playbook.yml -f 20
   ```

3. **Database Queries**
   - Create indexes for large datasets
   ```sql
   CREATE INDEX idx_server_status ON health_check_results(check_status);
   CREATE INDEX idx_check_timestamp ON health_check_results(check_timestamp);
   ```

## Next Steps

1. **Configure Credentials**
   - Set up Ansible vault with real passwords
   - Configure SSH keys for Linux systems

2. **Test Environment**
   - Run discovery on test network
   - Validate playbook execution
   - Review results

3. **Production Deployment**
   - Set up database backups
   - Configure monitoring
   - Enable API authentication
   - Deploy dashboard with HTTPS

4. **Automation**
   - Schedule orchestration script via cron
   - Set up webhooks for notifications
   - Configure alerting for critical issues

## Support

- Check logs: `logs/` directory
- Review database: `sqlite3 storage_results.db`
- See detailed guide: `STORAGE_DEPLOYMENT_GUIDE.md`
- API docs: `http://localhost:8000/docs`

