#!/usr/bin/env python3
"""
Storage Health Check - Master Orchestration Script
Orchestrates the complete workflow: discovery → playbook → processing → results
"""

import argparse
import logging
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StorageHealthCheckOrchestrator:
    """Orchestrate storage health check workflow"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize orchestrator
        
        Args:
            config_file: Configuration JSON file path
        """
        self.config = self._load_config(config_file)
        self.discovery_results = None
        self.inventory_file = None
        self.check_results = None
        logger.info("Initialized StorageHealthCheckOrchestrator")
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict:
        """Load configuration from file or use defaults"""
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")
                sys.exit(1)
        
        # Default configuration
        return {
            'network_range': '192.168.1.0/24',
            'discovery_timeout': 120,
            'scanner_threads': 20,
            'ansible_vault_file': 'ansible/vault.yml',
            'results_db': 'storage_results.db',
            'export_format': 'csv',
            'dry_run': False,
            'parallel_execution': True
        }
    
    def discover_servers(self) -> bool:
        """
        Step 1: Discover servers in network
        
        Returns:
            True if discovery succeeded
        """
        logger.info("=" * 70)
        logger.info("STEP 1: Network Server Discovery")
        logger.info("=" * 70)
        
        try:
            from app.discovery.network_scanner import NetworkScanner
            
            network_range = self.config.get('network_range')
            threads = self.config.get('scanner_threads', 20)
            
            logger.info(f"Scanning network range: {network_range}")
            logger.info(f"Using {threads} threads for scanning")
            
            scanner = NetworkScanner(timeout=2, threads=threads)
            servers = scanner.scan_network(network_range)
            
            logger.info(f"Discovery completed: Found {len(servers)} servers")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = f'discovered_servers_{timestamp}.json'
            csv_file = f'discovered_servers_{timestamp}.csv'
            
            scanner.save_to_json(json_file)
            scanner.save_to_csv(csv_file)
            
            self.discovery_results = {
                'timestamp': timestamp,
                'network_range': network_range,
                'servers_found': len(servers),
                'servers': [s.to_dict() for s in servers],
                'json_file': json_file,
                'csv_file': csv_file
            }
            
            logger.info(f"Results saved to {json_file} and {csv_file}")
            
            # Summary by OS type
            linux_servers = scanner.get_servers_by_os('Linux')
            windows_servers = scanner.get_servers_by_os('Windows')
            
            logger.info(f"  Windows servers: {len(windows_servers)}")
            logger.info(f"  Linux servers: {len(linux_servers)}")
            
            return True
        except Exception as e:
            logger.error(f"Discovery failed: {str(e)}")
            return False
    
    def generate_inventory(self) -> bool:
        """
        Step 2: Generate Ansible inventory from discovered servers
        
        Returns:
            True if inventory generation succeeded
        """
        logger.info("=" * 70)
        logger.info("STEP 2: Generate Ansible Inventory")
        logger.info("=" * 70)
        
        if not self.discovery_results:
            logger.error("No discovery results. Run discovery first.")
            return False
        
        try:
            from ansible.generate_inventory import AnsibleInventoryGenerator
            
            json_file = self.discovery_results['json_file']
            timestamp = self.discovery_results['timestamp']
            
            generator = AnsibleInventoryGenerator()
            generator.load_from_json(json_file)
            generator.organize_by_os()
            
            # Generate multiple formats
            inventory_ini = f'inventory_{timestamp}.ini'
            inventory_yaml = f'inventory_{timestamp}.yaml'
            inventory_json = f'inventory_{timestamp}.json'
            
            generator.generate_ini_inventory(inventory_ini)
            generator.generate_yaml_inventory(inventory_yaml)
            generator.generate_dynamic_inventory(inventory_json)
            
            logger.info(f"Generated inventory files:")
            logger.info(f"  INI: {inventory_ini}")
            logger.info(f"  YAML: {inventory_yaml}")
            logger.info(f"  JSON: {inventory_json}")
            
            self.inventory_file = inventory_ini
            return True
        except Exception as e:
            logger.error(f"Inventory generation failed: {str(e)}")
            return False
    
    def execute_playbook(self) -> bool:
        """
        Step 3: Execute Ansible playbook to deploy and run health checks
        
        Returns:
            True if playbook execution succeeded
        """
        logger.info("=" * 70)
        logger.info("STEP 3: Execute Ansible Playbook")
        logger.info("=" * 70)
        
        if not self.inventory_file:
            logger.error("No inventory file. Generate inventory first.")
            return False
        
        try:
            playbook = 'ansible/storage_health_check.yml'
            vault_file = self.config.get('ansible_vault_file')
            
            # Build ansible-playbook command
            cmd = [
                'ansible-playbook',
                '-i', self.inventory_file,
                playbook
            ]
            
            if vault_file and Path(vault_file).exists():
                cmd.extend(['--vault-password-file', vault_file])
            
            if self.config.get('dry_run'):
                cmd.append('--check')
            
            if self.config.get('parallel_execution'):
                cmd.extend(['-f', '10'])  # 10 parallel forks
            
            logger.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=False, text=True)
            
            if result.returncode == 0:
                logger.info("Playbook execution completed successfully")
                return True
            else:
                logger.error(f"Playbook execution failed with code {result.returncode}")
                return False
        except Exception as e:
            logger.error(f"Playbook execution failed: {str(e)}")
            return False
    
    def process_results(self) -> bool:
        """
        Step 4: Process collected results and store in database
        
        Returns:
            True if result processing succeeded
        """
        logger.info("=" * 70)
        logger.info("STEP 4: Process and Store Results")
        logger.info("=" * 70)
        
        try:
            from app.processors.storage_results import StorageResultsProcessor
            
            db_path = self.config.get('results_db', 'storage_results.db')
            processor = StorageResultsProcessor(db_path)
            
            # Process results from collected_results directory
            results_dir = Path('collected_results')
            if not results_dir.exists():
                logger.warning("No collected_results directory found")
                return False
            
            result_files = list(results_dir.glob('*_storage_check.json'))
            logger.info(f"Found {len(result_files)} result files")
            
            for result_file in result_files:
                hostname = result_file.stem.replace('_storage_check', '')
                try:
                    processor.process_json_result(hostname, str(result_file))
                    logger.info(f"Processed: {hostname}")
                except Exception as e:
                    logger.error(f"Failed to process {hostname}: {str(e)}")
            
            # Get summary
            summary = processor.get_summary()
            logger.info("Processing Summary:")
            logger.info(f"  Total Servers: {summary.get('total_servers')}")
            logger.info(f"  Total Capacity: {summary.get('total_capacity_gb')} GB")
            logger.info(f"  Total Used: {summary.get('total_used_gb')} GB")
            logger.info(f"  Usage: {summary.get('usage_percent')}%")
            logger.info(f"  Critical Issues: {summary.get('critical_issues_count')}")
            
            self.check_results = summary
            processor.close()
            
            return True
        except Exception as e:
            logger.error(f"Result processing failed: {str(e)}")
            return False
    
    def export_results(self) -> bool:
        """
        Step 5: Export results to requested format
        
        Returns:
            True if export succeeded
        """
        logger.info("=" * 70)
        logger.info("STEP 5: Export Results")
        logger.info("=" * 70)
        
        try:
            from app.processors.storage_results import StorageResultsProcessor
            
            db_path = self.config.get('results_db', 'storage_results.db')
            export_format = self.config.get('export_format', 'csv')
            
            processor = StorageResultsProcessor(db_path)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format.lower() == 'csv':
                output_file = f'storage_results_{timestamp}.csv'
                processor.export_to_csv(output_file)
                logger.info(f"Results exported to {output_file}")
            
            processor.close()
            return True
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return False
    
    def run_complete_workflow(self, skip_steps: List[str] = None) -> bool:
        """
        Run complete workflow
        
        Args:
            skip_steps: List of steps to skip (discovery, inventory, playbook, processing, export)
            
        Returns:
            True if all enabled steps succeeded
        """
        skip_steps = skip_steps or []
        
        logger.info("\n" + "=" * 70)
        logger.info("STORAGE HEALTH CHECK - COMPLETE WORKFLOW")
        logger.info("=" * 70 + "\n")
        
        steps = [
            ('discovery', self.discover_servers),
            ('inventory', self.generate_inventory),
            ('playbook', self.execute_playbook),
            ('processing', self.process_results),
            ('export', self.export_results)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            if step_name in skip_steps:
                logger.info(f"Skipping step: {step_name}")
                continue
            
            success = step_func()
            results[step_name] = success
            
            if not success:
                logger.error(f"Step '{step_name}' failed. Stopping workflow.")
                break
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("WORKFLOW SUMMARY")
        logger.info("=" * 70)
        for step_name, success in results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            logger.info(f"  {step_name.upper()}: {status}")
        
        logger.info("=" * 70 + "\n")
        
        return all(results.values())


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Storage Health Check Orchestration Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete workflow
  python orchestrate_storage_checks.py

  # Run with custom config
  python orchestrate_storage_checks.py --config storage_config.json

  # Skip specific steps
  python orchestrate_storage_checks.py --skip playbook export

  # Dry run (no actual execution)
  python orchestrate_storage_checks.py --dry-run
        """
    )
    
    parser.add_argument(
        '--config',
        help='Configuration JSON file'
    )
    parser.add_argument(
        '--network-range',
        default='192.168.1.0/24',
        help='Network range to scan (CIDR notation)'
    )
    parser.add_argument(
        '--skip',
        nargs='+',
        default=[],
        help='Steps to skip: discovery, inventory, playbook, processing, export'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no changes)'
    )
    parser.add_argument(
        '--vault-file',
        help='Ansible vault password file'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = StorageHealthCheckOrchestrator(args.config)
    
    # Override config with command-line arguments
    orchestrator.config['network_range'] = args.network_range
    orchestrator.config['dry_run'] = args.dry_run
    if args.vault_file:
        orchestrator.config['ansible_vault_file'] = args.vault_file
    
    # Run workflow
    success = orchestrator.run_complete_workflow(skip_steps=args.skip)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
