"""
PDD Analysis Utility Module
==========================

Módulo para análise e processamento de dados de PDD (Provisão para Devedores Duvidosos).
Fornece funcionalidades para extrair, processar e analisar dados PDD do sistema de monitoramento.

Funcionalidades principais:
- Extração de dados PDD dos JSONs diários consolidados
- Cálculo de dias consecutivos de violação PDD
- Análise detalhada por cedente com títulos mais atrasados
- Comparação metodológica (por cedente vs individual)
- Geração de tabelas para dashboard

Autor: AmFi Development Team
Data: 2025-07-22
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd


def load_historical_monitoring_data() -> List[Dict[str, Any]]:
    """
    Carrega dados históricos de monitoramento dos arquivos JSON diários.
    
    Returns:
        Lista de dados históricos ordenados por data (mais recente primeiro)
    """
    try:
        json_dir = Path('/mnt/c/amfi/data/output/monitoring_results/daily_consolidated')
        
        if not json_dir.exists():
            print(f"⚠️ Diretório não encontrado: {json_dir}")
            return []
        
        json_files = list(json_dir.glob('*.json'))
        if not json_files:
            print(f"⚠️ Nenhum arquivo JSON encontrado em {json_dir}")
            return []
        
        historical_data = []
        
        for json_file in sorted(json_files, reverse=True):  # Mais recente primeiro
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extrair data do nome do arquivo
                date_str = json_file.stem  # Remove .json
                
                historical_data.append({
                    'date': date_str,
                    'file': str(json_file),
                    'data': data
                })
                
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"⚠️ Erro ao ler {json_file}: {e}")
                continue
        
        print(f"✅ Carregados {len(historical_data)} arquivos históricos PDD")
        return historical_data
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados históricos PDD: {e}")
        return []


def extract_pdd_data(monitoring_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrai dados PDD dos resultados de monitoramento para dashboard.
    
    Args:
        monitoring_results: Dados JSON consolidados de monitoramento
        
    Returns:
        Lista de dados PDD estruturados para tabela principal
    """
    pdd_pools = []
    pools = monitoring_results.get('pools', {})
    
    # Carregar dados históricos para cálculo de dias consecutivos
    historical_data = load_historical_monitoring_data()
    
    for pool_name, pool_data in pools.items():
        if not pool_data.get('sucesso', False):
            continue
            
        resultados = pool_data.get('resultados', {})
        pdd_result = resultados.get('pdd', {})
        
        # Verificar se PDD foi executado com sucesso
        if not pdd_result.get('sucesso', False):
            continue
        
        # Extrair dados principais
        pdd_analysis = pdd_result.get('pdd_analysis', {})
        cedente_analysis = pdd_result.get('cedente_analysis', {})
        compliance = pdd_result.get('compliance', {})
        comparacao = pdd_result.get('comparacao_metodologica', {})
        
        totais = pdd_analysis.get('totais', {})
        provisao_total_pct = totais.get('provisao_percentual', 0)
        provisao_total_valor = totais.get('provisao_valor', 0)
        carteira_valor = totais.get('carteira_valor', 0)
        
        # Determinar status baseado em limites ou thresholds
        status = 'OK'
        is_violation = False
        
        # Considerar violação se provisão > 5% (threshold ajustável)
        if provisao_total_pct > 5.0:
            status = 'ALTO RISCO'
            is_violation = True
        elif provisao_total_pct > 2.0:
            status = 'ATENÇÃO'
            is_violation = True
        
        # Encontrar pior cedente (maior provisão)
        pior_cedente = {'nome': 'N/A', 'provisao_pct': 0, 'provisao_valor': 0}
        cedentes_data = cedente_analysis.get('cedentes', {})
        
        for cedente_nome, cedente_info in cedentes_data.items():
            if cedente_info.get('provisao_pct', 0) > pior_cedente['provisao_pct']:
                pior_cedente = {
                    'nome': cedente_nome,
                    'provisao_pct': cedente_info.get('provisao_pct', 0),
                    'provisao_valor': cedente_info.get('provisao_valor', 0)
                }
        
        # Calcular dias consecutivos
        dias_consecutivos = 0
        if is_violation:
            dias_consecutivos = calculate_pdd_consecutive_violation_days(pool_name, historical_data)
        
        pdd_pools.append({
            'pool_name': pool_name,
            'status': status,
            'is_violation': is_violation,
            'dias_consecutivos': dias_consecutivos,
            'provisao_total_pct': provisao_total_pct,
            'provisao_total_valor': provisao_total_valor,
            'carteira_valor': carteira_valor,
            'total_cedentes': cedente_analysis.get('total_cedentes', 0),
            'grupos_com_exposicao': compliance.get('grupos_com_exposicao', 0),
            'pior_cedente': pior_cedente,
            'metodologia': 'Por Cedente',
            'diferenca_metodologica': comparacao.get('diferenca_percentual', 0),
            'raw_data': pdd_result  # Para uso no drilldown
        })
    
    # Ordenar por violação primeiro, depois por provisão descendente
    pdd_pools.sort(key=lambda x: (not x['is_violation'], -x['provisao_total_pct']))
    
    return pdd_pools


