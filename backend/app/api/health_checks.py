"""
Health Checks API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..db import get_db
from ..models.health_check import HealthCheck, HealthCheckStatus, HealthCheckResultStatus
from ..health_checks.windows_server import WindowsServerHealthCheck
from ..core.logging import logger

router = APIRouter(prefix="/api/v1/health-checks", tags=["health-checks"])


class HealthCheckRequest:
    """Request model for health check execution"""
    
    def __init__(self, capability: str, account_name: str, config: Dict[str, Any]):
        self.capability = capability
        self.account_name = account_name
        self.config = config


@router.post("/execute")
async def execute_health_check(
    capability: str,
    account_name: str,
    config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute a health check for a specific capability
    
    Args:
        capability: Capability name (windows_server, storage, backup, etc.)
        account_name: Account/organization name
        config: Health check configuration
        background_tasks: FastAPI background tasks
        db: Database session
    
    Returns:
        Health check execution record with ID
    """
    try:
        # Create health check record
        health_check = HealthCheck(
            capability=capability,
            account_name=account_name,
            status=HealthCheckStatus.PENDING,
        )
        db.add(health_check)
        db.commit()
        db.refresh(health_check)
        
        logger.info(f"Created health check {health_check.id} for {capability}")
        
        # Execute health check in background
        background_tasks.add_task(
            _execute_health_check_task,
            health_check.id,
            capability,
            config,
        )
        
        return {
            "id": str(health_check.id),
            "capability": capability,
            "account_name": account_name,
            "status": health_check.status.value,
            "created_at": health_check.created_at.isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error executing health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{check_id}")
async def get_health_check(
    check_id: str,
    db: Session = Depends(get_db)
):
    """
    Get health check status and details
    
    Args:
        check_id: Health check ID
        db: Database session
    
    Returns:
        Health check details
    """
    try:
        health_check = db.query(HealthCheck).filter(HealthCheck.id == check_id).first()
        if not health_check:
            raise HTTPException(status_code=404, detail="Health check not found")
        
        return health_check.to_dict()
    
    except Exception as e:
        logger.error(f"Error retrieving health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{check_id}")
async def get_health_check_results(
    check_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed results of a health check
    
    Args:
        check_id: Health check ID
        db: Database session
    
    Returns:
        Health check results with details
    """
    try:
        health_check = db.query(HealthCheck).filter(HealthCheck.id == check_id).first()
        if not health_check:
            raise HTTPException(status_code=404, detail="Health check not found")
        
        results = health_check.to_dict()
        results["detailed_results"] = [r.to_dict() for r in health_check.results]
        
        return results
    
    except Exception as e:
        logger.error(f"Error retrieving health check results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_health_check_history(
    capability: str = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get health check execution history
    
    Args:
        capability: Filter by capability (optional)
        limit: Number of records to return
        offset: Pagination offset
        db: Database session
    
    Returns:
        List of health checks
    """
    try:
        query = db.query(HealthCheck)
        
        if capability:
            query = query.filter(HealthCheck.capability == capability)
        
        total = query.count()
        health_checks = query.order_by(HealthCheck.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [hc.to_dict() for hc in health_checks]
        }
    
    except Exception as e:
        logger.error(f"Error retrieving health check history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_health_check_task(check_id: str, capability: str, config: Dict[str, Any]):
    """
    Background task to execute health check
    
    Args:
        check_id: Health check ID
        capability: Capability name
        config: Configuration
    """
    from ..db import SessionLocal
    db = SessionLocal()
    
    try:
        health_check = db.query(HealthCheck).filter(HealthCheck.id == check_id).first()
        if not health_check:
            logger.error(f"Health check {check_id} not found")
            return
        
        # Update status to running
        health_check.status = HealthCheckStatus.RUNNING
        health_check.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Starting execution of health check {check_id}")
        
        # Select appropriate health check class
        if capability == "windows_server":
            health_check_instance = WindowsServerHealthCheck(config)
        else:
            raise ValueError(f"Unknown capability: {capability}")
        
        # Validate configuration
        if not health_check_instance.validate_config():
            raise ValueError("Invalid configuration")
        
        # Execute health check
        results = await health_check_instance.execute()
        
        # Store results
        from ..models.health_check import HealthCheckResult
        for result in results:
            db_result = HealthCheckResult(
                health_check_id=health_check.id,
                server_name=result.server,
                check_type=result.check_type,
                status=HealthCheckResultStatus[result.status.name],
                details=result.details,
            )
            db.add(db_result)
        
        # Update health check with summary
        summary = health_check_instance.get_summary()
        health_check.execution_result = summary
        health_check.status = HealthCheckStatus.COMPLETED
        health_check.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Health check {check_id} completed successfully")
    
    except Exception as e:
        logger.error(f"Error executing health check {check_id}: {str(e)}")
        health_check.status = HealthCheckStatus.FAILED
        health_check.error_message = str(e)
        health_check.completed_at = datetime.utcnow()
        db.commit()
    
    finally:
        db.close()
