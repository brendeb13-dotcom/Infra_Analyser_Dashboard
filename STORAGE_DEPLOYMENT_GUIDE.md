# Storage Health Check - Deployment & Integration Guide

## Overview

This guide explains how to deploy and use the storage health check system integrated with the Infrastructure Analyzer Dashboard. The system includes:

1. **Network Discovery** - Python script to discover servers in a network
2. **Storage Health Checks** - Python script to gather storage information
3. **Ansible Playbooks** - Automated deployment and execution
4. **Results Processing** - Database storage and aggregation
5. **API Integration** - REST endpoints for dashboard integration
6. **React Dashboard** - Visual display of storage metrics

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard                          │
│              (Storage Capability View)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼─────┐  ┌────▼─────┐  ┌───▼──────┐
   │ Discovery │  │ Health   │  │ Results  │
   │   API     │  │ Check    │  │   API    │
   │           │  │   API    │  │          │
   └────┬─────┘  └────┬─────┘  └───┬──────┘
        │             │             │
        │    FastAPI Backend        │
        │             │             │
   ┌────▼─────┬──────▼─────┬───────▼──────┐
   │ Network  │  Storage   │  Results     │
   │ Scanner  │  Health    │  Processor   │
   │          │  Check     │  (Database)  │
   └────┬─────┴──────┬─────┴───────┬──────┘
        │            │             │
        │  Ansible Playbook       │
        │            │             │
   ┌────▼────────────▼─────────────▼──────┐
   │       Target Servers (On-Prem)       │
   │  Windows  │  Linux  │  Storage Arrays│
   └──────────────────────────────────────┘
```

---

## Prerequisites

### Backend Requirements

```bash
# Python packages (add to requirements.txt)
pip install pywinrm paramiko psutil requests pyyaml ansible
```

### Ansible Requirements

```bash
# Install Ansible
pip install ansible

# Install required collections
ansible-galaxy collection install community.general
ansible-galaxy collection install community.windows
```

### Network Requirements

- Network access to target servers
- SSH (port 22) for Linux systems
- WinRM (port 5985/5986) for Windows systems
- Git access for downloading scripts

---

## Deployment Steps

### Step 1: Network Discovery

#### Execute Network Scanner

```python
# Using network_scanner.py
from app.discovery.network_scanner import NetworkScanner

scanner = NetworkScanner(timeout=2, threads=20)
servers = scanner.scan_network('192.168.1.0/24')
scanner.save_to_csv('discovered_servers.csv')
scanner.save_to_json('discovered_servers.json')
```

#### Via API

```bash
curl -X POST http://localhost:8000/api/v1/storage/discover \
  -H "Content-Type: application/json" \
  -d '{
    "network_range": "192.168.1.0/24",
    "ports": [22, 3389, 5985, 445]
  }'

# Response:
# {
#   "discovery_id": "1234567890.123",
#   "status": "RUNNING",
#   "message": "Discovering servers in 192.168.1.0/24"
# }
```

Check discovery status:

```bash
curl http://localhost:8000/api/v1/storage/discovery/1234567890.123
```

### Step 2: Generate Ansible Inventory

```bash
# From discovered servers
python ansible/generate_inventory.py \
  --input discovered_servers.json \
  --output inventory.ini \
  --format ini

# Output example:
# [windows]
# server1 ansible_host=192.168.1.10 ansible_port=5985 ansible_connection=winrm
#
# [linux]
# server2 ansible_host=192.168.1.20 ansible_port=22 ansible_connection=ssh
```

### Step 3: Create Ansible Vault for Credentials

```bash
# Create vault file
ansible-vault create ansible/vault.yml

# Add credentials:
---
vault_password: "Administrator_Password"
vault_ssh_key: "/path/to/ssh/key"
vault_storage_user: "storage_admin"
vault_storage_password: "storage_password"
```

### Step 4: Deploy and Execute Health Checks via Ansible

```bash
# Execute playbook
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  --ask-vault-pass

# Or with vault password file
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  --vault-password-file=/path/to/vault_pass.txt
```

### Step 5: Process Results

```python
from app.processors.storage_results import StorageResultsProcessor

processor = StorageResultsProcessor('storage_results.db')

