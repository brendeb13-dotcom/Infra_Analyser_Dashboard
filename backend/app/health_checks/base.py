"""
Base Health Check Class
All specific health checks inherit from this
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from ..core.logging import logger


class CheckStatus(str, Enum):
    """Status of individual checks"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check"""
    
    def __init__(self, server: str, check_type: str, status: CheckStatus, details: Dict[str, Any]):
        self.server = server
        self.check_type = check_type
        self.status = status
        self.details = details
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "server": self.server,
            "check_type": self.check_type,
            "status": self.status.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseHealthCheck(ABC):
    """Base class for all health checks"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize health check
        
        Args:
            config: Configuration dictionary for the check
        """
        self.config = config
        self.capability = config.get("capability", "unknown")
        self.account_name = config.get("account_name", "")
        self.results: List[HealthCheckResult] = []
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid
        """
        pass
    
    @abstractmethod
    async def execute(self) -> List[HealthCheckResult]:
        """
        Execute the health check
        
        Returns:
            List of health check results
        """
        pass
    
    def add_result(self, result: HealthCheckResult) -> None:
        """Add a result to the results list"""
        self.results.append(result)
        logger.info(f"Health check result for {result.server}: {result.check_type} = {result.status.value}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all results
        
        Returns:
            Summary dictionary with counts and status
        """
        healthy_count = sum(1 for r in self.results if r.status == CheckStatus.HEALTHY)
        warning_count = sum(1 for r in self.results if r.status == CheckStatus.WARNING)
        critical_count = sum(1 for r in self.results if r.status == CheckStatus.CRITICAL)
        unknown_count = sum(1 for r in self.results if r.status == CheckStatus.UNKNOWN)
        
        overall_status = CheckStatus.HEALTHY
        if critical_count > 0:
            overall_status = CheckStatus.CRITICAL
        elif warning_count > 0:
            overall_status = CheckStatus.WARNING
        elif unknown_count > 0:
            overall_status = CheckStatus.UNKNOWN
        
        return {
            "overall_status": overall_status.value,
            "total_checks": len(self.results),
            "healthy": healthy_count,
            "warning": warning_count,
            "critical": critical_count,
            "unknown": unknown_count,
            "results": [r.to_dict() for r in self.results],
        }
