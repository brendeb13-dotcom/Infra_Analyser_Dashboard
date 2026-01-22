"""
Health Check Models
"""
from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from ..db.database import Base


class HealthCheckStatus(str, PyEnum):
    """Health check execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HealthCheckResultStatus(str, PyEnum):
    """Individual check result status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthCheck(Base):
    """Health Check Execution Record"""
    __tablename__ = "health_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    capability = Column(String(100), index=True)
    account_name = Column(String(100))
    status = Column(Enum(HealthCheckStatus), default=HealthCheckStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    execution_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    results = relationship("HealthCheckResult", back_populates="health_check", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "capability": self.capability,
            "account_name": self.account_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_result": self.execution_result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class HealthCheckResult(Base):
    """Individual Health Check Result"""
    __tablename__ = "health_check_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    health_check_id = Column(UUID(as_uuid=True), ForeignKey("health_checks.id"), index=True)
    server_name = Column(String(255))
    check_type = Column(String(100))
    status = Column(Enum(HealthCheckResultStatus), default=HealthCheckResultStatus.UNKNOWN)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    health_check = relationship("HealthCheck", back_populates="results")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "health_check_id": str(self.health_check_id),
            "server_name": self.server_name,
            "check_type": self.check_type,
            "status": self.status.value,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