def calculate_pdd_consecutive_violation_days(pool_name: str, historical_data: List[Dict[str, Any]]) -> int:
    """
    Calcula dias consecutivos de violação PDD para um pool específico.
    
    Args:
        pool_name: Nome do pool
        historical_data: Dados históricos de monitoramento
        
    Returns:
        Número de dias consecutivos em violação PDD
    """
    if not historical_data:
        return 0
    
    consecutive_days = 0
    violation_threshold = 5.0  # 5% de provisão considerado violação
    
    # Percorrer histórico do mais recente para o mais antigo
    sorted_entries = sorted(historical_data, key=lambda x: x['date'], reverse=True)
    
    for entry in sorted_entries:
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name not in pools:
            continue
            
        pool_data = pools[pool_name]
        
        if not pool_data.get('sucesso', False):
            continue
            
        resultados = pool_data.get('resultados', {})
        pdd_result = resultados.get('pdd', {})
        
        if not pdd_result.get('sucesso', False):
            continue
        
        # Verificar se está em violação PDD
        pdd_analysis = pdd_result.get('pdd_analysis', {})
        totais = pdd_analysis.get('totais', {})
        provisao_pct = totais.get('provisao_percentual', 0)
        
        if provisao_pct > violation_threshold:
            consecutive_days += 1
        else:
            break  # Sequência de violação quebrada
    
    return consecutive_days


