"""
Ansible Inventory Management Script
Generates dynamic inventory for Ansible based on discovered servers
"""

import json
import csv
import argparse
import logging
from typing import Dict, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class AnsibleInventoryGenerator:
    """Generate Ansible inventory files from server data"""
    
    def __init__(self):
        """Initialize inventory generator"""
        self.servers = []
        self.groups = {}
        logger.info("Initialized AnsibleInventoryGenerator")
    
    def load_from_csv(self, csv_file: str) -> None:
        """
        Load server data from CSV file
        
        Args:
            csv_file: Path to CSV file with server data
        """
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                self.servers = list(reader)
            logger.info(f"Loaded {len(self.servers)} servers from {csv_file}")
        except Exception as e:
            logger.error(f"Failed to load CSV: {str(e)}")
            raise
    
    def load_from_json(self, json_file: str) -> None:
        """
        Load server data from JSON file
        
        Args:
            json_file: Path to JSON file with server data
        """
        try:
            with open(json_file, 'r') as f:
                self.servers = json.load(f)
            logger.info(f"Loaded {len(self.servers)} servers from {json_file}")
        except Exception as e:
            logger.error(f"Failed to load JSON: {str(e)}")
            raise
    
    def organize_by_os(self) -> Dict[str, List]:
        """
        Organize servers by OS type
        
        Returns:
            Dictionary with servers grouped by OS
        """
        groups = {}
        for server in self.servers:
            os_type = server.get('os_type', 'Unknown')
            if os_type not in groups:
                groups[os_type] = []
            groups[os_type].append(server)
        
        self.groups = groups
        logger.info(f"Organized servers into {len(groups)} OS groups")
        return groups
    
    def organize_by_network(self) -> Dict[str, List]:
        """
        Organize servers by network subnet
        
        Returns:
            Dictionary with servers grouped by network
        """
        groups = {}
        for server in self.servers:
            ip = server.get('ip_address', 'Unknown')
            subnet = '.'.join(ip.split('.')[:3]) + '.0'
            
            if subnet not in groups:
                groups[subnet] = []
            groups[subnet].append(server)
        
        self.groups = groups
        logger.info(f"Organized servers into {len(groups)} network groups")
        return groups
    
    def generate_ini_inventory(self, output_file: str) -> None:
        """
        Generate Ansible INI format inventory
        
        Args:
            output_file: Output inventory file path
        """
        if not self.groups:
            self.organize_by_os()
        
        try:
            with open(output_file, 'w') as f:
                f.write("# Ansible Inventory - Generated on {}\n\n".format(datetime.now()))
                
                # Windows group
                windows_servers = self.groups.get('Windows', [])
                if windows_servers:
                    f.write("[windows]\n")
                    for server in windows_servers:
                        f.write("{} ansible_host={} ansible_port={} ".format(
                            server.get('hostname', server.get('ip_address')),
                            server.get('ip_address'),
                            server.get('port', 5985)
                        ))
                        f.write("ansible_connection=winrm ")
                        f.write("ansible_user=Administrator ")
                        f.write("ansible_password='{{ vault_password }}'\n")
                    f.write("\n")
                
                # Linux group
                linux_servers = self.groups.get('Linux', [])
                if linux_servers:
                    f.write("[linux]\n")
                    for server in linux_servers:
                        f.write("{} ansible_host={} ansible_port={} ".format(
                            server.get('hostname', server.get('ip_address')),
                            server.get('ip_address'),
                            server.get('port', 22)
                        ))
                        f.write("ansible_connection=ssh ")
                        f.write("ansible_user=root ")
                        f.write("ansible_ssh_private_key_file='{{ vault_ssh_key }}'\n")
                    f.write("\n")
                
                # All hosts group
                f.write("[all]\n")
                for server in self.servers:
                    f.write("{}\n".format(server.get('hostname', server.get('ip_address'))))
                f.write("\n")
                
                # Group variables
                f.write("[all:vars]\n")
                f.write("ansible_python_interpreter=/usr/bin/python3\n")
                f.write("ansible_timeout=30\n")
            
            logger.info(f"Generated INI inventory: {output_file}")
        except Exception as e:
            logger.error(f"Failed to generate INI inventory: {str(e)}")
            raise
    
    def generate_yaml_inventory(self, output_file: str) -> None:
        """
        Generate Ansible YAML format inventory
        
        Args:
            output_file: Output inventory file path
        """
        if not self.groups:
            self.organize_by_os()
        
        try:
            inventory = {
                'all': {
                    'children': [],
                    'hosts': {}
                }
            }
            
            # Add Windows hosts
            windows_servers = self.groups.get('Windows', [])
            if windows_servers:
                inventory['all']['children'].append('windows')
                inventory['windows'] = {
                    'hosts': {},
                    'vars': {
                        'ansible_connection': 'winrm',
                        'ansible_user': 'Administrator',
                        'ansible_password': '{{ vault_password }}',
                        'ansible_port': 5985
                    }
                }
                for server in windows_servers:
                    hostname = server.get('hostname', server.get('ip_address'))
                    inventory['windows']['hosts'][hostname] = {
                        'ansible_host': server.get('ip_address'),
                        'ansible_port': server.get('port', 5985)
                    }
            
            # Add Linux hosts
            linux_servers = self.groups.get('Linux', [])
            if linux_servers:
                inventory['all']['children'].append('linux')
                inventory['linux'] = {
                    'hosts': {},
                    'vars': {
                        'ansible_connection': 'ssh',
                        'ansible_user': 'root',
                        'ansible_ssh_private_key_file': '{{ vault_ssh_key }}',
                        'ansible_port': 22
                    }
                }
                for server in linux_servers:
                    hostname = server.get('hostname', server.get('ip_address'))
                    inventory['linux']['hosts'][hostname] = {
                        'ansible_host': server.get('ip_address'),
                        'ansible_port': server.get('port', 22)
                    }
            
            # Add group variables
            if 'all' not in inventory:
                inventory['all'] = {}
            inventory['all']['vars'] = {
                'ansible_python_interpreter': '/usr/bin/python3',
                'ansible_timeout': 30
            }
            
            with open(output_file, 'w') as f:
                json.dump(inventory, f, indent=2)
            
            logger.info(f"Generated YAML inventory: {output_file}")
        except Exception as e:
            logger.error(f"Failed to generate YAML inventory: {str(e)}")
            raise
    
    def generate_dynamic_inventory(self, output_file: str) -> None:
        """
        Generate dynamic inventory JSON for Ansible
        
        Args:
            output_file: Output inventory file path
        """
        inventory = {}
        
        # Organize servers
        if not self.groups:
            self.organize_by_os()
        
        try:
            # Create groups
            for group_name, servers in self.groups.items():
                group_lower = group_name.lower()
                inventory[group_lower] = {
                    'hosts': [s.get('ip_address') for s in servers],
                    'vars': {}
                }
                
                if group_name == 'Windows':
                    inventory[group_lower]['vars'] = {
                        'ansible_connection': 'winrm',
                        'ansible_user': 'Administrator'
                    }
                elif group_name == 'Linux':
                    inventory[group_lower]['vars'] = {
                        'ansible_connection': 'ssh',
                        'ansible_user': 'root'
                    }
            
            # Add _meta hosts data
            inventory['_meta'] = {'hostvars': {}}
            for server in self.servers:
                ip = server.get('ip_address')
                inventory['_meta']['hostvars'][ip] = {
                    'hostname': server.get('hostname'),
                    'os_type': server.get('os_type'),
                    'port': server.get('port'),
                    'ansible_host': ip
                }
            
            with open(output_file, 'w') as f:
                json.dump(inventory, f, indent=2)
            
            logger.info(f"Generated dynamic inventory: {output_file}")
        except Exception as e:
            logger.error(f"Failed to generate dynamic inventory: {str(e)}")
            raise


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate Ansible inventory from discovered servers')
    parser.add_argument('--input', required=True, help='Input CSV or JSON file with server data')
    parser.add_argument('--output', required=True, help='Output inventory file')
    parser.add_argument('--format', choices=['ini', 'yaml', 'json'], default='ini', help='Inventory format')
    
    args = parser.parse_args()
    
    # Generate inventory
    generator = AnsibleInventoryGenerator()
    
    if args.input.endswith('.csv'):
        generator.load_from_csv(args.input)
    elif args.input.endswith('.json'):
        generator.load_from_json(args.input)
    else:
        print("Unsupported file format. Use CSV or JSON.")
        exit(1)
    
    generator.organize_by_os()
    
    if args.format == 'ini':
        generator.generate_ini_inventory(args.output)
    elif args.format == 'yaml':
        generator.generate_yaml_inventory(args.output)
    elif args.format == 'json':
        generator.generate_dynamic_inventory(args.output)
    
    print(f"Inventory generated: {args.output}")
