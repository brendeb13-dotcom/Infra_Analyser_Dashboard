# Supported Capabilities and Health Checks

## Overview
This document describes all supported infrastructure capabilities and their respective health checks.

## 1. Windows Server Health Check

**Version:** 1.2  
**Supported OS:** Windows Server 2008 R2, 2012, 2012 R2, 2016, 2019, 2022

### Available Checks

#### 1.1 Availability Check
- **Description:** Verifies server is online and accessible
- **Method:** WinRM connectivity test
- **Status Indicators:**
  - HEALTHY: Server responds to ping
  - CRITICAL: Server is unreachable

#### 1.2 Disk Capacity Check
- **Description:** Monitors disk usage across all drives
- **Metrics:**
  - Used space percentage per drive
  - Free space in GB
  - Drive health status
- **Configuration:**
  - `disk_threshold_percent`: Warning threshold (default: 80%)
  - `exclude_drives`: Drives to exclude (e.g., removable media)
- **Status Indicators:**
  - HEALTHY: All drives < threshold
  - WARNING: Drive between 80-95%
  - CRITICAL: Drive > 95%

#### 1.3 Memory Utilization Check
- **Description:** Monitors RAM usage
- **Metrics:**
  - Total memory
  - Available memory
  - Used memory percentage
  - Page file usage
- **Configuration:**
  - `memory_threshold_percent`: Warning threshold (default: 85%)
- **Status Indicators:**
  - HEALTHY: Usage < 85%
  - WARNING: Usage 85-95%
  - CRITICAL: Usage > 95%

#### 1.4 CPU Usage Check
- **Description:** Monitors CPU utilization
- **Metrics:**
  - Current CPU usage %
  - Number of cores
  - Processor frequency
  - Context switches
- **Configuration:**
  - `cpu_threshold_percent`: Warning threshold (default: 80%)
  - `sample_duration_seconds`: Sampling period (default: 5)
- **Status Indicators:**
  - HEALTHY: Usage < 80%
  - WARNING: Usage 80-95%
  - CRITICAL: Usage > 95%

#### 1.5 Services Status Check
- **Description:** Monitors critical Windows services
- **Default Services Checked:**
  - Windows Update
  - BITS (Background Intelligent Transfer Service)
  - WinRM (Windows Remote Management)
  - Remote Desktop Services
  - Network services
- **Configuration:**
  - `critical_services`: List of services to monitor
  - `expected_state`: Desired service state (Running/Stopped)
- **Status Indicators:**
  - HEALTHY: All services in expected state
  - WARNING: Non-critical service stopped
  - CRITICAL: Critical service stopped

#### 1.6 Uptime Check
- **Description:** Monitors server uptime and stability
- **Metrics:**
  - Days since last reboot
  - Total uptime
  - Last reboot timestamp
  - Reboot history
- **Configuration:**
  - `min_uptime_days`: Minimum expected uptime (default: 7)
  - `check_reboot_reason`: Include reboot reason
- **Status Indicators:**
  - HEALTHY: Uptime > minimum
  - WARNING: Uptime near minimum
  - CRITICAL: Recent unexpected reboot

#### 1.7 Event Log Analysis
- **Description:** Analyzes Windows Event Logs for errors
- **Events Analyzed:**
  - System errors
  - Critical events
  - Application crashes
  - Service failures
- **Configuration:**
  - `hours_to_check`: Hours of logs to analyze (default: 24)
  - `error_threshold`: Max allowed errors
- **Status Indicators:**
  - HEALTHY: No critical errors
  - WARNING: Minor errors found
  - CRITICAL: Multiple critical errors

### Configuration Example
```json
{
  "capability": "windows_server",
  "account_name": "PRODUCTION",
  "servers": ["SERVER1", "SERVER2"],
  "checks": {
    "availability": true,
    "disk_capacity": true,
    "disk_threshold_percent": 80,
    "memory": true,
    "memory_threshold_percent": 85,
    "cpu": true,
    "cpu_threshold_percent": 80,
    "services": true,
    "critical_services": ["WinRM", "BITS"],
    "uptime": true,
    "min_uptime_days": 7,
    "event_log": true,
    "event_log_hours": 24
  }
}
```

