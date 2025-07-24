"""
Liquidity Scenarios - Cenários de Liquidez
==========================================

Implementa os três cenários de análise de liquidez:
1. Otimista: Caixa atual vs próximo pagamento
2. Prevista: Caixa + recebimentos previstos até próximo pagamento
3. Conservadora: Excluir cedentes/sacados com histórico de atraso

Autor: AmFi Development Team
Data: 2025-07-18
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime


class LiquidityScenarios:
    """
    Análise de liquidez em três cenários distintos.
    
    Cenários:
    1. Otimista: Apenas caixa atual
    2. Prevista: Caixa + recebimentos previstos
    3. Conservadora: Excluir entidades com histórico de atraso
    """
    
    def __init__(self, csv_data: pd.DataFrame, xlsx_data: pd.DataFrame):
        """
        Inicializa análise de cenários de liquidez.
        
        Args:
            csv_data: DataFrame com dados do dashboard
            xlsx_data: DataFrame com portfolio detalhado (enriquecido)
        """
        self.csv_data = csv_data
        self.xlsx_data = xlsx_data
        
        # Validar dependências
        if 'dias_atraso' not in xlsx_data.columns:
            raise ValueError("Campo 'dias_atraso' não encontrado - dados não foram enriquecidos")
    
    def calculate_available_cash(self) -> float:
        """
        Calcula caixa disponível (caixa + saldo em aplicações).
        
        Returns:
            Valor do caixa disponível
        """
        try:
            caixa = float(self.csv_data['caixa'].iloc[0])
            saldo_aplicacoes = float(self.csv_data['saldo em aplicações'].iloc[0])
            return caixa + saldo_aplicacoes
        except Exception as e:
            raise ValueError(f"Erro ao calcular caixa disponível: {str(e)}")
    
    def calculate_predicted_receipts(self, next_payment_date: str) -> Dict[str, Any]:
        """
        Calcula recebimentos previstos até próximo pagamento.
        
        Args:
            next_payment_date: Data do próximo pagamento
            
        Returns:
            Dict com recebimentos previstos e detalhes
        """
        try:
            # Converter data para comparação
            payment_date = datetime.strptime(next_payment_date, '%Y-%m-%d').date()
            
            # Filtrar títulos com vencimento <= próximo pagamento
            xlsx_filtered = self.xlsx_data.copy()
            xlsx_filtered['vencimento'] = pd.to_datetime(xlsx_filtered['vencimento']).dt.date
            eligible_assets = xlsx_filtered[xlsx_filtered['vencimento'] <= payment_date]
            
            # Somar valor presente dos títulos elegíveis
            total_receipts = eligible_assets['valor_presente'].sum()
            
            return {
                'total_receipts': round(total_receipts, 2),
                'eligible_assets_count': len(eligible_assets),
                'cutoff_date': next_payment_date,
                'methodology': 'all_assets_with_maturity_before_payment'
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular recebimentos previstos: {str(e)}")
    
    def identify_defaulted_entities(self) -> Dict[str, List[str]]:
        """
        Identifica cedentes e sacados com histórico de atraso.
        
        Returns:
            Dict com listas de cedentes e sacados com atraso
        """
        try:
            # Identificar entidades com dias_atraso > 0
            defaulted_data = self.xlsx_data[self.xlsx_data['dias_atraso'] > 0]
            
            defaulted_cedentes = defaulted_data['cedente'].unique().tolist()
            defaulted_sacados = defaulted_data['sacado'].unique().tolist()
            
            return {
                'cedentes': defaulted_cedentes,
                'sacados': defaulted_sacados,
                'total_defaulted_cedentes': len(defaulted_cedentes),
                'total_defaulted_sacados': len(defaulted_sacados)
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao identificar entidades inadimplentes: {str(e)}")
    
    def calculate_conservative_receipts(self, next_payment_date: str) -> Dict[str, Any]:
        """
        Calcula recebimentos conservadores excluindo entidades com atraso.
        
        Args:
            next_payment_date: Data do próximo pagamento
            
        Returns:
            Dict com recebimentos conservadores e detalhes
        """
        try:
            # Identificar entidades com atraso
            defaulted_entities = self.identify_defaulted_entities()
            
            # Filtrar títulos excluindo entidades com atraso
            xlsx_filtered = self.xlsx_data.copy()
            xlsx_filtered['vencimento'] = pd.to_datetime(xlsx_filtered['vencimento']).dt.date
            payment_date = datetime.strptime(next_payment_date, '%Y-%m-%d').date()
            
            # Excluir TODOS os ativos de cedentes/sacados com atraso
            conservative_assets = xlsx_filtered[
                (~xlsx_filtered['cedente'].isin(defaulted_entities['cedentes'])) &
                (~xlsx_filtered['sacado'].isin(defaulted_entities['sacados'])) &
                (xlsx_filtered['vencimento'] <= payment_date)
            ]
            
            # Somar valor presente dos títulos "confiáveis"
            total_receipts = conservative_assets['valor_presente'].sum()
            
            # Calcular exclusões
            all_eligible = xlsx_filtered[xlsx_filtered['vencimento'] <= payment_date]
            excluded_value = all_eligible['valor_presente'].sum() - total_receipts
            
            return {
                'total_receipts': round(total_receipts, 2),
                'eligible_assets_count': len(conservative_assets),
                'excluded_value': round(excluded_value, 2),
                'excluded_entities': defaulted_entities,
                'cutoff_date': next_payment_date,
                'methodology': 'exclude_defaulted_entities'
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular recebimentos conservadores: {str(e)}")
    
    def optimistic_scenario(self, next_payment_amount: float) -> Dict[str, Any]:
        """
        Cenário 1: Caixa atual vs próximo pagamento.
        
        Args:
            next_payment_amount: Valor do próximo pagamento
            
        Returns:
            Dict com análise do cenário otimista
        """
        try:
            available_cash = self.calculate_available_cash()
            
            return {
                'scenario': 'optimistic',
                'description': 'Apenas caixa atual vs próximo pagamento',
                'available_cash': round(available_cash, 2),
                'next_payment': round(next_payment_amount, 2),
                'sufficient': available_cash >= next_payment_amount,
                'gap': round(max(0, next_payment_amount - available_cash), 2),
                'surplus': round(max(0, available_cash - next_payment_amount), 2),
                'coverage_ratio': round(available_cash / next_payment_amount, 4) if next_payment_amount > 0 else float('inf'),
                'methodology': 'cash_only'
            }
            
        except Exception as e:
            raise ValueError(f"Erro no cenário otimista: {str(e)}")
    
    def predicted_scenario(self, next_payment_amount: float, next_payment_date: str) -> Dict[str, Any]:
        """
        Cenário 2: Caixa + recebimentos previstos até próximo pagamento.
        
        Args:
            next_payment_amount: Valor do próximo pagamento
            next_payment_date: Data do próximo pagamento
            
        Returns:
            Dict com análise do cenário previsto
        """
        try:
            available_cash = self.calculate_available_cash()
            predicted_receipts = self.calculate_predicted_receipts(next_payment_date)
            
            total_availability = available_cash + predicted_receipts['total_receipts']
            
            return {
                'scenario': 'predicted',
                'description': 'Caixa + recebimentos previstos até próximo pagamento',
                'available_cash': round(available_cash, 2),
                'predicted_receipts': predicted_receipts['total_receipts'],
                'total_availability': round(total_availability, 2),
                'next_payment': round(next_payment_amount, 2),
                'sufficient': total_availability >= next_payment_amount,
                'gap': round(max(0, next_payment_amount - total_availability), 2),
                'surplus': round(max(0, total_availability - next_payment_amount), 2),
                'coverage_ratio': round(total_availability / next_payment_amount, 4) if next_payment_amount > 0 else float('inf'),
                'receipts_details': predicted_receipts,
                'methodology': 'cash_plus_all_receipts'
            }
            
        except Exception as e:
            raise ValueError(f"Erro no cenário previsto: {str(e)}")
    
    def conservative_scenario(self, next_payment_amount: float, next_payment_date: str) -> Dict[str, Any]:
        """
        Cenário 3: Excluir cedentes/sacados com histórico de atraso.
        
        Args:
            next_payment_amount: Valor do próximo pagamento
            next_payment_date: Data do próximo pagamento
            
        Returns:
            Dict com análise do cenário conservador
        """
        try:
            available_cash = self.calculate_available_cash()
            conservative_receipts = self.calculate_conservative_receipts(next_payment_date)
            
            total_availability = available_cash + conservative_receipts['total_receipts']
            
            return {
                'scenario': 'conservative',
                'description': 'Excluir cedentes/sacados com histórico de atraso',
                'available_cash': round(available_cash, 2),
                'conservative_receipts': conservative_receipts['total_receipts'],
                'total_availability': round(total_availability, 2),
                'next_payment': round(next_payment_amount, 2),
                'sufficient': total_availability >= next_payment_amount,
                'gap': round(max(0, next_payment_amount - total_availability), 2),
                'surplus': round(max(0, total_availability - next_payment_amount), 2),
                'coverage_ratio': round(total_availability / next_payment_amount, 4) if next_payment_amount > 0 else float('inf'),
                'receipts_details': conservative_receipts,
                'methodology': 'cash_plus_conservative_receipts'
            }
            
        except Exception as e:
            raise ValueError(f"Erro no cenário conservador: {str(e)}")
    
    def run_all_scenarios(self, next_payment_amount: float, next_payment_date: str) -> Dict[str, Any]:
        """
        Executa os três cenários de liquidez.
        
        Args:
            next_payment_amount: Valor do próximo pagamento
            next_payment_date: Data do próximo pagamento
            
        Returns:
            Dict com análise dos três cenários
        """
        try:
            return {
                'optimistic': self.optimistic_scenario(next_payment_amount),
                'predicted': self.predicted_scenario(next_payment_amount, next_payment_date),
                'conservative': self.conservative_scenario(next_payment_amount, next_payment_date),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }


# Função de compatibilidade para uso direto
def run_liquidity_analysis(csv_data: pd.DataFrame, xlsx_data: pd.DataFrame, 
                          next_payment_amount: float, next_payment_date: str) -> Dict[str, Any]:
    """
    Função de compatibilidade para análise de liquidez.
    
    Args:
        csv_data: DataFrame com dados do dashboard
        xlsx_data: DataFrame com portfolio detalhado
        next_payment_amount: Valor do próximo pagamento
        next_payment_date: Data do próximo pagamento
        
    Returns:
        Dict com análise dos três cenários
    """
    scenarios = LiquidityScenarios(csv_data, xlsx_data)
    return scenarios.run_all_scenarios(next_payment_amount, next_payment_date)