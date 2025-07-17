"""
Monitor de Inadimplência - Refatorado com BaseMonitor
====================================================

Migração do monitor de inadimplência para usar BaseMonitor,
mantendo toda a funcionalidade de enriquecimento de dados.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base_monitor import BaseMonitor


class InadimplenciaMonitor(BaseMonitor):
    """
    Monitor de Inadimplência usando BaseMonitor.
    
    Mantém funcionalidade de enriquecimento progressivo do XLSX
    com campos calculados: dias_atraso, grupo_de_risco.
    """
    
    def get_monitor_type(self) -> str:
        """Return monitor type identifier."""
        return 'inadimplencia'
    
    def calculate(self) -> Dict[str, Any]:
        """
        Execute delinquency analysis with data enrichment.
        
        Enriquece XLSX global com:
        - dias_atraso: Dias em atraso calculados
        - grupo_de_risco: Classificação AA-H baseada em atraso
        """
        # Get delinquency configurations
        delinquency_configs = self._parse_delinquency_configs()
        if not delinquency_configs:
            raise ValueError("No delinquency monitors configured")
        
        # Ensure XLSX data is available
        if self.xlsx_data is None:
            raise ValueError("XLSX portfolio data required for delinquency analysis")
        
        # Enrich XLSX data globally (affects all pools)
        self._enrich_xlsx_data()
        
        # Get pool-specific data for analysis
        pool_portfolio = self.xlsx_data[self.xlsx_data['pool'] == self.pool_id].copy()
        if pool_portfolio.empty:
            raise ValueError(f"No portfolio data found for pool {self.pool_id}")
        
        # Process each delinquency configuration
        resultados = []
        for config in delinquency_configs:
            self._log_info(f"Processing delinquency window: {config['janela_dias']} days")
            
            resultado = self._process_delinquency_window(config, pool_portfolio)
            resultados.append(resultado)
        
        # Calculate overall delinquency metrics
        metricas_gerais = self._calculate_overall_metrics(pool_portfolio)
        
        # Compile results
        result = {
            'pool_id': self.pool_id,
            'resultados_por_janela': resultados,
            'metricas_gerais': metricas_gerais,
            'enriquecimento_aplicado': {
                'dias_atraso': 'dias_atraso' in self.xlsx_data.columns,
                'grupo_de_risco': 'grupo_de_risco' in self.xlsx_data.columns
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Add metadata
        self._add_metadata('total_configs_processed', len(delinquency_configs))
        self._add_metadata('portfolio_records', len(pool_portfolio))
        self._add_metadata('enrichment_applied', True)
        
        self._log_info(f"Delinquency analysis completed: {len(delinquency_configs)} windows processed")
        
        return result
    
    def _parse_delinquency_configs(self) -> List[Dict[str, Any]]:
        """Parse delinquency monitoring configurations."""
        if not self.monitor_config or 'configuracao' not in self.monitor_config:
            return []
        
        config = self.monitor_config['configuracao']
        configs = []
        
        # Parse different window configurations
        for key, limit in config.items():
            if key.startswith('janela_') and key.endswith('_dias'):
                try:
                    dias = int(key.replace('janela_', '').replace('_dias', ''))
                    configs.append({
                        'janela_dias': dias,
                        'limite': limit,
                        'tipo': 'percentual'
                    })
                except ValueError:
                    continue
        
        return configs
    
    def _enrich_xlsx_data(self) -> None:
        """
        Enrich XLSX data with calculated fields (global enrichment).
        
        This modifies the XLSX data globally, benefiting all monitors.
        """
        # Calculate dias_atraso if not already present
        if 'dias_atraso' not in self.xlsx_data.columns:
            self._log_info("Calculating 'dias_atraso' for entire portfolio")
            self.xlsx_data['dias_atraso'] = self._calculate_dias_atraso(self.xlsx_data)
            self._log_info(f"Added 'dias_atraso' column to {len(self.xlsx_data)} records")
        
        # Calculate grupo_de_risco if not already present
        if 'grupo_de_risco' not in self.xlsx_data.columns:
            self._log_info("Calculating 'grupo_de_risco' for entire portfolio")
            self.xlsx_data['grupo_de_risco'] = self._calculate_grupo_de_risco(self.xlsx_data)
            self._log_info(f"Added 'grupo_de_risco' column to {len(self.xlsx_data)} records")
    
    def _calculate_dias_atraso(self, data: pd.DataFrame) -> pd.Series:
        """Calculate days overdue for each record."""
        today = datetime.now().date()
        
        # Handle different possible column names for due date
        date_columns = ['vencimento_original', 'data_vencimento', 'due_date']
        
        vencimento_col = None
        for col in date_columns:
            if col in data.columns:
                vencimento_col = col
                break
        
        if vencimento_col is None:
            self._log_warning("No due date column found, setting dias_atraso to 0")
            return pd.Series([0] * len(data), index=data.index)
        
        # Calculate days overdue
        def calc_atraso(vencimento):
            if pd.isna(vencimento):
                return 0
            
            # Convert to date if needed
            if isinstance(vencimento, str):
                try:
                    vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
                except:
                    try:
                        vencimento = datetime.strptime(vencimento, '%d/%m/%Y').date()
                    except:
                        return 0
            elif hasattr(vencimento, 'date'):
                vencimento = vencimento.date()
            
            # Calculate difference
            diff = (today - vencimento).days
            return max(0, diff)  # Only positive days (overdue)
        
        return data[vencimento_col].apply(calc_atraso)
    
    def _calculate_grupo_de_risco(self, data: pd.DataFrame) -> pd.Series:
        """Calculate risk group based on days overdue."""
        if 'dias_atraso' not in data.columns:
            return pd.Series(['AA'] * len(data), index=data.index)
        
        def classify_risk(dias_atraso):
            if pd.isna(dias_atraso) or dias_atraso <= 0:
                return 'AA'  # Performing
            elif dias_atraso <= 30:
                return 'BB'  # 1-30 days
            elif dias_atraso <= 60:
                return 'CC'  # 31-60 days
            elif dias_atraso <= 90:
                return 'DD'  # 61-90 days
            elif dias_atraso <= 120:
                return 'EE'  # 91-120 days
            elif dias_atraso <= 180:
                return 'FF'  # 121-180 days
            elif dias_atraso <= 360:
                return 'GG'  # 181-360 days
            else:
                return 'HH'  # 360+ days
        
        return data['dias_atraso'].apply(classify_risk)
    
    def _process_delinquency_window(
        self, 
        config: Dict[str, Any], 
        portfolio_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Process delinquency analysis for a specific window."""
        
        janela_dias = config['janela_dias']
        limite = config['limite']
        
        # Filter records by window
        overdue_records = portfolio_data[portfolio_data['dias_atraso'] >= janela_dias]
        
        # Calculate metrics
        total_value = portfolio_data['valor_presente'].sum()
        overdue_value = overdue_records['valor_presente'].sum()
        
        inadimplencia_percentual = (overdue_value / total_value) if total_value > 0 else 0
        
        # Check compliance
        status = 'ok' if inadimplencia_percentual <= limite else 'violado'
        
        # Calculate space/excess
        if status == 'ok':
            espaco = (limite - inadimplencia_percentual) * total_value
            excesso = 0
        else:
            espaco = 0
            excesso = (inadimplencia_percentual - limite) * total_value
        
        return {
            'janela_dias': janela_dias,
            'limite': limite,
            'inadimplencia_percentual': inadimplencia_percentual,
            'valor_inadimplente': overdue_value,
            'total_registros_inadimplentes': len(overdue_records),
            'status': status,
            'espaco': espaco,
            'excesso': excesso
        }
    
    def _calculate_overall_metrics(self, portfolio_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall delinquency metrics."""
        total_value = portfolio_data['valor_presente'].sum()
        total_records = len(portfolio_data)
        
        # Group by risk categories
        risk_summary = portfolio_data.groupby('grupo_de_risco').agg({
            'valor_presente': 'sum',
            'pool': 'count'  # Count records
        }).rename(columns={'pool': 'count'})
        
        # Calculate percentages
        risk_summary['percentual_valor'] = risk_summary['valor_presente'] / total_value
        risk_summary['percentual_registros'] = risk_summary['count'] / total_records
        
        return {
            'total_valor': total_value,
            'total_registros': total_records,
            'distribuicao_risco': risk_summary.to_dict('index'),
            'inadimplencia_geral': {
                '30_dias': len(portfolio_data[portfolio_data['dias_atraso'] >= 30]),
                '90_dias': len(portfolio_data[portfolio_data['dias_atraso'] >= 90]),
                '180_dias': len(portfolio_data[portfolio_data['dias_atraso'] >= 180])
            }
        }


# Compatibility functions
def run_delinquency_monitoring(
    pool_id: str,
    config: Dict[str, Any],
    csv_data: pd.DataFrame, 
    xlsx_data: pd.DataFrame
) -> Dict[str, Any]:
    """Compatibility function maintaining existing API."""
    monitor = InadimplenciaMonitor(pool_id, config, csv_data, xlsx_data)
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


def _find_delinquency_monitors(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compatibility function for finding delinquency monitors."""
    monitor = InadimplenciaMonitor('temp', config, pd.DataFrame(), pd.DataFrame())
    if monitor.is_active():
        return [monitor.monitor_config]
    return []