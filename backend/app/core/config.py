"""
Application Configuration Management
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_LOG_LEVEL: str = "info"
    API_VERSION: str = "v1"
    
    # Project Info
    PROJECT_NAME: str = "Infrastructure Analyzer Dashboard"
    PROJECT_DESCRIPTION: str = "Comprehensive infrastructure health monitoring and analysis platform"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/infra_analyzer"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.company.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@company.com"
    SMTP_PASSWORD: str = ""
    SMTP_FROM_ADDR: str = "noreply@company.com"
    ENABLE_EMAIL_REPORTS: bool = True
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Remote Execution
    WINRM_PORT: int = 5985
    WINRM_SECURE_PORT: int = 5986
    WINRM_USERNAME: str = ""
    WINRM_PASSWORD: str = ""
    WINRM_AUTH_METHOD: str = "kerberos"
    WINRM_TIMEOUT: int = 300
    
    SSH_KEY_PATH: str = "/root/.ssh/id_rsa"
    SSH_PORT: int = 22
    SSH_TIMEOUT: int = 300
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Features
    ENABLE_REPORT_EXPORT: bool = True
    REPORT_RETENTION_DAYS: int = 30
    MAX_CONCURRENT_CHECKS: int = 5
    EXECUTION_TIMEOUT_SECONDS: int = 600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
