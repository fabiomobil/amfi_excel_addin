"""
Cash Flow Orchestrator - Orquestrador de Análise de Fluxo de Caixa
================================================================

Interface principal para análise de fluxo de caixa do sistema AmFi.
Integra as duas modalidades de análise com os três cenários de liquidez.

Modalidades:
1. PU_Analysis_Engine: Segregar juros vs amortização
2. PL_Percentage_Engine: Pagamento total proporcional

Cenários de Liquidez:
1. Otimista: Caixa atual
2. Prevista: Caixa + recebimentos previstos
3. Conservadora: Excluir entidades com atraso

Autor: AmFi Development Team
Data: 2025-07-18
"""

from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime

# Imports das engines
try:
    from .pu_analysis_engine import PU_Analysis_Engine
    from .pl_percentage_engine import PL_Percentage_Engine
    from .liquidity_scenarios import LiquidityScenarios
except ImportError:
    from pu_analysis_engine import PU_Analysis_Engine
    from pl_percentage_engine import PL_Percentage_Engine
    from liquidity_scenarios import LiquidityScenarios

# Import do data_loader para carregar dados
try:
    from ..utils.data_loader import load_pool_data
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
    from data_loader import load_pool_data


def run_cash_flow_analysis(pool_name: str, current_pu: float, 
                          modality: str = "pu_analysis") -> Dict[str, Any]:
    """
    Interface principal para análise de fluxo de caixa.
    
    Args:
        pool_name: Nome do pool
        current_pu: PU atual do pool
        modality: "pu_analysis" ou "pl_percentage"
        
    Returns:
        Dict com análise completa de fluxo de caixa
    """
    try:
        # 1. Carregar dados do pool
        print(f"Carregando dados do pool: {pool_name}")
        dados = load_pool_data()
        
        # 2. Filtrar dados do pool específico
        if pool_name not in dados.get('pools_configs', {}):
            raise ValueError(f"Pool '{pool_name}' não encontrado")
        
        config = dados['pools_configs'][pool_name]
        csv_data = dados['csv_data']
        xlsx_data = dados['xlsx_enriched']  # Dados já enriquecidos
        
        # 3. Escolher engine baseado na modalidade
        if modality == "pu_analysis":
            engine = PU_Analysis_Engine(config, csv_data, xlsx_data)
        elif modality == "pl_percentage":
            engine = PL_Percentage_Engine(config, csv_data, xlsx_data)
        else:
            raise ValueError(f"Modalidade '{modality}' não suportada. Use 'pu_analysis' ou 'pl_percentage'")
        
        print(f"Executando análise com modalidade: {modality}")
        
        # 4. Executar análise de pagamento
        payment_analysis = engine.calculate_payment_need()
        new_pu_analysis = engine.calculate_new_pu(current_pu)
        
        # 5. Executar análise de liquidez
        liquidity = LiquidityScenarios(csv_data, xlsx_data)
        liquidity_scenarios = liquidity.run_all_scenarios(
            payment_analysis['payment_amount'],
            payment_analysis['next_payment_date']
        )
        
        # 6. Compilar resultado final
        result = {
            'pool': pool_name,
            'modality': modality,
            'current_pu': current_pu,
            'payment_analysis': payment_analysis,
            'new_pu_analysis': new_pu_analysis,
            'liquidity_scenarios': liquidity_scenarios,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Análise concluída com sucesso para {pool_name}")
        return result
        
    except Exception as e:
        error_result = {
            'pool': pool_name,
            'modality': modality,
            'current_pu': current_pu,
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }
        print(f"❌ Erro na análise de fluxo de caixa: {str(e)}")
        return error_result


def run_cash_flow_comparison(pool_name: str, current_pu: float) -> Dict[str, Any]:
    """
    Executa análise comparativa entre as duas modalidades.
    
    Args:
        pool_name: Nome do pool
        current_pu: PU atual do pool
        
    Returns:
        Dict com análise comparativa
    """
    try:
        # Executar análise com ambas as modalidades
        pu_analysis = run_cash_flow_analysis(pool_name, current_pu, "pu_analysis")
        pl_analysis = run_cash_flow_analysis(pool_name, current_pu, "pl_percentage")
        
        # Compilar comparação
        if pu_analysis['success'] and pl_analysis['success']:
            comparison = {
                'pool': pool_name,
                'current_pu': current_pu,
                'modality_comparison': {
                    'pu_analysis': {
                        'new_pu': pu_analysis['new_pu_analysis']['new_pu'],
                        'pu_change': pu_analysis['new_pu_analysis']['pu_change'],
                        'segregated': pu_analysis['new_pu_analysis']['segregated_flow']
                    },
                    'pl_percentage': {
                        'new_pu': pl_analysis['new_pu_analysis']['new_pu'],
                        'pu_change': pl_analysis['new_pu_analysis']['pu_change'],
                        'segregated': pl_analysis['new_pu_analysis']['segregated_flow']
                    }
                },
                'pu_difference': round(
                    pu_analysis['new_pu_analysis']['new_pu'] - pl_analysis['new_pu_analysis']['new_pu'], 
                    4
                ),
                'liquidity_comparison': {
                    'pu_analysis': pu_analysis['liquidity_scenarios'],
                    'pl_percentage': pl_analysis['liquidity_scenarios']
                },
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
            return comparison
        else:
            return {
                'pool': pool_name,
                'current_pu': current_pu,
                'pu_analysis': pu_analysis,
                'pl_analysis': pl_analysis,
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            'pool': pool_name,
            'current_pu': current_pu,
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }


def run_multi_pool_analysis(current_pus: Dict[str, float], 
                           modality: str = "pu_analysis") -> Dict[str, Any]:
    """
    Executa análise de fluxo de caixa para múltiplos pools.
    
    Args:
        current_pus: Dict com {pool_name: current_pu}
        modality: "pu_analysis" ou "pl_percentage"
        
    Returns:
        Dict com análise de múltiplos pools
    """
    try:
        results = {}
        
        for pool_name, current_pu in current_pus.items():
            print(f"Analisando pool: {pool_name}")
            results[pool_name] = run_cash_flow_analysis(pool_name, current_pu, modality)
        
        # Compilar estatísticas
        successful_pools = [pool for pool, result in results.items() if result.get('success', False)]
        failed_pools = [pool for pool, result in results.items() if not result.get('success', False)]
        
        return {
            'modality': modality,
            'results': results,
            'statistics': {
                'total_pools': len(current_pus),
                'successful': len(successful_pools),
                'failed': len(failed_pools),
                'success_rate': round(len(successful_pools) / len(current_pus) * 100, 2) if current_pus else 0,
                'successful_pools': successful_pools,
                'failed_pools': failed_pools
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'modality': modality,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Função de compatibilidade para integração com orquestrador principal
def integrate_with_main_orchestrator(pool_name: str, current_pu: float) -> Dict[str, Any]:
    """
    Integração com orquestrador principal do sistema.
    
    Args:
        pool_name: Nome do pool
        current_pu: PU atual do pool
        
    Returns:
        Dict com análise formatada para orquestrador principal
    """
    try:
        # Executar análise padrão
        analysis = run_cash_flow_analysis(pool_name, current_pu, "pu_analysis")
        
        # Formatar para compatibilidade com orquestrador principal
        if analysis['success']:
            return {
                'sucesso': True,
                'monitor': 'cash_flow_analysis',
                'pool': pool_name,
                'cash_flow_analysis': analysis,
                'timestamp': analysis['timestamp']
            }
        else:
            return {
                'sucesso': False,
                'monitor': 'cash_flow_analysis',
                'pool': pool_name,
                'erro': analysis['error'],
                'timestamp': analysis['timestamp']
            }
            
    except Exception as e:
        return {
            'sucesso': False,
            'monitor': 'cash_flow_analysis',
            'pool': pool_name,
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }