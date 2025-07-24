"""
PU Analysis Engine - Modalidade 1
================================

Análise de fluxo de caixa por PU (Preço Unitário).
Segrega juros vs amortização com cálculo direto do novo PU.

Lógica:
- Juros: Tudo que excede PU = 1
- Amortização: Tudo que diminui PU = 1 conforme cronograma JSON
- Novo PU: current_pu - interest - amortization (redução direta)

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


class PU_Analysis_Engine(BaseCashFlowEngine):
    """
    Engine de análise de fluxo de caixa por PU.
    
    Modalidade 1: Segregar juros vs amortização
    - Juros = excesso sobre PU = 1
    - Amortização = conforme cronograma JSON
    - Novo PU = redução direta
    """
    
    def calculate_interest_flow(self, current_pu: float) -> float:
        """
        Calcula juros baseado em PU > 1.
        
        Args:
            current_pu: PU atual do pool
            
        Returns:
            Valor dos juros (excesso sobre PU = 1)
        """
        return max(0.0, current_pu - 1.0)
    
    def calculate_amortization_flow(self, next_payment_date: str) -> float:
        """
        Calcula amortização conforme cronograma JSON.
        
        Args:
            next_payment_date: Data do próximo pagamento
            
        Returns:
            Valor da amortização
        """
        try:
            # Obter percentual do cronograma
            _, payment_percentage = self.get_next_payment_info()
            
            # Aplicar sobre PL atual
            current_pl = self.get_current_pl()
            amortization_amount = payment_percentage * current_pl
            
            return amortization_amount
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular amortização: {str(e)}")
    
    def calculate_new_pu(self, current_pu: float) -> Dict[str, Any]:
        """
        Calcula o novo PU após o próximo pagamento.
        
        Modalidade 1: Redução direta
        Novo PU = current_pu - interest - amortization
        
        Args:
            current_pu: PU atual do pool
            
        Returns:
            Dict com novo PU e detalhes do cálculo
        """
        try:
            # Obter próximo pagamento
            next_date, _ = self.get_next_payment_info()
            
            # Calcular componentes
            interest = self.calculate_interest_flow(current_pu)
            amortization = self.calculate_amortization_flow(next_date)
            
            # Calcular novo PU (redução direta)
            new_pu = current_pu - interest - amortization
            pu_change = new_pu - current_pu
            
            return {
                'calculation_method': 'direct_reduction',
                'current_pu': current_pu,
                'interest_component': round(interest, 4),
                'amortization_component': round(amortization, 4),
                'new_pu': round(new_pu, 4),
                'pu_change': round(pu_change, 4),
                'segregated_flow': True,
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
            payment_amount = payment_percentage * current_pl
            
            # Segregar em juros e amortização
            # Para modalidade 1, usamos PU atual para calcular juros
            # Assumindo que temos PU atual disponível (será passado externamente)
            
            return {
                'next_payment_date': next_date,
                'payment_percentage': payment_percentage,
                'current_pl': current_pl,
                'payment_amount': round(payment_amount, 2),
                'calculation_method': 'percentage_on_pl',
                'segregation_available': True
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular necessidade de pagamento: {str(e)}")


# Função de compatibilidade para uso direto
def run_pu_analysis(config: Dict[str, Any], csv_data: pd.DataFrame, 
                   xlsx_data: pd.DataFrame, current_pu: float) -> Dict[str, Any]:
    """
    Função de compatibilidade para análise PU.
    
    Args:
        config: Configuração JSON do pool
        csv_data: DataFrame com dados do dashboard
        xlsx_data: DataFrame com portfolio detalhado
        current_pu: PU atual do pool
        
    Returns:
        Dict com análise completa
    """
    engine = PU_Analysis_Engine(config, csv_data, xlsx_data)
    return engine.run_analysis(current_pu)


# Função factory para criar engine
def create_pu_analysis_engine(config: Dict[str, Any], csv_data: pd.DataFrame, 
                             xlsx_data: pd.DataFrame) -> PU_Analysis_Engine:
    """
    Factory function para criar engine de análise PU.
    
    Args:
        config: Configuração JSON do pool
        csv_data: DataFrame com dados do dashboard
        xlsx_data: DataFrame com portfolio detalhado
        
    Returns:
        Instância de PU_Analysis_Engine
    """
    return PU_Analysis_Engine(config, csv_data, xlsx_data)