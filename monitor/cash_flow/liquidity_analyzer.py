"""
Liquidity Analyzer - Análise Simplificada de Liquidez
====================================================

Foco: Analisar disponibilidade de liquidez até próximo pagamento
SEM necessidade de PU - apenas análise de cobertura

Pergunta central: "Quanto haverá disponível até a data do próximo pagamento?"

Cenários:
1. Otimista: Apenas caixa atual
2. Prevista: Caixa + recebimentos previstos
3. Conservadora: Excluir cedentes/sacados com histórico de atraso

Autor: AmFi Development Team
Data: 2025-07-18
"""

from typing import Dict, Any, Tuple
import pandas as pd
from datetime import datetime


class LiquidityAnalyzer:
    """
    Analisador de liquidez simplificado.
    
    Foca apenas na disponibilidade vs necessidade de pagamento,
    sem cálculos complexos de PU ou modalidades.
    """
    
    def __init__(self, config: Dict[str, Any], csv_data: pd.DataFrame, xlsx_data: pd.DataFrame):
        """
        Inicializa analisador de liquidez.
        
        Args:
            config: Configuração JSON completa do pool
            csv_data: DataFrame com dados do dashboard
            xlsx_data: DataFrame com portfolio detalhado (enriquecido)
        """
        self.config = config
        self.csv_data = csv_data
        self.xlsx_data = xlsx_data
        
        # Validar dependências
        self._validate_data()
    
    def _validate_data(self) -> None:
        """Valida dados necessários para análise."""
        if self.csv_data.empty or self.xlsx_data.empty:
            raise ValueError("Dados CSV ou XLSX estão vazios")
        
        if 'dias_atraso' not in self.xlsx_data.columns:
            raise ValueError("Campo 'dias_atraso' não encontrado - dados não foram enriquecidos")
        
        # Check for cronograma_pagamentos (correct field name)
        if 'cronograma_pagamentos' not in self.config:
            raise ValueError("Cronograma de pagamentos não encontrado no JSON")
    
    def get_next_payment_info(self) -> Tuple[str, float, float]:
        """
        Identifica próximo pagamento e seu valor.
        
        Returns:
            Tuple com (data_pagamento, percentual, valor_pagamento)
        """
        try:
            # Get cronograma_amortizacao from cronograma_pagamentos dict
            cronograma_pagamentos = self.config.get('cronograma_pagamentos', {})
            schedule = cronograma_pagamentos.get('cronograma_amortizacao', [])
            
            if not schedule:
                raise ValueError("Cronograma de pagamentos não encontrado")
            
            # Encontrar próxima data > hoje
            today = datetime.now().date()
            
            for payment in schedule:
                payment_date = datetime.strptime(payment['data'], '%Y-%m-%d').date()
                if payment_date > today:
                    # Calcular valor do pagamento
                    current_pl = float(self.csv_data['pl'].iloc[0])
                    payment_percentage = payment['percentual']
                    payment_amount = payment_percentage * current_pl
                    
                    return payment['data'], payment_percentage, payment_amount
            
            # Se não encontrou, usar primeiro do cronograma
            first_payment = schedule[0]
            current_pl = float(self.csv_data['pl'].iloc[0])
            payment_percentage = first_payment['percentual']
            payment_amount = payment_percentage * current_pl
            
            return first_payment['data'], payment_percentage, payment_amount
            
        except Exception as e:
            raise ValueError(f"Erro ao obter próximo pagamento: {str(e)}")
    
    def calculate_available_cash(self) -> float:
        """
        Calcula caixa disponível (caixa + saldo em aplicações).
        
        Returns:
            Valor do caixa disponível
        """
        try:
            # Try different column name variations
            caixa = 0
            saldo_aplicacoes = 0
            
            # Look for caixa column variations
            if 'caixa' in self.csv_data.columns:
                caixa = float(self.csv_data['caixa'].iloc[0])
            elif 'caixa_livre' in self.csv_data.columns:
                caixa = float(self.csv_data['caixa_livre'].iloc[0])
            
            # Look for saldo em aplicações column variations
            if 'saldo em aplicações' in self.csv_data.columns:
                saldo_aplicacoes = float(self.csv_data['saldo em aplicações'].iloc[0])
            elif 'saldo_em_aplicacões' in self.csv_data.columns:
                saldo_aplicacoes = float(self.csv_data['saldo_em_aplicacões'].iloc[0])
            
            return caixa + saldo_aplicacoes
        except Exception as e:
            raise ValueError(f"Erro ao calcular caixa disponível: {str(e)}")
    
    def calculate_predicted_receipts(self, payment_date: str) -> Dict[str, Any]:
        """
        Calcula recebimentos previstos até data do pagamento.
        
        Args:
            payment_date: Data do próximo pagamento
            
        Returns:
            Dict com recebimentos previstos e detalhes
        """
        try:
            # Converter data para comparação
            cutoff_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            
            # Filtrar títulos com vencimento <= próximo pagamento
            xlsx_filtered = self.xlsx_data.copy()
            xlsx_filtered['vencimento'] = pd.to_datetime(xlsx_filtered['vencimento']).dt.date
            eligible_assets = xlsx_filtered[xlsx_filtered['vencimento'] <= cutoff_date]
            
            # Somar valor presente dos títulos elegíveis
            total_receipts = eligible_assets['valor_presente'].sum()
            
            return {
                'total_receipts': round(total_receipts, 2),
                'eligible_assets_count': len(eligible_assets),
                'total_assets_count': len(self.xlsx_data),
                'coverage_percentage': round(len(eligible_assets) / len(self.xlsx_data) * 100, 2),
                'cutoff_date': payment_date
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular recebimentos previstos: {str(e)}")
    
    def identify_defaulted_entities(self) -> Dict[str, Any]:
        """
        Identifica cedentes e sacados com histórico de atraso.
        
        Returns:
            Dict com entidades inadimplentes
        """
        try:
            # Identificar entidades com dias_atraso > 0
            defaulted_data = self.xlsx_data[self.xlsx_data['dias_atraso'] > 0]
            
            # Use correct column names
            cedente_col = 'nome_do_cedente' if 'nome_do_cedente' in defaulted_data.columns else 'cedente'
            sacado_col = 'nome_do_sacado' if 'nome_do_sacado' in defaulted_data.columns else 'sacado'
            
            defaulted_cedentes = defaulted_data[cedente_col].unique().tolist()
            defaulted_sacados = defaulted_data[sacado_col].unique().tolist()
            
            # Calcular valor em risco
            defaulted_value = defaulted_data['valor_presente'].sum()
            total_value = self.xlsx_data['valor_presente'].sum()
            
            return {
                'cedentes': defaulted_cedentes,
                'sacados': defaulted_sacados,
                'total_defaulted_cedentes': len(defaulted_cedentes),
                'total_defaulted_sacados': len(defaulted_sacados),
                'defaulted_value': round(defaulted_value, 2),
                'total_value': round(total_value, 2),
                'default_percentage': round(defaulted_value / total_value * 100, 2) if total_value > 0 else 0
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao identificar entidades inadimplentes: {str(e)}")
    
    def calculate_conservative_receipts(self, payment_date: str) -> Dict[str, Any]:
        """
        Calcula recebimentos conservadores excluindo entidades com atraso.
        
        Args:
            payment_date: Data do próximo pagamento
            
        Returns:
            Dict com recebimentos conservadores
        """
        try:
            # Identificar entidades com atraso
            defaulted_info = self.identify_defaulted_entities()
            
            # Filtrar títulos excluindo entidades com atraso
            xlsx_filtered = self.xlsx_data.copy()
            xlsx_filtered['vencimento'] = pd.to_datetime(xlsx_filtered['vencimento']).dt.date
            cutoff_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            
            # Use correct column names
            cedente_col = 'nome_do_cedente' if 'nome_do_cedente' in xlsx_filtered.columns else 'cedente'
            sacado_col = 'nome_do_sacado' if 'nome_do_sacado' in xlsx_filtered.columns else 'sacado'
            
            # Excluir TODOS os ativos de cedentes/sacados com atraso
            conservative_assets = xlsx_filtered[
                (~xlsx_filtered[cedente_col].isin(defaulted_info['cedentes'])) &
                (~xlsx_filtered[sacado_col].isin(defaulted_info['sacados'])) &
                (xlsx_filtered['vencimento'] <= cutoff_date)
            ]
            
            # Somar valor presente dos títulos "confiáveis"
            total_receipts = conservative_assets['valor_presente'].sum()
            
            # Calcular o que foi excluído
            all_eligible = xlsx_filtered[xlsx_filtered['vencimento'] <= cutoff_date]
            excluded_value = all_eligible['valor_presente'].sum() - total_receipts
            
            return {
                'total_receipts': round(total_receipts, 2),
                'eligible_assets_count': len(conservative_assets),
                'excluded_value': round(excluded_value, 2),
                'excluded_percentage': round(excluded_value / all_eligible['valor_presente'].sum() * 100, 2) if len(all_eligible) > 0 else 0,
                'defaulted_entities': defaulted_info,
                'cutoff_date': payment_date
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular recebimentos conservadores: {str(e)}")
    
    def scenario_optimistic(self, payment_amount: float) -> Dict[str, Any]:
        """
        Cenário 1: Apenas caixa atual vs próximo pagamento.
        
        Args:
            payment_amount: Valor do próximo pagamento
            
        Returns:
            Dict com análise otimista
        """
        available_cash = self.calculate_available_cash()
        
        return {
            'scenario': 'optimistic',
            'description': 'Apenas caixa atual',
            'available_cash': round(available_cash, 2),
            'payment_needed': round(payment_amount, 2),
            'sufficient': available_cash >= payment_amount,
            'gap': round(max(0, payment_amount - available_cash), 2),
            'surplus': round(max(0, available_cash - payment_amount), 2),
            'coverage_ratio': round(available_cash / payment_amount, 4) if payment_amount > 0 else float('inf')
        }
    
    def scenario_predicted(self, payment_amount: float, payment_date: str) -> Dict[str, Any]:
        """
        Cenário 2: Caixa + recebimentos previstos.
        
        Args:
            payment_amount: Valor do próximo pagamento
            payment_date: Data do próximo pagamento
            
        Returns:
            Dict com análise prevista
        """
        available_cash = self.calculate_available_cash()
        predicted_receipts = self.calculate_predicted_receipts(payment_date)
        
        total_available = available_cash + predicted_receipts['total_receipts']
        
        return {
            'scenario': 'predicted',
            'description': 'Caixa + recebimentos previstos',
            'available_cash': round(available_cash, 2),
            'predicted_receipts': predicted_receipts['total_receipts'],
            'total_available': round(total_available, 2),
            'payment_needed': round(payment_amount, 2),
            'sufficient': total_available >= payment_amount,
            'gap': round(max(0, payment_amount - total_available), 2),
            'surplus': round(max(0, total_available - payment_amount), 2),
            'coverage_ratio': round(total_available / payment_amount, 4) if payment_amount > 0 else float('inf'),
            'receipts_details': predicted_receipts
        }
    
    def scenario_conservative(self, payment_amount: float, payment_date: str) -> Dict[str, Any]:
        """
        Cenário 3: Excluir cedentes/sacados com histórico de atraso.
        
        Args:
            payment_amount: Valor do próximo pagamento
            payment_date: Data do próximo pagamento
            
        Returns:
            Dict com análise conservadora
        """
        available_cash = self.calculate_available_cash()
        conservative_receipts = self.calculate_conservative_receipts(payment_date)
        
        total_available = available_cash + conservative_receipts['total_receipts']
        
        return {
            'scenario': 'conservative',
            'description': 'Excluir cedentes/sacados com atraso',
            'available_cash': round(available_cash, 2),
            'conservative_receipts': conservative_receipts['total_receipts'],
            'total_available': round(total_available, 2),
            'payment_needed': round(payment_amount, 2),
            'sufficient': total_available >= payment_amount,
            'gap': round(max(0, payment_amount - total_available), 2),
            'surplus': round(max(0, total_available - payment_amount), 2),
            'coverage_ratio': round(total_available / payment_amount, 4) if payment_amount > 0 else float('inf'),
            'receipts_details': conservative_receipts
        }
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Executa análise completa de liquidez.
        
        Returns:
            Dict com análise completa dos três cenários
        """
        try:
            # Obter informações do próximo pagamento
            payment_date, payment_percentage, payment_amount = self.get_next_payment_info()
            
            # Executar os três cenários
            optimistic = self.scenario_optimistic(payment_amount)
            predicted = self.scenario_predicted(payment_amount, payment_date)
            conservative = self.scenario_conservative(payment_amount, payment_date)
            
            # Compilar resultado
            return {
                'pool': self.config.get('pool_name', 'Unknown'),
                'analysis_type': 'liquidity_only',
                'next_payment': {
                    'date': payment_date,
                    'percentage': payment_percentage,
                    'amount': round(payment_amount, 2),
                    'current_pl': round(float(self.csv_data['pl'].iloc[0]), 2)
                },
                'scenarios': {
                    'optimistic': optimistic,
                    'predicted': predicted,
                    'conservative': conservative
                },
                'summary': {
                    'all_scenarios_sufficient': all([
                        optimistic['sufficient'],
                        predicted['sufficient'],
                        conservative['sufficient']
                    ]),
                    'worst_case_gap': max([
                        optimistic['gap'],
                        predicted['gap'],
                        conservative['gap']
                    ]),
                    'best_case_surplus': max([
                        optimistic['surplus'],
                        predicted['surplus'],
                        conservative['surplus']
                    ])
                },
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'pool': self.config.get('pool_name', 'Unknown'),
                'analysis_type': 'liquidity_only',
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }


# Função principal para uso direto
def run_liquidity_analysis(pool_name: str) -> Dict[str, Any]:
    """
    Executa análise de liquidez simplificada.
    
    Args:
        pool_name: Nome do pool
        
    Returns:
        Dict com análise completa de liquidez
    """
    try:
        # Carregar dados
        from ..utils.data_loader import load_pool_data
        dados = load_pool_data()
        
        # Filtrar dados do pool
        if pool_name not in dados.get('pools_configs', {}):
            raise ValueError(f"Pool '{pool_name}' não encontrado")
        
        config = dados['pools_configs'][pool_name]
        csv_data = dados['csv_data']
        xlsx_data = dados['xlsx_enriched']
        
        # Executar análise
        analyzer = LiquidityAnalyzer(config, csv_data, xlsx_data)
        return analyzer.run_full_analysis()
        
    except Exception as e:
        return {
            'pool': pool_name,
            'analysis_type': 'liquidity_only',
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }


# Função para múltiplos pools
def run_multi_pool_liquidity_analysis(pool_names: list = None) -> Dict[str, Any]:
    """
    Executa análise de liquidez para múltiplos pools.
    
    Args:
        pool_names: Lista de nomes dos pools (None = todos)
        
    Returns:
        Dict com análise de múltiplos pools
    """
    try:
        # Carregar dados
        from ..utils.data_loader import load_pool_data
        dados = load_pool_data()
        
        # Determinar pools a processar
        if pool_names is None:
            pools_to_process = list(dados.get('pools_configs', {}).keys())
        else:
            pools_to_process = pool_names
        
        # Executar análise para cada pool
        results = {}
        for pool_name in pools_to_process:
            print(f"Analisando liquidez do pool: {pool_name}")
            results[pool_name] = run_liquidity_analysis(pool_name)
        
        # Compilar estatísticas
        successful_pools = [pool for pool, result in results.items() if result.get('success', False)]
        
        return {
            'analysis_type': 'multi_pool_liquidity',
            'results': results,
            'statistics': {
                'total_pools': len(pools_to_process),
                'successful': len(successful_pools),
                'success_rate': round(len(successful_pools) / len(pools_to_process) * 100, 2) if pools_to_process else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'analysis_type': 'multi_pool_liquidity',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }