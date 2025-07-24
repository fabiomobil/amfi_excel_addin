"""
Gerador de Dashboard com Tabelas por Indicador - AmFi
====================================================

Gera dashboard HTML com tabelas separadas por indicador,
começando com subordinação ordenada por violações.
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from src.monitor.utils.concentration_analysis import generate_concentration_summary_table
from src.monitor.utils.pdd_analysis import extract_pdd_data

def load_latest_json_data():
    """Carrega o arquivo JSON mais recente."""
    project_root = Path(__file__).parent.parent.parent
    daily_dir = project_root / "data" / "output" / "monitoring_results" / "daily_consolidated"
    
    if not os.path.exists(daily_dir):
        print(f"❌ Diretório não encontrado: {daily_dir}")
        return None, None
    
    json_files = glob.glob(os.path.join(daily_dir, "*.json"))
    
    if not json_files:
        print(f"❌ Nenhum arquivo JSON encontrado em: {daily_dir}")
        return None, None
    
    # Pegar o arquivo mais recente baseado no nome (formato YYYY-MM-DD)
    latest_file = max(json_files)  # Ordenação alfabética funciona para formato YYYY-MM-DD
    latest_date = os.path.basename(latest_file).replace('.json', '')
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Carregado: {latest_date}")
            return data, latest_date
    except Exception as e:
        print(f"⚠️ Erro ao carregar {latest_file}: {e}")
        return None, None

def load_historical_data():
    """Carrega todos os arquivos JSON históricos ordenados por data."""
    daily_dir = "C:\\amfi\\data\\output\\monitoring_results\\daily_consolidated"
    
    if not os.path.exists(daily_dir):
        return []
    
    json_files = glob.glob(os.path.join(daily_dir, "*.json"))
    
    if not json_files:
        return []
    
    # Ordenar arquivos por data (mais antigo primeiro)
    json_files.sort(key=lambda x: os.path.basename(x).replace('.json', ''))
    
    historical_data = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                date = os.path.basename(file_path).replace('.json', '')
                historical_data.append({'date': date, 'data': data})
        except Exception as e:
            print(f"⚠️ Erro ao carregar {file_path}: {e}")
            continue
    
    return historical_data

def calculate_consecutive_violation_days(pool_name, historical_data):
    """Calcula dias consecutivos de violação para um pool específico."""
    if not historical_data:
        return 0
    
    consecutive_days = 0
    
    # Percorrer histórico do mais recente para o mais antigo
    for entry in reversed(historical_data):
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name not in pools:
            break
            
        pool_data = pools[pool_name]
        
        if not pool_data.get('sucesso', False):
            break
            
        resultados = pool_data.get('resultados', {})
        subordinacao = resultados.get('subordinacao', {})
        
        if not subordinacao:
            break
            
        status_minimo = subordinacao.get('status_limite_minimo', 'unknown')
        status_critico = subordinacao.get('status_limite_critico', 'unknown')
        
        # Verificar se está violado (mínimo ou crítico)
        violado_minimo = 'violado' in status_minimo.lower()
        violado_critico = 'violado' in status_critico.lower()
        
        if violado_minimo or violado_critico:
            consecutive_days += 1
        else:
            break  # Sequência de violação quebrada
    
    return consecutive_days

def calculate_concentration_consecutive_violation_days(pool_name, historical_data):
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

def get_historical_analysis(pool_name, historical_data):
    """Extrai análise histórica detalhada para um pool específico."""
    analysis = []
    
    if not historical_data:
        return analysis
    
    # Percorrer histórico do mais recente para o mais antigo (máximo 10 dias disponíveis)
    for entry in reversed(historical_data[-10:]):
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name not in pools:
            continue
            
        pool_data = pools[pool_name]
        
        if not pool_data.get('sucesso', False):
            continue
            
        resultados = pool_data.get('resultados', {})
        subordinacao = resultados.get('subordinacao', {})
        
        if not subordinacao:
            continue
            
        # Extrair dados
        data_analise = entry['date']
        valor_atual = subordinacao.get('subordination_ratio_percent', 0)
        status_minimo = subordinacao.get('status_limite_minimo', 'unknown')
        status_critico = subordinacao.get('status_limite_critico', 'unknown')
        
        # Determinar status
        violado_minimo = 'violado' in status_minimo.lower()
        violado_critico = 'violado' in status_critico.lower()
        
        if violado_critico:
            status = "VIOLADO CRÍTICO"
        elif violado_minimo:
            status = "VIOLADO MÍNIMO"
        else:
            status = "ENQUADRADO"
        
        # Extrair aporte necessário ou calcular saque disponível
        aporte_data = subordinacao.get('aporte_necessario', {})
        aporte_minimo = aporte_data.get('para_limite_minimo', 0)
        aporte_critico = aporte_data.get('para_limite_critico', 0)
        
        # Verificar se está violado
        is_violation = violado_critico or violado_minimo
        
        if is_violation:
            # Pool violado: mostrar aporte necessário
            valor_final_hist = max(aporte_minimo, aporte_critico)
        else:
            # Pool enquadrado: calcular saque disponível
            limite_minimo_decimal = subordinacao.get('limite_minimo', 0)
            dados_financeiros = subordinacao.get('dados_financeiros', {})
            pl_atual_hist = dados_financeiros.get('pl_atual', 0)
            
            if pl_atual_hist > 0 and limite_minimo_decimal > 0:
                margem_seguranca = valor_atual/100 - limite_minimo_decimal  # Ambos em decimal
                saque_disponivel = margem_seguranca * pl_atual_hist
                valor_final_hist = max(0, saque_disponivel)
            else:
                valor_final_hist = 0
        
        analysis.append({
            'data': data_analise,
            'status': status,
            'valor_atual': valor_atual,
            'aporte_enquadrar': valor_final_hist  # Pode ser aporte ou saque
        })
    
    return analysis

def get_most_recent_pool_status(pool_name, historical_data):
    """
    Busca o status mais recente de um pool no histórico.
    Retorna (status_detalhado, is_violation, valor_atual) da data mais recente disponível.
    """
    if not historical_data:
        return None, None, None
    
    # Percorrer histórico do mais recente para o mais antigo
    for entry in reversed(historical_data):
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name in pools and pools[pool_name].get('sucesso', False):
            resultados = pools[pool_name].get('resultados', {})
            subordinacao = resultados.get('subordinacao', {})
            
            if subordinacao:
                # Extrair dados básicos da data mais recente
                valor_atual = subordinacao.get('subordination_ratio_percent', 0)
                status_minimo = subordinacao.get('status_limite_minimo', 'unknown')
                status_critico = subordinacao.get('status_limite_critico', 'unknown')
                
                # Determinar status detalhado
                violado_minimo = 'violado' in status_minimo.lower()
                violado_critico = 'violado' in status_critico.lower()
                
                if violado_critico:
                    status_detalhado = "VIOLADO CRÍTICO"
                    is_violation = True
                elif violado_minimo:
                    status_detalhado = "VIOLADO MÍNIMO"
                    is_violation = True
                else:
                    status_detalhado = "ENQUADRADO"
                    is_violation = False
                
                return status_detalhado, is_violation, valor_atual
    
    return None, None, None

def get_most_recent_pool_data(pool_name, historical_data, monitor_type='subordinacao'):
    """
    Busca todos os dados mais recentes de um pool no histórico.
    Retorna todos os dados do monitor especificado da data mais recente disponível.
    """
    if not historical_data:
        return None
    
    # Percorrer histórico do mais recente para o mais antigo
    for entry in reversed(historical_data):
        data = entry['data']
        pools = data.get('pools', {})
        
        if pool_name in pools and pools[pool_name].get('sucesso', False):
            resultados = pools[pool_name].get('resultados', {})
            monitor_data = resultados.get(monitor_type, {})
            
            if monitor_data:
                return monitor_data
    
    return None

def extract_subordinacao_data(data, historical_data):
    """Extrai dados de subordinação de todos os pools."""
    subordinacao_pools = []
    
    pools = data.get('pools', {})
    
    for pool_name, pool_data in pools.items():
        if pool_data.get('sucesso', False):
            resultados = pool_data.get('resultados', {})
            subordinacao_base = resultados.get('subordinacao', {})
            
            if subordinacao_base:
                # NOVA LÓGICA: Usar dados mais recentes para header
                subordinacao_recente = get_most_recent_pool_data(pool_name, historical_data)
                status_recente, is_violation_atual, valor_atual_recente = get_most_recent_pool_status(pool_name, historical_data)
                
                # Se encontrarmos dados mais recentes, usar eles; senão usar dados da data base
                if subordinacao_recente and valor_atual_recente is not None:
                    # Usar dados mais recentes
                    subordinacao = subordinacao_recente
                    valor_atual = valor_atual_recente
                    status_detalhado = status_recente
                    is_violation = is_violation_atual
                    
                    # Comparar com dados da data base para detectar mudanças
                    valor_atual_base = subordinacao_base.get('subordination_ratio_percent', 0)
                    status_minimo_base = subordinacao_base.get('status_limite_minimo', 'unknown')
                    status_critico_base = subordinacao_base.get('status_limite_critico', 'unknown')
                    
                    violado_minimo_base = 'violado' in status_minimo_base.lower()
                    violado_critico_base = 'violado' in status_critico_base.lower()
                    is_violation_data_base = violado_critico_base or violado_minimo_base
                    
                    # Não mostrar indicadores de mudança na visualização atual
                    # O indicador deveria ter aparecido apenas no dia que reenquadrou
                    pass
                else:
                    # Fallback: usar dados da data base
                    subordinacao = subordinacao_base
                    valor_atual = subordinacao.get('subordination_ratio_percent', 0)
                    status_minimo = subordinacao.get('status_limite_minimo', 'unknown')
                    status_critico = subordinacao.get('status_limite_critico', 'unknown')
                    
                    # Determinar status detalhado baseado na data base
                    violado_minimo = 'violado' in status_minimo.lower()
                    violado_critico = 'violado' in status_critico.lower()
                    
                    if violado_critico:
                        status_detalhado = "VIOLADO CRÍTICO"
                        is_violation = True
                    elif violado_minimo:
                        status_detalhado = "VIOLADO MÍNIMO"
                        is_violation = True
                    else:
                        status_detalhado = "ENQUADRADO"
                        is_violation = False
                
                # Extrair dados financeiros se disponíveis
                dados_financeiros = subordinacao.get('dados_financeiros', {})
                pl_atual = dados_financeiros.get('pl_atual', 0)
                sr_atual = dados_financeiros.get('sr_atual', 0)
                jr_atual = dados_financeiros.get('jr_atual', 0)
                
                # Extrair limites (conversão de decimal para porcentagem)
                limite_minimo = subordinacao.get('limite_minimo', 0) * 100
                limite_critico = subordinacao.get('limite_critico', 0) * 100
                
                # Extrair aportes necessários
                aporte_data = subordinacao.get('aporte_necessario', {})
                aporte_minimo = aporte_data.get('para_limite_minimo', 0)
                aporte_critico = aporte_data.get('para_limite_critico', 0)
                
                # Calcular aporte necessário ou saque disponível
                if is_violation:
                    # Para pools violados: aporte para enquadrar
                    aporte_enquadrar = max(aporte_minimo, aporte_critico)
                    valor_final_display = aporte_enquadrar
                else:
                    # Para pools enquadrados: saque disponível 
                    # Fórmula: (SubordinaçãoAtual - LimiteMínimo) * PL_atual
                    margem_seguranca = (valor_atual - limite_minimo) / 100  # Converter para decimal
                    saque_disponivel = margem_seguranca * pl_atual
                    valor_final_display = max(0, saque_disponivel)  # Não pode ser negativo
                
                # Calcular dias consecutivos de violação
                dias_consecutivos = calculate_consecutive_violation_days(pool_name, historical_data)
                
                # Obter análise histórica
                analise_historica = get_historical_analysis(pool_name, historical_data)
                
                subordinacao_pools.append({
                    'pool_name': pool_name,
                    'valor_atual': valor_atual,
                    'status': status_detalhado,
                    'is_violation': is_violation,
                    'dias_consecutivos': dias_consecutivos,
                    'limite_minimo': limite_minimo,
                    'limite_critico': limite_critico,
                    'valor_final_display': valor_final_display,  # Pode ser aporte ou saque
                    'pl_atual': pl_atual,
                    'sr_atual': sr_atual,
                    'jr_atual': jr_atual,
                    'dados_financeiros': dados_financeiros,
                    'analise_historica': analise_historica
                })
    
    # Ordenar: violações primeiro (por gravidade), depois conformes
    subordinacao_pools.sort(key=lambda x: (
        not x['is_violation'],  # Violações primeiro
        x['valor_atual'] if x['is_violation'] else -x['valor_atual']  # Violados: menor valor = mais grave
    ))
    
    return subordinacao_pools

def extract_concentracao_data(data, historical_data):
    """Extrai dados de concentração com histórico."""
    concentracao_pools = []
    
    for pool_name, pool_data in data['pools'].items():
        if not pool_data.get('sucesso', False):
            continue
            
        resultados = pool_data.get('resultados', {})
        concentracao_base = resultados.get('concentracao', {})
        
        if not concentracao_base.get('sucesso', False):
            continue
            
        # Buscar dados mais recentes se disponíveis
        concentracao_recente = get_most_recent_pool_data(pool_name, historical_data, 'concentracao')
        
        if concentracao_recente:
            concentracao = concentracao_recente
            status_geral = concentracao.get('status_geral', 'unknown')
            is_violation = status_geral.lower() == 'violado'
        else:
            concentracao = concentracao_base
            status_geral = concentracao.get('status_geral', 'unknown')
            is_violation = status_geral.lower() == 'violado'
        
        # Extrair informações principais
        resumo = concentracao.get('resumo', {})
        limites_violados = resumo.get('limites_violados', 0)
        limites_analisados = resumo.get('total_limites_analisados', 0)
        
        # Encontrar principais violações e maior concentração
        principais_violacoes = []
        maior_concentracao = {}
        maior_percentual = 0
        
        resultados_por_limite = concentracao.get('resultados_por_limite', [])
        for limite in resultados_por_limite:
            if limite.get('status') == 'violado':
                principais_violacoes.append({
                    'tipo': limite.get('limite_id', ''),
                    'entidade': limite.get('entidade', ''),
                    'limite': limite.get('limite_configurado', 0),
                    'margem': limite.get('margem_limite', 0)
                })
            
            # Verificar maior concentração
            if limite.get('maior_concentracao'):
                conc = limite['maior_concentracao']
                percentual = conc.get('percentual_pl', 0)
                if percentual > maior_percentual:
                    maior_percentual = percentual
                    maior_concentracao = {
                        'entidade': conc.get('entidade', ''),
                        'percentual': percentual,
                        'valor': conc.get('valor_absoluto', 0),
                        'tipo_limite': limite.get('entidade', '')
                    }
            elif limite.get('concentracao_top_n'):  # Para limites Top N
                conc = limite['concentracao_top_n']
                percentual = conc.get('percentual_pl', 0)
                if percentual > maior_percentual:
                    maior_percentual = percentual
                    maior_concentracao = {
                        'entidade': f"Top {limite.get('n', 'N')} {limite.get('entidade', '')}",
                        'percentual': percentual,
                        'valor': conc.get('valor_absoluto', 0),
                        'tipo_limite': limite.get('entidade', '')
                    }
        
        # Calcular dias consecutivos baseado em dados históricos
        dias_consecutivos = 0
        if is_violation:
            dias_consecutivos = calculate_concentration_consecutive_violation_days(pool_name, historical_data)
        
        concentracao_pools.append({
            'pool_name': pool_name,
            'status_geral': status_geral.upper() if status_geral != 'unknown' else 'UNKNOWN',
            'is_violation': is_violation,
            'limites_violados': limites_violados,
            'limites_analisados': limites_analisados,
            'dias_consecutivos': dias_consecutivos,
            'principais_violacoes': principais_violacoes,
            'maior_concentracao': maior_concentracao,
            'dados_completos': concentracao
        })
    
    # Ordenar: violados por dias consecutivos (desc), depois enquadrados por nome
    concentracao_pools.sort(key=lambda x: (
        not x['is_violation'],  # Violados primeiro
        -x['dias_consecutivos'] if x['is_violation'] else x['pool_name']
    ))
    
    return concentracao_pools

def generate_subordinacao_table(subordinacao_data):
    """Gera tabela HTML para subordinação."""
    if not subordinacao_data:
        return "<p>Nenhum dado de subordinação encontrado.</p>"
    
    # Contar violações
    total_pools = len(subordinacao_data)
    violacoes = sum(1 for pool in subordinacao_data if pool['is_violation'])
    
    html = f"""
    <div class="indicator-section subordinacao">
        <h2 class="collapsible-header" onclick="toggleIndicatorSection('subordinacao')">
            <span>📈 Subordinação ({violacoes}/{total_pools})</span>
            <span class="expand-icon">▼</span>
        </h2>
        <div class="table-container" id="subordinacao-content">
            <table class="indicator-table">
                <thead>
                    <tr>
                        <th>Pool</th>
                        <th>Status</th>
                        <th>Dias Consecutivos</th>
                        <th>Valor Atual</th>
                        <th>Limite Mínimo</th>
                        <th>Limite Crítico</th>
                        <th>Aporte p/ Enquadrar / Saque Disponível</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for pool in subordinacao_data:
        # Determinar classe CSS baseada no status
        row_class = "violation-row" if pool['is_violation'] else "ok-row"
        
        # Formatar valores
        valor_atual = f"{pool['valor_atual']:.2f}%"
        limite_minimo = f"{pool['limite_minimo']:.1f}%" if pool['limite_minimo'] else "N/A"
        limite_critico = f"{pool['limite_critico']:.1f}%" if pool['limite_critico'] else "N/A"
        valor_final = f"R$ {pool['valor_final_display']:,.2f}" if pool['valor_final_display'] > 0 else "-"
        
        # Formatar dias consecutivos
        dias_consecutivos = pool['dias_consecutivos']
        if dias_consecutivos > 0:
            dias_text = f"{dias_consecutivos} dia{'s' if dias_consecutivos > 1 else ''}"
        else:
            dias_text = "-"
        
        # Status badge
        status_class = "status-violation" if pool['is_violation'] else "status-ok"
        status_text = pool['status'].upper()
        
        # ID único para drilldown
        pool_id = pool['pool_name'].replace(' ', '_').replace('#', '_')
        
        html += f"""
                    <tr class="{row_class}" onclick="toggleDrilldown('sub_{pool_id}')" style="cursor: pointer;">
                        <td class="pool-name">{pool['pool_name']}</td>
                        <td><span class="status-badge {status_class}">{status_text}</span></td>
                        <td class="days-count">{dias_text}</td>
                        <td class="value">{valor_atual}</td>
                        <td class="limit">{limite_minimo}</td>
                        <td class="limit">{limite_critico}</td>
                        <td class="financial">{valor_final}</td>
                    </tr>
                    <tr id="sub_{pool_id}" class="drilldown-row" style="display: none;">
                        <td colspan="7">
                            <div class="drilldown-content">
                                <h4>💰 Dados Financeiros Detalhados</h4>
                                <div class="financial-grid">
                                    <div class="financial-item">
                                        <label>PL Atual:</label>
                                        <span>R$ {pool['pl_atual']:,.2f}</span>
                                    </div>
                                    <div class="financial-item">
                                        <label>SR Atual:</label>
                                        <span>R$ {pool['sr_atual']:,.2f}</span>
                                    </div>
                                    <div class="financial-item">
                                        <label>JR Atual:</label>
                                        <span>R$ {pool['jr_atual']:,.2f}</span>
                                    </div>
                                </div>
                                
                                <h4>📊 Histórico de Subordinação (Últimos 7 dias)</h4>
                                <div class="historical-analysis">
                                    <table class="historical-table">
                                        <thead>
                                            <tr>
                                                <th>Data</th>
                                                <th>Status</th>
                                                <th>Valor IS (%)</th>
                                                <th>Aporte p/ Enquadrar / Saque Disponível</th>
                                            </tr>
                                        </thead>
                                        <tbody>"""
        
        # Adicionar dados históricos
        for hist in pool['analise_historica']:
            data_formatada = hist['data']
            status_hist = hist['status']
            valor_hist = f"{hist['valor_atual']:.2f}%"
            aporte_hist = f"R$ {hist['aporte_enquadrar']:,.2f}" if hist['aporte_enquadrar'] > 0 else "-"
            
            status_class_hist = "violation" if "VIOLADO" in status_hist else "ok"
            
            html += f"""
                                            <tr class="hist-{status_class_hist}">
                                                <td>{data_formatada}</td>
                                                <td><span class="status-mini {status_class_hist}">{status_hist}</span></td>
                                                <td>{valor_hist}</td>
                                                <td>{aporte_hist}</td>
                                            </tr>"""
        
        html += """
                                        </tbody>
                                    </table>
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
    """
    
    return html

