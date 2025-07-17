"""
Pytest Configuration and Fixtures for AmFi Monitoring System
===========================================================

This module provides centralized test configuration and fixtures that eliminate
the need for each test to create its own mock data.

Fixtures provided:
- sample_csv_data: Mock CSV dashboard data
- sample_xlsx_data: Mock XLSX portfolio data
- sample_pool_config: Mock pool configuration
- sample_monitor_config: Mock monitor configuration
"""

import pytest
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List


@pytest.fixture
def sample_csv_data() -> pd.DataFrame:
    """
    Create sample CSV dashboard data for testing.
    
    Returns:
        pd.DataFrame: Mock CSV data with realistic structure
    """
    data = {
        'nome': ['AFA Pool #1', 'LeCapital Pool #1', 'UnionNational Pool #5'],
        'pl_senior': [50000000, 30000000, 45000000],
        'pl_subordinado': [5000000, 3000000, 4500000],
        'pl': [55000000, 33000000, 49500000],
        'sr': [0.091, 0.091, 0.091],
        'tipo_de_produto': ['Pool', 'Pool', 'Pool'],
        'valor_presente': [52000000, 31000000, 47000000],
        'data_arquivo': [datetime.now() - timedelta(days=1)] * 3
    }
    
    df = pd.DataFrame(data)
    df.attrs = {
        'arquivo': 'test_dashboard.csv',
        'data_arquivo': datetime.now() - timedelta(days=1)
    }
    
    return df


@pytest.fixture
def sample_xlsx_data() -> pd.DataFrame:
    """
    Create sample XLSX portfolio data for testing.
    
    Returns:
        pd.DataFrame: Mock XLSX data with realistic structure
    """
    data = {
        'pool': ['AFA Pool #1'] * 5 + ['LeCapital Pool #1'] * 3 + ['UnionNational Pool #5'] * 4,
        'loan_id': [f'LOAN_{i:03d}' for i in range(1, 13)],
        'id_do_ativo': [f'ATIVO_{i:03d}' for i in range(1, 13)],
        'valor_presente': [100000, 150000, 200000, 120000, 180000,  # AFA
                          250000, 300000, 180000,  # LeCapital
                          200000, 160000, 220000, 190000],  # Union
        'vencimento_original': [datetime.now() + timedelta(days=30 + i*10) for i in range(12)],
        'data_de_aquisicao': [datetime.now() - timedelta(days=10 + i*5) for i in range(12)],
        'status': ['Performante'] * 10 + ['Inadimplente'] * 2,
        'nome_do_sacado': [f'Sacado_{i:03d}' for i in range(1, 13)],
        'nome_do_cedente': [f'Cedente_{i:03d}' for i in range(1, 13)]
    }
    
    df = pd.DataFrame(data)
    df.attrs = {
        'arquivo': 'test_portfolio.xlsx',
        'data_arquivo': datetime.now() - timedelta(days=1)
    }
    
    return df


@pytest.fixture
def sample_pool_config() -> Dict[str, Any]:
    """
    Create sample pool configuration for testing.
    
    Returns:
        Dict: Mock pool configuration with realistic structure
    """
    return {
        "pool_id": "AFA Pool #1",
        "version": "2.3",
        "monitoramentos_ativos": [
            {
                "id": "subordinacao",
                "ativo": True,
                "limite_minimo": 0.05,
                "limite_critico": 0.03,
                "configuracao": {
                    "base_calculo": "valor_carteira",
                    "frequencia": "diaria"
                }
            },
            {
                "id": "concentracao",
                "ativo": True,
                "configuracao": {
                    "limite_individual_cedente": 0.15,
                    "limite_individual_sacado": 0.10,
                    "limite_top_5_cedentes": 0.60,
                    "limite_top_10_sacados": 0.70
                }
            },
            {
                "id": "inadimplencia",
                "ativo": True,
                "configuracao": {
                    "janela_30_dias": 0.04,
                    "janela_90_dias": 0.02,
                    "janela_180_dias": 0.01
                }
            }
        ],
        "provisoes_pdd": {
            "percentual_nivel_1": 0.005,
            "percentual_nivel_2": 0.03,
            "percentual_nivel_3": 0.1,
            "percentual_nivel_4": 0.3,
            "percentual_nivel_5": 0.6,
            "percentual_nivel_6": 1.0
        }
    }


@pytest.fixture
def sample_monitor_config() -> Dict[str, Any]:
    """
    Create sample monitor configuration for testing.
    
    Returns:
        Dict: Mock monitor configuration
    """
    return {
        "id": "subordinacao",
        "ativo": True,
        "limite_minimo": 0.05,
        "limite_critico": 0.03,
        "configuracao": {
            "base_calculo": "valor_carteira",
            "frequencia": "diaria"
        }
    }