---

## 2. Storage Systems Health Check

**Version:** 1.0  
**Supported Arrays:** EMC Symmetrix, EMC VMAX, HPE 3PAR

### Available Checks

#### 2.1 Capacity Monitoring
- **Metrics:**
  - Total capacity
  - Used capacity
  - Available capacity
  - Capacity utilization %
  - Thin provisioning status
- **Status Indicators:**
  - HEALTHY: Utilization < 80%
  - WARNING: Utilization 80-90%
  - CRITICAL: Utilization > 90%

#### 2.2 Performance Monitoring
- **Metrics:**
  - I/O operations per second
  - Read/Write latency
  - Throughput (MB/s)
  - Cache hit ratio
- **Status Indicators:**
  - HEALTHY: Latency within baseline
  - WARNING: 20% above baseline
  - CRITICAL: 50% above baseline

#### 2.3 Array Health
- **Checks:**
  - Controller status
  - Port status
  - Drive status
  - Power supply status
  - Fan status
  - Temperature sensors
- **Status Indicators:**
  - HEALTHY: All components operational
  - WARNING: Degraded component
  - CRITICAL: Failed component

#### 2.4 RAID Status
- **Checks:**
  - RAID set status
  - Parity status
  - Rebuild progress
  - Failed drives
- **Status Indicators:**
  - HEALTHY: All RAID healthy
  - WARNING: Degraded RAID set
  - CRITICAL: RAID failure risk

---

## 3. Backup Systems Health Check

**Version:** 1.0  
**Supported Systems:** NetBackup, Backup Exec, ArcServe, DataProtector

### Available Checks

#### 3.1 Backup Job Status
- **Metrics:**
  - Job completion status
  - Duration vs. baseline
  - Data size backed up
  - Failed/partial backups
  - Success rate
- **Configuration:**
  - `min_success_rate`: Minimum success % (default: 95%)
  - `max_runtime_hours`: Maximum job duration
- **Status Indicators:**
  - HEALTHY: Success rate > threshold
  - WARNING: Success rate 90-95%
  - CRITICAL: Success rate < 90%

#### 3.2 Backup Capacity
- **Metrics:**
  - Storage pool utilization
  - Tape library capacity
  - Disk storage usage
  - Growth rate
- **Status Indicators:**
  - HEALTHY: Utilization < 80%
  - WARNING: Utilization 80-90%
  - CRITICAL: Utilization > 90%

#### 3.3 Backup Devices
- **Checks:**
  - Tape drive status
  - Library status
  - Storage pool health
  - Device availability
- **Status Indicators:**
  - HEALTHY: All devices operational
  - WARNING: Device degraded
  - CRITICAL: Device failed

#### 3.4 Backup Database
- **Checks:**
  - Catalog database health
  - Database backup status
  - Index status
  - Storage size
- **Status Indicators:**
  - HEALTHY: Database healthy
  - WARNING: Database warnings
  - CRITICAL: Database errors

---

## 4. Virtualization Health Check

**Version:** 1.0  
**Supported Platforms:** HyperV, VMware vSphere, KVM

### Available Checks

#### 4.1 Host Status
- **Checks:**
  - Host connectivity
  - Resource utilization
  - Memory available
  - CPU load
  - Disk space
- **Status Indicators:**
  - HEALTHY: All metrics within normal
  - WARNING: Resource constrained
  - CRITICAL: Resource critical

#### 4.2 Virtual Machine Status
- **Checks:**
  - VM power state
  - CPU/Memory allocation
  - Disk space usage
  - Network connectivity
  - Guest OS health
- **Status Indicators:**
  - HEALTHY: All VMs operational
  - WARNING: VM warnings
  - CRITICAL: VM failed

#### 4.3 Cluster Status
- **Checks:**
  - Cluster connectivity
  - Node status
  - Quorum status
  - Shared storage status