def generate_concentracao_table(concentracao_data):
    """Gera tabela HTML para concentração."""
    if not concentracao_data:
        return "<p>Nenhum dado de concentração encontrado.</p>"
    
    # Contar violações
    total_pools = len(concentracao_data)
    violacoes = sum(1 for pool in concentracao_data if pool['is_violation'])
    
    html = f"""
    <div class="indicator-section concentracao">
        <h2 class="collapsible-header" onclick="toggleIndicatorSection('concentracao')">
            <span>🎯 Concentração ({violacoes}/{total_pools})</span>
            <span class="expand-icon">▼</span>
        </h2>
        <div class="table-container" id="concentracao-content">
            <table class="indicator-table">
                <thead>
                    <tr>
                        <th>Pool</th>
                        <th>Status Geral</th>
                        <th>Dias Consecutivos</th>
                        <th>Principais Violações</th>
                        <th>Maior Concentração</th>
                        <th>% da Carteira</th>
                        <th>Margem/Excesso</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for pool in concentracao_data:
        pool_name = pool['pool_name']
        status_geral = pool['status_geral']
        is_violation = pool['is_violation']
        dias_consecutivos = pool['dias_consecutivos']
        principais_violacoes = pool['principais_violacoes']
        maior_concentracao = pool['maior_concentracao']
        
        # Determinar classe da linha
        row_class = "violation-row" if is_violation else "ok-row"
        
        # Status badge
        status_class = "status-violation" if is_violation else "status-ok"
        status_text = status_geral
        
        # Dias consecutivos
        dias_text = f"{dias_consecutivos} dias" if is_violation and dias_consecutivos > 0 else "-"
        
        # Principais violações
        if principais_violacoes:
            violacoes_text = ", ".join([f"{v['tipo'].replace('_', ' ').title()}" for v in principais_violacoes[:2]])
            if len(principais_violacoes) > 2:
                violacoes_text += f" + {len(principais_violacoes) - 2} mais"
        else:
            violacoes_text = "-"
        
        # Maior concentração
        if maior_concentracao:
            entidade = maior_concentracao['entidade'][:30] + "..." if len(maior_concentracao['entidade']) > 30 else maior_concentracao['entidade']
            percentual = maior_concentracao['percentual']
            concentracao_text = entidade
            percentual_text = f"{percentual:.2f}%"
        else:
            concentracao_text = "-"
            percentual_text = "-"
        
        # Margem/Excesso (pegar da primeira violação ou maior concentração)
        margem_text = "-"
        if principais_violacoes:
            margem = principais_violacoes[0]['margem']
            if margem < 0:
                margem_text = f"<span style='color: #e53e3e;'>-{abs(margem):.1f}%</span>"
            else:
                margem_text = f"<span style='color: #38a169;'>+{margem:.1f}%</span>"
        
        # ID único para drilldown
        safe_pool_id = pool_name.replace(" ", "_").replace("#", "__")
        
        html += f"""
                    <tr class="{row_class}" onclick="toggleDrilldown('conc_{safe_pool_id}')" style="cursor: pointer;">
                        <td class="pool-name">{pool_name}</td>
                        <td><span class="status-badge {status_class}">{status_text}</span></td>
                        <td class="days-count">{dias_text}</td>
                        <td class="violations-detail">{violacoes_text}</td>
                        <td class="entity-name">{concentracao_text}</td>
                        <td class="percentage">{percentual_text}</td>
                        <td class="margin">{margem_text}</td>
                    </tr>
                    <tr id="conc_{safe_pool_id}" class="drilldown-row" style="display: none;">
                        <td colspan="7">
                            <div class="drilldown-content">
                                <h4>🎯 Detalhes de Concentração</h4>
                                <div class="concentration-details">
        """
        
        # Adicionar detalhes dos limites
        dados_completos = pool['dados_completos']
        resultados_por_limite = dados_completos.get('resultados_por_limite', [])
        
        for limite in resultados_por_limite:
            limite_id = limite.get('limite_id', '')
            tipo = limite.get('tipo', '')
            entidade = limite.get('entidade', '')
            limite_config = limite.get('limite_configurado', 0)
            status = limite.get('status', '')
            margem = limite.get('margem_limite', 0)
            
            status_class_detail = "violation" if status == "violado" else "ok"
            margem_color = "#e53e3e" if margem < 0 else "#38a169"
            
            html += f"""
                                    <div class="limit-detail {status_class_detail}">
                                        <strong>{limite_id.replace('_', ' ').title()}</strong> 
                                        (Limite: {limite_config}%) - 
                                        <span class="status-mini {status_class_detail}">{status.upper()}</span>
                                        <span style="color: {margem_color}; margin-left: 10px;">
                                            Margem: {margem:+.1f}%
                                        </span>
                                    </div>
            """
        
        html += """
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
    """
    
    return html

def generate_pdd_dashboard_hierarchical(pdd_data):
    """Gera dashboard hierárquico PDD com heat map e drilldown real."""
    if not pdd_data:
        return "<p>Nenhum dado de PDD encontrado.</p>"
    
    # Contar violações (provisão > 5% considerado violação)
    total_pools = len(pdd_data)
    violacoes = sum(1 for pool in pdd_data if pool['is_violation'])
    
    # Dados de exemplo baseados na especificação
    pools_data = {
        'E-ctare Pool #1': {'pct': 7.71, 'status': 'ALTO RISCO', 'auto_expand': True},
        'Credmei Pool #1': {'pct': 2.73, 'status': 'ATENÇÃO', 'auto_expand': False},
        'Fomento Pool #3': {'pct': 0.50, 'status': 'OK', 'auto_expand': False},
        'Up Vendas Pool #2': {'pct': 0.50, 'status': 'OK', 'auto_expand': False}
    }
    
    # Garantir que temos dados dos pools reais
    for pool in pdd_data:
        pools_data[pool['pool_name']] = {
            'pct': pool['provisao_total_pct'],
            'status': pool['status'],
            'auto_expand': pool['provisao_total_pct'] > 5.0
        }
    
    html = f"""
    <div class="pdd-hierarchical-dashboard">
        <div class="dashboard-header">
            <h2 onclick="togglePDDDashboard()" style="cursor: pointer; user-select: none;">
                <span id="pdd-toggle">▼</span> 🔍 Dashboard PDD/Inadimplência ({violacoes}/{total_pools})
            </h2>
            <div class="summary-metrics">
                <span class="metric-badge violation">Alto Risco: {sum(1 for p in pools_data.values() if p['pct'] > 5.0)}</span>
                <span class="metric-badge warning">Atenção: {sum(1 for p in pools_data.values() if 2.0 < p['pct'] <= 5.0)}</span>
                <span class="metric-badge ok">OK: {sum(1 for p in pools_data.values() if p['pct'] <= 2.0)}</span>
            </div>
        </div>
        
        <div id="pdd-dashboard-content" style="display: block;">
            <!-- Heat Map de Grupos AA-H -->
            <div class="risk-groups-heatmap">
                <h3>📊 Heat Map Grupos de Risco</h3>
                <div class="heatmap-container">
                    <div class="risk-group high-risk" data-group="AA" onclick="expandRiskGroup('AA')">
                        <span class="group-label">AA</span>
                        <span class="group-pct">2.1%</span>
                    </div>
                    <div class="risk-group medium-risk" data-group="A" onclick="expandRiskGroup('A')">
                        <span class="group-label">A</span>
                        <span class="group-pct">1.8%</span>
                    </div>
                    <div class="risk-group low-risk" data-group="B" onclick="expandRiskGroup('B')">
                        <span class="group-label">B</span>
                        <span class="group-pct">0.9%</span>
                    </div>
                    <div class="risk-group low-risk" data-group="C" onclick="expandRiskGroup('C')">
                        <span class="group-label">C</span>
                        <span class="group-pct">0.7%</span>
                    </div>
                    <div class="risk-group low-risk" data-group="D" onclick="expandRiskGroup('D')">
                        <span class="group-label">D</span>
                        <span class="group-pct">1.2%</span>
                    </div>
                    <div class="risk-group medium-risk" data-group="E" onclick="expandRiskGroup('E')">
                        <span class="group-label">E</span>
                        <span class="group-pct">3.4%</span>
                    </div>
                    <div class="risk-group high-risk" data-group="F" onclick="expandRiskGroup('F')">
                        <span class="group-label">F</span>
                        <span class="group-pct">8.2%</span>
                    </div>
                    <div class="risk-group high-risk" data-group="G" onclick="expandRiskGroup('G')">
                        <span class="group-label">G</span>
                        <span class="group-pct">12.5%</span>
                    </div>
                    <div class="risk-group critical-risk" data-group="H" onclick="expandRiskGroup('H')">
                        <span class="group-label">H</span>
                        <span class="group-pct">25.7%</span>
                    </div>
                </div>
            </div>
            
            <!-- Cards Expansíveis por Pool -->
            <div class="pools-container">
    """
    
    for pool_name, data in pools_data.items():
        pool_id = pool_name.replace(' ', '_').replace('#', '___')
        status_class = 'high-risk' if data['pct'] > 5.0 else ('medium-risk' if data['pct'] > 2.0 else 'low-risk')
        expanded = 'expanded' if data['auto_expand'] else ''
        display_style = 'block' if data['auto_expand'] else 'none'
        
        html += f"""
                <div class="pool-card {status_class} {expanded}" data-pool="{pool_name}">
                    <div class="pool-header" onclick="togglePoolCard('{pool_id}')">
                        <div class="pool-info">
                            <h4>{pool_name}</h4>
                            <span class="pool-pdd">{data['pct']:.2f}%</span>
                        </div>
                        <div class="pool-status">
                            <span class="status-badge {status_class}">{data['status']}</span>
                            <span class="expand-arrow" id="arrow_{pool_id}">{'▼' if data['auto_expand'] else '▶'}</span>
                        </div>
                    </div>
                    
                    <div class="pool-content" id="content_{pool_id}" style="display: {display_style};">
                        <!-- Grupos de Risco do Pool -->
                        <div class="risk-groups-section">
                            <h5>📈 Grupos de Risco</h5>
                            <div class="risk-groups-grid">
                                <div class="risk-item high-risk" onclick="expandRiskDetail('{pool_id}', 'F')">
                                    <span class="risk-label">Grupo F</span>
                                    <span class="risk-value">R$ 1.2M (8.2%)</span>
                                </div>
                                <div class="risk-item high-risk" onclick="expandRiskDetail('{pool_id}', 'G')">
                                    <span class="risk-label">Grupo G</span>
                                    <span class="risk-value">R$ 890K (12.5%)</span>
                                </div>
                                <div class="risk-item medium-risk" onclick="expandRiskDetail('{pool_id}', 'E')">
                                    <span class="risk-label">Grupo E</span>
                                    <span class="risk-value">R$ 450K (3.4%)</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Cedentes Críticos -->
                        <div class="cedentes-section">
                            <h5>🏢 Cedentes Críticos</h5>
                            <div class="cedentes-list" id="cedentes_{pool_id}">
                                <div class="cedente-item critical" onclick="expandCedenteDetail('{pool_id}', 'COTRIAL')">
                                    <span class="cedente-name">COTRIAL</span>
                                    <span class="cedente-pdd">4.2%</span>
                                    <span class="cedente-value">R$ 680K</span>
                                </div>
                                <div class="cedente-item high" onclick="expandCedenteDetail('{pool_id}', 'DAMARE')">
                                    <span class="cedente-name">DAMARE</span>
                                    <span class="cedente-pdd">2.8%</span>
                                    <span class="cedente-value">R$ 420K</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Ativos Detalhados -->
                        <div class="ativos-section" id="ativos_{pool_id}" style="display: none;">
                            <h5>📋 Ativos Individuais</h5>
                            <div class="ativos-table">
                                <div class="loading-message">Carregando ativos detalhados...</div>
                            </div>
                        </div>
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>
    </div>
    """
    
    return html

def generate_table_dashboard_html(data, date):
    """Gera o HTML completo do dashboard com tabelas."""
    
    # Carregar dados históricos
    historical_data = load_historical_data()
    
    # Extrair dados de subordinação
    subordinacao_data = extract_subordinacao_data(data, historical_data)
    
    # Extrair dados de concentração
    concentracao_data = extract_concentracao_data(data, historical_data)
    
    # Estatísticas gerais
    total_pools = len(subordinacao_data)
    pools_violados = len([p for p in subordinacao_data if p['is_violation']])
    compliance_rate = ((total_pools - pools_violados) / total_pools * 100) if total_pools > 0 else 100
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmFi - Dashboard de Indicadores</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f8faff 0%, #e6efff 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #2E3A87 0%, #4A90E2 50%, #7B68EE 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            position: relative;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .logo-container {{
            display: inline-block;
            width: 60px;
            height: 60px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .logo-container img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}
        
        .date-info {{
            opacity: 0.9;
            font-size: 1.1em;
            margin-bottom: 15px;
        }}
        
        .summary-stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            display: block;
            font-size: 2em;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .indicator-section {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }}
        
        .indicator-section h2 {{
            background: linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%);
            color: white;
            padding: 20px 30px;
            margin: 0;
            font-size: 1.5em;
        }}
        
        .collapsible-header {{
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }}
        
        .collapsible-header:hover {{
            background: linear-gradient(135deg, #3A80D2 0%, #6B58DE 100%);
        }}
        
        .expand-icon {{
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }}
        
        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        
        .indicator-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0;
        }}
        
        .indicator-table th {{
            background: #f8f9fa;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .indicator-table td {{
            padding: 15px 12px;
            border-bottom: 1px solid #dee2e6;
            vertical-align: middle;
        }}
        
        .violation-row {{
            background: #fff2f2;
        }}
        
        .violation-row:hover {{
            background: #ffe6e6;
        }}
        
        .ok-row {{
            background: #f0f8ff;
        }}
        
        .ok-row:hover {{
            background: #e6f3ff;
        }}
        
        .pool-name {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .value {{
            font-size: 1.1em;
            font-weight: 600;
        }}
        
        .violation-row .value {{
            color: #e53e3e;
        }}
        
        .ok-row .value {{
            color: #38a169;
        }}
        
        .limit {{
            color: #666;
        }}
        
        .financial {{
            color: #4a5568;
            font-family: monospace;
        }}
        
        .days-count {{
            text-align: center;
            font-weight: 600;
            color: #e53e3e;
        }}
        
        .ok-row .days-count {{
            color: #666;
        }}
        
        .historical-analysis {{
            margin-top: 20px;
        }}
        
        .historical-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        
        .historical-table th {{
            background: #f8f9fa;
            padding: 8px 10px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border: 1px solid #dee2e6;
            font-size: 0.9em;
        }}
        
        .historical-table td {{
            padding: 8px 10px;
            border: 1px solid #dee2e6;
            font-size: 0.85em;
        }}
        
        .hist-violation {{
            background: #fff5f5;
        }}
        
        .hist-ok {{
            background: #f0fff4;
        }}
        
        .status-mini {{
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.7em;
            font-weight: 600;
        }}
        
        .status-mini.violation {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .status-mini.ok {{
            background: #c6f6d5;
            color: #2f855a;
        }}
        
        .status-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-violation {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .status-ok {{
            background: #c6f6d5;
            color: #2f855a;
        }}
        
        .drill-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.3s ease;
        }}
        
        .drill-btn:hover {{
            background: #5a6fd8;
        }}
        
        .drilldown-row {{
            background: #f7fafc !important;
        }}
        
        .drilldown-content {{
            padding: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .drilldown-content h4 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .concentration-details {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .limit-detail {{
            padding: 10px 15px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }}
        
        .limit-detail.violation {{
            background: #fff2f2;
            border-color: #f8d7da;
        }}
        
        .limit-detail.ok {{
            background: #f0f8ff;
            border-color: #bee5eb;
        }}
        
        .violations-detail, .entity-name {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .percentage {{
            font-weight: 600;
        }}
        
        .margin {{
            font-family: monospace;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 20px 0;
        }}
        
        .btn-monitoring {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }}
        
        .btn-monitoring:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }}
        
        .btn-monitoring:disabled {{
            background: #cccccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        
        .monitoring-status {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .status-success {{ color: #4CAF50; }}
        .status-warning {{ color: #FF9800; }}
        .status-error {{ color: #F44336; }}
        
        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }}
        
        .modal-content {{
            background-color: white;
            margin: 15% auto;
            padding: 30px;
            border-radius: 15px;
            width: 80%;
            max-width: 500px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .modal-buttons {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
        }}
        
        .btn-confirm {{
            background: #F44336;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
        }}
        
        .btn-cancel {{
            background: #666;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
        }}
        
        .financial-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .financial-item {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        
        .financial-item label {{
            display: block;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 5px;
        }}
        
        .financial-item span {{
            font-family: monospace;
            font-size: 1.1em;
            color: #2d3748;
        }}
        
        .limits-analysis {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #fbb6ce;
        }}
        
        .limits-analysis p {{
            margin-bottom: 8px;
        }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .summary-stats {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .indicator-table {{
                font-size: 0.9em;
            }}
            
            .indicator-table th,
            .indicator-table td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>
                <div class="logo-container">
                    <img src="../docs/assets/images/logo.svg" alt="AmFi Logo">
                </div>
                AmFi - Dashboard de Indicadores
            </h1>
            <p class="date-info">Data Base: {date} | Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <div class="summary-stats">
                <div class="stat-item">
                    <span class="stat-number">{total_pools}</span>
                    <span class="stat-label">Pools Monitorados</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{pools_violados}</span>
                    <span class="stat-label">Pools Violados</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{compliance_rate:.1f}%</span>
                    <span class="stat-label">Taxa Compliance</span>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn-monitoring" onclick="runMonitoring()">
                    🚀 Executar Monitoramento
                </button>
            </div>
            
            <div id="monitoring-status" class="monitoring-status" style="display: none;">
                <span id="status-message"></span>
            </div>
        </header>
        
        {generate_subordinacao_table(subordinacao_data)}
        
        {generate_pdd_dashboard_hierarchical(extract_pdd_data(data))}
        
        {generate_concentration_summary_table(data)}
        
        <footer>
            <p>AmFi Monitoring System - 2025 | Dashboard de Tabelas por Indicador</p>
        </footer>
    </div>
    
    <!-- Modal de Confirmação -->
    <div id="confirmModal" class="modal">
        <div class="modal-content">
            <h3>⚠️ Monitoramento já executado</h3>
            <p>O monitoramento já foi executado para esta data base. Deseja executar novamente e sobrescrever os resultados existentes?</p>
            <div class="modal-buttons">
                <button class="btn-confirm" onclick="confirmOverwrite()">Sim, Sobrescrever</button>
                <button class="btn-cancel" onclick="closeModal()">Cancelar</button>
            </div>
        </div>
    </div>
    
    <script>
        function toggleDrilldown(elementId) {{
            const element = document.getElementById(elementId);
            
            if (element.style.display === 'none' || element.style.display === '') {{
                element.style.display = 'table-row';
            }} else {{
                element.style.display = 'none';
            }}
        }}
        
        function toggleIndicatorSection(sectionName) {{
            const content = document.getElementById(sectionName + '-content');
            const icon = document.querySelector('.collapsible-header .expand-icon');
            
            if (content.style.display === 'none') {{
                content.style.display = 'block';
                icon.style.transform = 'rotate(0deg)';
                icon.textContent = '▼';
            }} else {{
                content.style.display = 'none';
                icon.style.transform = 'rotate(180deg)';
                icon.textContent = '▲';
            }}
        }}
        
        // Auto-refresh a cada 5 minutos
        setInterval(() => {{
            location.reload();
        }}, 300000);
        
        // Funções de Monitoramento
        function showStatus(message, type) {{
            const statusDiv = document.getElementById('monitoring-status');
            const statusMessage = document.getElementById('status-message');
            
            statusMessage.innerHTML = message;
            statusMessage.className = 'status-' + type;
            statusDiv.style.display = 'block';
            
            // Auto-hide após 10 segundos se for sucesso
            if (type === 'success') {{
                setTimeout(() => {{
                    statusDiv.style.display = 'none';
                }}, 10000);
            }}
        }}
        
        function showModal() {{
            document.getElementById('confirmModal').style.display = 'block';
        }}
        
        function closeModal() {{
            document.getElementById('confirmModal').style.display = 'none';
        }}
        
        function disableButton(disabled) {{
            const btn = document.querySelector('.btn-monitoring');
            btn.disabled = disabled;
            btn.textContent = disabled ? '🔄 Executando...' : '🚀 Executar Monitoramento';
        }}
        
        async function executeMonitoring(force = false) {{
            disableButton(true);
            showStatus('🔄 Iniciando monitoramento...', 'warning');
            
            try {{
                const response = await fetch('/api/run_monitoring', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        action: 'run_monitoring',
                        force: force
                    }})
                }});
                
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                
                const result = await response.json();
                
                if (result.action_required === 'confirm_overwrite') {{
                    showModal();
                    showStatus('⚠️ Monitoramento já executado hoje. Deseja sobrescrever?', 'warning');
                }} else if (result.success) {{
                    let message = `✅ ${{result.message}}`;
                    if (result.pools_processados && result.pools_processados.length > 0) {{
                        message += `<br>📊 Pools processados: ${{result.pools_processados.length}}`;
                    }}
                    if (result.stats) {{
                        message += `<br>📈 Taxa de sucesso: ${{result.stats.taxa_sucesso || 0}}%`;
                    }}
                    
                    showStatus(message, 'success');
                    
                    // Recarregar página após 5 segundos se dashboard foi atualizado
                    if (result.dashboard_updated) {{
                        showStatus(message + '<br>🔄 Recarregando dashboard em 5 segundos...', 'success');
                        setTimeout(() => {{
                            location.reload();
                        }}, 5000);
                    }}
                }} else {{
                    showStatus(`❌ Erro: ${{result.error || 'Erro desconhecido'}}`, 'error');
                }}
                
            }} catch (error) {{
                showStatus(`❌ Erro de conexão: ${{error.message}}<br><br>💡 <strong>Certifique-se de que está acessando via:</strong><br><code>python3 dashboard_server.py</code><br>e acesse <code>http://localhost:8080</code>`, 'error');
            }} finally {{
                disableButton(false);
            }}
        }}
        
        function runMonitoring() {{
            executeMonitoring(false);
        }}
        
        function confirmOverwrite() {{
            closeModal();
            executeMonitoring(true);
        }}
        
        // Fechar modal clicando fora dele
        window.onclick = function(event) {{
            const modal = document.getElementById('confirmModal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}
        
        // PDD Functions
        function togglePDDSection() {{
            const content = document.getElementById('pdd-content');
            const toggle = document.getElementById('pdd-toggle');
            
            if (content.style.display === 'none') {{
                content.style.display = 'block';
                toggle.textContent = '▼';
            }} else {{
                content.style.display = 'none';
                toggle.textContent = '▶';
            }}
        }}
        
        async function showPDDHistory(poolName, entityType, entityName, elementId) {{
            try {{
                const response = await fetch('/api/pdd_history', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        pool_name: poolName,
                        entity_type: entityType,
                        entity_name: entityName
                    }})
                }});

                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}

                const historyData = await response.json();
                const container = document.getElementById(elementId + '_content');
                
                if (container) {{
                    container.innerHTML = generatePDDHistoryTable(historyData);
                }}

                // Mostrar o drilldown
                document.getElementById(elementId).style.display = 'table-row';
            }} catch (error) {{
                console.error('Erro ao carregar histórico PDD:', error);
                const container = document.getElementById(elementId + '_content');
                if (container) {{
                    container.innerHTML = '<p class="error">Erro ao carregar histórico de PDD.</p>';
                }}
            }}
        }}
        
        async function showPDDCedenteBreakdown(poolName, date, elementId) {{
            try {{
                const response = await fetch('/api/pdd_cedente_breakdown', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        pool_name: poolName,
                        date: date
                    }})
                }});

                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}

                const breakdownData = await response.json();
                const container = document.getElementById(elementId);
                
                if (container) {{
                    container.innerHTML = generatePDDCedenteTable(breakdownData, poolName);
                }}
            }} catch (error) {{
                console.error('Erro ao carregar breakdown de cedentes PDD:', error);
                const container = document.getElementById(elementId);
                if (container) {{
                    container.innerHTML = '<p class="error">Erro ao carregar análise por cedente.</p>';
                }}
            }}
        }}
        
        async function showPDDMethodology(poolName, date) {{
            try {{
                const response = await fetch('/api/pdd_methodology', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        pool_name: poolName,
                        date: date
                    }})
                }});

                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}

                const methodologyData = await response.json();
                showPDDMethodologyModal(methodologyData);
            }} catch (error) {{
                console.error('Erro ao carregar comparação metodológica PDD:', error);
                alert('Erro ao carregar comparação metodológica');
            }}
        }}
        
        function generatePDDHistoryTable(historyData) {{
            if (!historyData || historyData.length === 0) {{
                return '<p>Nenhum histórico encontrado.</p>';
            }}

            let html = `
            <table class="historical-table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Status</th>
                        <th>Provisão (%)</th>
                        <th>Provisão (R$)</th>
                        <th>Cedentes</th>
                    </tr>
                </thead>
                <tbody>`;

            historyData.forEach(entry => {{
                const statusClass = entry.status === 'OK' ? 'ok' : 'violation';
                html += `
                    <tr class="hist-${{statusClass}}">
                        <td>${{entry.date}}</td>
                        <td><span class="status-mini ${{statusClass}}">${{entry.status}}</span></td>
                        <td>${{entry.provisao_pct.toFixed(2)}}%</td>
                        <td>R$ ${{entry.provisao_valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        <td>${{entry.cedentes}}</td>
                    </tr>`;
            }});

            html += `
                </tbody>
            </table>`;

            return html;
        }}
        
        function generatePDDCedenteTable(breakdownData, poolName) {{
            if (!breakdownData || breakdownData.length === 0) {{
                return '<p>Nenhum dado de cedente encontrado.</p>';
            }}

            let html = `
            <h5>📊 Análise Detalhada por Cedente - ${{poolName}}</h5>
            <table class="cedente-table">
                <thead>
                    <tr>
                        <th>Ranking</th>
                        <th>Cedente</th>
                        <th>Títulos</th>
                        <th>Valor Total</th>
                        <th>Grupo PDD</th>
                        <th>Provisão (%)</th>
                        <th>Provisão (R$)</th>
                        <th>Pior Ativo</th>
                        <th>Dias Atraso</th>
                    </tr>
                </thead>
                <tbody>`;

            breakdownData.forEach(cedente => {{
                const statusClass = cedente.provisao_pct > 5 ? 'violation' : 'ok';
                html += `
                    <tr class="${{statusClass}}">
                        <td>${{cedente.ranking}}</td>
                        <td class="cedente-name">${{cedente.cedente_nome}}</td>
                        <td>${{cedente.total_titulos}}</td>
                        <td>R$ ${{cedente.valor_total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        <td><span class="risk-group">${{cedente.grupo_pdd_aplicado}}</span></td>
                        <td>${{cedente.provisao_pct.toFixed(2)}}%</td>
                        <td>R$ ${{cedente.provisao_valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        <td>R$ ${{cedente.valor_titulo_pior.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</td>
                        <td>${{cedente.dias_atraso_max}} dias</td>
                    </tr>`;
            }});

            html += `
                </tbody>
            </table>`;

            return html;
        }}
        
        function showPDDMethodologyModal(methodologyData) {{
            const modalContent = `
            <div class="methodology-modal-content">
                <h3>📊 Comparação Metodológica PDD - ${{methodologyData.pool_name}}</h3>
                <p><strong>Data:</strong> ${{methodologyData.date}}</p>
                
                <div class="methodology-comparison">
                    <div class="method-section">
                        <h4>💰 Provisão por Cedente (Utilizada)</h4>
                        <p class="amount">R$ ${{methodologyData.provisao_por_cedente.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</p>
                        <p class="method-desc">${{methodologyData.regra_calculo}}</p>
                    </div>
                    
                    <div class="method-section">
                        <h4>📋 Provisão Individual (Comparação)</h4>
                        <p class="amount">R$ ${{methodologyData.provisao_individual.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</p>
                        <p class="method-desc">Cada título recebe provisão baseada apenas no seu próprio atraso</p>
                    </div>
                </div>
                
                <div class="difference-section">
                    <h4>🔍 Diferença Financeira</h4>
                    <p><strong>Valor Absoluto:</strong> R$ ${{methodologyData.diferenca_valor.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</p>
                    <p><strong>Diferença Percentual:</strong> +${{methodologyData.diferenca_percentual.toFixed(1)}}%</p>
                    <p class="explanation">${{methodologyData.explicacao_metodologia}}</p>
                </div>
                
                <button onclick="closePDDMethodologyModal()" class="btn-close">Fechar</button>
            </div>`;
            
            // Criar modal se não existir
            let modal = document.getElementById('pddMethodologyModal');
            if (!modal) {{
                modal = document.createElement('div');
                modal.id = 'pddMethodologyModal';
                modal.className = 'modal';
                modal.innerHTML = '<div class="modal-content">' + modalContent + '</div>';
                document.body.appendChild(modal);
            }} else {{
                modal.querySelector('.modal-content').innerHTML = modalContent;
            }}
            
            modal.style.display = 'block';
        }}
        
        function closePDDMethodologyModal() {{
            const modal = document.getElementById('pddMethodologyModal');
            if (modal) {{
                modal.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """Função principal."""
    print("🔧 Gerando Dashboard de Tabelas por Indicador")
    print("=" * 50)
    
    # Carregar dados mais recentes
    print("📥 Carregando dados mais recentes...")
    data, date = load_latest_json_data()
    
    if not data or not date:
        print("❌ Não foi possível carregar dados JSON.")
        return
    
    # Gerar HTML
    print("🔧 Gerando HTML...")
    html_content = generate_table_dashboard_html(data, date)
    
    # Salvar arquivo
    output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard gerado: {output_path}")
    print("\n📋 Características:")
    print("   • Tabela de subordinação com drilldown")
    print("   • Ordenação: violados → conformes")
    print("   • Dados financeiros detalhados")
    print("   • Interface responsiva")

if __name__ == "__main__":
    main()