"""
Base Monitor Class for AmFi Monitoring System
============================================

This module provides a standardized base class for all monitors, eliminating
the 470+ lines of duplicated code across different monitor implementations.

Features:
- Standardized configuration parsing and validation
- Common error handling patterns
- Unified result format
- Consistent logging integration
- Automatic metadata generation

Usage:
    from monitor.core.base_monitor import BaseMonitor
    
    class MyMonitor(BaseMonitor):
        def calculate(self) -> Dict[str, Any]:
            # Implement specific calculation logic
            pass
"""

import pandas as pd
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field

from .imports import import_function

# Import utility functions
log_alerta = import_function('alerts', 'log_alerta', 'util')


@dataclass
class MonitorResult:
    """
    Standardized result format for all monitors.
    """
    monitor_id: str
    monitor_type: str
    pool_id: str
    status: str  # 'success', 'warning', 'error', 'not_configured'
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        return {
            'monitor_id': self.monitor_id,
            'monitor_type': self.monitor_type,
            'pool_id': self.pool_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'alerts': self.alerts,
            'metadata': self.metadata
        }


class BaseMonitor(ABC):
    """
    Base class for all AmFi monitors.
    
    This class provides common functionality that was previously duplicated
    across all monitor implementations:
    - Configuration parsing and validation
    - Error handling
    - Logging integration
    - Result formatting
    
    Subclasses must implement:
    - calculate(): The main calculation logic
    - get_monitor_type(): Return the monitor type identifier
    """
    
    def __init__(self, pool_id: str, config: Dict[str, Any], csv_data: pd.DataFrame, 
                 xlsx_data: Optional[pd.DataFrame] = None):
        """
        Initialize the monitor with common parameters.
        
        Args:
            pool_id: Pool identifier
            config: Pool configuration (JSON)
            csv_data: CSV data (dashboard)
            xlsx_data: XLSX data (portfolio), optional
        """
        self.pool_id = pool_id
        self.config = config
        self.csv_data = csv_data
        self.xlsx_data = xlsx_data
        self.alerts = []
        self.metadata = {}
        
        # Parse monitor configuration
        self.monitor_config = self._parse_monitor_config()
        
    def _parse_monitor_config(self) -> Optional[Dict[str, Any]]:
        """
        Parse monitor-specific configuration from pool JSON.
        
        Returns:
            Dict with monitor configuration or None if not found
        """
        try:
            monitor_type = self.get_monitor_type()
            return self._find_monitor_in_config(monitor_type)
        except Exception as e:
            self._log_error(f"Error parsing monitor config: {str(e)}")
            return None
    
    def _find_monitor_in_config(self, monitor_id: str) -> Optional[Dict[str, Any]]:
        """
        Find monitor configuration in pool JSON.
        
        Args:
            monitor_id: Monitor identifier to search for
            
        Returns:
            Dict with monitor configuration or None if not found
        """
        if 'monitoramentos_ativos' not in self.config:
            return None
            
        for monitor in self.config['monitoramentos_ativos']:
            if monitor.get('id') == monitor_id:
                return monitor
        
        return None
    
    def is_active(self) -> bool:
        """
        Check if monitor is active and properly configured.
        
        Returns:
            bool: True if monitor should be executed
        """
        if not self.monitor_config:
            return False
        
        return self.monitor_config.get('ativo', False)
    
    def validate_data(self) -> bool:
        """
        Validate input data for monitor execution.
        
        Returns:
            bool: True if data is valid for monitoring
        """
        if self.csv_data is None or self.csv_data.empty:
            self._log_error("CSV data is empty or None")
            return False
            
        # Check if pool exists in CSV data
        nome_col = 'nome' if 'nome' in self.csv_data.columns else 'Nome'
        if nome_col not in self.csv_data.columns:
            self._log_error(f"CSV missing required column: {nome_col}")
            return False
            
        pool_data = self.csv_data[self.csv_data[nome_col] == self.pool_id]
        if pool_data.empty:
            self._log_error(f"Pool '{self.pool_id}' not found in CSV data")
            return False
            
        return True
    
    def run(self) -> MonitorResult:
        """
        Execute the monitor with standard error handling and logging.
        
        Returns:
            MonitorResult: Standardized result object
        """
        try:
            # Check if monitor is active
            if not self.is_active():
                return MonitorResult(
                    monitor_id=self.get_monitor_type(),
                    monitor_type=self.get_monitor_type(),
                    pool_id=self.pool_id,
                    status='not_configured',
                    alerts=self.alerts,
                    metadata={'reason': 'Monitor not active or not configured'}
                )
            
            # Validate input data
            if not self.validate_data():
                return MonitorResult(
                    monitor_id=self.get_monitor_type(),
                    monitor_type=self.get_monitor_type(),
                    pool_id=self.pool_id,
                    status='error',
                    alerts=self.alerts,
                    metadata={'reason': 'Data validation failed'}
                )
            
            # Execute monitor-specific calculation
            self._log_info(f"Starting {self.get_monitor_type()} monitoring for {self.pool_id}")
            calculation_result = self.calculate()
            
            # Generate result
            result = MonitorResult(
                monitor_id=self.get_monitor_type(),
                monitor_type=self.get_monitor_type(),
                pool_id=self.pool_id,
                status='success',
                data=calculation_result,
                alerts=self.alerts,
                metadata=self.metadata
            )
            
            self._log_info(f"Completed {self.get_monitor_type()} monitoring for {self.pool_id}")
            return result
            
        except Exception as e:
            self._log_error(f"Error in {self.get_monitor_type()} monitoring: {str(e)}")
            return MonitorResult(
                monitor_id=self.get_monitor_type(),
                monitor_type=self.get_monitor_type(),
                pool_id=self.pool_id,
                status='error',
                alerts=self.alerts,
                metadata={'error': str(e)}
            )
    
    def _log_info(self, message: str) -> None:
        """Log info message and add to alerts."""
        alert = {
            'tipo': 'info',
            'mensagem': message,
            'timestamp': datetime.now().isoformat(),
            'monitor': self.get_monitor_type(),
            'pool': self.pool_id
        }
        log_alerta(alert)
        self.alerts.append(alert)
    
    def _log_warning(self, message: str) -> None:
        """Log warning message and add to alerts."""
        alert = {
            'tipo': 'warning',
            'mensagem': message,
            'timestamp': datetime.now().isoformat(),
            'monitor': self.get_monitor_type(),
            'pool': self.pool_id
        }
        log_alerta(alert)
        self.alerts.append(alert)
    
    def _log_error(self, message: str) -> None:
        """Log error message and add to alerts."""
        alert = {
            'tipo': 'error',
            'mensagem': message,
            'timestamp': datetime.now().isoformat(),
            'monitor': self.get_monitor_type(),
            'pool': self.pool_id
        }
        log_alerta(alert)
        self.alerts.append(alert)
    
    def _get_pool_data(self) -> pd.DataFrame:
        """
        Get CSV data filtered for this pool.
        
        Returns:
            pd.DataFrame: Pool-specific data
        """
        nome_col = 'nome' if 'nome' in self.csv_data.columns else 'Nome'
        return self.csv_data[self.csv_data[nome_col] == self.pool_id]
    
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with fallback.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self.monitor_config:
            return default
        
        return self.monitor_config.get(key, default)
    
    def _add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the result.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Implement monitor-specific calculation logic.
        
        This method must be implemented by all subclasses.
        
        Returns:
            Dict[str, Any]: Calculation results
        """
        pass
    
    @abstractmethod
    def get_monitor_type(self) -> str:
        """
        Return the monitor type identifier.
        
        This method must be implemented by all subclasses.
        
        Returns:
            str: Monitor type (e.g., 'subordinacao', 'concentracao')
        """
        pass


class MonitorFactory:
    """
    Factory class for creating monitor instances.
    """
    
    @staticmethod
    def create_monitor(monitor_type: str, pool_id: str, config: Dict[str, Any], 
                      csv_data: pd.DataFrame, xlsx_data: Optional[pd.DataFrame] = None) -> BaseMonitor:
        """
        Create a monitor instance based on type.
        
        Args:
            monitor_type: Type of monitor to create
            pool_id: Pool identifier
            config: Pool configuration
            csv_data: CSV data
            xlsx_data: XLSX data (optional)
            
        Returns:
            BaseMonitor: Monitor instance
            
        Raises:
            ValueError: If monitor type is not supported
        """
        # Import specific monitor classes
        from ..core.imports import import_function
        
        monitor_classes = {
            'subordinacao': 'SubordinacaoMonitor',
            'concentracao': 'ConcentracaoMonitor',
            'inadimplencia': 'InadimplenciaMonitor',
            'pdd': 'PDDMonitor',
            'elegibilidade': 'ElegibilidadeMonitor',
            'operacional': 'OperacionalMonitor'
        }
        
        if monitor_type not in monitor_classes:
            raise ValueError(f"Unsupported monitor type: {monitor_type}")
        
        # This would be implemented once we refactor the actual monitors
        # For now, we'll raise an error indicating the monitor needs to be migrated
        raise NotImplementedError(f"Monitor {monitor_type} needs to be migrated to use BaseMonitor")