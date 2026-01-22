"""
Server Models
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..db.database import Base


class Server(Base):
    """Server Configuration"""
    __tablename__ = "servers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, index=True)
    hostname = Column(String(255))
    ip_address = Column(String(15), nullable=True)
    server_type = Column(String(50))  # windows, linux, storage, backup, etc.
    port = Column(Integer, nullable=True)
    username = Column(String(255), nullable=True)
    auth_type = Column(String(50))  # local, domain, ssh_key, etc.
    capabilities = Column(JSON)  # List of capabilities this server supports
    is_active = Column(Boolean, default=True)
    connection_details = Column(JSON)  # Additional connection parameters
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "server_type": self.server_type,
            "port": self.port,
            "username": self.username,
            "auth_type": self.auth_type,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "connection_details": self.connection_details,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
