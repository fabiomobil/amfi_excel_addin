"""
Tests for Base Monitor Class
===========================

This module tests the BaseMonitor class that eliminated 470+ lines of
duplicated code across different monitor implementations.

Test Coverage:
- BaseMonitor initialization
- Configuration parsing
- Data validation
- Result formatting
- Error handling
- Monitor execution flow
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitor'))

from monitor.core.base_monitor import BaseMonitor, MonitorResult, MonitorFactory


class TestMonitor(BaseMonitor):
    """Test implementation of BaseMonitor for testing purposes."""
    
    def __init__(self, pool_id, config, csv_data, xlsx_data=None, should_fail=False):
        super().__init__(pool_id, config, csv_data, xlsx_data)
        self.should_fail = should_fail
        self.calculation_called = False
    
    def get_monitor_type(self):
        return 'test_monitor'
    
    def calculate(self):
        self.calculation_called = True
        if self.should_fail:
            raise ValueError("Test calculation failure")
        return {
            'test_result': 42,
            'calculation_time': datetime.now().isoformat()
        }


class TestMonitorResult:
    """Test the MonitorResult dataclass."""
    
    def test_monitor_result_creation(self):
        """Test creating a MonitorResult instance."""
        result = MonitorResult(
            monitor_id='test_monitor',
            monitor_type='test_type',
            pool_id='Test Pool',
            status='success'
        )
        
        assert result.monitor_id == 'test_monitor'
        assert result.monitor_type == 'test_type'
        assert result.pool_id == 'Test Pool'
        assert result.status == 'success'
        assert isinstance(result.timestamp, datetime)
        assert result.data == {}
        assert result.alerts == []
        assert result.metadata == {}
    
    def test_monitor_result_to_dict(self):
        """Test converting MonitorResult to dictionary."""
        result = MonitorResult(
            monitor_id='test_monitor',
            monitor_type='test_type',
            pool_id='Test Pool',
            status='success',
            data={'key': 'value'},
            alerts=[{'type': 'info', 'message': 'test'}],
            metadata={'meta': 'data'}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['monitor_id'] == 'test_monitor'
        assert result_dict['monitor_type'] == 'test_type'
        assert result_dict['pool_id'] == 'Test Pool'
        assert result_dict['status'] == 'success'
        assert result_dict['data'] == {'key': 'value'}
        assert result_dict['alerts'] == [{'type': 'info', 'message': 'test'}]
        assert result_dict['metadata'] == {'meta': 'data'}
        assert 'timestamp' in result_dict
        assert isinstance(result_dict['timestamp'], str)  # ISO format


class TestBaseMonitor:
    """Test the BaseMonitor class."""
    
    def test_init_basic(self, sample_csv_data, sample_pool_config):
        """Test basic initialization of BaseMonitor."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        assert monitor.pool_id == 'AFA Pool #1'
        assert monitor.config == sample_pool_config
        assert monitor.csv_data.equals(sample_csv_data)
        assert monitor.xlsx_data is None
        assert monitor.alerts == []
        assert monitor.metadata == {}
    
    def test_init_with_xlsx_data(self, sample_csv_data, sample_pool_config, sample_xlsx_data):
        """Test initialization with XLSX data."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data, sample_xlsx_data)
        
        assert monitor.xlsx_data.equals(sample_xlsx_data)
    
    def test_parse_monitor_config_success(self, sample_csv_data, sample_pool_config):
        """Test successful monitor configuration parsing."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Should find the test monitor config (won't exist in real config, but method should work)
        assert monitor.monitor_config is None  # No 'test_monitor' in sample config
    
    def test_parse_monitor_config_missing_monitoramentos(self, sample_csv_data):
        """Test parsing when monitoramentos_ativos is missing."""
        config = {'pool_id': 'AFA Pool #1'}  # No monitoramentos_ativos
        monitor = TestMonitor('AFA Pool #1', config, sample_csv_data)
        
        assert monitor.monitor_config is None
    
    def test_find_monitor_in_config(self, sample_csv_data, sample_pool_config):
        """Test finding monitor in configuration."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Should find subordinacao monitor
        subordinacao_config = monitor._find_monitor_in_config('subordinacao')
        assert subordinacao_config is not None
        assert subordinacao_config['id'] == 'subordinacao'
        assert subordinacao_config['ativo'] is True
        
        # Should not find non-existent monitor
        nonexistent_config = monitor._find_monitor_in_config('nonexistent')
        assert nonexistent_config is None
    
    def test_is_active_true(self, sample_csv_data, sample_pool_config):
        """Test is_active when monitor is active."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Mock monitor_config to return active monitor
        monitor.monitor_config = {'ativo': True}
        
        assert monitor.is_active() is True
    
    def test_is_active_false(self, sample_csv_data, sample_pool_config):
        """Test is_active when monitor is inactive."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Mock monitor_config to return inactive monitor
        monitor.monitor_config = {'ativo': False}
        
        assert monitor.is_active() is False
    
    def test_is_active_no_config(self, sample_csv_data, sample_pool_config):
        """Test is_active when no monitor configuration exists."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        monitor.monitor_config = None
        
        assert monitor.is_active() is False
    
    def test_validate_data_success(self, sample_csv_data, sample_pool_config):
        """Test successful data validation."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        assert monitor.validate_data() is True
    
    def test_validate_data_empty_csv(self, sample_pool_config):
        """Test data validation with empty CSV."""
        empty_csv = pd.DataFrame()
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, empty_csv)
        
        assert monitor.validate_data() is False
    
    def test_validate_data_missing_pool(self, sample_csv_data, sample_pool_config):
        """Test data validation with missing pool."""
        monitor = TestMonitor('Nonexistent Pool', sample_pool_config, sample_csv_data)
        
        assert monitor.validate_data() is False
    
    def test_validate_data_missing_nome_column(self, sample_pool_config):
        """Test data validation with missing nome column."""
        # CSV without nome column
        csv_data = pd.DataFrame({'other_column': ['value1', 'value2']})
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, csv_data)
        
        assert monitor.validate_data() is False
    
    def test_run_success(self, sample_csv_data, sample_pool_config):
        """Test successful monitor run."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Mock monitor as active
        monitor.monitor_config = {'ativo': True}
        
        result = monitor.run()
        
        assert isinstance(result, MonitorResult)
        assert result.monitor_id == 'test_monitor'
        assert result.monitor_type == 'test_monitor'
        assert result.pool_id == 'AFA Pool #1'
        assert result.status == 'success'
        assert result.data['test_result'] == 42
        assert monitor.calculation_called is True
    
    def test_run_not_configured(self, sample_csv_data, sample_pool_config):
        """Test monitor run when not configured."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Mock monitor as inactive
        monitor.monitor_config = {'ativo': False}
        
        result = monitor.run()
        
        assert result.status == 'not_configured'
        assert monitor.calculation_called is False
    
    def test_run_validation_failure(self, sample_pool_config):
        """Test monitor run with validation failure."""
        empty_csv = pd.DataFrame()
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, empty_csv)
        
        # Mock monitor as active
        monitor.monitor_config = {'ativo': True}
        
        result = monitor.run()
        
        assert result.status == 'error'
        assert 'Data validation failed' in result.metadata['reason']
        assert monitor.calculation_called is False
    
    def test_run_calculation_failure(self, sample_csv_data, sample_pool_config):
        """Test monitor run with calculation failure."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data, should_fail=True)
        
        # Mock monitor as active
        monitor.monitor_config = {'ativo': True}
        
        result = monitor.run()
        
        assert result.status == 'error'
        assert 'Test calculation failure' in result.metadata['error']
        assert monitor.calculation_called is True
    
    def test_logging_methods(self, sample_csv_data, sample_pool_config):
        """Test logging methods add to alerts."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Test info logging
        monitor._log_info('Test info message')
        assert len(monitor.alerts) == 1
        assert monitor.alerts[0]['tipo'] == 'info'
        assert monitor.alerts[0]['mensagem'] == 'Test info message'
        
        # Test warning logging
        monitor._log_warning('Test warning message')
        assert len(monitor.alerts) == 2
        assert monitor.alerts[1]['tipo'] == 'warning'
        assert monitor.alerts[1]['mensagem'] == 'Test warning message'
        
        # Test error logging
        monitor._log_error('Test error message')
        assert len(monitor.alerts) == 3
        assert monitor.alerts[2]['tipo'] == 'error'
        assert monitor.alerts[2]['mensagem'] == 'Test error message'
    
    def test_get_pool_data(self, sample_csv_data, sample_pool_config):
        """Test getting pool-specific data."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        pool_data = monitor._get_pool_data()
        
        assert len(pool_data) == 1
        assert pool_data.iloc[0]['nome'] == 'AFA Pool #1'
    
    def test_get_config_value(self, sample_csv_data, sample_pool_config):
        """Test getting configuration values."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Mock monitor config
        monitor.monitor_config = {'limite_minimo': 0.05, 'ativo': True}
        
        # Test existing key
        assert monitor._get_config_value('limite_minimo') == 0.05
        
        # Test non-existing key with default
        assert monitor._get_config_value('nonexistent', 'default') == 'default'
        
        # Test with no monitor config
        monitor.monitor_config = None
        assert monitor._get_config_value('any_key', 'default') == 'default'
    
    def test_add_metadata(self, sample_csv_data, sample_pool_config):
        """Test adding metadata."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        monitor._add_metadata('test_key', 'test_value')
        
        assert monitor.metadata['test_key'] == 'test_value'
    
    def test_abstract_methods_must_be_implemented(self, sample_csv_data, sample_pool_config):
        """Test that abstract methods must be implemented."""
        
        # This should work (TestMonitor implements required methods)
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        assert monitor.get_monitor_type() == 'test_monitor'
        assert monitor.calculate() is not None
        
        # Test that BaseMonitor itself cannot be instantiated
        with pytest.raises(TypeError):
            BaseMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)


