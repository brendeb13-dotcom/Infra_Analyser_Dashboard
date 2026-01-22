"""
Network Server Discovery Script
Scans network ranges and discovers available servers
"""

import ipaddress
import socket
import threading
import logging
import json
import csv
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import subprocess
import platform

logger = logging.getLogger(__name__)


@dataclass
class ServerInfo:
    """Data class for server information"""
    ip_address: str
    hostname: str
    port: int
    os_type: str
    is_reachable: bool
    timestamp: str
    vendor: Optional[str] = None
    model: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'port': self.port,
            'os_type': self.os_type,
            'is_reachable': self.is_reachable,
            'timestamp': self.timestamp,
            'vendor': self.vendor,
            'model': self.model
        }


class NetworkScanner:
    """Network scanning and server discovery"""
    
    def __init__(self, timeout: int = 2, threads: int = 20):
        """
        Initialize network scanner
        
        Args:
            timeout: Connection timeout in seconds
            threads: Number of threads for parallel scanning
        """
        self.timeout = timeout
        self.threads = threads
        self.discovered_servers = []
        self.lock = threading.Lock()
        logger.info(f"Initialized NetworkScanner with timeout={timeout}s, threads={threads}")
    
    def ping_host(self, ip_address: str) -> bool:
        """
        Ping a host to check if it's reachable
        
        Args:
            ip_address: IP address to ping
            
        Returns:
            True if host responds to ping
        """
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(self.timeout * 1000), ip_address],
                    capture_output=True,
                    timeout=self.timeout
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(self.timeout * 1000), ip_address],
                    capture_output=True,
                    timeout=self.timeout
                )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Ping failed for {ip_address}: {str(e)}")
            return False
    
    def resolve_hostname(self, ip_address: str) -> str:
        """
        Resolve hostname from IP address
        
        Args:
            ip_address: IP address to resolve
            
        Returns:
            Hostname or IP address if resolution fails
        """
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except socket.herror:
            return ip_address
        except Exception as e:
            logger.debug(f"Hostname resolution failed for {ip_address}: {str(e)}")
            return ip_address
    
    def check_port(self, ip_address: str, port: int) -> bool:
        """
        Check if a port is open on a host
        
        Args:
            ip_address: IP address to check
            port: Port number
            
        Returns:
            True if port is open
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Port check failed for {ip_address}:{port}: {str(e)}")
            return False
    
    def scan_host(self, ip_address: str, ports: List[int] = None) -> Optional[ServerInfo]:
        """
        Scan a single host
        
        Args:
            ip_address: IP address to scan
            ports: List of ports to check
            
        Returns:
            ServerInfo if host is reachable, None otherwise
        """
        if ports is None:
            ports = [22, 3389, 5985, 445, 80, 443]  # SSH, RDP, WinRM, SMB, HTTP, HTTPS
        
        if not self.ping_host(ip_address):
            return None
        
        hostname = self.resolve_hostname(ip_address)
        
        # Detect OS type based on open ports
        os_type = 'Unknown'
        open_port = None
        
        for port in ports:
            if self.check_port(ip_address, port):
                open_port = port
                if port == 3389 or port == 5985 or port == 445:
                    os_type = 'Windows'
                elif port == 22:
                    os_type = 'Linux'
                break
        
        if open_port is None:
            return None
        
        server_info = ServerInfo(
            ip_address=ip_address,
            hostname=hostname,
            port=open_port,
            os_type=os_type,
            is_reachable=True,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Discovered server: {hostname} ({ip_address}) - {os_type}")
        return server_info
    
    def scan_network(self, network_range: str, ports: List[int] = None) -> List[ServerInfo]:
        """
        Scan a network range for servers
        
        Args:
            network_range: Network range in CIDR notation (e.g., '192.168.1.0/24')
            ports: List of ports to check
            
        Returns:
            List of discovered servers
        """
        logger.info(f"Starting network scan for range: {network_range}")
        
        try:
            network = ipaddress.ip_network(network_range, strict=False)
        except ValueError as e:
            logger.error(f"Invalid network range: {network_range}")
            raise
        
        self.discovered_servers = []
        threads_list = []
        
        # Create thread pool for scanning
        semaphore = threading.Semaphore(self.threads)
        
        def scan_with_semaphore(ip):
            with semaphore:
                server_info = self.scan_host(str(ip), ports)
                if server_info:
                    with self.lock:
                        self.discovered_servers.append(server_info)
        
        # Scan all IPs in the network
        for ip in network.hosts():
            thread = threading.Thread(target=scan_with_semaphore, args=(ip,))
            thread.start()
            threads_list.append(thread)
        
        # Wait for all threads to complete
        for thread in threads_list:
            thread.join()
        
        logger.info(f"Network scan completed. Found {len(self.discovered_servers)} servers")
        return self.discovered_servers
    
    def save_to_csv(self, filename: str) -> None:
        """
        Save discovered servers to CSV file
        
        Args:
            filename: Output CSV filename
        """
        if not self.discovered_servers:
            logger.warning("No servers to save")
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['ip_address', 'hostname', 'port', 'os_type', 'is_reachable', 'timestamp', 'vendor', 'model']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for server in self.discovered_servers:
                    writer.writerow(server.to_dict())
            logger.info(f"Servers saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save to CSV: {str(e)}")
            raise
    
    def save_to_json(self, filename: str) -> None:
        """
        Save discovered servers to JSON file
        
        Args:
            filename: Output JSON filename
        """
        if not self.discovered_servers:
            logger.warning("No servers to save")
            return
        
        try:
            with open(filename, 'w') as jsonfile:
                data = [server.to_dict() for server in self.discovered_servers]
                json.dump(data, jsonfile, indent=2)
            logger.info(f"Servers saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save to JSON: {str(e)}")
            raise
    
    def get_servers_by_os(self, os_type: str) -> List[ServerInfo]:
        """
        Get servers filtered by OS type
        
        Args:
            os_type: OS type filter (Windows, Linux)
            
        Returns:
            Filtered list of servers
        """
        return [s for s in self.discovered_servers if s.os_type == os_type]


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    scanner = NetworkScanner(timeout=2, threads=20)
    
    # Scan network range
    servers = scanner.scan_network('192.168.1.0/24')
    
    # Save results
    scanner.save_to_csv('discovered_servers.csv')
    scanner.save_to_json('discovered_servers.json')
    
    # Print results
    print(f"\nTotal servers discovered: {len(servers)}")
    for server in servers:
        print(f"  {server.hostname} ({server.ip_address}) - {server.os_type}")
