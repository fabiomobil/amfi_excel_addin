"""
Análise Detalhada de Concentração
=================================

Gera análise granular de concentração por pool com colunas específicas:
- Pool, Status, Dias Consecutivos
- Individual Cedente, Individual Sacado  
- Top N Cedentes, Top N Sacados
- Margem/Excesso de cada limite

Autor: AmFi Development Team
Data: 2025-07-21
"""

import pandas as pd
import json
import os
import glob
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

def extract_concentration_analysis(monitoring_results: Dict[str, Any]) -> pd.DataFrame:
    """
    Extrai análise detalhada de concentração de todos os pools.
    
    Args:
        monitoring_results: Resultados do monitoramento completo
        
    Returns:
        DataFrame com análise granular de concentração
    """
    analysis_data = []
    
    for pool_name, pool_result in monitoring_results.get('pools', {}).items():
        if not pool_result.get('sucesso', False):
            continue
            
        resultados = pool_result.get('resultados', {})
        concentracao_result = resultados.get('concentracao', {})
        
        if not concentracao_result.get('sucesso', False):
            continue
            
        # Dados básicos do pool
        pool_data = {
            'pool': pool_name,
            'status_geral': concentracao_result.get('status_geral', 'unknown').upper(),
            'dias_consecutivos': _calculate_consecutive_days(pool_name, concentracao_result),
            'cedente_individual_pct': None,
            'cedente_individual_nome': None,
            'cedente_individual_status': None,
            'sacado_individual_pct': None,
            'sacado_individual_nome': None, 
            'sacado_individual_status': None,
            'top_n_cedentes_pct': None,
            'top_n_cedentes_n': None,
            'top_n_cedentes_status': None,
            'top_n_sacados_pct': None,
            'top_n_sacados_n': None,
            'top_n_sacados_status': None,
            'margem_pior_violacao': 0.0
        }
        
        # Analisar resultados por limite
        resultados_por_limite = concentracao_result.get('resultados_por_limite', [])
        pior_margem = 0.0
        
        for limite_result in resultados_por_limite:
            tipo = limite_result.get('tipo', '')
            entidade = limite_result.get('entidade', '')
            status = limite_result.get('status', '')
            margem = limite_result.get('margem_limite', 0.0)
            
            # Tracking da pior violação
            if status == 'violado' and margem < pior_margem:
                pior_margem = margem
            
            # Individual Cedente
            if tipo == 'individual' and entidade == 'cedente':
                if 'maior_concentracao' in limite_result and limite_result['maior_concentracao']:
                    maior = limite_result['maior_concentracao']
                    pool_data['cedente_individual_pct'] = maior.get('percentual_pl', 0.0)
                    pool_data['cedente_individual_nome'] = maior.get('entidade', '')
                    pool_data['cedente_individual_status'] = status.upper()
                    
            # Individual Sacado
            elif tipo == 'individual' and entidade == 'sacado':
                if 'maior_concentracao' in limite_result and limite_result['maior_concentracao']:
                    maior = limite_result['maior_concentracao']
                    pool_data['sacado_individual_pct'] = maior.get('percentual_pl', 0.0)
                    pool_data['sacado_individual_nome'] = maior.get('entidade', '')
                    pool_data['sacado_individual_status'] = status.upper()
                    
            # Top N Cedentes
            elif tipo == 'top_n' and entidade == 'cedente':
                if 'concentracao_top_n' in limite_result and limite_result['concentracao_top_n']:
                    top_n = limite_result['concentracao_top_n']
                    pool_data['top_n_cedentes_pct'] = top_n.get('percentual_pl', 0.0)
                    pool_data['top_n_cedentes_n'] = limite_result.get('n', 0)
                    pool_data['top_n_cedentes_status'] = status.upper()
                    
            # Top N Sacados
            elif tipo == 'top_n' and entidade == 'sacado':
                if 'concentracao_top_n' in limite_result and limite_result['concentracao_top_n']:
                    top_n = limite_result['concentracao_top_n']
                    pool_data['top_n_sacados_pct'] = top_n.get('percentual_pl', 0.0)
                    pool_data['top_n_sacados_n'] = limite_result.get('n', 0)
                    pool_data['top_n_sacados_status'] = status.upper()
        
        pool_data['margem_pior_violacao'] = pior_margem
        analysis_data.append(pool_data)
    
    return pd.DataFrame(analysis_data)

def load_historical_monitoring_data() -> List[Dict[str, Any]]:
    """
    Carrega dados históricos de monitoramento dos últimos 10 dias.
    
    Returns:
        Lista de dicionários com dados históricos ordenados por data
    """
    daily_dir = "C:\\amfi\\data\\output\\monitoring_results\\daily_consolidated"
    
    if not os.path.exists(daily_dir):
        return []
    
    json_files = glob.glob(os.path.join(daily_dir, "*.json"))
    
    if not json_files:
        return []
    
    # Ordenar arquivos por data (mais recente primeiro)
    json_files.sort(key=lambda x: os.path.basename(x).replace('.json', ''), reverse=True)
    
    historical_data = []
    for file_path in json_files[:10]:  # Últimos 10 dias
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                date = os.path.basename(file_path).replace('.json', '')
                historical_data.append({'date': date, 'data': data})
        except Exception as e:
            print(f"⚠️ Erro ao carregar {file_path}: {e}")
            continue
    
    return historical_data

