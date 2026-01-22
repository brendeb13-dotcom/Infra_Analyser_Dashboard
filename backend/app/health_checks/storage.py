"""
Storage Health Check Script
Collects storage device information and configuration details
Designed to be executed on target servers via Ansible
"""

import os
import json
import platform
import logging
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class DiskInfo:
    """Data class for disk information"""
    name: str
    device: str
    size_gb: float
    used_gb: float
    available_gb: float
    used_percent: float
    filesystem: str
    mount_point: str


@dataclass
class StorageConfig:
    """Data class for storage configuration"""
    device_name: str
    device_path: str
    size_gb: float
    status: str
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None


class StorageHealthCheck:
    """Check storage device health and configuration"""
    
    def __init__(self):
        """Initialize storage health check"""
        self.os_type = platform.system()
        self.disks = []
        self.storage_configs = []
        self.timestamp = datetime.now().isoformat()
        logger.info(f"Initialized StorageHealthCheck on {self.os_type}")
    
    def get_disk_info_windows(self) -> List[DiskInfo]:
        """
        Get disk information on Windows
        
        Returns:
            List of DiskInfo objects
        """
        disks = []
        try:
            # Use WMI to get logical disk information
            cmd = (
                'wmic logicaldisk get name,size,freespace,filesystem /format:csv'
            )
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split(',')
                if len(parts) >= 4:
                    name = parts[1]
                    size_bytes = int(parts[2]) if parts[2] else 0
                    free_bytes = int(parts[3]) if parts[3] else 0
                    filesystem = parts[4] if len(parts) > 4 else 'Unknown'
                    
                    if size_bytes == 0:
                        continue
                    
                    size_gb = size_bytes / (1024**3)
                    free_gb = free_bytes / (1024**3)
                    used_gb = size_gb - free_gb
                    used_percent = (used_gb / size_gb * 100) if size_gb > 0 else 0
                    
                    disks.append(DiskInfo(
                        name=name,
                        device=f"{name}:\\",
                        size_gb=round(size_gb, 2),
                        used_gb=round(used_gb, 2),
                        available_gb=round(free_gb, 2),
                        used_percent=round(used_percent, 2),
                        filesystem=filesystem,
                        mount_point=f"{name}:\\"
                    ))
        except Exception as e:
            logger.error(f"Failed to get Windows disk info: {str(e)}")
        
        return disks
    
    def get_disk_info_linux(self) -> List[DiskInfo]:
        """
        Get disk information on Linux
        
        Returns:
            List of DiskInfo objects
        """
        disks = []
        try:
            cmd = 'df -BG | tail -n +2'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 6:
                    device = parts[0]
                    size_gb = int(parts[1].rstrip('G'))
                    used_gb = int(parts[2].rstrip('G'))
                    available_gb = int(parts[3].rstrip('G'))
                    used_percent = int(parts[4].rstrip('%'))
                    mount_point = parts[5]
                    
                    # Get filesystem type
                    fs_cmd = f'df -T {device} | tail -n 1'
                    fs_result = subprocess.run(fs_cmd, capture_output=True, text=True, shell=True)
                    filesystem = 'Unknown'
                    if fs_result.stdout:
                        fs_parts = fs_result.stdout.split()
                        if len(fs_parts) >= 2:
                            filesystem = fs_parts[1]
                    
                    disks.append(DiskInfo(
                        name=os.path.basename(device),
                        device=device,
                        size_gb=float(size_gb),
                        used_gb=float(used_gb),
                        available_gb=float(available_gb),
                        used_percent=float(used_percent),
                        filesystem=filesystem,
                        mount_point=mount_point
                    ))
        except Exception as e:
            logger.error(f"Failed to get Linux disk info: {str(e)}")
        
        return disks
    
    def get_storage_config_windows(self) -> List[StorageConfig]:
        """
        Get storage configuration on Windows
        
        Returns:
            List of StorageConfig objects
        """
        configs = []
        try:
            # Get physical disk information
            cmd = (
                'wmic physicaldisk get name,size,status,vendor,model,serialnumber /format:csv'
            )
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split(',')
                if len(parts) >= 2:
                    device_name = parts[1]
                    size_bytes = int(parts[2]) if parts[2] else 0
                    status = parts[3] if len(parts) > 3 else 'Unknown'
                    vendor = parts[4] if len(parts) > 4 else None
                    model = parts[5] if len(parts) > 5 else None
                    serial = parts[6] if len(parts) > 6 else None
                    
                    if size_bytes == 0:
                        continue
                    
                    size_gb = size_bytes / (1024**3)
                    
                    configs.append(StorageConfig(
                        device_name=device_name,
                        device_path=device_name,
                        size_gb=round(size_gb, 2),
                        status=status.strip(),
                        vendor=vendor.strip() if vendor else None,
                        model=model.strip() if model else None,
                        serial_number=serial.strip() if serial else None
                    ))
        except Exception as e:
            logger.error(f"Failed to get Windows storage config: {str(e)}")
        
        return configs
    
    def get_storage_config_linux(self) -> List[StorageConfig]:
        """
        Get storage configuration on Linux
        
        Returns:
            List of StorageConfig objects
        """
        configs = []
        try:
            # Get block device information
            cmd = 'lsblk -b -d -o NAME,SIZE,TYPE,VENDOR,MODEL,SERIAL,STATE'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    device_name = parts[0]
                    size_bytes = int(parts[1]) if parts[1].isdigit() else 0
                    device_type = parts[2] if len(parts) > 2 else 'disk'
                    vendor = parts[3] if len(parts) > 3 else None
                    model = parts[4] if len(parts) > 4 else None
                    serial = parts[5] if len(parts) > 5 else None
                    status = parts[6] if len(parts) > 6 else 'online'
                    
                    if size_bytes == 0 or device_type != 'disk':
                        continue
                    
                    size_gb = size_bytes / (1024**3)
                    
                    configs.append(StorageConfig(
                        device_name=device_name,
                        device_path=f'/dev/{device_name}',
                        size_gb=round(size_gb, 2),
                        status=status.strip(),
                        vendor=vendor.strip() if vendor and vendor != 'N/A' else None,
                        model=model.strip() if model and model != 'N/A' else None,
                        serial_number=serial.strip() if serial and serial != 'N/A' else None
                    ))
        except Exception as e:
            logger.error(f"Failed to get Linux storage config: {str(e)}")
        
        return configs
    
    def check_disk_health(self) -> Dict[str, any]:
        """
        Check overall disk health and return results
        
        Returns:
            Dictionary with health check results
        """
        if self.os_type == 'Windows':
            self.disks = self.get_disk_info_windows()
            self.storage_configs = self.get_storage_config_windows()
        elif self.os_type == 'Linux':
            self.disks = self.get_disk_info_linux()
            self.storage_configs = self.get_storage_config_linux()
        
        # Determine overall health
        issues = []
        for disk in self.disks:
            if disk.used_percent > 90:
                issues.append(f"Critical: {disk.mount_point} is {disk.used_percent}% full")
            elif disk.used_percent > 80:
                issues.append(f"Warning: {disk.mount_point} is {disk.used_percent}% full")
        
        status = 'CRITICAL' if any('Critical' in i for i in issues) else 'WARNING' if issues else 'HEALTHY'
        
        return {
            'status': status,
            'timestamp': self.timestamp,
            'os_type': self.os_type,
            'disk_info': [asdict(d) for d in self.disks],
            'storage_config': [asdict(c) for c in self.storage_configs],
            'total_disks': len(self.disks),
            'total_capacity_gb': sum(d.size_gb for d in self.disks),
            'total_used_gb': sum(d.used_gb for d in self.disks),
            'issues': issues
        }
    
    def export_to_json(self, filename: str) -> None:
        """
        Export results to JSON file
        
        Args:
            filename: Output JSON filename
        """
        try:
            results = self.check_disk_health()
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results exported to {filename}")
        except Exception as e:
            logger.error(f"Failed to export to JSON: {str(e)}")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    checker = StorageHealthCheck()
    results = checker.check_disk_health()
    
    print(json.dumps(results, indent=2))
    
    # Export results
    checker.export_to_json('storage_health_check.json')
