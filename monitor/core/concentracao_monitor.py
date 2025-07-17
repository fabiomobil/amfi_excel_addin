"""
Monitor de Concentração - Refatorado com BaseMonitor
===================================================

Este monitor demonstra como migrar o monitor de concentração (1.341 linhas)
para usar a classe base, mantendo compatibilidade total com a API existente.

Benefícios da migração:
- Redução de ~200 linhas de código duplicado
- Validação e error handling padronizados
- Logs consistentes com outros monitores
- Facilita testes e manutenção
"""

import pandas as pd
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .base_monitor import BaseMonitor
from ..core.imports import import_function

# Import das funções específicas de concentração (mantidas como funções puras)
calcular_concentracao_individual = import_function('concentracao', 'calcular_concentracao_individual')
calcular_concentracao_top_n = import_function('concentracao', 'calcular_concentracao_top_n')
_process_capacity_analysis = import_function('concentracao', '_process_capacity_analysis')
_load_concentration_filters = import_function('concentracao', '_load_concentration_filters')
_filter_concentration_data = import_function('concentracao', '_filter_concentration_data')


class ConcentracaoMonitor(BaseMonitor):
    """
    Monitor de Concentração usando BaseMonitor.
    
    Este monitor refatorado mantém toda a funcionalidade original mas com:
    - Validação padronizada
    - Error handling consistente  
    - Logs estruturados
    - Código organizado e testável
    """
    
    def get_monitor_type(self) -> str:
        """Return monitor type identifier."""
        return 'concentracao'
    
    def calculate(self) -> Dict[str, Any]:
        """
        Execute concentration analysis with all existing functionality.
        
        Maintains complete compatibility with existing concentration logic
        while benefiting from BaseMonitor standardization.
        """
        # Get configuration and validate
        concentracao_configs = self._parse_concentration_configs()
        if not concentracao_configs:
            raise ValueError("No concentration monitors configured")
        
        # Load filters
        filters_config = _load_concentration_filters()
        
        # Get pool data
        pool_data = self._get_pool_data()
        if pool_data.empty:
            raise ValueError(f"No data found for pool {self.pool_id}")
        
        # Get portfolio data for concentration analysis
        if self.xlsx_data is None:
            raise ValueError("XLSX portfolio data required for concentration analysis")
        
        # Filter portfolio data for this pool
        pool_portfolio = self.xlsx_data[self.xlsx_data['pool'] == self.pool_id].copy()
        if pool_portfolio.empty:
            raise ValueError(f"No portfolio data found for pool {self.pool_id}")
        
        # Get PL from CSV data
        pl_total = self._get_pl_total(pool_data)
        
        # Execute concentration analysis for each configuration
        resultados_por_limite = []
        analises_capacidade = {}
        
        for config in concentracao_configs:
            self._log_info(f"Processing concentration config: {config['entidade']} - {config['tipo']}")
            
            resultado = self._process_single_concentration_config(
                config, pool_portfolio, pl_total, filters_config
            )
            resultados_por_limite.append(resultado)
            
            # Add capacity analysis if configured
            if config.get('analise_capacidade', False):
                analises_capacidade[config['entidade']] = self._process_capacity_analysis_for_config(
                    config, pool_portfolio, pl_total, filters_config
                )
        
        # Compile final results
        result = {
            'pool_id': self.pool_id,
            'pl_total': pl_total,
            'resultados_por_limite': resultados_por_limite,
            'timestamp': datetime.now().isoformat(),
            'filtros_aplicados': bool(filters_config.get('entidades_ignoradas'))
        }
        
        # Add capacity analysis if any was performed
        if analises_capacidade:
            result['analises_capacidade'] = analises_capacidade
        
        # Add metadata
        self._add_metadata('total_configs_processed', len(concentracao_configs))
        self._add_metadata('pl_total', pl_total)
        self._add_metadata('portfolio_records', len(pool_portfolio))
        
        self._log_info(f"Concentration analysis completed: {len(concentracao_configs)} configurations processed")
        
        return result
    
    def _parse_concentration_configs(self) -> List[Dict[str, Any]]:
        """Parse concentration monitoring configurations from pool config."""
        if not self.monitor_config:
            return []
        
        # Handle both old and new configuration formats
        configs = []
        
        # Check for direct configuration in monitor_config
        if 'configuracao' in self.monitor_config:
            base_config = self.monitor_config['configuracao']
            
            # Parse individual limits
            if 'limite_individual_cedente' in base_config:
                configs.append({
                    'tipo': 'individual',
                    'entidade': 'cedente',
                    'limite': base_config['limite_individual_cedente']
                })
            
            if 'limite_individual_sacado' in base_config:
                configs.append({
                    'tipo': 'individual', 
                    'entidade': 'sacado',
                    'limite': base_config['limite_individual_sacado']
                })
            
            # Parse top-N limits
            for key, value in base_config.items():
                if key.startswith('limite_top_') and key.endswith('_cedentes'):
                    n = key.replace('limite_top_', '').replace('_cedentes', '')
                    try:
                        n_value = int(n)
                        configs.append({
                            'tipo': 'top_n',
                            'entidade': 'cedente',
                            'n': n_value,
                            'limite': value,
                            'analise_capacidade': True
                        })
                    except ValueError:
                        continue
                
                elif key.startswith('limite_top_') and key.endswith('_sacados'):
                    n = key.replace('limite_top_', '').replace('_sacados', '')
                    try:
                        n_value = int(n)
                        configs.append({
                            'tipo': 'top_n',
                            'entidade': 'sacado', 
                            'n': n_value,
                            'limite': value,
                            'analise_capacidade': True
                        })
                    except ValueError:
                        continue
        
        return configs
    
    def _get_pl_total(self, pool_data: pd.DataFrame) -> float:
        """Extract total PL from pool data."""
        row = pool_data.iloc[0]
        
        # Try different possible column names for PL
        pl_columns = ['pl', 'PL', 'patrimonio_liquido', 'valor_presente']
        
        for col in pl_columns:
            if col in row.index and pd.notna(row[col]):
                try:
                    return float(row[col])
                except (ValueError, TypeError):
                    continue
        
        raise ValueError("Could not find valid PL value in pool data")
    
    def _process_single_concentration_config(
        self, 
        config: Dict[str, Any], 
        portfolio_data: pd.DataFrame,
        pl_total: float,
        filters_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single concentration configuration."""
        
        # Apply filters
        filtered_data = _filter_concentration_data(
            portfolio_data, config['entidade'], filters_config
        )
        
        if config['tipo'] == 'individual':
            return self._process_individual_concentration(
                config, filtered_data, pl_total
            )
        elif config['tipo'] == 'top_n':
            return self._process_top_n_concentration(
                config, filtered_data, pl_total
            )
        else:
            raise ValueError(f"Unknown concentration type: {config['tipo']}")
    
    def _process_individual_concentration(
        self,
        config: Dict[str, Any],
        portfolio_data: pd.DataFrame, 
        pl_total: float
    ) -> Dict[str, Any]:
        """Process individual concentration analysis."""
        
        # Use existing calculation function
        resultado = calcular_concentracao_individual(
            portfolio_data,
            config['entidade'],
            pl_total,
            config['limite']
        )
        
        # Add configuration info
        resultado.update({
            'tipo': 'individual',
            'entidade': config['entidade'],
            'limite_configurado': config['limite']
        })
        
        return resultado
    
    def _process_top_n_concentration(
        self,
        config: Dict[str, Any],
        portfolio_data: pd.DataFrame,
        pl_total: float
    ) -> Dict[str, Any]:
        """Process top-N concentration analysis."""
        
        # Use existing calculation function  
        resultado = calcular_concentracao_top_n(
            portfolio_data,
            config['entidade'],
            config['n'],
            pl_total,
            config['limite']
        )
        
        # Add configuration info
        resultado.update({
            'tipo': 'top_n',
            'entidade': config['entidade'],
            'n': config['n'],
            'limite_configurado': config['limite']
        })
        
        return resultado
    
    def _process_capacity_analysis_for_config(
        self,
        config: Dict[str, Any],
        portfolio_data: pd.DataFrame,
        pl_total: float,
        filters_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process capacity analysis for a configuration."""
        
        # Apply filters
        filtered_data = _filter_concentration_data(
            portfolio_data, config['entidade'], filters_config
        )
        
        # Use existing capacity analysis function
        return _process_capacity_analysis(
            filtered_data,
            config,
            pl_total
        )


# Compatibility functions - maintain existing API
def run_concentration_monitoring(
    pool_id: str,
    config: Dict[str, Any], 
    csv_data: pd.DataFrame,
    xlsx_data: pd.DataFrame
) -> Dict[str, Any]:
    """
    Compatibility function that maintains the existing API.
    
    This allows existing code to continue working unchanged while 
    benefiting from the new BaseMonitor architecture.
    """
    monitor = ConcentracaoMonitor(pool_id, config, csv_data, xlsx_data)
    result = monitor.run()
    
    # Transform result to match existing API format
    if result.status == 'success':
        return {
            'status': 'sucesso',
            'pool_id': pool_id,
            **result.data
        }
    else:
        return {
            'status': 'erro',
            'pool_id': pool_id,
            'erro': result.metadata.get('error', 'Unknown error'),
            'alerts': result.alerts
        }


def _has_concentration_monitoring(config: Dict[str, Any]) -> bool:
    """
    Compatibility function for checking if concentration monitoring is configured.
    """
    monitor = ConcentracaoMonitor('temp', config, pd.DataFrame(), pd.DataFrame())
    return monitor.is_active()


# Export both new class and compatibility functions
__all__ = [
    'ConcentracaoMonitor',
    'run_concentration_monitoring', 
    '_has_concentration_monitoring'
]