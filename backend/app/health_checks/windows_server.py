"""
Windows Server Health Check
Checks server disk, memory, CPU, services, uptime, etc.
"""
from typing import Dict, List, Any
from .base import BaseHealthCheck, HealthCheckResult, CheckStatus
from ..utils.remote_executor import WindowsRemoteExecutor
from ..core.logging import logger


class WindowsServerHealthCheck(BaseHealthCheck):
    """Windows Server Health Check"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.executor = WindowsRemoteExecutor(config)
    
    def validate_config(self) -> bool:
        """Validate Windows Server health check configuration"""
        required_fields = ["servers", "account_name"]
        return all(field in self.config for field in required_fields)
    
    async def execute(self) -> List[HealthCheckResult]:
        """
        Execute Windows Server health checks
        
        Returns:
            List of health check results
        """
        self.results = []
        servers = self.config.get("servers", [])
        
        logger.info(f"Starting Windows Server health checks for {len(servers)} servers")
        
        for server in servers:
            try:
                await self._check_server(server)
            except Exception as e:
                logger.error(f"Error checking server {server}: {str(e)}")
                result = HealthCheckResult(
                    server=server,
                    check_type="connectivity",
                    status=CheckStatus.CRITICAL,
                    details={"error": str(e)}
                )
                self.add_result(result)
        
        return self.results
    
    async def _check_server(self, server: str) -> None:
        """
        Check a single Windows server
        
        Args:
            server: Server name or IP
        """
        logger.debug(f"Checking server: {server}")
        
        checks_config = self.config.get("checks", {})
        
        # Check availability
        if checks_config.get("availability", True):
            await self._check_availability(server)
        
        # Check disk capacity
        if checks_config.get("disk_capacity", True):
            await self._check_disk_capacity(server)
        
        # Check memory
        if checks_config.get("memory", True):
            await self._check_memory(server)
        
        # Check CPU
        if checks_config.get("cpu", True):
            await self._check_cpu(server)
        
        # Check services
        if checks_config.get("services", True):
            await self._check_services(server)
        
        # Check uptime
        if checks_config.get("uptime", True):
            await self._check_uptime(server)
    
    async def _check_availability(self, server: str) -> None:
        """Check server availability (connectivity)"""
        try:
            # This would use WinRM or similar to connect
            is_available = await self.executor.test_connectivity(server)
            status = CheckStatus.HEALTHY if is_available else CheckStatus.CRITICAL
            result = HealthCheckResult(
                server=server,
                check_type="availability",
                status=status,
                details={"available": is_available}
            )
            self.add_result(result)
        except Exception as e:
            logger.error(f"Availability check failed for {server}: {str(e)}")
            result = HealthCheckResult(
                server=server,
                check_type="availability",
                status=CheckStatus.CRITICAL,
                details={"error": str(e)}
            )
            self.add_result(result)
    
    async def _check_disk_capacity(self, server: str) -> None:
        """Check disk capacity and thresholds"""
        try:
            disk_info = await self.executor.get_disk_info(server)
            threshold = self.config.get("checks", {}).get("disk_threshold_percent", 80)
            
            status = CheckStatus.HEALTHY
            for drive, usage in disk_info.items():
                if usage >= threshold:
                    status = CheckStatus.WARNING
                if usage >= 95:
                    status = CheckStatus.CRITICAL
                    break
            
            result = HealthCheckResult(
                server=server,
                check_type="disk_capacity",
                status=status,
                details={"drives": disk_info, "threshold": threshold}
            )
            self.add_result(result)
        except Exception as e:
            logger.error(f"Disk check failed for {server}: {str(e)}")
            result = HealthCheckResult(
                server=server,
                check_type="disk_capacity",
                status=CheckStatus.UNKNOWN,
                details={"error": str(e)}
            )
            self.add_result(result)
    
    async def _check_memory(self, server: str) -> None:
        """Check memory utilization"""
        try:
            memory_info = await self.executor.get_memory_info(server)
            memory_percent = memory_info.get("percent_used", 0)
            
            status = CheckStatus.HEALTHY
            if memory_percent >= 85:
                status = CheckStatus.WARNING
            if memory_percent >= 95:
                status = CheckStatus.CRITICAL
            
            result = HealthCheckResult(
                server=server,
                check_type="memory",
                status=status,
                details=memory_info
            )
            self.add_result(result)
        except Exception as e:
            logger.error(f"Memory check failed for {server}: {str(e)}")
            result = HealthCheckResult(
                server=server,
                check_type="memory",
                status=CheckStatus.UNKNOWN,
                details={"error": str(e)}
            )
            self.add_result(result)
    
    async def _check_cpu(self, server: str) -> None:
        """Check CPU utilization"""
        try:
            cpu_info = await self.executor.get_cpu_info(server)
            cpu_percent = cpu_info.get("percent", 0)
            
            status = CheckStatus.HEALTHY
            if cpu_percent >= 80:
                status = CheckStatus.WARNING
            if cpu_percent >= 95:
                status = CheckStatus.CRITICAL
            
            result = HealthCheckResult(
                server=server,
                check_type="cpu",
                status=status,
                details=cpu_info
            )
            self.add_result(result)
        except Exception as e:
            logger.error(f"CPU check failed for {server}: {str(e)}")
            result = HealthCheckResult(
                server=server,
                check_type="cpu",
                status=CheckStatus.UNKNOWN,
                details={"error": str(e)}
            )
            self.add_result(result)
    
    async def _check_services(self, server: str) -> None:
        """Check critical services status"""
        try:
            critical_services = self.config.get("checks", {}).get("critical_services", [])
            if not critical_services:
                critical_services = ["Windows Update", "BITS", "WinRM"]
            
            services_status = await self.executor.get_services_status(server, critical_services)
            
            status = CheckStatus.HEALTHY
            for service, is_running in services_status.items():
                if not is_running:
                    status = CheckStatus.WARNING
            
            result = HealthCheckResult(
                server=server,
                check_type="services",
                status=status,
                details={"services": services_status}
            )
            self.add_result(result)
        except Exception as e:
            logger.error(f"Services check failed for {server}: {str(e)}")
            result = HealthCheckResult(
                server=server,
                check_type="services",
                status=CheckStatus.UNKNOWN,
                details={"error": str(e)}
            )
            self.add_result(result)
    
    async def _check_uptime(self, server: str) -> None:
        """Check server uptime"""
        try:
            uptime_info = await self.executor.get_uptime(server)
            days_uptime = uptime_info.get("days", 0)
            
            min_uptime_days = self.config.get("checks", {}).get("min_uptime_days", 7)
            status = CheckStatus.HEALTHY
            if days_uptime < min_uptime_days:
                status = CheckStatus.WARNING
            
            result = HealthCheckResult(
                server=server,
                check_type="uptime",
                status=status,
                details=uptime_info
            )
            self.add_result(result)
        except Exception as e:
            logger.error(f"Uptime check failed for {server}: {str(e)}")
            result = HealthCheckResult(
                server=server,
                check_type="uptime",
                status=CheckStatus.UNKNOWN,
                details={"error": str(e)}
            )
            self.add_result(result)