- **Status Indicators:**
  - HEALTHY: Cluster operational
  - WARNING: Cluster degraded
  - CRITICAL: Cluster unhealthy

---

## 5. Active Directory Health Check

**Version:** 1.0  
**Supported Versions:** Windows Server 2008 R2, 2012, 2016, 2019, 2022

### Available Checks

#### 5.1 Replication Status
- **Checks:**
  - DC-to-DC replication
  - Replication latency
  - Failed replications
  - SYSVOL replication
- **Status Indicators:**
  - HEALTHY: Replication successful
  - WARNING: Replication delays
  - CRITICAL: Replication failures

#### 5.2 Domain Controller Health
- **Checks:**
  - DC availability
  - Kerberos service
  - LDAP availability
  - DNS resolution
  - Time synchronization
- **Status Indicators:**
  - HEALTHY: All services operational
  - WARNING: Service warnings
  - CRITICAL: Service failure

#### 5.3 Forest/Domain Health
- **Checks:**
  - Forest functional level
  - Domain functional level
  - Schema status
  - Trust relationships
  - Global Catalog availability
- **Status Indicators:**
  - HEALTHY: Forest healthy
  - WARNING: Functional level issues
  - CRITICAL: Forest unhealthy

---

## 6. Exchange Server Health Check

**Version:** 1.0  
**Supported Versions:** 2010, 2013, 2016, 2019

### Available Checks

#### 6.1 Database Availability Group (DAG)
- **Checks:**
  - DAG status
  - Database copies
  - Replication health
  - Failover readiness
- **Status Indicators:**
  - HEALTHY: DAG healthy
  - WARNING: Copy degraded
  - CRITICAL: DAG failure risk

#### 6.2 Mailbox Database Health
- **Checks:**
  - Database availability
  - Database size
  - Disk space
  - Corruption status
- **Status Indicators:**
  - HEALTHY: Database healthy
  - WARNING: Database warnings
  - CRITICAL: Database issues

#### 6.3 Exchange Services
- **Checks:**
  - Mailbox service
  - Client Access service
  - Transport service
  - Hub Transport
  - OWA availability
- **Status Indicators:**
  - HEALTHY: All services running
  - WARNING: Service degraded
  - CRITICAL: Service failed

---

## Health Check Execution

### Scheduling
Health checks can be:
- Executed on-demand via API
- Scheduled via cron (Linux) or Task Scheduler (Windows)
- Triggered by events
- Run in parallel across multiple servers

### Timeout Settings
- **Windows Server:** 5 minutes per server
- **Storage:** 10 minutes
- **Backup:** 15 minutes (job-dependent)
- **Virtualization:** 10 minutes
- **Active Directory:** 5 minutes
- **Exchange:** 10 minutes

### Concurrency
- Default: 5 concurrent checks
- Maximum: 20 concurrent checks
- Configurable via `MAX_CONCURRENT_CHECKS`

### Error Handling
- Transient errors: Retry up to 3 times
- Permanent errors: Fail immediately
- Partial results: Continue with available servers
- Network failures: Mark as unknown status

### Result Retention
- Default: 30 days
- Configurable via `REPORT_RETENTION_DAYS`
- Archived results: Compress and move to cold storage

---

## Adding New Capabilities

To add a new health check capability:

1. Create new check class in `backend/app/health_checks/{capability}.py`
2. Extend `BaseHealthCheck`
3. Implement `validate_config()` and `execute()` methods
4. Add capability to `CAPABILITIES` dict in `backend/app/api/capabilities.py`
5. Update this documentation
6. Add tests for new capability
7. Deploy and test

---

## Best Practices

1. **Configure thresholds appropriately** for your infrastructure
2. **Start with basic checks** before enabling all checks
3. **Monitor baseline metrics** to set realistic thresholds
4. **Schedule checks during low-load periods** if possible
5. **Set up alerts** for critical status changes
6. **Review health reports regularly** for trends
7. **Maintain server inventory** accurately
8. **Test configurations** before production deployment