def get_entity_historical_concentration(pool_name: str, entity_type: str, entity_name: str, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrai histórico de concentração para uma entidade específica.
    
    Args:
        pool_name: Nome do pool
        entity_type: 'cedente' ou 'sacado'
        entity_name: Nome da entidade
        historical_data: Dados históricos carregados
        
    Returns:
        Lista com histórico diário da concentração
    """
    entity_history = []
    
    for entry in historical_data:
        date = entry['date']
        data = entry['data']
        
        pools = data.get('pools', {})
        if pool_name not in pools:
            continue
            
        pool_data = pools[pool_name]
        if not pool_data.get('sucesso', False):
            continue
            
        resultados = pool_data.get('resultados', {})
        concentracao = resultados.get('concentracao', {})
        
        if not concentracao.get('sucesso', False):
            continue
        
        # Buscar concentração da entidade nos resultados por limite
        resultados_por_limite = concentracao.get('resultados_por_limite', [])
        entity_concentration = None
        
        for limite_result in resultados_por_limite:
            if limite_result.get('entidade') == entity_type:
                # Para limites individuais
                if limite_result.get('tipo') == 'individual' and 'maior_concentracao' in limite_result:
                    maior_conc = limite_result['maior_concentracao']
                    if maior_conc and maior_conc.get('entidade') == entity_name:
                        entity_concentration = {
                            'percentual': maior_conc.get('percentual_pl', 0.0),
                            'valor_absoluto': maior_conc.get('valor_absoluto', 0.0),
                            'status': limite_result.get('status', 'enquadrado'),
                            'limite': limite_result.get('limite_configurado', 0.0),
                            'margem': limite_result.get('margem_limite', 0.0)
                        }
                        break
        
        if entity_concentration:
            entity_history.append({
                'date': date,
                'pool': pool_name,
                'entity_name': entity_name,
                'entity_type': entity_type,
                **entity_concentration
            })
    
    return entity_history

def get_top_n_breakdown_for_date(pool_name: str, entity_type: str, date: str, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrai breakdown detalhado do Top N para um pool, tipo de entidade e data específicos.
    
    Args:
        pool_name: Nome do pool
        entity_type: 'cedente' ou 'sacado' 
        date: Data específica (formato YYYY-MM-DD)
        historical_data: Dados históricos carregados
        
    Returns:
        Lista com breakdown do Top N daquela data
    """
    # Encontrar dados da data específica
    target_data = None
    
    if date == 'latest' and historical_data:
        # Usar os dados mais recentes (primeiro item - dados estão em ordem decrescente)
        target_data = historical_data[0]['data']
    else:
        # Buscar data específica
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
    concentracao = resultados.get('concentracao', {})
    
    if not concentracao.get('sucesso', False):
        return []
    
    # Buscar dados de análise sequencial - dados reais gerados pelo monitor
    analises = concentracao.get('analises_capacidade', {})
    top_n_breakdown = []
    
    # Procurar análise para o tipo de entidade
    for analise_key, analise_data in analises.items():
        if entity_type in analise_key.lower():
            analise_sequencial = analise_data.get('analise_sequencial', [])
            resumo = analise_data.get('resumo', {})
            
            if analise_sequencial:
                # Usar dados reais da análise sequencial gerada pelo monitor
                for item in analise_sequencial:
                    top_n_breakdown.append({
                        'ranking': item.get('posicao', 0),
                        'entity_name': item.get('entidade', '').strip(),
                        'percentual': item.get('percentual_atual', 0.0),
                        'valor_absoluto': item.get('exposicao_atual', 0.0),
                        'n_total': resumo.get('top_n_size', 0),
                        'limite_configurado': resumo.get('limite_top_n_pct', 0.0),
                        'status_geral': 'enquadrado',  # Pode ser derivado dos dados se necessário
                        'capacidade_efetiva': item.get('capacidade_efetiva', 0.0),
                        'capacidade_individual': item.get('capacidade_individual', 0.0),
                        'saldo_antes': item.get('saldo_antes', 0.0),
                        'saldo_apos': item.get('saldo_apos', 0.0),
                        'limitada_por': item.get('limitada_por', 'N/A'),
                        'explicacao': item.get('explicacao', ''),
                        # Manter compatibilidade com campos antigos
                        'espaco_disponivel': item.get('capacidade_efetiva', 0.0),
                        'motivo_limite': item.get('limitada_por', 'Top N limit')
                    })
                break
    
    # Fallback: se não encontrou análise sequencial, usar detalhamento básico
    if not top_n_breakdown:
        resultados_por_limite = concentracao.get('resultados_por_limite', [])
        
        for limite_result in resultados_por_limite:
            if (limite_result.get('tipo') == 'top_n' and 
                limite_result.get('entidade') == entity_type):
                
                n_value = limite_result.get('n', 0)
                limite_config = limite_result.get('limite_configurado', 0.0)
                status_geral = limite_result.get('status', 'enquadrado')
                
                if 'detalhamento_top_n' in limite_result:
                    detalhamento = limite_result['detalhamento_top_n']
                    for idx, item in enumerate(detalhamento, 1):
                        top_n_breakdown.append({
                            'ranking': idx,
                            'entity_name': item.get('entidade', ''),
                            'percentual': item.get('percentual_pl', 0.0),
                            'valor_absoluto': item.get('valor_absoluto', 0.0),
                            'n_total': n_value,
                            'limite_configurado': limite_config,
                            'status_geral': status_geral,
                            'espaco_disponivel': 0.0,
                            'motivo_limite': 'Top N limit (dados básicos)'
                        })
                else:
                    # Entrada genérica
                    concentracao_top_n = limite_result.get('concentracao_top_n', {})
                    top_n_breakdown.append({
                        'ranking': 'Total',
                        'entity_name': f'Top {n_value} {entity_type}s (total)',
                        'percentual': concentracao_top_n.get('percentual_pl', 0.0),
                        'valor_absoluto': concentracao_top_n.get('valor_absoluto', 0.0),
                        'n_total': n_value,
                        'limite_configurado': limite_config,
                        'status_geral': status_geral,
                        'note': 'Detalhamento não disponível'
                    })
                break
    
    return top_n_breakdown

def get_entity_allocation_margins(pool_name: str, entity_type: str, entity_name: str, date: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extrai margens de alocação detalhadas para uma entidade específica em uma data.
    
    Args:
        pool_name: Nome do pool
        entity_type: 'cedente' ou 'sacado'
        entity_name: Nome da entidade
        date: Data específica
        historical_data: Dados históricos carregados
        
    Returns:
        Dicionário com margens de alocação detalhadas
    """
    # Encontrar dados da data específica
    target_data = None
    
    if date == 'latest' and historical_data:
        # Usar os dados mais recentes (primeiro item - dados estão em ordem decrescente)
        target_data = historical_data[0]['data']
    else:
        # Buscar data específica
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
    concentracao = resultados.get('concentracao', {})
    
    if not concentracao.get('sucesso', False):
        return {}
    
    # Buscar informações da entidade específica
    resultados_por_limite = concentracao.get('resultados_por_limite', [])
    allocation_margins = {
        'entity_name': entity_name,
        'entity_type': entity_type,
        'pool_name': pool_name,
        'date': date,
        'individual_limit': None,
        'top_n_limits': [],
        'financial_details': {},
        'total_portfolio_value': 0.0
    }
    
    for limite_result in resultados_por_limite:
        if limite_result.get('entidade') == entity_type:
            # Limite individual
            if limite_result.get('tipo') == 'individual':
                if 'maior_concentracao' in limite_result:
                    maior_conc = limite_result['maior_concentracao']
                    if maior_conc and maior_conc.get('entidade') == entity_name:
                        allocation_margins['individual_limit'] = {
                            'percentual_atual': maior_conc.get('percentual_pl', 0.0),
                            'valor_absoluto': maior_conc.get('valor_absoluto', 0.0),
                            'limite_configurado': limite_result.get('limite_configurado', 0.0),
                            'status': limite_result.get('status', 'enquadrado'),
                            'margem_limite': limite_result.get('margem_limite', 0.0),
                            'margem_absoluta': maior_conc.get('valor_absoluto', 0.0) - (limite_result.get('limite_configurado', 0.0) / 100.0 * pool_data.get('pl_atual', 0.0))
                        }
            
            # Limites Top N que incluem a entidade
            elif limite_result.get('tipo') == 'top_n':
                if 'detalhamento_top_n' in limite_result:
                    detalhamento = limite_result['detalhamento_top_n']
                    # Verificar se a entidade está no Top N
                    entity_in_top_n = None
                    for idx, item in enumerate(detalhamento, 1):
                        if item.get('entidade') == entity_name:
                            entity_in_top_n = {
                                'ranking': idx,
                                'percentual': item.get('percentual_pl', 0.0),
                                'valor_absoluto': item.get('valor_absoluto', 0.0)
                            }
                            break
                    
                    if entity_in_top_n:
                        top_n_total = limite_result.get('concentracao_top_n', {}).get('percentual_pl', 0.0)
                        allocation_margins['top_n_limits'].append({
                            'n_value': limite_result.get('n', 0),
                            'entity_ranking': entity_in_top_n['ranking'],
                            'entity_percentual': entity_in_top_n['percentual'],
                            'entity_valor_absoluto': entity_in_top_n['valor_absoluto'],
                            'top_n_total_percentual': top_n_total,
                            'limite_configurado': limite_result.get('limite_configurado', 0.0),
                            'status': limite_result.get('status', 'enquadrado'),
                            'margem_limite': limite_result.get('margem_limite', 0.0)
                        })
    
    # Adicionar detalhes financeiros do pool
    if 'dados_financeiros' in pool_data.get('resultados', {}).get('concentracao', {}):
        allocation_margins['financial_details'] = pool_data['resultados']['concentracao']['dados_financeiros']
    
    allocation_margins['total_portfolio_value'] = pool_data.get('pl_atual', 0.0)
    
    return allocation_margins

def _get_top_n_detail_from_monitoring_results(monitoring_results: Dict[str, Any], pool_name: str, entity_type: str) -> Dict[str, Any]:
    """
    Extrai detalhamento do Top N diretamente dos resultados de monitoramento.
    
    Args:
        monitoring_results: Resultados completos do monitoramento
        pool_name: Nome do pool
        entity_type: 'cedente' ou 'sacado'
        
    Returns:
        Dicionário com detalhamento do Top N ou None se não encontrado
    """
    try:
        pools = monitoring_results.get('pools', {})
        if pool_name not in pools:
            return None
            
        pool_data = pools[pool_name]
        if not pool_data.get('sucesso', False):
            return None
            
        resultados = pool_data.get('resultados', {})
        concentracao = resultados.get('concentracao', {})
        
        if not concentracao.get('sucesso', False):
            return None
        
        # Buscar resultado Top N para o tipo de entidade
        resultados_por_limite = concentracao.get('resultados_por_limite', [])
        
        for limite_result in resultados_por_limite:
            if (limite_result.get('tipo') == 'top_n' and 
                limite_result.get('entidade') == entity_type):
                return limite_result
                
        return None
    except Exception:
        return None

def _calculate_consecutive_days(pool_name: str, concentracao_result: Dict[str, Any]) -> int:
    """
    Calcula dias consecutivos de violação para um pool baseado em dados históricos.
    
    Args:
        pool_name: Nome do pool
        concentracao_result: Resultado de concentração atual
        
    Returns:
        Número de dias consecutivos em violação
    """
    status_geral = concentracao_result.get('status_geral', '').lower()
    
    if 'violado' not in status_geral:
        return 0
    
    # Carregar dados históricos para calcular dias consecutivos
    try:
        historical_data = load_historical_monitoring_data()
        return _calc_consecutive_violations(pool_name, historical_data)
    except Exception as e:
        print(f"⚠️ Erro ao calcular dias consecutivos para {pool_name}: {e}")
        return 1  # Fallback para 1 dia se não conseguir calcular

def _calc_consecutive_violations(pool_name: str, historical_data) -> int:
    """Calcula dias consecutivos de violação de concentração para um pool específico."""
    if not historical_data:
        return 0
    
    consecutive_days = 0
    
    # Percorrer histórico do mais recente para o mais antigo
    # Ordenar entries por data (mais recente primeiro)
    sorted_entries = sorted(historical_data, key=lambda x: x['date'], reverse=True)
    
    for entry in sorted_entries:
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name not in pools:
            continue  # Continuar procurando em outras datas
            
        pool_data = pools[pool_name]
        
        if not pool_data.get('sucesso', False):
            continue  # Continuar procurando em outras datas
            
        resultados = pool_data.get('resultados', {})
        concentracao = resultados.get('concentracao', {})
        
        if not concentracao:
            continue  # Continuar procurando em outras datas
        
        # Verificar se está violado na concentração
        status_geral = concentracao.get('status_geral', '').lower()
        
        if 'violado' in status_geral:
            consecutive_days += 1
        else:
            break  # Sequência de violação quebrada
    
    return consecutive_days

def gen_concentration_table(monitoring_results: Dict[str, Any]) -> str:
    """
    Gera tabela HTML formatada com análise de concentração e drilldown multi-nível.
    
    Args:
        monitoring_results: Resultados completos do monitoramento
        
    Returns:
        String HTML com tabela de concentração e funcionalidades de drilldown
    """
    df = extract_concentration_analysis(monitoring_results)
    
    if df.empty:
        return "<p>Nenhum dado de concentração disponível.</p>"
    
    # Carregar dados históricos para drilldown
    historical_data = load_historical_monitoring_data()
    
    # Ordenar: violados primeiro, depois por nome
    df['_sort_key'] = df['status_geral'] != 'VIOLADO'  # Violados primeiro
    df_sorted = df.sort_values(['_sort_key', 'pool'])
    
    # Contar violações para o header
    violations_count = len(df_sorted[df_sorted['status_geral'] == 'VIOLADO'])
    total_pools = len(df_sorted)
    
    html = f"""
    <div class="indicator-section concentracao">
        <h2 class="collapsible-header" onclick="toggleIndicatorSection('concentracao')">
            <span>🎯 Análise de Concentração ({violations_count}/{total_pools})</span>
            <span class="expand-icon">▼</span>
        </h2>
        <div class="table-container" id="concentracao-content">
            <table class="indicator-table concentration-table">
            <thead>
                <tr>
                    <th>Pool</th>
                    <th>Status</th>
                    <th>Dias Consecutivos</th>
                    <th>Individual Cedente</th>
                    <th>Individual Sacado</th>
                    <th>Top N Cedentes</th>
                    <th>Top N Sacados</th>
                    <th>Margem/Excesso</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df_sorted.iterrows():
        # Status da linha
        row_class = "violation-row" if row['status_geral'] == 'VIOLADO' else "ok-row"
        
        # Formatação individual cedente com drilldown
        if pd.notna(row['cedente_individual_pct']):
            cedente_text = f"{row['cedente_individual_pct']:.2f}%"
            cedente_class = "violation" if row['cedente_individual_status'] == 'VIOLADO' else "ok"
            cedente_entity_id = f"ced_{row['pool'].replace(' ', '_').replace('#', '__')}"
            cedente_html = f'''<span class="{cedente_class} clickable-entity" 
                onclick="showEntityHistory('{row['pool']}', 'cedente', '{row['cedente_individual_nome']}', '{cedente_entity_id}')"
                style="cursor: pointer; text-decoration: underline;">
                {cedente_text}</span><br><small>{row["cedente_individual_nome"][:20]}...</small>'''
        else:
            cedente_html = "N/A"
        
        # Formatação individual sacado com drilldown  
        if pd.notna(row['sacado_individual_pct']):
            sacado_text = f"{row['sacado_individual_pct']:.2f}%"
            sacado_class = "violation" if row['sacado_individual_status'] == 'VIOLADO' else "ok"
            sacado_entity_id = f"sac_{row['pool'].replace(' ', '_').replace('#', '__')}"
            sacado_html = f'''<span class="{sacado_class} clickable-entity" 
                onclick="showEntityHistory('{row['pool']}', 'sacado', '{row['sacado_individual_nome']}', '{sacado_entity_id}')"
                style="cursor: pointer; text-decoration: underline;">
                {sacado_text}</span><br><small>{row["sacado_individual_nome"][:20]}...</small>'''
        else:
            sacado_html = "N/A"
            
        # Formatação Top N cedentes com detalhamento individual
        if pd.notna(row['top_n_cedentes_pct']):
            cedentes_n_text = f"{row['top_n_cedentes_pct']:.2f}%"
            cedentes_n_class = "violation" if row['top_n_cedentes_status'] == 'VIOLADO' else "ok"
            top_n_ced_id = f"topnced_{row['pool'].replace(' ', '_').replace('#', '__')}"
            
            # Obter detalhamento individual do Top N cedentes
            cedentes_detalhamento = _get_top_n_detail_from_monitoring_results(
                monitoring_results, row['pool'], 'cedente'
            )
            
            # Formato simplificado - só percentual clicável
            cedentes_n_html = f'''<span class="{cedentes_n_class} clickable-topn" 
                onclick="showTopNBreakdown('{row['pool']}', 'cedente', '{top_n_ced_id}')"
                style="cursor: pointer; text-decoration: underline; font-weight: bold;">
                {cedentes_n_text}</span><br><small class="clickable-topn" 
                onclick="showTopNBreakdown('{row['pool']}', 'cedente', '{top_n_ced_id}')"
                style="cursor: pointer; text-decoration: underline;">Top {int(row["top_n_cedentes_n"])}</small>'''
        else:
            cedentes_n_html = "N/A"
            
        # Formatação Top N sacados com detalhamento individual
        if pd.notna(row['top_n_sacados_pct']):
            sacados_n_text = f"{row['top_n_sacados_pct']:.2f}%"
            sacados_n_class = "violation" if row['top_n_sacados_status'] == 'VIOLADO' else "ok"
            top_n_sac_id = f"topnsac_{row['pool'].replace(' ', '_').replace('#', '__')}"
            
            # Obter detalhamento individual do Top N sacados
            sacados_detalhamento = _get_top_n_detail_from_monitoring_results(
                monitoring_results, row['pool'], 'sacado'
            )
            
            # Formato simplificado - só percentual clicável
            sacados_n_html = f'''<span class="{sacados_n_class} clickable-topn" 
                onclick="showTopNBreakdown('{row['pool']}', 'sacado', '{top_n_sac_id}')"
                style="cursor: pointer; text-decoration: underline; font-weight: bold;">
                {sacados_n_text}</span><br><small class="clickable-topn" 
                onclick="showTopNBreakdown('{row['pool']}', 'sacado', '{top_n_sac_id}')"
                style="cursor: pointer; text-decoration: underline;">Top {int(row["top_n_sacados_n"])}</small>'''
        else:
            sacados_n_html = "N/A"
            
        # Margem/Excesso
        margem = row['margem_pior_violacao']
        if margem < 0:
            margem_html = f'<span class="violation">{margem:.1f}%</span>'
        elif margem > 0:
            margem_html = f'<span class="ok">+{margem:.1f}%</span>'
        else:
            margem_html = "0.0%"
        
        # Status badge
        status_class = "status-violation" if row['status_geral'] == 'VIOLADO' else "status-ok"
        
        # IDs únicos para os drilldowns
        pool_safe_id = row['pool'].replace(' ', '_').replace('#', '__')
        
        html += f"""
                <tr class="{row_class}">
                    <td class="pool-name">{row['pool']}</td>
                    <td><span class="status-badge {status_class}">{row['status_geral']}</span></td>
                    <td class="days-count">{row['dias_consecutivos']} dias</td>
                    <td class="concentration-detail">{cedente_html}</td>
                    <td class="concentration-detail">{sacado_html}</td>
                    <td class="concentration-detail">{cedentes_n_html}</td>
                    <td class="concentration-detail">{sacados_n_html}</td>
                    <td class="margin">{margem_html}</td>
                </tr>
                
                <!-- Drilldown rows ocultas -->
                <tr id="ced_{pool_safe_id}_history" class="drilldown-row entity-history-row" style="display: none;">
                    <td colspan="8">
                        <div class="drilldown-content">
                            <h4>📈 Histórico de Concentração - Cedente</h4>
                            <div id="ced_{pool_safe_id}_content" class="historical-content">
                                Carregando histórico...
                            </div>
                        </div>
                    </td>
                </tr>
                
                <tr id="sac_{pool_safe_id}_history" class="drilldown-row entity-history-row" style="display: none;">
                    <td colspan="8">
                        <div class="drilldown-content">
                            <h4>📈 Histórico de Concentração - Sacado</h4>
                            <div id="sac_{pool_safe_id}_content" class="historical-content">
                                Carregando histórico...
                            </div>
                        </div>
                    </td>
                </tr>
                
                <tr id="topnced_{pool_safe_id}_breakdown" class="drilldown-row topn-breakdown-row" style="display: none;">
                    <td colspan="8">
                        <div class="drilldown-content">
                            <h4>🏆 Breakdown Top N Cedentes</h4>
                            <div id="topnced_{pool_safe_id}_content" class="topn-content">
                                Carregando breakdown...
                            </div>
                        </div>
                    </td>
                </tr>
                
                <tr id="topnsac_{pool_safe_id}_breakdown" class="drilldown-row topn-breakdown-row" style="display: none;">
                    <td colspan="8">
                        <div class="drilldown-content">
                            <h4>🏆 Breakdown Top N Sacados</h4>
                            <div id="topnsac_{pool_safe_id}_content" class="topn-content">
                                Carregando breakdown...
                            </div>
                        </div>
                    </td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
        </div>
    </div>
    
    <style>
    
    .concentration-detail {
        text-align: center;
    }
    
    .concentration-detail .violation {
        color: #e53e3e;
        font-weight: bold;
    }
    
    .concentration-detail .ok {
        color: #38a169;
        font-weight: bold;
    }
    
    .concentration-detail small {
        color: #666;
        display: block;
        font-size: 0.8em;
    }
    
    /* Estilos para Top N detalhado */
    .topn-summary {
        padding: 8px;
        border-radius: 6px;
        background: rgba(255,255,255,0.5);
        text-align: left;
        font-size: 0.85em;
        line-height: 1.3;
    }
    
    .topn-summary.ok {
        border-left: 3px solid #38a169;
    }
    
    .topn-summary.violation {
        border-left: 3px solid #e53e3e;
    }
    
    .topn-total {
        font-size: 1em;
        margin-bottom: 4px;
    }
    
    .topn-margin {
        margin-bottom: 6px;
        font-size: 0.9em;
    }
    
    .margin-value {
        font-weight: bold;
        color: #2d3748;
    }
    
    .topn-details {
        font-size: 0.8em;
    }
    
    .topn-details small {
        display: block;
        margin-bottom: 2px;
        color: #4a5568;
    }
    
    .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-violation {
        background: #fed7d7;
        color: #c53030;
    }
    
    .status-ok {
        background: #c6f6d5;
        color: #2f855a;
    }
    
    .days-count {
        text-align: center;
        font-weight: 600;
    }
    
    .margin .violation {
        color: #e53e3e;
        font-weight: bold;
    }
    
    .margin .ok {
        color: #38a169;
        font-weight: bold;
    }
    
    /* Drilldown styles */
    .drilldown-row {
        background: #f8f9fa !important;
    }
    
    .drilldown-content {
        padding: 20px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .drilldown-content h4 {
        color: #2d3748;
        margin-bottom: 15px;
        font-size: 1.1em;
    }
    
    .clickable-entity, .clickable-topn {
        cursor: pointer;
        text-decoration: underline;
    }
    
    .clickable-entity:hover, .clickable-topn:hover {
        opacity: 0.8;
    }
    
    .historical-table, .topn-table, .allocation-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 0.9em;
    }
    
    .historical-table th, .topn-table th, .allocation-table th {
        background: #f8f9fa;
        padding: 8px 10px;
        text-align: left;
        font-weight: 600;
        color: #333;
        border: 1px solid #dee2e6;
    }
    
    .historical-table td, .topn-table td, .allocation-table td {
        padding: 8px 10px;
        border: 1px solid #dee2e6;
    }
    
    .historical-violation {
        background: #fff5f5;
    }
    
    .historical-ok {
        background: #f0fff4;
    }
    
    .entity-clickable {
        cursor: pointer;
        text-decoration: underline;
        color: #667eea;
    }
    
    .entity-clickable:hover {
        opacity: 0.8;
    }
    
    .allocation-details {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    
    .topn-note {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 10px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 0.9em;
        color: #856404;
    }
    </style>
    
    <script>
    // Dados históricos globais (serão populados pelo backend)
    let historicalData = [];
    
    // Função para mostrar histórico de entidade
    async function showEntityHistory(poolName, entityType, entityName, elementId) {
        const historyRow = document.getElementById(elementId + '_history');
        const contentDiv = document.getElementById(elementId + '_content');
        
        // Toggle visibility
        if (historyRow.style.display === 'none' || historyRow.style.display === '') {
            historyRow.style.display = 'table-row';
            
            // Carregar dados históricos via AJAX
            try {
                const response = await fetch('/api/concentration_history', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pool_name: poolName,
                        entity_type: entityType,
                        entity_name: entityName
                    })
                });
                
                if (response.ok) {
                    const historyData = await response.json();
                    contentDiv.innerHTML = generateHistoryTable(historyData, entityType, entityName);
                } else {
                    contentDiv.innerHTML = '<p>Erro ao carregar histórico.</p>';
                }
            } catch (error) {
                console.error('Erro ao carregar histórico:', error);
                contentDiv.innerHTML = '<p>Erro de conexão ao carregar histórico.</p>';
            }
        } else {
            historyRow.style.display = 'none';
        }
    }
    
    // Função para mostrar breakdown Top N
    async function showTopNBreakdown(poolName, entityType, elementId) {
        const breakdownRow = document.getElementById(elementId + '_breakdown');
        const contentDiv = document.getElementById(elementId + '_content');
        
        // Toggle visibility
        if (breakdownRow.style.display === 'none' || breakdownRow.style.display === '') {
            breakdownRow.style.display = 'table-row';
            
            // Carregar breakdown Top N via AJAX
            try {
                const response = await fetch('/api/topn_breakdown', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pool_name: poolName,
                        entity_type: entityType,
                        date: 'latest'  // Usar data mais recente por default
                    })
                });
                
                if (response.ok) {
                    const breakdownData = await response.json();
                    contentDiv.innerHTML = generateTopNTable(breakdownData, entityType, poolName);
                } else {
                    contentDiv.innerHTML = '<p>Erro ao carregar breakdown Top N.</p>';
                }
            } catch (error) {
                console.error('Erro ao carregar breakdown:', error);
                contentDiv.innerHTML = '<p>Erro de conexão ao carregar breakdown.</p>';
            }
        } else {
            breakdownRow.style.display = 'none';
        }
    }
    
    // Função para mostrar margens de alocação
    async function showAllocationMargins(poolName, entityType, entityName, date) {
        // Criar modal ou área expandida para mostrar margens detalhadas
        const modalId = 'allocation_modal_' + Date.now();
        
        try {
            const response = await fetch('/api/allocation_margins', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pool_name: poolName,
                    entity_type: entityType,
                    entity_name: entityName,
                    date: date
                })
            });
            
            if (response.ok) {
                const allocationData = await response.json();
                showAllocationModal(allocationData);
            } else {
                alert('Erro ao carregar margens de alocação.');
            }
        } catch (error) {
            console.error('Erro ao carregar margens:', error);
            alert('Erro de conexão ao carregar margens de alocação.');
        }
    }
    
    // Gerar tabela de histórico
    function generateHistoryTable(historyData, entityType, entityName) {
        if (!historyData || historyData.length === 0) {
            return '<p>Nenhum histórico encontrado para esta entidade.</p>';
        }
        
        let html = `
        <div class="history-header">
            <h5>${entityType === 'cedente' ? 'Cedente' : 'Sacado'}: ${entityName}</h5>
        </div>
        <table class="historical-table">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Concentração</th>
                    <th>Status</th>
                    <th>Limite</th>
                    <th>Margem</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>`;
        
        historyData.forEach(item => {
            const rowClass = item.status === 'violado' ? 'historical-violation' : 'historical-ok';
            const statusBadge = item.status === 'violado' ? 
                '<span class="status-mini violation">VIOLADO</span>' : 
                '<span class="status-mini ok">ENQUADRADO</span>';
            
            html += `
                <tr class="${rowClass}">
                    <td>${item.date}</td>
                    <td><strong>${item.percentual.toFixed(2)}%</strong></td>
                    <td>${statusBadge}</td>
                    <td>${item.limite.toFixed(1)}%</td>
                    <td>${item.margem >= 0 ? '+' : ''}${item.margem.toFixed(2)}%</td>
                    <td>
                        <span class="entity-clickable" onclick="showAllocationMargins('${item.pool}', '${item.entity_type}', '${item.entity_name}', '${item.date}')">
                            Ver Margens
                        </span>
                    </td>
                </tr>`;
        });
        
        html += `
            </tbody>
        </table>`;
        
        return html;
    }
    
    // Gerar tabela Top N
    function generateTopNTable(breakdownData, entityType, poolName) {
        if (!breakdownData || breakdownData.length === 0) {
            return '<p>Nenhum breakdown Top N encontrado.</p>';
        }
        
        let html = `
        <div class="topn-header">
            <h5>Top ${breakdownData[0].n_total} ${entityType === 'cedente' ? 'Cedentes' : 'Sacados'}</h5>
            <p>Status Geral: <span class="status-mini ${breakdownData[0].status_geral === 'violado' ? 'violation' : 'ok'}">
                ${breakdownData[0].status_geral.toUpperCase()}</span></p>
            <p>Limite: ${breakdownData[0].limite_configurado.toFixed(1)}%</p>
        </div>
        
        ${breakdownData[0].note ? '<div class="topn-note"><strong>Nota:</strong> ' + breakdownData[0].note + '</div>' : ''}
        
        <table class="topn-table">
            <thead>
                <tr>
                    <th>Posição</th>
                    <th>Entidade</th>
                    <th>Exposição Atual</th>
                    <th>% Atual</th>
                    <th>Pode Crescer</th>
                    <th>Saldo Após</th>
                    <th>Limitada Por</th>
                    <th>Explicação</th>
                </tr>
            </thead>
            <tbody>`;
        
        breakdownData.forEach(item => {
            // Debug: log dos dados para verificar
            console.log('Item breakdown:', item);
            
            // Formatar valores da análise sequencial - usar valores específicos
            const exposicaoAtual = item.valor_absoluto || item.exposicao_atual || 0;
            const percentualAtual = item.percentual || item.percentual_atual || 0;
            const capacidadeEfetiva = item.capacidade_efetiva || 0;
            const saldoApos = item.saldo_apos || 0;
            const limitadaPor = item.limitada_por || item.motivo_limite || 'N/A';
            const explicacao = item.explicacao || 'N/A';
            
            // Verificar se valores são válidos
            const exposicaoFormatted = (typeof exposicaoAtual === 'number' && !isNaN(exposicaoAtual)) 
                ? exposicaoAtual.toLocaleString('pt-BR', {minimumFractionDigits: 2})
                : '0,00';
            const capacidadeFormatted = (typeof capacidadeEfetiva === 'number' && !isNaN(capacidadeEfetiva))
                ? capacidadeEfetiva.toLocaleString('pt-BR', {minimumFractionDigits: 2})
                : '0,00';
            const saldoFormatted = (typeof saldoApos === 'number' && !isNaN(saldoApos))
                ? saldoApos.toLocaleString('pt-BR', {minimumFractionDigits: 2})
                : '0,00';
            const percentualFormatted = (typeof percentualAtual === 'number' && !isNaN(percentualAtual))
                ? percentualAtual.toFixed(2)
                : '0,00';
            
            html += `
                <tr>
                    <td><strong>${item.ranking === 'Total' ? 'Total' : '#' + item.ranking}</strong></td>
                    <td title="${item.entity_name || 'N/A'}">${(item.entity_name || 'N/A').length > 30 ? (item.entity_name || 'N/A').substring(0, 30) + '...' : (item.entity_name || 'N/A')}</td>
                    <td>R$ ${exposicaoFormatted}</td>
                    <td><strong>${percentualFormatted}%</strong></td>
                    <td>R$ ${capacidadeFormatted}</td>
                    <td>R$ ${saldoFormatted}</td>
                    <td><span class="limit-reason">${limitadaPor}</span></td>
                    <td title="${explicacao}">${explicacao.length > 40 ? explicacao.substring(0, 40) + '...' : explicacao}</td>
                </tr>`;
        });
        
        html += `
            </tbody>
        </table>`;
        
        return html;
    }
    
    // Mostrar modal de margens de alocação
    function showAllocationModal(allocationData) {
        // Implementar modal simples
        let modalHtml = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;" onclick="this.remove()">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 15px; max-width: 800px; max-height: 80vh; overflow-y: auto;" onclick="event.stopPropagation()">
                <h3>📊 Margens de Alocação - ${allocationData.entity_name}</h3>
                <p><strong>Pool:</strong> ${allocationData.pool_name} | <strong>Data:</strong> ${allocationData.date}</p>
                
                ${allocationData.individual_limit ? `
                <div class="allocation-details">
                    <h4>Limite Individual</h4>
                    <p><strong>Concentração Atual:</strong> ${allocationData.individual_limit.percentual_atual.toFixed(2)}%</p>
                    <p><strong>Limite Configurado:</strong> ${allocationData.individual_limit.limite_configurado.toFixed(1)}%</p>
                    <p><strong>Status:</strong> <span class="status-mini ${allocationData.individual_limit.status === 'violado' ? 'violation' : 'ok'}">${allocationData.individual_limit.status.toUpperCase()}</span></p>
                    <p><strong>Margem:</strong> ${allocationData.individual_limit.margem_limite >= 0 ? '+' : ''}${allocationData.individual_limit.margem_limite.toFixed(2)}%</p>
                    <p><strong>Valor Absoluto:</strong> R$ ${allocationData.individual_limit.valor_absoluto.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</p>
                </div>
                ` : ''}
                
                ${allocationData.top_n_limits.map(topN => `
                <div class="allocation-details">
                    <h4>Limite Top ${topN.n_value}</h4>
                    <p><strong>Ranking da Entidade:</strong> #${topN.entity_ranking}</p>
                    <p><strong>Concentração da Entidade:</strong> ${topN.entity_percentual.toFixed(2)}%</p>
                    <p><strong>Total Top ${topN.n_value}:</strong> ${topN.top_n_total_percentual.toFixed(2)}%</p>
                    <p><strong>Limite Configurado:</strong> ${topN.limite_configurado.toFixed(1)}%</p>
                    <p><strong>Status:</strong> <span class="status-mini ${topN.status === 'violado' ? 'violation' : 'ok'}">${topN.status.toUpperCase()}</span></p>
                    <p><strong>Margem:</strong> ${topN.margem_limite >= 0 ? '+' : ''}${topN.margem_limite.toFixed(2)}%</p>
                </div>
                `).join('')}
                
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="this.closest('div[style*=\"position: fixed\"]').remove()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;">Fechar</button>
                </div>
            </div>
        </div>`;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    </script>
    """
    
    return html

if __name__ == "__main__":
    # Teste da funcionalidade
    from src.monitor.orchestrator import run_monitoring
    
    result = run_monitoring()
    if result['sucesso']:
        df = extract_concentration_analysis(result)
        print("=== ANÁLISE DE CONCENTRAÇÃO ===")
        print(df.to_string())
        
        html = gen_concentration_table(result)
        with open('/tmp/concentration_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\nHTML salvo em /tmp/concentration_analysis.html")