# Process individual results
processor.process_json_result('server1', 'server1_storage_check.json')

# Get summary
summary = processor.get_summary()
print(f"Total Servers: {summary['total_servers']}")
print(f"Total Capacity: {summary['total_capacity_gb']} GB")
print(f"Usage: {summary['usage_percent']}%")

# Export to CSV
processor.export_to_csv('storage_results_summary.csv')

processor.close()
```

### Step 6: Execute via Dashboard API

```bash
# Start health check on discovered servers
curl -X POST http://localhost:8000/api/v1/storage/health-check \
  -H "Content-Type: application/json" \
  -d '{
    "servers": ["192.168.1.10", "192.168.1.20"],
    "check_types": ["disk", "config", "health"]
  }'

# Response:
# {
#   "check_id": "1234567890.456",
#   "status": "RUNNING",
#   "servers_count": 2,
#   "message": "Storage health check started"
# }

# Check status
curl http://localhost:8000/api/v1/storage/health-check/1234567890.456

# Get results
curl http://localhost:8000/api/v1/storage/results

# Get summary
curl http://localhost:8000/api/v1/storage/summary

# Export to CSV
curl -X POST http://localhost:8000/api/v1/storage/export \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}' \
  -o storage_results.csv
```

---

## Integration with React Dashboard

### 1. Update React Storage Component

Create `frontend/src/components/StorageHealthCheck.jsx`:

```jsx
import React, { useState, useEffect } from 'react';
import {
  Card, CardContent, CardHeader, CardTitle,
  LinearProgress, Button, Alert, Table, TableBody, TableCell, TableHead, TableRow,
  Paper, Grid, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Chip
} from '@mui/material';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { storageAPI } from '../services/api';