@pytest.fixture
def sample_concentration_data() -> pd.DataFrame:
    """
    Create sample data for concentration analysis testing.
    
    Returns:
        pd.DataFrame: Mock data with concentration scenarios
    """
    data = {
        'pool': ['AFA Pool #1'] * 20,
        'valor_presente': [
            # Create concentration scenario: top 3 entities have 60% of total
            1000000, 800000, 600000,  # Top 3 = 2.4M (60% of 4M total)
            200000, 150000, 100000, 100000, 50000,  # Next 5 = 600K
            50000, 40000, 30000, 30000, 20000,  # Next 5 = 170K
            20000, 10000, 10000, 10000, 10000,  # Next 5 = 60K
            10000, 10000  # Last 2 = 20K
        ],
        'nome_do_cedente': [f'Cedente_{i:02d}' for i in range(1, 21)],
        'nome_do_sacado': [f'Sacado_{i:02d}' for i in range(1, 21)]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_delinquency_data() -> pd.DataFrame:
    """
    Create sample data for delinquency analysis testing.
    
    Returns:
        pd.DataFrame: Mock data with delinquency scenarios
    """
    base_date = datetime.now().date()
    
    data = {
        'pool': ['AFA Pool #1'] * 15,
        'valor_presente': [100000] * 15,
        'vencimento_original': [
            # Create different delinquency scenarios
            base_date - timedelta(days=45),  # 45 days overdue
            base_date - timedelta(days=100), # 100 days overdue
            base_date - timedelta(days=200), # 200 days overdue
            base_date - timedelta(days=15),  # 15 days overdue
            base_date - timedelta(days=60),  # 60 days overdue
            base_date + timedelta(days=30),  # Future (performing)
            base_date + timedelta(days=60),  # Future (performing)
            base_date + timedelta(days=90),  # Future (performing)
            base_date - timedelta(days=5),   # 5 days overdue
            base_date - timedelta(days=35),  # 35 days overdue
            base_date - timedelta(days=95),  # 95 days overdue
            base_date - timedelta(days=185), # 185 days overdue
            base_date + timedelta(days=15),  # Future (performing)
            base_date + timedelta(days=45),  # Future (performing)
            base_date + timedelta(days=75),  # Future (performing)
        ],
        'nome_do_sacado': [f'Sacado_{i:02d}' for i in range(1, 16)]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def mock_file_system(tmp_path):
    """
    Create mock file system structure for testing.
    
    Args:
        tmp_path: Pytest temporary directory fixture
        
    Returns:
        Dict: Paths to mock files
    """
    # Create directory structure
    config_dir = tmp_path / "config" / "pools"
    config_dir.mkdir(parents=True)
    
    data_dir = tmp_path / "data" / "input"
    data_dir.mkdir(parents=True)
    
    # Create mock config file
    config_file = config_dir / "AFA Pool #1.json"
    config_data = {
        "pool_id": "AFA Pool #1",
        "version": "2.3",
        "monitoramentos_ativos": [
            {
                "id": "subordinacao",
                "ativo": True,
                "limite_minimo": 0.05,
                "limite_critico": 0.03
            }
        ]
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    return {
        'config_dir': str(config_dir),
        'data_dir': str(data_dir),
        'config_file': str(config_file)
    }


@pytest.fixture
def mock_alerts():
    """
    Create mock alert system for testing.
    
    Returns:
        List: Container for collected alerts
    """
    alerts = []
    
    def mock_log_alerta(alerta):
        alerts.append(alerta)
    
    return alerts, mock_log_alerta


# Test data generators
class TestDataGenerator:
    """
    Utility class for generating test data with specific characteristics.
    """
    
    @staticmethod
    def create_pool_data(pool_id: str, num_records: int = 10) -> pd.DataFrame:
        """
        Generate pool data with specified characteristics.
        
        Args:
            pool_id: Pool identifier
            num_records: Number of records to generate
            
        Returns:
            pd.DataFrame: Generated pool data
        """
        data = {
            'pool': [pool_id] * num_records,
            'loan_id': [f'LOAN_{i:03d}' for i in range(1, num_records + 1)],
            'valor_presente': [100000 + i * 10000 for i in range(num_records)],
            'nome_do_sacado': [f'Sacado_{i:02d}' for i in range(1, num_records + 1)],
            'nome_do_cedente': [f'Cedente_{i:02d}' for i in range(1, num_records + 1)]
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_concentration_scenario(total_value: float, concentration_ratio: float) -> pd.DataFrame:
        """
        Generate data with specific concentration characteristics.
        
        Args:
            total_value: Total portfolio value
            concentration_ratio: Ratio of top entity to total
            
        Returns:
            pd.DataFrame: Data with specified concentration
        """
        top_value = total_value * concentration_ratio
        remaining_value = total_value - top_value
        
        data = {
            'pool': ['Test Pool'] * 10,
            'valor_presente': [top_value] + [remaining_value / 9] * 9,
            'nome_do_cedente': [f'Cedente_{i:02d}' for i in range(1, 11)],
            'nome_do_sacado': [f'Sacado_{i:02d}' for i in range(1, 11)]
        }
        
        return pd.DataFrame(data)


@pytest.fixture
def test_data_generator():
    """
    Provide TestDataGenerator instance for tests.
    
    Returns:
        TestDataGenerator: Test data generator instance
    """
    return TestDataGenerator()


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "monitor: marks tests related to specific monitors"
    )