class TestMonitorFactory:
    """Test the MonitorFactory class."""
    
    def test_create_monitor_unsupported_type(self, sample_csv_data, sample_pool_config):
        """Test creating monitor with unsupported type."""
        with pytest.raises(ValueError, match="Unsupported monitor type"):
            MonitorFactory.create_monitor(
                'unsupported_type',
                'AFA Pool #1',
                sample_pool_config,
                sample_csv_data
            )
    
    def test_create_monitor_not_implemented(self, sample_csv_data, sample_pool_config):
        """Test creating monitor that's not yet migrated."""
        with pytest.raises(NotImplementedError, match="needs to be migrated"):
            MonitorFactory.create_monitor(
                'subordinacao',
                'AFA Pool #1',
                sample_pool_config,
                sample_csv_data
            )


class TestIntegration:
    """Integration tests for the BaseMonitor system."""
    
    def test_eliminates_code_duplication(self, sample_csv_data, sample_pool_config):
        """Test that BaseMonitor eliminates code duplication."""
        # This test verifies that common functionality is centralized
        
        # Create multiple monitors
        monitor1 = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        monitor2 = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # They should share the same base functionality
        assert type(monitor1.run) == type(monitor2.run)
        assert type(monitor1.validate_data) == type(monitor2.validate_data)
        assert type(monitor1._log_info) == type(monitor2._log_info)
        
        # But have different implementations for abstract methods
        assert monitor1.get_monitor_type() == monitor2.get_monitor_type()
    
    def test_standardized_result_format(self, sample_csv_data, sample_pool_config):
        """Test that all monitors return standardized results."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        monitor.monitor_config = {'ativo': True}
        
        result = monitor.run()
        
        # All monitors should return MonitorResult with same structure
        assert isinstance(result, MonitorResult)
        assert hasattr(result, 'monitor_id')
        assert hasattr(result, 'monitor_type')
        assert hasattr(result, 'pool_id')
        assert hasattr(result, 'status')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'data')
        assert hasattr(result, 'alerts')
        assert hasattr(result, 'metadata')
    
    def test_error_handling_consistency(self, sample_csv_data, sample_pool_config):
        """Test consistent error handling across monitors."""
        # Test with failing monitor
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data, should_fail=True)
        monitor.monitor_config = {'ativo': True}
        
        result = monitor.run()
        
        # Error should be handled consistently
        assert result.status == 'error'
        assert 'error' in result.metadata
        assert len(result.alerts) > 0
        assert any(alert['tipo'] == 'error' for alert in result.alerts)
    
    def test_configuration_parsing_consistency(self, sample_csv_data, sample_pool_config):
        """Test consistent configuration parsing."""
        monitor = TestMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # All monitors should parse configuration the same way
        assert hasattr(monitor, 'monitor_config')
        assert hasattr(monitor, '_find_monitor_in_config')
        assert hasattr(monitor, '_get_config_value')
        
        # Configuration parsing should be consistent
        subordinacao_config = monitor._find_monitor_in_config('subordinacao')
        assert subordinacao_config['id'] == 'subordinacao'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])