def get_pdd_pool_historical_analysis(pool_name: str, entity_type: str, entity_name: str, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Obter análise histórica de PDD para um pool específico.
    
    Args:
        pool_name: Nome do pool
        entity_type: Tipo de entidade (não usado em PDD, mantido por compatibilidade)
        entity_name: Nome da entidade (não usado em PDD, mantido por compatibilidade)
        historical_data: Dados históricos
        
    Returns:
        Lista com histórico de PDD do pool
    """
    analysis = []
    
    # Limitar aos últimos 10 registros
    sorted_data = sorted(historical_data, key=lambda x: x['date'], reverse=True)[:10]
    
    for entry in sorted_data:
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name not in pools:
            continue
            
        pool_data = pools[pool_name]
        
        if not pool_data.get('sucesso', False):
            analysis.append({
                'date': entry['date'],
                'status': 'ERRO',
                'provisao_pct': 0,
                'provisao_valor': 0,
                'cedentes': 0
            })
            continue
            
        resultados = pool_data.get('resultados', {})
        pdd_result = resultados.get('pdd', {})
        
        if not pdd_result.get('sucesso', False):
            analysis.append({
                'date': entry['date'],
                'status': 'FALHA PDD',
                'provisao_pct': 0,
                'provisao_valor': 0,
                'cedentes': 0
            })
            continue
        
        # Extrair métricas PDD
        pdd_analysis = pdd_result.get('pdd_analysis', {})
        cedente_analysis = pdd_result.get('cedente_analysis', {})
        
        totais = pdd_analysis.get('totais', {})
        provisao_pct = totais.get('provisao_percentual', 0)
        provisao_valor = totais.get('provisao_valor', 0)
        total_cedentes = cedente_analysis.get('total_cedentes', 0)
        
        # Determinar status
        if provisao_pct > 5.0:
            status = 'ALTO RISCO'
        elif provisao_pct > 2.0:
            status = 'ATENÇÃO'
        else:
            status = 'OK'
        
        analysis.append({
            'date': entry['date'],
            'status': status,
            'provisao_pct': provisao_pct,
            'provisao_valor': provisao_valor,
            'cedentes': total_cedentes
        })
    
    return analysis


def get_pdd_cedente_breakdown_for_date(pool_name: str, date: str, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Obter breakdown detalhado por cedente para uma data específica.
    
    Args:
        pool_name: Nome do pool
        date: Data específica ou 'latest'
        historical_data: Dados históricos
        
    Returns:
        Lista com análise detalhada por cedente
    """
    # Se date é 'latest', usar a data mais recente disponível
    if date == 'latest' and historical_data:
        sorted_entries = sorted(historical_data, key=lambda x: x['date'], reverse=True)
        target_data = sorted_entries[0]['data']
    else:
        # Encontrar data específica
        target_data = None
        for entry in historical_data:
            if entry['date'] == date:
                target_data = entry['data']
                break
        
        if not target_data:
            return []
    
    pools = target_data.get('pools', {})
    
    if pool_name not in pools:
        return []
    
    pool_data = pools[pool_name]
    
    if not pool_data.get('sucesso', False):
        return []
    
    resultados = pool_data.get('resultados', {})
    pdd_result = resultados.get('pdd', {})
    
    if not pdd_result.get('sucesso', False):
        return []
    
    # Extrair análise por cedente
    cedente_analysis = pdd_result.get('cedente_analysis', {})
    cedentes_data = cedente_analysis.get('cedentes', {})
    
    breakdown_data = []
    
    for cedente_nome, cedente_info in cedentes_data.items():
        titulo_mais_atrasado = cedente_info.get('titulo_mais_atrasado', {})
        
        breakdown_data.append({
            'ranking': len(breakdown_data) + 1,
            'cedente_nome': cedente_nome,
            'total_titulos': cedente_info.get('total_titulos', 0),
            'valor_total': cedente_info.get('valor_total', 0),
            'grupo_pdd_aplicado': cedente_info.get('grupo_pdd_aplicado', 'N/A'),
            'provisao_pct': cedente_info.get('provisao_pct', 0),
            'provisao_valor': cedente_info.get('provisao_valor', 0),
            'dias_atraso_max': titulo_mais_atrasado.get('dias_atraso', 0),
            'valor_titulo_pior': titulo_mais_atrasado.get('valor', 0),
            'data_vencimento_pior': titulo_mais_atrasado.get('data_vencimento', ''),
            'grupo_original_pior': titulo_mais_atrasado.get('grupo_original', 'N/A'),
            'distribuicao_grupos': cedente_info.get('distribuicao_grupos_originais', {})
        })
    
    # Ordenar por provisão descendente
    breakdown_data.sort(key=lambda x: x['provisao_valor'], reverse=True)
    
    # Atualizar ranking após ordenação
    for i, item in enumerate(breakdown_data):
        item['ranking'] = i + 1
    
    return breakdown_data


def get_pdd_methodology_comparison(pool_name: str, date: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Obter comparação metodológica PDD (por cedente vs individual).
    
    Args:
        pool_name: Nome do pool
        date: Data específica ou 'latest'
        historical_data: Dados históricos
        
    Returns:
        Dict com comparação metodológica
    """
    # Se date é 'latest', usar a data mais recente disponível
    if date == 'latest' and historical_data:
        sorted_entries = sorted(historical_data, key=lambda x: x['date'], reverse=True)
        target_data = sorted_entries[0]['data']
        used_date = sorted_entries[0]['date']
    else:
        # Encontrar data específica
        target_data = None
        used_date = date
        for entry in historical_data:
            if entry['date'] == date:
                target_data = entry['data']
                break
        
        if not target_data:
            return {}
    
    pools = target_data.get('pools', {})
    
    if pool_name not in pools:
        return {}
    
    pool_data = pools[pool_name]
    
    if not pool_data.get('sucesso', False):
        return {}
    
    resultados = pool_data.get('resultados', {})
    pdd_result = resultados.get('pdd', {})
    
    if not pdd_result.get('sucesso', False):
        return {}
    
    # Extrair comparação metodológica
    comparacao = pdd_result.get('comparacao_metodologica', {})
    metodologia = pdd_result.get('metodologia', {})
    pdd_analysis = pdd_result.get('pdd_analysis', {})
    
    return {
        'pool_name': pool_name,
        'date': used_date,
        'provisao_por_cedente': comparacao.get('provisao_por_cedente', 0),
        'provisao_individual': comparacao.get('provisao_individual', 0),
        'diferenca_valor': comparacao.get('diferenca_valor', 0),
        'diferenca_percentual': comparacao.get('diferenca_percentual', 0),
        'metodologia_utilizada': comparacao.get('metodologia_utilizada', 'por_cedente'),
        'explicacao_metodologia': metodologia.get('explicacao', ''),
        'regra_calculo': metodologia.get('regra', ''),
        'carteira_valor': pdd_analysis.get('totais', {}).get('carteira_valor', 0),
        'grupos_configurados': len(pdd_analysis.get('grupos', {})),
        'explicacao_completa': comparacao.get('explicacao', '')
    }


# Função para debug/teste
if __name__ == "__main__":
    print("🔍 Testando módulo PDD Analysis...")
    
    # Carregar dados históricos
    historical_data = load_historical_monitoring_data()
    
    if historical_data:
        print(f"📊 Dados carregados: {len(historical_data)} arquivos")
        
        # Testar extração de dados
        latest_data = historical_data[0]['data']
        pdd_data = extract_pdd_data(latest_data)
        
        print(f"🎯 Pools com PDD: {len(pdd_data)}")
        for pool in pdd_data[:3]:  # Mostrar primeiros 3
            print(f"  - {pool['pool_name']}: {pool['provisao_total_pct']:.2f}% provisão")
    else:
        print("❌ Nenhum dado histórico encontrado")