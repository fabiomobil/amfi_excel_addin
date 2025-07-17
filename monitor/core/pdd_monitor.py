"""
Monitor de PDD - Refatorado com BaseMonitor
==========================================

Migração do monitor de PDD (Provisão para Devedores Duvidosos)
para usar BaseMonitor, aproveitando dados já enriquecidos.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_monitor import BaseMonitor


class PDDMonitor(BaseMonitor):
    """
    Monitor de PDD usando BaseMonitor.
    
    Aproveita dados já enriquecidos pelo monitor de inadimplência:
    - grupo_de_risco: Para aplicar percentuais de provisão
    - dias_atraso: Para validação adicional
    """
    
    def get_monitor_type(self) -> str:
        """Return monitor type identifier."""
        return 'pdd'
    
    def calculate(self) -> Dict[str, Any]:
        """
        Calculate PDD (Provision for Doubtful Debts).
        
        Uses enriched data from delinquency monitor to apply
        provision percentages by risk group.
        """
        # Ensure XLSX data is available and enriched
        if self.xlsx_data is None:
            raise ValueError("XLSX portfolio data required for PDD analysis")
        
        if 'grupo_de_risco' not in self.xlsx_data.columns:
            raise ValueError("Data must be enriched with 'grupo_de_risco' (run inadimplencia monitor first)")
        
        # Get PDD configuration
        pdd_config = self._get_pdd_percentages()
        
        # Get pool-specific data
        pool_portfolio = self.xlsx_data[self.xlsx_data['pool'] == self.pool_id].copy()
        if pool_portfolio.empty:
            raise ValueError(f"No portfolio data found for pool {self.pool_id}")
        
        # Calculate PDD by risk group
        pdd_por_grupo = self._calculate_pdd_by_risk_group(pool_portfolio, pdd_config)
        
        # Calculate totals
        totais = self._calculate_totals(pdd_por_grupo)
        
        # Get pool PL for percentage calculation
        pool_data = self._get_pool_data()
        pl_total = self._get_pl_total(pool_data)
        
        # Calculate PDD as percentage of PL
        pdd_percentual_pl = (totais['valor_pdd_total'] / pl_total) if pl_total > 0 else 0
        
        # Check if CCB (Covered Bond) limitation applies
        ccb_limitation = self._check_ccb_limitation(totais, pl_total)
        
        # Compile results
        result = {
            'pool_id': self.pool_id,
            'pl_total': pl_total,
            'pdd_por_grupo': pdd_por_grupo,
            'totais': totais,
            'pdd_percentual_pl': pdd_percentual_pl,
            'ccb_limitation': ccb_limitation,
            'configuracao_usada': pdd_config,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add metadata
        self._add_metadata('total_registros', len(pool_portfolio))
        self._add_metadata('pl_total', pl_total)
        self._add_metadata('pdd_total', totais['valor_pdd_total'])
        self._add_metadata('pdd_percentual_pl', pdd_percentual_pl)
        
        self._log_info(f"PDD calculation completed: R$ {totais['valor_pdd_total']:,.2f} ({pdd_percentual_pl:.2%} of PL)")
        
        return result
    
    def _get_pdd_percentages(self) -> Dict[str, float]:
        """Get PDD percentages from configuration."""
        # Try to get from pool configuration first
        if 'provisoes_pdd' in self.config:
            pdd_config = self.config['provisoes_pdd']
        else:
            # Use default percentages
            self._log_warning("Using default PDD percentages - no configuration found")
            pdd_config = {
                'percentual_nivel_1': 0.005,  # AA
                'percentual_nivel_2': 0.03,   # BB 
                'percentual_nivel_3': 0.1,    # CC
                'percentual_nivel_4': 0.3,    # DD
                'percentual_nivel_5': 0.6,    # EE-FF
                'percentual_nivel_6': 1.0     # GG-HH
            }
        
        # Map risk groups to provision levels
        mapping = {
            'AA': pdd_config.get('percentual_nivel_1', 0.005),
            'BB': pdd_config.get('percentual_nivel_2', 0.03),
            'CC': pdd_config.get('percentual_nivel_3', 0.1),
            'DD': pdd_config.get('percentual_nivel_4', 0.3),
            'EE': pdd_config.get('percentual_nivel_5', 0.6),
            'FF': pdd_config.get('percentual_nivel_5', 0.6),
            'GG': pdd_config.get('percentual_nivel_6', 1.0),
            'HH': pdd_config.get('percentual_nivel_6', 1.0)
        }
        
        return mapping
    
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
    
    def _calculate_pdd_by_risk_group(
        self, 
        portfolio_data: pd.DataFrame, 
        pdd_config: Dict[str, float]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate PDD provisions by risk group."""
        
        pdd_por_grupo = {}
        
        # Group by risk category
        for grupo, records in portfolio_data.groupby('grupo_de_risco'):
            if grupo not in pdd_config:
                self._log_warning(f"No PDD percentage configured for risk group '{grupo}', using 0%")
                percentual_pdd = 0.0
            else:
                percentual_pdd = pdd_config[grupo]
            
            # Calculate group metrics
            valor_total_grupo = records['valor_presente'].sum()
            quantidade_registros = len(records)
            valor_pdd_grupo = valor_total_grupo * percentual_pdd
            
            pdd_por_grupo[grupo] = {
                'quantidade_registros': quantidade_registros,
                'valor_total': valor_total_grupo,
                'percentual_pdd': percentual_pdd,
                'valor_pdd': valor_pdd_grupo
            }
        
        return pdd_por_grupo
    
    def _calculate_totals(self, pdd_por_grupo: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total PDD metrics."""
        
        total_registros = sum(grupo['quantidade_registros'] for grupo in pdd_por_grupo.values())
        valor_total_carteira = sum(grupo['valor_total'] for grupo in pdd_por_grupo.values())
        valor_pdd_total = sum(grupo['valor_pdd'] for grupo in pdd_por_grupo.values())
        
        # Calculate weighted average PDD percentage
        percentual_pdd_medio = (valor_pdd_total / valor_total_carteira) if valor_total_carteira > 0 else 0
        
        return {
            'total_registros': total_registros,
            'valor_total_carteira': valor_total_carteira,
            'valor_pdd_total': valor_pdd_total,
            'percentual_pdd_medio': percentual_pdd_medio
        }
    
    def _check_ccb_limitation(self, totais: Dict[str, Any], pl_total: float) -> Dict[str, Any]:
        """
        Check CCB (Covered Bond) limitation.
        
        CCB limitation prevents PDD calculation when certain conditions are met.
        This is a known limitation documented in the system.
        """
        # For now, implement basic check
        # TODO: Implement full CCB limitation logic based on business requirements
        
        ccb_applicable = False  # Would need business logic to determine this
        
        if ccb_applicable:
            return {
                'applicable': True,
                'reason': 'CCB limitation prevents PDD calculation',
                'action_required': 'Review CCB documentation and business rules'
            }
        else:
            return {
                'applicable': False,
                'pdd_calculation_valid': True
            }


# Compatibility functions
def run_pdd_monitoring(
    pool_id: str,
    config: Dict[str, Any],
    csv_data: pd.DataFrame,
    xlsx_data: pd.DataFrame
) -> Dict[str, Any]:
    """Compatibility function maintaining existing API."""
    monitor = PDDMonitor(pool_id, config, csv_data, xlsx_data)
    result = monitor.run()
    
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


def _has_pdd_monitoring(config: Dict[str, Any]) -> bool:
    """Compatibility function for checking if PDD monitoring is configured."""
    # Check if provisoes_pdd exists in config
    return 'provisoes_pdd' in config