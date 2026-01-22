"""
Storage Health Check API Endpoints
Handles storage discovery, execution, and results
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
from pathlib import Path

from ..db import get_db
from ..discovery.network_scanner import NetworkScanner
from ..health_checks.storage import StorageHealthCheck
from ..processors.storage_results import StorageResultsProcessor
from ..core.logging import logger

router = APIRouter(prefix="/api/v1/storage", tags=["storage"])


class StorageDiscoveryRequest:
    """Request model for storage discovery"""
    def __init__(self, network_range: str, ports: Optional[List[int]] = None):
        self.network_range = network_range
        self.ports = ports or [22, 3389, 445, 5985]


class StorageCheckRequest:
    """Request model for storage health check"""
    def __init__(self, servers: List[str], check_types: Optional[List[str]] = None):
        self.servers = servers
        self.check_types = check_types or ['disk', 'config', 'health']


# Store ongoing discoveries
ongoing_discoveries = {}
ongoing_checks = {}


@router.post("/discover")
async def discover_storage_servers(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Discover servers in network and identify storage capabilities
    
    Args:
        request: Discovery request with network_range and optional ports
        
    Returns:
        Discovery task ID and status
    """
    try:
        network_range = request.get('network_range')
        ports = request.get('ports', [22, 3389, 445, 5985])
        
        if not network_range:
            raise HTTPException(status_code=400, detail="network_range is required")
        
        discovery_id = str(datetime.now().timestamp())
        
        # Start discovery in background
        background_tasks.add_task(
            _run_discovery,
            discovery_id,
            network_range,
            ports
        )
        
        ongoing_discoveries[discovery_id] = {
            'status': 'RUNNING',
            'network_range': network_range,
            'started_at': datetime.now().isoformat(),
            'servers_found': 0
        }
        
        logger.info(f"Started discovery {discovery_id} for {network_range}")
        
        return {
            'discovery_id': discovery_id,
            'status': 'RUNNING',
            'message': f'Discovering servers in {network_range}'
        }
    except Exception as e:
        logger.error(f"Discovery error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discovery/{discovery_id}")
async def get_discovery_status(discovery_id: str):
    """
    Get status of ongoing discovery
    
    Args:
        discovery_id: Discovery task ID
        
    Returns:
        Discovery status and results if complete
    """
    if discovery_id not in ongoing_discoveries:
        raise HTTPException(status_code=404, detail="Discovery not found")
    
    return ongoing_discoveries[discovery_id]


@router.post("/health-check")
async def execute_storage_health_check(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute storage health check on target servers
    
    Args:
        request: Health check request with servers and check_types
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Health check execution ID
    """
    try:
        servers = request.get('servers', [])
        check_types = request.get('check_types', ['disk', 'config', 'health'])
        
        if not servers:
            raise HTTPException(status_code=400, detail="servers list is required")
        
        check_id = str(datetime.now().timestamp())
        
        # Start health check in background
        background_tasks.add_task(
            _run_storage_check,
            check_id,
            servers,
            check_types,
            db
        )
        
        ongoing_checks[check_id] = {
            'status': 'RUNNING',
            'servers': servers,
            'check_types': check_types,
            'started_at': datetime.now().isoformat(),
            'results': {}
        }
        
        logger.info(f"Started health check {check_id} for {len(servers)} servers")
        
        return {
            'check_id': check_id,
            'status': 'RUNNING',
            'servers_count': len(servers),
            'message': 'Storage health check started'
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-check/{check_id}")
async def get_health_check_status(check_id: str):
    """
    Get status of ongoing health check
    
    Args:
        check_id: Health check task ID
        
    Returns:
        Health check status and partial results
    """
    if check_id not in ongoing_checks:
        raise HTTPException(status_code=404, detail="Health check not found")
    
    check_data = ongoing_checks[check_id]
    
    return {
        'check_id': check_id,
        'status': check_data['status'],
        'servers_count': len(check_data['servers']),
        'completed_count': len(check_data['results']),
        'results': check_data['results'],
        'started_at': check_data['started_at']
    }


@router.get("/results")
async def get_storage_results(
    status_filter: Optional[str] = Query(None, description="Filter by status: HEALTHY, WARNING, CRITICAL"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get stored storage health check results
    
    Args:
        status_filter: Optional status filter
        limit: Maximum results to return
        
    Returns:
        List of storage health check results
    """
    try:
        processor = StorageResultsProcessor()
        results = processor.query_servers(status_filter)
        processor.close()
        
        return {
            'total': len(results),
            'results': results[:limit]
        }
    except Exception as e:
        logger.error(f"Failed to get results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_storage_summary():
    """
    Get summary statistics of all storage health checks
    
    Returns:
        Summary statistics
    """
    try:
        processor = StorageResultsProcessor()
        summary = processor.get_summary()
        processor.close()
        
        return summary
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_storage_results(request: Dict[str, Any]):
    """
    Export storage results to CSV
    
    Args:
        request: Export request with format
        
    Returns:
        CSV file download
    """
    try:
        output_file = f'storage_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        processor = StorageResultsProcessor()
        processor.export_to_csv(output_file)
        processor.close()
        
        return FileResponse(
            path=output_file,
            filename=output_file,
            media_type='text/csv'
        )
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task functions

async def _run_discovery(discovery_id: str, network_range: str, ports: List[int]):
    """Run network discovery in background"""
    try:
        scanner = NetworkScanner(timeout=2, threads=20)
        servers = scanner.scan_network(network_range, ports)
        
        # Save discovery results
        scanner.save_to_json(f'discovery_{discovery_id}.json')
        
        ongoing_discoveries[discovery_id].update({
            'status': 'COMPLETED',
            'servers_found': len(servers),
            'servers': [s.to_dict() for s in servers],
            'completed_at': datetime.now().isoformat()
        })
        
        logger.info(f"Discovery {discovery_id} completed: found {len(servers)} servers")
    except Exception as e:
        ongoing_discoveries[discovery_id].update({
            'status': 'FAILED',
            'error': str(e),
            'completed_at': datetime.now().isoformat()
        })
        logger.error(f"Discovery {discovery_id} failed: {str(e)}")


async def _run_storage_check(
    check_id: str,
    servers: List[str],
    check_types: List[str],
    db: Session
):
    """Run storage health check in background"""
    try:
        processor = StorageResultsProcessor()
        
        for server in servers:
            try:
                # Execute health check on server
                checker = StorageHealthCheck()
                results = checker.check_disk_health()
                
                # Store in database
                processor.process_json_result(server, json.dumps(results))
                
                ongoing_checks[check_id]['results'][server] = {
                    'status': results['status'],
                    'total_disks': results['total_disks'],
                    'total_capacity_gb': results['total_capacity_gb'],
                    'total_used_gb': results['total_used_gb']
                }
                
                logger.info(f"Completed health check for {server}")
            except Exception as e:
                ongoing_checks[check_id]['results'][server] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                logger.error(f"Health check failed for {server}: {str(e)}")
        
        processor.close()
        ongoing_checks[check_id]['status'] = 'COMPLETED'
        ongoing_checks[check_id]['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"Health check {check_id} completed")
    except Exception as e:
        ongoing_checks[check_id].update({
            'status': 'FAILED',
            'error': str(e),
            'completed_at': datetime.now().isoformat()
        })
        logger.error(f"Health check {check_id} failed: {str(e)}")
