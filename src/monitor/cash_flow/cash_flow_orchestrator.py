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


# Função run_cash_flow_comparison removida - não utilizada no sistema


# Função run_multi_pool_analysis removida - não utilizada no sistema


# Função integrate_with_main_orchestrator removida - não utilizada no sistema