export default function StorageHealthCheck() {
  const [discovery, setDiscovery] = useState(null);
  const [healthCheck, setHealthCheck] = useState(null);
  const [results, setResults] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [networkRange, setNetworkRange] = useState('192.168.1.0/24');
  const [discoveryDialog, setDiscoveryDialog] = useState(false);

  // Discover servers
  const handleDiscovery = async () => {
    try {
      setLoading(true);
      const response = await storageAPI.discover({
        network_range: networkRange
      });
      setDiscovery(response);
      setDiscoveryDialog(true);
    } catch (error) {
      console.error('Discovery failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Poll discovery status
  useEffect(() => {
    if (!discovery || discovery.status !== 'RUNNING') return;

    const interval = setInterval(async () => {
      try {
        const status = await storageAPI.getDiscoveryStatus(discovery.discovery_id);
        setDiscovery(status);
      } catch (error) {
        console.error('Poll failed:', error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [discovery]);

  // Execute health check
  const handleHealthCheck = async () => {
    try {
      setLoading(true);
      const servers = discovery.servers.map(s => s.ip_address);
      const response = await storageAPI.executeHealthCheck({
        servers: servers,
        check_types: ['disk', 'config', 'health']
      });
      setHealthCheck(response);
    } catch (error) {
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Poll health check status
  useEffect(() => {
    if (!healthCheck || healthCheck.status !== 'RUNNING') return;

    const interval = setInterval(async () => {
      try {
        const status = await storageAPI.getHealthCheckStatus(healthCheck.check_id);
        setHealthCheck(status);
      } catch (error) {
        console.error('Poll failed:', error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [healthCheck]);

  // Get results and summary
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const [resultsData, summaryData] = await Promise.all([
          storageAPI.getResults(),
          storageAPI.getSummary()
        ]);
        setResults(resultsData);
        setSummary(summaryData);
      } catch (error) {
        console.error('Failed to fetch results:', error);
      }
    };

    if (healthCheck?.status === 'COMPLETED') {
      fetchResults();
    }
  }, [healthCheck?.status]);

  return (
    <div>
      {/* Discovery Section */}
      <Card sx={{ mb: 2 }}>
        <CardHeader title="Network Discovery" />
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField
                fullWidth
                label="Network Range (CIDR)"
                value={networkRange}
                onChange={(e) => setNetworkRange(e.target.value)}
                placeholder="192.168.1.0/24"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleDiscovery}
                disabled={loading}
              >
                Discover Servers
              </Button>
            </Grid>
          </Grid>

          {discovery && (
            <Paper sx={{ p: 2, mt: 2 }}>
              <div>
                <strong>Status:</strong> {discovery.status}
                {discovery.status === 'RUNNING' && <LinearProgress sx={{ mt: 1 }} />}
              </div>
              {discovery.servers && (
                <div sx={{ mt: 2 }}>
                  <strong>Discovered Servers: {discovery.servers.length}</strong>
                  <Table size="small" sx={{ mt: 1 }}>
                    <TableHead>
                      <TableRow>
                        <TableCell>Hostname</TableCell>
                        <TableCell>IP Address</TableCell>
                        <TableCell>OS Type</TableCell>
                        <TableCell>Port</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {discovery.servers.map((server, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{server.hostname}</TableCell>
                          <TableCell>{server.ip_address}</TableCell>
                          <TableCell>{server.os_type}</TableCell>
                          <TableCell>{server.port}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </Paper>
          )}
        </CardContent>
      </Card>

      {/* Health Check Section */}
      {discovery?.status === 'COMPLETED' && (
        <Card sx={{ mb: 2 }}>
          <CardHeader title="Storage Health Check" />
          <CardContent>
            <Button
              variant="contained"
              color="success"
              onClick={handleHealthCheck}
              disabled={loading || !discovery.servers?.length}
            >
              Execute Health Check
            </Button>

            {healthCheck && (
              <Paper sx={{ p: 2, mt: 2 }}>
                <div>
                  <strong>Status:</strong> {healthCheck.status}
                  {healthCheck.status === 'RUNNING' && (
                    <>
                      <LinearProgress sx={{ mt: 1 }} />
                      <div sx={{ mt: 1 }}>
                        Completed: {healthCheck.completed_count} / {healthCheck.servers_count}
                      </div>
                    </>
                  )}
                </div>
              </Paper>
            )}
          </CardContent>
        </Card>
      )}

      {/* Results Section */}
      {summary && (
        <Grid container spacing={2}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <CardTitle>Total Servers</CardTitle>
                <div style={{ fontSize: '2em', fontWeight: 'bold' }}>
                  {summary.total_servers}
                </div>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <CardTitle>Total Capacity</CardTitle>
                <div style={{ fontSize: '2em', fontWeight: 'bold' }}>
                  {summary.total_capacity_gb} GB
                </div>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <CardTitle>Usage</CardTitle>
                <div style={{ fontSize: '2em', fontWeight: 'bold' }}>
                  {summary.usage_percent}%
                </div>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <CardTitle>Critical Issues</CardTitle>
                <div style={{ fontSize: '2em', fontWeight: 'bold', color: 'red' }}>
                  {summary.critical_issues_count}
                </div>
              </CardContent>
            </Card>
          </Grid>

          {/* Status Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Status Distribution" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(summary.status_distribution).map(([status, count]) => ({
                        name: status,
                        value: count
                      }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Results Table */}
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Detailed Results" />
              <CardContent>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Hostname</TableCell>
                      <TableCell>IP Address</TableCell>
                      <TableCell>OS Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Capacity (GB)</TableCell>
                      <TableCell>Used (GB)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results?.results?.map((result, idx) => (
                      <TableRow key={idx}>
                        <TableCell>{result.hostname}</TableCell>
                        <TableCell>{result.ip_address}</TableCell>
                        <TableCell>{result.os_type}</TableCell>
                        <TableCell>
                          <Chip
                            label={result.check_status}
                            color={
                              result.check_status === 'HEALTHY' ? 'success' :
                              result.check_status === 'WARNING' ? 'warning' :
                              'error'
                            }
                          />
                        </TableCell>
                        <TableCell>{result.total_capacity_gb}</TableCell>
                        <TableCell>{result.total_used_gb}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </div>
  );
}
```

### 2. Update API Client

Add to `frontend/src/services/api.js`:

```javascript
// Storage API
export const storageAPI = {
  discover: (config) => apiClient.post('/storage/discover', config),
  getDiscoveryStatus: (discoveryId) => apiClient.get(`/storage/discovery/${discoveryId}`),
  executeHealthCheck: (config) => apiClient.post('/storage/health-check', config),
  getHealthCheckStatus: (checkId) => apiClient.get(`/storage/health-check/${checkId}`),
  getResults: (statusFilter = null) =>
    apiClient.get('/storage/results', { params: { status_filter: statusFilter } }),
  getSummary: () => apiClient.get('/storage/summary'),
  exportResults: (format = 'csv') =>
    apiClient.post('/storage/export', { format }, { responseType: 'blob' })
};
```

---

## Environment Configuration

Update `backend/.env`:

```bash
# Storage Health Check Configuration
STORAGE_DB_PATH=storage_results.db
STORAGE_SCRIPT_REPO=https://github.com/your-org/infra-analyzer-scripts.git
STORAGE_SCRIPT_BRANCH=main
STORAGE_SCRIPTS_DIR=/tmp/infra-analyzer-scripts

# Ansible Configuration
ANSIBLE_INVENTORY=inventory.ini
ANSIBLE_VAULT_FILE=ansible/vault.yml
ANSIBLE_BECOME_USER=root
ANSIBLE_BECOME_METHOD=sudo

# Network Discovery
NETWORK_SCANNER_TIMEOUT=2
NETWORK_SCANNER_THREADS=20
NETWORK_SCANNER_PORTS=22,3389,5985,445
```

---

## Running the Complete Workflow

### Option 1: Automated End-to-End

```bash
# 1. Discover servers
curl -X POST http://localhost:8000/api/v1/storage/discover \
  -H "Content-Type: application/json" \
  -d '{"network_range": "192.168.1.0/24"}'

# 2. Generate inventory
python ansible/generate_inventory.py \
  --input discovered_servers.json \
  --output inventory.ini

# 3. Run Ansible playbook
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  --vault-password-file=vault_pass.txt

# 4. Process results
python -c "
from app.processors.storage_results import StorageResultsProcessor
processor = StorageResultsProcessor()
processor.process_json_result('server1', 'server1_storage_check.json')
summary = processor.get_summary()
print(summary)
processor.close()
"

# 5. View in Dashboard
# Open: http://localhost:3000 → Storage Health Check
```

### Option 2: Via Dashboard UI

1. Open Storage Health Check page
2. Enter network range (e.g., 192.168.1.0/24)
3. Click "Discover Servers" → View discovered servers
4. Click "Execute Health Check" → Wait for completion
5. View results in charts and tables
6. Export to CSV if needed

---

## Troubleshooting

### Network Discovery Issues

```bash
# Test ping to single host
python -c "
from app.discovery.network_scanner import NetworkScanner
scanner = NetworkScanner()
print(scanner.ping_host('192.168.1.10'))
"

# Test port connectivity
python -c "
from app.discovery.network_scanner import NetworkScanner
scanner = NetworkScanner()
print(scanner.check_port('192.168.1.10', 22))
"
```

### Ansible Playbook Issues

```bash
# Validate playbook syntax
ansible-playbook ansible/storage_health_check.yml --syntax-check

# Run with verbose output
ansible-playbook \
  -i inventory.ini \
  ansible/storage_health_check.yml \
  -vvv

# Test connectivity
ansible all -i inventory.ini -m ping
```

### Database Issues

```bash
# Check database
sqlite3 storage_results.db "SELECT COUNT(*) FROM servers;"

# Clear database
rm storage_results.db
```

---

## Performance Considerations

- **Network Scanning**: Adjust `threads` parameter in `NetworkScanner` (default: 20)
- **Health Checks**: Use Ansible for parallel execution across servers
- **Database**: Create indexes on `server_id` and `check_timestamp` for large datasets
- **API Polling**: Adjust polling interval in React component (default: 5 seconds)

---

## Security Notes

1. **Credentials**: Store in Ansible vault, never in code
2. **Network Access**: Restrict Ansible execution to trusted networks
3. **Database**: Use file permissions or database encryption
4. **Scripts**: Download from trusted Git repositories only
5. **API**: Implement authentication/authorization in production

---

## Next Steps

1. Configure target server credentials in vault
2. Test network discovery on small subnet
3. Validate Ansible playbook execution
4. Set up database backups
5. Configure dashboard authentication
6. Deploy to production with monitoring

