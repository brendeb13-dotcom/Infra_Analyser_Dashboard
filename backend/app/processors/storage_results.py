"""
Storage Health Check Results Processor
Processes collected results and stores them in database
"""

import json
import csv
import sqlite3
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

logger = logging.getLogger(__name__)


class StorageResultsProcessor:
    """Process and store storage health check results"""
    
    def __init__(self, db_path: str = 'storage_results.db'):
        """
        Initialize results processor
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.connection = None
        self._init_database()
        logger.info(f"Initialized StorageResultsProcessor with db: {db_path}")
    
    def _init_database(self) -> None:
        """Initialize SQLite database with schema"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Create servers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT UNIQUE NOT NULL,
                ip_address TEXT NOT NULL,
                os_type TEXT,
                check_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create disk_info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disk_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                device_name TEXT,
                device_path TEXT,
                size_gb REAL,
                used_gb REAL,
                available_gb REAL,
                used_percent REAL,
                filesystem TEXT,
                mount_point TEXT,
                status TEXT,
                check_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id)
            )
        ''')
        
        # Create storage_config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS storage_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                device_name TEXT,
                device_path TEXT,
                size_gb REAL,
                status TEXT,
                vendor TEXT,
                model TEXT,
                serial_number TEXT,
                check_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id)
            )
        ''')
        
        # Create health_check_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_check_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                check_status TEXT,
                total_disks INTEGER,
                total_capacity_gb REAL,
                total_used_gb REAL,
                issues TEXT,
                check_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers(id)
            )
        ''')
        
        self.connection.commit()
        logger.info("Database schema initialized")
    
    def process_json_result(self, hostname: str, json_file: str) -> bool:
        """
        Process a single JSON result file
        
        Args:
            hostname: Hostname of the server
            json_file: Path to JSON result file
            
        Returns:
            True if processing was successful
        """
        try:
            with open(json_file, 'r') as f:
                result = json.load(f)
            
            logger.info(f"Processing results for {hostname}")
            
            # Get or create server record
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO servers (hostname, ip_address, os_type)
                VALUES (?, ?, ?)
            ''', (hostname, result.get('ip_address', 'Unknown'), result.get('os_type')))
            
            cursor.execute('SELECT id FROM servers WHERE hostname = ?', (hostname,))
            server_id = cursor.fetchone()[0]
            
            # Insert disk info
            for disk in result.get('disk_info', []):
                cursor.execute('''
                    INSERT INTO disk_info 
                    (server_id, device_name, device_path, size_gb, used_gb, available_gb, 
                     used_percent, filesystem, mount_point, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    server_id,
                    disk.get('name'),
                    disk.get('device'),
                    disk.get('size_gb'),
                    disk.get('used_gb'),
                    disk.get('available_gb'),
                    disk.get('used_percent'),
                    disk.get('filesystem'),
                    disk.get('mount_point'),
                    'HEALTHY' if disk.get('used_percent', 0) < 80 else 
                    'WARNING' if disk.get('used_percent', 0) < 90 else 'CRITICAL'
                ))
            
            # Insert storage config
            for config in result.get('storage_config', []):
                cursor.execute('''
                    INSERT INTO storage_config
                    (server_id, device_name, device_path, size_gb, status, vendor, model, serial_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    server_id,
                    config.get('device_name'),
                    config.get('device_path'),
                    config.get('size_gb'),
                    config.get('status'),
                    config.get('vendor'),
                    config.get('model'),
                    config.get('serial_number')
                ))
            
            # Insert health check result
            cursor.execute('''
                INSERT INTO health_check_results
                (server_id, check_status, total_disks, total_capacity_gb, total_used_gb, issues)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                server_id,
                result.get('status'),
                result.get('total_disks'),
                result.get('total_capacity_gb'),
                result.get('total_used_gb'),
                json.dumps(result.get('issues', []))
            ))
            
            self.connection.commit()
            logger.info(f"Successfully processed results for {hostname}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process results for {hostname}: {str(e)}")
            return False
    
    def process_aggregated_results(self, json_file: str) -> bool:
        """
        Process aggregated results from all servers
        
        Args:
            json_file: Path to aggregated JSON file
            
        Returns:
            True if processing was successful
        """
        try:
            with open(json_file, 'r') as f:
                aggregated = json.load(f)
            
            logger.info(f"Processing aggregated results from {json_file}")
            
            for hostname, result in aggregated.items():
                self.process_json_result(hostname, result)
            
            return True
        except Exception as e:
            logger.error(f"Failed to process aggregated results: {str(e)}")
            return False
    
    def export_to_csv(self, output_file: str) -> None:
        """
        Export results to CSV file
        
        Args:
            output_file: Output CSV filename
        """
        try:
            cursor = self.connection.cursor()
            
            # Query disk info with server details
            cursor.execute('''
                SELECT s.hostname, s.ip_address, d.device_name, d.size_gb, d.used_gb, 
                       d.available_gb, d.used_percent, d.filesystem, d.mount_point, d.status
                FROM disk_info d
                JOIN servers s ON d.server_id = s.id
                ORDER BY s.hostname, d.mount_point
            ''')
            
            rows = cursor.fetchall()
            
            if not rows:
                logger.warning("No data to export")
                return
            
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['Hostname', 'IP Address', 'Device', 'Size (GB)', 'Used (GB)',
                            'Available (GB)', 'Used %', 'Filesystem', 'Mount Point', 'Status']
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                writer.writerows(rows)
            
            logger.info(f"Results exported to {output_file}")
        except Exception as e:
            logger.error(f"Failed to export to CSV: {str(e)}")
    
    def get_summary(self) -> Dict:
        """
        Get summary of all health checks
        
        Returns:
            Dictionary with summary statistics
        """
        try:
            cursor = self.connection.cursor()
            
            # Get total servers
            cursor.execute('SELECT COUNT(*) FROM servers')
            total_servers = cursor.fetchone()[0]
            
            # Get health status distribution
            cursor.execute('''
                SELECT check_status, COUNT(*) FROM health_check_results
                GROUP BY check_status
            ''')
            status_dist = dict(cursor.fetchall())
            
            # Get total capacity
            cursor.execute('SELECT SUM(total_capacity_gb) FROM health_check_results')
            total_capacity = cursor.fetchone()[0] or 0
            
            # Get total used
            cursor.execute('SELECT SUM(total_used_gb) FROM health_check_results')
            total_used = cursor.fetchone()[0] or 0
            
            # Get critical issues
            cursor.execute('''
                SELECT server_id, issues FROM health_check_results
                WHERE check_status = 'CRITICAL'
            ''')
            critical_issues = cursor.fetchall()
            
            return {
                'total_servers': total_servers,
                'status_distribution': status_dist,
                'total_capacity_gb': round(total_capacity, 2),
                'total_used_gb': round(total_used, 2),
                'usage_percent': round((total_used / total_capacity * 100) if total_capacity > 0 else 0, 2),
                'critical_issues_count': len(critical_issues),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get summary: {str(e)}")
            return {}
    
    def query_servers(self, status_filter: str = None) -> List[Dict]:
        """
        Query servers with optional status filter
        
        Args:
            status_filter: Filter by status (HEALTHY, WARNING, CRITICAL)
            
        Returns:
            List of server records
        """
        try:
            cursor = self.connection.cursor()
            
            if status_filter:
                cursor.execute('''
                    SELECT s.hostname, s.ip_address, s.os_type, h.check_status,
                           h.total_capacity_gb, h.total_used_gb
                    FROM servers s
                    LEFT JOIN health_check_results h ON s.id = h.server_id
                    WHERE h.check_status = ?
                    ORDER BY s.hostname
                ''', (status_filter,))
            else:
                cursor.execute('''
                    SELECT s.hostname, s.ip_address, s.os_type, h.check_status,
                           h.total_capacity_gb, h.total_used_gb
                    FROM servers s
                    LEFT JOIN health_check_results h ON s.id = h.server_id
                    ORDER BY s.hostname
                ''')
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
        except Exception as e:
            logger.error(f"Failed to query servers: {str(e)}")
            return []
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    processor = StorageResultsProcessor('storage_results.db')
    
    # Example: Process a single result
    # processor.process_json_result('server1.example.com', 'server1_storage_check.json')
    
    # Get and print summary
    summary = processor.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export to CSV
    processor.export_to_csv('storage_results_summary.csv')
    
    processor.close()
