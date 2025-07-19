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

def load_latest_json_data():
    """Carrega o arquivo JSON mais recente."""
    daily_dir = "/mnt/c/amfi/data/output/monitoring_results/daily_consolidated"
    
    if not os.path.exists(daily_dir):
        print(f"❌ Diretório não encontrado: {daily_dir}")
        return None, None
    
    json_files = glob.glob(os.path.join(daily_dir, "*.json"))
    
    if not json_files:
        print(f"❌ Nenhum arquivo JSON encontrado em: {daily_dir}")
        return None, None
    
    # Pegar o arquivo mais recente
    latest_file = max(json_files, key=os.path.getctime)
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
    daily_dir = "/mnt/c/amfi/data/output/monitoring_results/daily_consolidated"
    
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

def get_historical_analysis(pool_name, historical_data):
    """Extrai análise histórica detalhada para um pool específico."""
    analysis = []
    
    if not historical_data:
        return analysis
    
    # Percorrer histórico do mais recente para o mais antigo (últimos 7 dias)
    for entry in reversed(historical_data[-7:]):
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

def extract_subordinacao_data(data, historical_data):
    """Extrai dados de subordinação de todos os pools."""
    subordinacao_pools = []
    
    pools = data.get('pools', {})
    
    for pool_name, pool_data in pools.items():
        if pool_data.get('sucesso', False):
            resultados = pool_data.get('resultados', {})
            subordinacao = resultados.get('subordinacao', {})
            
            if subordinacao:
                # Extrair dados básicos
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

def generate_subordinacao_table(subordinacao_data):
    """Gera tabela HTML para subordinação."""
    if not subordinacao_data:
        return "<p>Nenhum dado de subordinação encontrado.</p>"
    
    html = """
    <div class="indicator-section subordinacao">
        <h2>📈 Subordinação</h2>
        <div class="table-container">
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

def generate_table_dashboard_html(data, date):
    """Gera o HTML completo do dashboard com tabelas."""
    
    # Carregar dados históricos
    historical_data = load_historical_data()
    
    # Extrair dados de subordinação
    subordinacao_data = extract_subordinacao_data(data, historical_data)
    
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
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            margin: 0;
            font-size: 1.5em;
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
            background: #fff5f5;
        }}
        
        .violation-row:hover {{
            background: #fed7d7;
        }}
        
        .ok-row {{
            background: #f0fff4;
        }}
        
        .ok-row:hover {{
            background: #c6f6d5;
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
            <h1>📊 AmFi - Dashboard de Indicadores</h1>
            <p class="date-info">Data de Referência: {date} | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
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
        </header>
        
        {generate_subordinacao_table(subordinacao_data)}
        
        <footer>
            <p>AmFi Monitoring System - 2025 | Dashboard de Tabelas por Indicador</p>
        </footer>
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
        
        // Auto-refresh a cada 5 minutos
        setInterval(() => {{
            location.reload();
        }}, 300000);
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
    output_path = "/mnt/c/amfi/data/output/monitoring_results/dashboard/table_dashboard.html"
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