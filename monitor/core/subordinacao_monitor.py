"""
Subordinação Monitor - Refactored to use BaseMonitor
==================================================

This is an example of how the existing subordinacao monitor would be
refactored to use the new BaseMonitor class, eliminating code duplication.

This serves as a template for refactoring other monitors.
"""

import pandas as pd
from typing import Dict, Any, Optional
from .base_monitor import BaseMonitor
from ..constants import get_subordination_limit


class SubordinacaoMonitor(BaseMonitor):
    """
    Monitor de Subordinação using BaseMonitor architecture.
    
    This replaces the previous standalone functions with a class-based
    approach that eliminates code duplication.
    """
    
    def get_monitor_type(self) -> str:
        """Return monitor type identifier."""
        return 'subordinacao'
    
    def calculate(self) -> Dict[str, Any]:
        """
        Calculate subordination ratio and check limits.
        
        Returns:
            Dict containing subordination analysis results
        """
        # Get pool-specific data
        pool_data = self._get_pool_data()
        
        if pool_data.empty:
            raise ValueError(f"No data found for pool {self.pool_id}")
        
        # Extract values from pool data
        row = pool_data.iloc[0]  # Assumindo uma linha por pool
        
        # Get required values with proper column name handling
        pl_senior = self._get_numeric_value(row, ['pl_senior', 'PL Senior', 'patrimonio_senior'])
        pl_subordinado = self._get_numeric_value(row, ['pl_subordinado', 'PL Subordinado', 'patrimonio_subordinado'])
        valor_carteira = self._get_numeric_value(row, ['valor_presente', 'Valor Presente (R$)', 'carteira_total'])
        
        # Calculate subordination ratio
        subordinacao_ratio = self._calculate_subordination_ratio(pl_senior, pl_subordinado, valor_carteira)
        
        # Get limits from configuration with centralized defaults
        limite_minimo = self._get_config_value('limite_minimo', get_subordination_limit('minimum'))
        limite_critico = self._get_config_value('limite_critico', get_subordination_limit('critical'))
        
        # Check compliance
        status_resultado = self._check_subordination_limits(subordinacao_ratio, limite_minimo, limite_critico)
        
        # Add metadata
        self._add_metadata('pl_senior', pl_senior)
        self._add_metadata('pl_subordinado', pl_subordinado)
        self._add_metadata('valor_carteira', valor_carteira)
        self._add_metadata('limite_minimo', limite_minimo)
        self._add_metadata('limite_critico', limite_critico)
        
        # Generate result
        result = {
            'subordinacao_ratio': subordinacao_ratio,
            'subordinacao_percentual': subordinacao_ratio * 100,
            'limite_minimo': limite_minimo,
            'limite_critico': limite_critico,
            'status': status_resultado['status'],
            'mensagem': status_resultado['mensagem'],
            'espaco_minimo': limite_minimo - subordinacao_ratio,
            'espaco_critico': limite_critico - subordinacao_ratio,
            'detalhes': {
                'pl_senior': pl_senior,
                'pl_subordinado': pl_subordinado,
                'valor_carteira': valor_carteira,
                'calculo': f"({pl_subordinado} / {valor_carteira}) = {subordinacao_ratio:.4f}"
            }
        }
        
        # Log result
        self._log_info(f"Subordination ratio: {subordinacao_ratio:.4f} ({subordinacao_ratio*100:.2f}%)")
        self._log_info(f"Status: {status_resultado['status']} - {status_resultado['mensagem']}")
        
        return result
    
    def _get_numeric_value(self, row: pd.Series, possible_columns: list) -> float:
        """
        Extract numeric value from row using possible column names.
        
        Args:
            row: DataFrame row
            possible_columns: List of possible column names
            
        Returns:
            float: Numeric value
            
        Raises:
            ValueError: If no valid column found
        """
        for col in possible_columns:
            if col in row.index and pd.notna(row[col]):
                try:
                    return float(row[col])
                except (ValueError, TypeError):
                    continue
        
        raise ValueError(f"Could not find valid numeric value in columns: {possible_columns}")
    
    def _calculate_subordination_ratio(self, pl_senior: float, pl_subordinado: float, valor_carteira: float) -> float:
        """
        Calculate subordination ratio.
        
        Args:
            pl_senior: Senior tranche value
            pl_subordinado: Subordinated tranche value
            valor_carteira: Total portfolio value
            
        Returns:
            float: Subordination ratio
        """
        if valor_carteira <= 0:
            raise ValueError("Portfolio value must be positive")
        
        # Standard subordination ratio calculation
        return pl_subordinado / valor_carteira
    
    def _check_subordination_limits(self, ratio: float, limite_minimo: float, limite_critico: float) -> Dict[str, str]:
        """
        Check subordination ratio against limits.
        
        Args:
            ratio: Current subordination ratio
            limite_minimo: Minimum acceptable ratio
            limite_critico: Critical ratio threshold
            
        Returns:
            Dict with status and message
        """
        if ratio >= limite_minimo:
            return {
                'status': 'adequado',
                'mensagem': f'Subordinação adequada ({ratio:.2%} >= {limite_minimo:.2%})'
            }
        elif ratio >= limite_critico:
            self._log_warning(f'Subordinação próxima ao limite crítico: {ratio:.2%}')
            return {
                'status': 'atencao',
                'mensagem': f'Subordinação requer atenção ({ratio:.2%} < {limite_minimo:.2%})'
            }
        else:
            self._log_warning(f'Subordinação abaixo do limite crítico: {ratio:.2%}')
            return {
                'status': 'critico',
                'mensagem': f'Subordinação crítica ({ratio:.2%} < {limite_critico:.2%})'
            }


# Compatibility function for existing code
def run_subordination_monitoring(pool_id: str, config: Dict[str, Any], 
                               csv_data: pd.DataFrame, xlsx_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Compatibility function that maintains the existing API.
    
    This allows existing code to continue working while we migrate to the new architecture.
    """
    monitor = SubordinacaoMonitor(pool_id, config, csv_data, xlsx_data)
    result = monitor.run()
    return result.to_dict()


# _find_subordination_monitor() removed - use BaseMonitor._find_monitor_in_config() instead