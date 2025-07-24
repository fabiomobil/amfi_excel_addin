"""
PL Percentage Engine - Modalidade 2
==================================

Análise de fluxo de caixa por % sobre PL.
Pagamento total sem segregação com cálculo proporcional do novo PU.

Lógica:
- Pagamento: % aplicado sobre PL atual (juros + amortização sem distinção)
- Novo PL: PL - pagamento (redução direta)
- Novo PU: current_pu × (new_pl / current_pl) (redução proporcional)

Autor: AmFi Development Team
Data: 2025-07-18
"""

from typing import Dict, Any
import pandas as pd
from datetime import datetime

try:
    from .base_cash_flow_engine import BaseCashFlowEngine
except ImportError:
    from base_cash_flow_engine import BaseCashFlowEngine


class PL_Percentage_Engine(BaseCashFlowEngine):
    """
    Engine de análise de fluxo de caixa por % sobre PL.
    
    Modalidade 2: Pagamento total proporcional
    - Pagamento = % × PL atual (sem segregação)
    - Novo PL = PL - pagamento
    - Novo PU = proporcional à redução do PL
    """
    
    def calculate_total_payment(self, payment_percentage: float, current_pl: float) -> float:
        """
        Calcula pagamento total sem segregação.
        
        Args:
            payment_percentage: Percentual do pagamento
            current_pl: PL atual do pool
            
        Returns:
            Valor do pagamento total
        """
        return payment_percentage * current_pl
    
    def calculate_new_pl(self, current_pl: float, payment_amount: float) -> float:
        """
        Calcula o novo PL após o pagamento.
        
        Args:
            current_pl: PL atual do pool
            payment_amount: Valor do pagamento
            
        Returns:
            Novo PL após pagamento
        """
        return current_pl - payment_amount
    
    def calculate_new_pu(self, current_pu: float) -> Dict[str, Any]:
        """
        Calcula o novo PU após o próximo pagamento.
        
        Modalidade 2: Redução proporcional ao PL
        Novo PU = current_pu × (new_pl / current_pl)
        
        Args:
            current_pu: PU atual do pool
            
        Returns:
            Dict com novo PU e detalhes do cálculo
        """
        try:
            # Obter próximo pagamento
            next_date, payment_percentage = self.get_next_payment_info()
            
            # Calcular componentes
            current_pl = self.get_current_pl()
            payment_amount = self.calculate_total_payment(payment_percentage, current_pl)
            new_pl = self.calculate_new_pl(current_pl, payment_amount)
            
            # Calcular novo PU (redução proporcional)
            if current_pl > 0:
                new_pu = current_pu * (new_pl / current_pl)
            else:
                raise ValueError("PL atual é zero - impossível calcular proporção")
            
            pu_change = new_pu - current_pu
            
            return {
                'calculation_method': 'proportional_reduction',
                'current_pu': current_pu,
                'current_pl': current_pl,
                'payment_amount': round(payment_amount, 2),
                'new_pl': round(new_pl, 2),
                'pl_reduction_ratio': round(new_pl / current_pl, 4),
                'new_pu': round(new_pu, 4),
                'pu_change': round(pu_change, 4),
                'segregated_flow': False,
                'next_payment_date': next_date
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular novo PU: {str(e)}")
    
    def calculate_payment_need(self) -> Dict[str, Any]:
        """
        Calcula a necessidade de pagamento do próximo vencimento.
        
        Returns:
            Dict com valor do pagamento e detalhes
        """
        try:
            # Obter próximo pagamento
            next_date, payment_percentage = self.get_next_payment_info()
            
            # Calcular valor do pagamento
            current_pl = self.get_current_pl()
            payment_amount = self.calculate_total_payment(payment_percentage, current_pl)
            
            return {
                'next_payment_date': next_date,
                'payment_percentage': payment_percentage,
                'current_pl': current_pl,
                'payment_amount': round(payment_amount, 2),
                'calculation_method': 'percentage_on_pl',
                'segregation_available': False,
                'payment_components': {
                    'total_payment': round(payment_amount, 2),
                    'note': 'Juros + amortização sem distinção'
                }
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular necessidade de pagamento: {str(e)}")


# Função de compatibilidade para uso direto
def run_pl_percentage_analysis(config: Dict[str, Any], csv_data: pd.DataFrame, 
                              xlsx_data: pd.DataFrame, current_pu: float) -> Dict[str, Any]:
    """
    Função de compatibilidade para análise por % PL.
    
    Args:
        config: Configuração JSON do pool
        csv_data: DataFrame com dados do dashboard
        xlsx_data: DataFrame com portfolio detalhado
        current_pu: PU atual do pool
        
    Returns:
        Dict com análise completa
    """
    engine = PL_Percentage_Engine(config, csv_data, xlsx_data)
    return engine.run_analysis(current_pu)


# Função factory para criar engine
def create_pl_percentage_engine(config: Dict[str, Any], csv_data: pd.DataFrame, 
                               xlsx_data: pd.DataFrame) -> PL_Percentage_Engine:
    """
    Factory function para criar engine de análise por % PL.
    
    Args:
        config: Configuração JSON do pool
        csv_data: DataFrame com dados do dashboard
        xlsx_data: DataFrame com portfolio detalhado
        
    Returns:
        Instância de PL_Percentage_Engine
    """
    return PL_Percentage_Engine(config, csv_data, xlsx_data)