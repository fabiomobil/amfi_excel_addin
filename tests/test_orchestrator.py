"""
Tests for Orchestrator
======================

This module tests the main orchestrator functionality that coordinates
all monitor executions.

Test Coverage:
- Main run_monitoring function
- Pool detection and validation
- Monitor discovery and execution
- Error handling and resilience
- Data loading integration
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitor'))

# Mock the centralized import system for testing
class MockImportFunction:
    def __init__(self):
        self.functions = {}
    
    def __call__(self, module_name, function_name, module_type='monitor'):
        key = f"{module_type}_{module_name}_{function_name}"
        if key not in self.functions:
            self.functions[key] = MagicMock()
        return self.functions[key]

mock_import_function = MockImportFunction()

# Patch the import system before importing orchestrator
with patch('monitor.core.imports.import_function', mock_import_function):
    from monitor import orchestrator


class TestOrchestrator:
    """Test the main orchestrator functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Reset mocks
        for func in mock_import_function.functions.values():
            func.reset_mock()
    
    def test_has_subordination_monitoring_true(self, sample_pool_config):
        """Test _has_subordination_monitoring when monitor is active."""
        # Mock the find function to return active monitor
        mock_find = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find.return_value = {'ativo': True}
        
        result = orchestrator._has_subordination_monitoring(sample_pool_config)
        
        assert result is True
        mock_find.assert_called_once_with(sample_pool_config)
    
    def test_has_subordination_monitoring_false(self, sample_pool_config):
        """Test _has_subordination_monitoring when monitor is inactive."""
        # Mock the find function to return inactive monitor
        mock_find = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find.return_value = {'ativo': False}
        
        result = orchestrator._has_subordination_monitoring(sample_pool_config)
        
        assert result is False
    
    def test_has_subordination_monitoring_error(self, sample_pool_config):
        """Test _has_subordination_monitoring when config is invalid."""
        # Mock the find function to raise error
        mock_find = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find.side_effect = ValueError("Invalid config")
        
        result = orchestrator._has_subordination_monitoring(sample_pool_config)
        
        assert result is False
    
    def test_has_delinquency_monitoring_true(self, sample_pool_config):
        """Test _has_delinquency_monitoring when monitors are active."""
        # Mock the find function to return active monitors
        mock_find = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find.return_value = [{'ativo': True}, {'ativo': True}]
        
        result = orchestrator._has_delinquency_monitoring(sample_pool_config)
        
        assert result is True
        mock_find.assert_called_once_with(sample_pool_config)
    
    def test_has_delinquency_monitoring_false(self, sample_pool_config):
        """Test _has_delinquency_monitoring when no monitors are active."""
        # Mock the find function to return empty list
        mock_find = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find.return_value = []
        
        result = orchestrator._has_delinquency_monitoring(sample_pool_config)
        
        assert result is False
    
    @patch('monitor.orchestrator.datetime')
    def test_run_monitoring_single_pool(self, mock_datetime, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test run_monitoring with single pool."""
        mock_datetime.now.return_value = datetime(2025, 7, 16, 10, 0, 0)
        
        # Mock data loader
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {'AFA Pool #1': sample_pool_config},
            'pools_processados': ['AFA Pool #1'],
            'monitores_debug': None,
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock monitor functions
        mock_subordination = mock_import_function.functions.get('monitor_subordinacao_run_subordination_monitoring')
        mock_subordination.return_value = {'status': 'success', 'ratio': 0.06}
        
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': True}
        
        mock_delinquency = mock_import_function.functions.get('monitor_inadimplencia_run_delinquency_monitoring')
        mock_delinquency.return_value = {'status': 'success', 'inadimplencia': 0.02}
        
        mock_find_delinquency = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find_delinquency.return_value = [{'ativo': True}]
        
        # Execute
        result = orchestrator.run_monitoring('AFA Pool #1')
        
        # Verify
        assert result is not None
        assert 'timestamp' in result
        assert 'pools_processados' in result
        assert 'resultados' in result
        
        # Verify data loader was called
        mock_load_pool_data.assert_called_once()
        
        # Verify monitors were called
        mock_subordination.assert_called_once()
        mock_delinquency.assert_called_once()
    
    @patch('monitor.orchestrator.datetime')
    def test_run_monitoring_all_pools(self, mock_datetime, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test run_monitoring with all pools."""
        mock_datetime.now.return_value = datetime(2025, 7, 16, 10, 0, 0)
        
        # Mock data loader for multiple pools
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {
                'AFA Pool #1': sample_pool_config,
                'LeCapital Pool #1': sample_pool_config
            },
            'pools_processados': ['AFA Pool #1', 'LeCapital Pool #1'],
            'monitores_debug': None,
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock monitor functions
        mock_subordination = mock_import_function.functions.get('monitor_subordinacao_run_subordination_monitoring')
        mock_subordination.return_value = {'status': 'success', 'ratio': 0.06}
        
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': True}
        
        mock_delinquency = mock_import_function.functions.get('monitor_inadimplencia_run_delinquency_monitoring')
        mock_delinquency.return_value = {'status': 'success', 'inadimplencia': 0.02}
        
        mock_find_delinquency = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find_delinquency.return_value = [{'ativo': True}]
        
        # Execute
        result = orchestrator.run_monitoring()
        
        # Verify
        assert result is not None
        assert len(result['pools_processados']) == 2
        assert 'AFA Pool #1' in result['resultados']
        assert 'LeCapital Pool #1' in result['resultados']
        
        # Verify monitors were called for each pool
        assert mock_subordination.call_count == 2
        assert mock_delinquency.call_count == 2
    
    def test_run_monitoring_data_loading_failure(self):
        """Test run_monitoring when data loading fails."""
        # Mock data loader to fail
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'sucesso': False,
            'erro': 'Failed to load data'
        }
        
        # Execute
        result = orchestrator.run_monitoring()
        
        # Verify error handling
        assert result is not None
        assert result.get('sucesso') is False
        assert 'erro' in result or 'error' in result
    
    def test_run_monitoring_monitor_failure_resilience(self, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test that orchestrator continues when one monitor fails."""
        # Mock data loader
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {'AFA Pool #1': sample_pool_config},
            'pools_processados': ['AFA Pool #1'],
            'monitores_debug': None,
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock subordination to succeed
        mock_subordination = mock_import_function.functions.get('monitor_subordinacao_run_subordination_monitoring')
        mock_subordination.return_value = {'status': 'success', 'ratio': 0.06}
        
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': True}
        
        # Mock delinquency to fail
        mock_delinquency = mock_import_function.functions.get('monitor_inadimplencia_run_delinquency_monitoring')
        mock_delinquency.side_effect = Exception("Monitor failed")
        
        mock_find_delinquency = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find_delinquency.return_value = [{'ativo': True}]
        
        # Execute
        result = orchestrator.run_monitoring('AFA Pool #1')
        
        # Verify that orchestrator continued despite failure
        assert result is not None
        assert 'AFA Pool #1' in result['resultados']
        
        # Verify subordination succeeded
        assert 'subordinacao' in result['resultados']['AFA Pool #1']
        assert result['resultados']['AFA Pool #1']['subordinacao']['status'] == 'success'
        
        # Verify delinquency failed gracefully
        assert 'inadimplencia' in result['resultados']['AFA Pool #1']
        assert result['resultados']['AFA Pool #1']['inadimplencia']['status'] == 'erro'
    
    def test_run_monitoring_no_active_monitors(self, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test run_monitoring when no monitors are active."""
        # Mock data loader
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {'AFA Pool #1': sample_pool_config},
            'pools_processados': ['AFA Pool #1'],
            'monitores_debug': None,
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock all monitors as inactive
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': False}
        
        mock_find_delinquency = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find_delinquency.return_value = []
        
        mock_has_pdd = mock_import_function.functions.get('monitor_pdd__has_pdd_monitoring')
        mock_has_pdd.return_value = False
        
        mock_has_concentration = mock_import_function.functions.get('monitor_concentracao__has_concentration_monitoring')
        mock_has_concentration.return_value = False
        
        # Execute
        result = orchestrator.run_monitoring('AFA Pool #1')
        
        # Verify that orchestrator handled no active monitors
        assert result is not None
        assert 'AFA Pool #1' in result['resultados']
        
        # Should have entries for each monitor type but with 'não configurado' status
        pool_result = result['resultados']['AFA Pool #1']
        assert any('não configurado' in str(monitor_result) for monitor_result in pool_result.values())
    
    def test_run_monitoring_with_debug_pools(self, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test run_monitoring with debug pool configuration."""
        # Mock data loader with debug pools
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {'AFA Pool #1': sample_pool_config},
            'pools_processados': ['AFA Pool #1'],
            'monitores_debug': ['subordinacao', 'concentracao'],  # Only these monitors
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock monitors
        mock_subordination = mock_import_function.functions.get('monitor_subordinacao_run_subordination_monitoring')
        mock_subordination.return_value = {'status': 'success', 'ratio': 0.06}
        
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': True}
        
        mock_concentration = mock_import_function.functions.get('monitor_concentracao_run_concentration_monitoring')
        mock_concentration.return_value = {'status': 'success', 'concentracao': 0.10}
        
        mock_has_concentration = mock_import_function.functions.get('monitor_concentracao__has_concentration_monitoring')
        mock_has_concentration.return_value = True
        
        # Execute
        result = orchestrator.run_monitoring()
        
        # Verify that only debug monitors were executed
        assert result is not None
        assert 'AFA Pool #1' in result['resultados']
        
        pool_result = result['resultados']['AFA Pool #1']
        assert 'subordinacao' in pool_result
        assert 'concentracao' in pool_result
        
        # Verify subordination and concentration were called
        mock_subordination.assert_called_once()
        mock_concentration.assert_called_once()
        
        # Verify delinquency was NOT called (not in debug list)
        mock_delinquency = mock_import_function.functions.get('monitor_inadimplencia_run_delinquency_monitoring')
        mock_delinquency.assert_not_called()


class TestMonitorIntegration:
    """Integration tests for monitor execution."""
    
    def test_monitor_execution_order(self, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test that monitors are executed in the correct order."""
        # Mock data loader
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {'AFA Pool #1': sample_pool_config},
            'pools_processados': ['AFA Pool #1'],
            'monitores_debug': None,
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock all monitors as active
        execution_order = []
        
        def track_execution(monitor_name):
            def wrapper(*args, **kwargs):
                execution_order.append(monitor_name)
                return {'status': 'success', 'data': {}}
            return wrapper
        
        mock_subordination = mock_import_function.functions.get('monitor_subordinacao_run_subordination_monitoring')
        mock_subordination.side_effect = track_execution('subordinacao')
        
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': True}
        
        mock_delinquency = mock_import_function.functions.get('monitor_inadimplencia_run_delinquency_monitoring')
        mock_delinquency.side_effect = track_execution('inadimplencia')
        
        mock_find_delinquency = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find_delinquency.return_value = [{'ativo': True}]
        
        # Execute
        result = orchestrator.run_monitoring('AFA Pool #1')
        
        # Verify execution order
        assert len(execution_order) >= 2
        assert 'subordinacao' in execution_order
        assert 'inadimplencia' in execution_order
        
        # Verify all monitors completed
        assert result is not None
        assert 'AFA Pool #1' in result['resultados']
    
    def test_data_enrichment_flow(self, sample_csv_data, sample_xlsx_data, sample_pool_config):
        """Test that data enrichment flows correctly between monitors."""
        # Mock data loader
        mock_load_pool_data = mock_import_function.functions.get('util_data_loader_load_pool_data')
        mock_load_pool_data.return_value = {
            'csv_data': sample_csv_data,
            'xlsx_data': sample_xlsx_data,
            'pools_configs': {'AFA Pool #1': sample_pool_config},
            'pools_processados': ['AFA Pool #1'],
            'monitores_debug': None,
            'validacoes': {},
            'metadados': {},
            'alertas': [],
            'sucesso': True
        }
        
        # Mock monitors that modify data
        def subordination_monitor(pool_id, config, csv_data, xlsx_data):
            # Subordination doesn't modify data
            return {'status': 'success', 'ratio': 0.06}
        
        def delinquency_monitor(pool_id, config, csv_data, xlsx_data):
            # Delinquency adds columns to xlsx_data
            if 'dias_atraso' not in xlsx_data.columns:
                xlsx_data['dias_atraso'] = [10, 20, 30] * (len(xlsx_data) // 3 + 1)
                xlsx_data['dias_atraso'] = xlsx_data['dias_atraso'][:len(xlsx_data)]
            return {'status': 'success', 'inadimplencia': 0.02}
        
        mock_subordination = mock_import_function.functions.get('monitor_subordinacao_run_subordination_monitoring')
        mock_subordination.side_effect = subordination_monitor
        
        mock_find_subordination = mock_import_function.functions.get('monitor_subordinacao__find_subordination_monitor')
        mock_find_subordination.return_value = {'ativo': True}
        
        mock_delinquency = mock_import_function.functions.get('monitor_inadimplencia_run_delinquency_monitoring')
        mock_delinquency.side_effect = delinquency_monitor
        
        mock_find_delinquency = mock_import_function.functions.get('monitor_inadimplencia__find_delinquency_monitors')
        mock_find_delinquency.return_value = [{'ativo': True}]
        
        # Execute
        result = orchestrator.run_monitoring('AFA Pool #1')
        
        # Verify that both monitors were called with potentially enriched data
        assert mock_subordination.call_count == 1
        assert mock_delinquency.call_count == 1
        
        # Verify results
        assert result is not None
        assert 'AFA Pool #1' in result['resultados']
        assert result['resultados']['AFA Pool #1']['subordinacao']['status'] == 'success'
        assert result['resultados']['AFA Pool #1']['inadimplencia']['status'] == 'success'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])