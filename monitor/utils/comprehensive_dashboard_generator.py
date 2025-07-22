"""
Gerador de Dashboard HTML Completo
=================================

Responsável por:
- Gerar dashboard HTML completo com TODOS os indicadores
- Incluir análise temporal (delta D-1)
- Mostrar indicadores mesmo sem violações
- Providenciar visão operacional abrangente

Funcionalidades:
- Dashboard principal com todos os pools e indicadores
- Seções detalhadas por tipo: subordinação, concentração, inadimplência, liquidez
- Análise temporal com variações percentuais
- Interface profissional com métricas executivas
- Drill-down com dados históricos
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Compatibilidade Spyder vs módulo
try:
    from .daily_results_persistence import DailyResultsPersistence
    from .alerts import log_alerta
    from .concentration_analysis import generate_concentration_summary_table
except (ImportError, ValueError):
    import sys
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from daily_results_persistence import DailyResultsPersistence
    from alerts import log_alerta
    from concentration_analysis import generate_concentration_summary_table


class ComprehensiveDashboardGenerator:
    """
    Gerador de dashboard HTML completo para monitoramento AmFi.
    
    Funcionalidades:
    - Dashboard principal com visão executiva
    - Todos os indicadores, com ou sem violações
    - Análise temporal com variações D-1
    - Interface responsiva e profissional
    """
    
    def __init__(self, persistence: DailyResultsPersistence = None):
        """
        Inicializa o gerador de dashboard.
        
        Args:
            persistence: Instância de DailyResultsPersistence
        """
        self.persistence = persistence or DailyResultsPersistence()
        self.output_path = Path("/mnt/c/amfi/data/output/monitoring_results/dashboard")
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_dashboard(self) -> str:
        """
        Gera dashboard HTML completo com todos os indicadores.
        
        Returns:
            str: Caminho para o arquivo HTML gerado
        """
        try:
            # Carregar dados completos do dia atual
            current_data = self._get_current_day_data()
            
            if not current_data:
                log_alerta({
                    "tipo": "warning",
                    "titulo": "Dashboard Completo",
                    "mensagem": "Nenhum dado encontrado para hoje"
                })
                return self._generate_empty_dashboard()
            
            # Gerar HTML completo
            html_content = self._generate_complete_html_content(current_data)
            
            # Salvar arquivo
            dashboard_file = self.output_path / "comprehensive_dashboard.html"
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log_alerta({
                "tipo": "info",
                "titulo": "Dashboard Completo",
                "mensagem": f"Dashboard completo gerado: {dashboard_file}",
                "detalhes": {
                    "pools_processados": len(current_data.get('pools', {})),
                    "tem_dados_anteriores": current_data.get('metadata', {}).get('has_previous_data', False),
                    "total_violations": current_data.get('summary', {}).get('total_violations', 0)
                }
            })
            
            return str(dashboard_file)
            
        except Exception as e:
            log_alerta({
                "tipo": "erro",
                "titulo": "Erro no Dashboard Completo",
                "mensagem": f"Falha ao gerar dashboard: {str(e)}"
            })
            return ""
    
    def _get_current_day_data(self) -> Dict[str, Any]:
        """Obtém dados consolidados do dia atual."""
        
        from datetime import date
        
        today = date.today().isoformat()
        current_file = self.persistence.daily_path / f"{today}.json"
        
        if not current_file.exists():
            return {}
        
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_alerta({
                "tipo": "warning",
                "titulo": "Dados Atuais",
                "mensagem": f"Falha ao carregar dados de hoje: {str(e)}"
            })
            return {}
    
    def _generate_complete_html_content(self, current_data: Dict[str, Any]) -> str:
        """Gera conteúdo HTML completo do dashboard."""
        
        execution_date = current_data.get('execution_date', 'N/A')
        execution_timestamp = current_data.get('execution_timestamp', datetime.now().isoformat())
        summary = current_data.get('summary', {})
        temporal_analysis = current_data.get('temporal_analysis', {})
        has_previous_data = current_data.get('metadata', {}).get('has_previous_data', False)
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmFi - Dashboard Operacional Completo</title>
    <style>
        {self._get_comprehensive_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 AmFi - Dashboard Operacional Completo</h1>
            <p class="last-updated">Data: {self._format_date(execution_date)} | Atualizado: {self._format_timestamp(execution_timestamp)}</p>
            {self._generate_temporal_status(has_previous_data, temporal_analysis)}
        </header>
        
        <div class="executive-summary">
            <h2>📈 Resumo Executivo</h2>
            <div class="summary-grid">
                <div class="summary-card pools">
                    <h3>Pools Monitorados</h3>
                    <span class="number">{summary.get('total_pools', 0)}</span>
                </div>
                <div class="summary-card violations">
                    <h3>Violações Ativas</h3>
                    <span class="number">{summary.get('total_violations', 0)}</span>
                    <span class="detail">({summary.get('critical_violations', 0)} críticas)</span>
                </div>
                <div class="summary-card compliance">
                    <h3>Taxa de Compliance</h3>
                    <span class="number">{self._calculate_compliance_rate(summary)}%</span>
                </div>
                <div class="summary-card trend">
                    <h3>Tendência Geral</h3>
                    <span class="trend-indicator">{self._calculate_overall_trend(temporal_analysis)}</span>
                </div>
            </div>
        </div>
        
        {self._generate_pools_overview(current_data)}
        
        {self._generate_concentration_analysis_section(current_data)}
        
        <footer>
            <p>AmFi Monitoring System - {datetime.now().year} | Gerado automaticamente</p>
        </footer>
    </div>
    
    <script>
        {self._get_comprehensive_javascript()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_temporal_status(self, has_previous_data: bool, 
                                temporal_analysis: Dict[str, Any]) -> str:
        """Gera indicador de status temporal."""
        
        if not has_previous_data:
            return '<div class="temporal-status no-data">⚠️ Primeira execução - Sem dados para comparação</div>'
        
        comparison_date = temporal_analysis.get('comparison_date', 'N/A')
        return f'<div class="temporal-status with-data">📅 Comparação com: {self._format_date(comparison_date)}</div>'
    
    def _generate_pools_overview(self, current_data: Dict[str, Any]) -> str:
        """Gera visão geral de todos os pools."""
        
        pools_data = current_data.get('pools', {})
        temporal_analysis = current_data.get('temporal_analysis', {})
        pools_temporal = temporal_analysis.get('pools', {})
        
        if not pools_data:
            return '<div class="no-pools">Nenhum pool encontrado</div>'
        
        html = '<div class="pools-overview"><h2>🏦 Visão Geral dos Pools</h2>'
        
        for pool_name, pool_data in pools_data.items():
            if not pool_data.get('sucesso', False):
                continue
                
            pool_temporal = pools_temporal.get(pool_name, {})
            
            html += f"""
            <div class="pool-section">
                <div class="pool-header" onclick="togglePoolDetails('{self._safe_id(pool_name)}')">
                    <h3>{pool_name}</h3>
                    <div class="pool-status">
                        {self._generate_pool_status_badges(pool_data)}
                    </div>
                    <span class="expand-icon">▼</span>
                </div>
                
                <div class="pool-details" id="pool_{self._safe_id(pool_name)}" style="display: none;">
                    {self._generate_pool_indicators(pool_name, pool_data, pool_temporal)}
                </div>
            </div>"""
        
        html += '</div>'
        return html
    
    def _generate_concentration_analysis_section(self, current_data: Dict[str, Any]) -> str:
        """Gera seção de análise de concentração."""
        try:
            concentration_table = generate_concentration_summary_table(current_data)
            
            return f"""
        <div class="concentration-analysis-section">
            <h2>🎯 Análise de Concentração Detalhada</h2>
            <div class="concentration-content">
                {concentration_table}
            </div>
        </div>"""
        except Exception as e:
            return f"""
        <div class="concentration-analysis-section">
            <h2>🎯 Análise de Concentração</h2>
            <div class="error-message">
                <p>Erro ao gerar tabela de concentração: {str(e)}</p>
            </div>
        </div>"""
    
    def _generate_pool_status_badges(self, pool_data: Dict[str, Any]) -> str:
        """Gera badges de status para o pool."""
        
        indicators = pool_data.get('resultados', {})
        badges = []
        
        # Badge de Subordinação
        if 'subordinacao' in indicators:
            sub_data = indicators['subordinacao']
            status = sub_data.get('status_limite_minimo', 'unknown')
            ratio = sub_data.get('subordination_ratio_percent', 0)
            
            if status == 'violado':
                badges.append(f'<span class="badge violation">SUB: {ratio:.2f}%</span>')
            else:
                badges.append(f'<span class="badge ok">SUB: {ratio:.2f}%</span>')
        
        # Badge de Inadimplência
        if 'inadimplencia' in indicators:
            inad_data = indicators['inadimplencia']
            violations = 0
            for monitor_id, monitor_data in inad_data.get('resultados', {}).items():
                if monitor_data.get('status') == 'violado':
                    violations += 1
            
            if violations > 0:
                badges.append(f'<span class="badge violation">INAD: {violations} violações</span>')
            else:
                badges.append('<span class="badge ok">INAD: OK</span>')
        
        # Badge de Concentração
        if 'concentracao' in indicators:
            conc_data = indicators['concentracao']
            violations = len(conc_data.get('concentracao_individual', {}).get('sacados', {}).get('violacoes', []))
            violations += len(conc_data.get('concentracao_individual', {}).get('cedentes', {}).get('violacoes', []))
            
            if violations > 0:
                badges.append(f'<span class="badge violation">CONC: {violations} violações</span>')
            else:
                badges.append('<span class="badge ok">CONC: OK</span>')
        
        # Badge de Liquidez
        if 'liquidez' in indicators:
            liq_data = indicators['liquidez']
            sufficient = liq_data.get('summary', {}).get('all_scenarios_sufficient', True)
            
            if sufficient:
                badges.append('<span class="badge ok">LIQ: OK</span>')
            else:
                badges.append('<span class="badge violation">LIQ: Insuficiente</span>')
        
        return ''.join(badges)
    
    def _generate_pool_indicators(self, pool_name: str, pool_data: Dict[str, Any], 
                                pool_temporal: Dict[str, Any]) -> str:
        """Gera seção detalhada de indicadores do pool."""
        
        indicators = pool_data.get('resultados', {})
        temporal_indicators = pool_temporal.get('indicators', {})
        
        html = '<div class="indicators-grid">'
        
        # Indicador de Subordinação
        if 'subordinacao' in indicators:
            html += self._generate_subordinacao_indicator(
                indicators['subordinacao'], 
                temporal_indicators.get('subordinacao', {})
            )
        
        # Indicador de Inadimplência
        if 'inadimplencia' in indicators:
            html += self._generate_inadimplencia_indicator(
                indicators['inadimplencia'], 
                temporal_indicators.get('inadimplencia', {})
            )
        
        # Indicador de Concentração
        if 'concentracao' in indicators:
            html += self._generate_concentracao_indicator(
                indicators['concentracao'], 
                temporal_indicators.get('concentracao', {})
            )
        
        # Indicador de Liquidez
        if 'liquidez' in indicators:
            html += self._generate_liquidez_indicator(
                indicators['liquidez'], 
                temporal_indicators.get('liquidez', {})
            )
        
        html += '</div>'
        return html
    
    def _generate_subordinacao_indicator(self, sub_data: Dict[str, Any], 
                                       temporal_data: Dict[str, Any]) -> str:
        """Gera card do indicador de subordinação."""
        
        current_ratio = sub_data.get('subordination_ratio_percent', 0)
        status = sub_data.get('status_limite_minimo', 'unknown')
        limite = sub_data.get('limite_minimo', 0) * 100
        
        # Análise temporal
        delta_html = ""
        if temporal_data:
            delta = temporal_data.get('delta', 0)
            trend = temporal_data.get('trend', 'stable')
            
            delta_symbol = "↗️" if trend == "up" else "↘️" if trend == "down" else "➡️"
            delta_color = "green" if trend == "up" else "red" if trend == "down" else "gray"
            
            delta_html = f"""
            <div class="delta-info">
                <span class="delta-symbol" style="color: {delta_color}">{delta_symbol}</span>
                <span class="delta-value">{delta:+.2f}%</span>
                <span class="delta-label">vs D-1</span>
            </div>"""
        
        status_class = "violation" if status == "violado" else "ok"
        
        return f"""
        <div class="indicator-card subordinacao {status_class}">
            <h4>📈 Subordinação</h4>
            <div class="indicator-value">
                <span class="main-value">{current_ratio:.2f}%</span>
                <span class="limit-info">Limite: {limite:.1f}%</span>
            </div>
            {delta_html}
            <div class="status-info">
                <span class="status-badge {status_class}">{status.upper()}</span>
            </div>
        </div>"""
    
    def _generate_inadimplencia_indicator(self, inad_data: Dict[str, Any], 
                                        temporal_data: Dict[str, Any]) -> str:
        """Gera card do indicador de inadimplência."""
        
        results = inad_data.get('resultados', {})
        violations_count = sum(1 for data in results.values() if data.get('status') == 'violado')
        
        # Pegar inadimplência 30d como principal
        main_inad = None
        for monitor_id, data in results.items():
            if '30' in monitor_id:
                main_inad = data
                break
        
        if not main_inad:
            main_inad = list(results.values())[0] if results else {}
        
        current_percent = main_inad.get('inadimplencia_percent', 0)
        
        # Análise temporal
        delta_html = ""
        if temporal_data and temporal_data.get('status') != 'insufficient_data':
            delta = temporal_data.get('delta', 0)
            trend = temporal_data.get('trend', 'stable')
            
            delta_symbol = "↗️" if trend == "worse" else "↘️" if trend == "better" else "➡️"
            delta_color = "red" if trend == "worse" else "green" if trend == "better" else "gray"
            
            delta_html = f"""
            <div class="delta-info">
                <span class="delta-symbol" style="color: {delta_color}">{delta_symbol}</span>
                <span class="delta-value">{delta:+.2f}%</span>
                <span class="delta-label">vs D-1</span>
            </div>"""
        
        status_class = "violation" if violations_count > 0 else "ok"
        
        return f"""
        <div class="indicator-card inadimplencia {status_class}">
            <h4>⏰ Inadimplência</h4>
            <div class="indicator-value">
                <span class="main-value">{current_percent:.2f}%</span>
                <span class="violations-info">{violations_count} violação(ões)</span>
            </div>
            {delta_html}
            <div class="status-info">
                <span class="status-badge {status_class}">
                    {'VIOLADO' if violations_count > 0 else 'CONFORME'}
                </span>
            </div>
        </div>"""
    
    def _generate_concentracao_indicator(self, conc_data: Dict[str, Any], 
                                       temporal_data: Dict[str, Any]) -> str:
        """Gera card do indicador de concentração."""
        
        violations_sacados = len(conc_data.get('concentracao_individual', {}).get('sacados', {}).get('violacoes', []))
        violations_cedentes = len(conc_data.get('concentracao_individual', {}).get('cedentes', {}).get('violacoes', []))
        total_violations = violations_sacados + violations_cedentes
        
        # Análise temporal
        delta_html = ""
        if temporal_data:
            delta_violations = temporal_data.get('delta_violations', 0)
            trend = temporal_data.get('trend', 'stable')
            
            delta_symbol = "↗️" if trend == "worse" else "↘️" if trend == "better" else "➡️"
            delta_color = "red" if trend == "worse" else "green" if trend == "better" else "gray"
            
            delta_html = f"""
            <div class="delta-info">
                <span class="delta-symbol" style="color: {delta_color}">{delta_symbol}</span>
                <span class="delta-value">{delta_violations:+d}</span>
                <span class="delta-label">violações vs D-1</span>
            </div>"""
        
        status_class = "violation" if total_violations > 0 else "ok"
        
        return f"""
        <div class="indicator-card concentracao {status_class}">
            <h4>🎯 Concentração</h4>
            <div class="indicator-value">
                <span class="main-value">{total_violations}</span>
                <span class="violations-info">violações ativas</span>
            </div>
            <div class="breakdown">
                <span>Sacados: {violations_sacados}</span>
                <span>Cedentes: {violations_cedentes}</span>
            </div>
            {delta_html}
            <div class="status-info">
                <span class="status-badge {status_class}">
                    {'VIOLADO' if total_violations > 0 else 'CONFORME'}
                </span>
            </div>
        </div>"""
    
    def _generate_liquidez_indicator(self, liq_data: Dict[str, Any], 
                                   temporal_data: Dict[str, Any]) -> str:
        """Gera card do indicador de liquidez."""
        
        summary = liq_data.get('summary', {})
        all_sufficient = summary.get('all_scenarios_sufficient', True)
        next_payment = liq_data.get('next_payment', {})
        
        # Análise temporal
        delta_html = ""
        if temporal_data:
            trend = temporal_data.get('trend', 'stable')
            status_changed = temporal_data.get('status_changed', False)
            
            if status_changed:
                delta_symbol = "🔄"
                delta_color = "orange"
                delta_text = "Status alterado"
            else:
                delta_symbol = "➡️"
                delta_color = "gray"
                delta_text = "Status mantido"
            
            delta_html = f"""
            <div class="delta-info">
                <span class="delta-symbol" style="color: {delta_color}">{delta_symbol}</span>
                <span class="delta-value">{delta_text}</span>
                <span class="delta-label">vs D-1</span>
            </div>"""
        
        status_class = "violation" if not all_sufficient else "ok"
        
        return f"""
        <div class="indicator-card liquidez {status_class}">
            <h4>💧 Liquidez</h4>
            <div class="indicator-value">
                <span class="main-value">{'Suficiente' if all_sufficient else 'Insuficiente'}</span>
                <span class="next-payment">Próximo: {next_payment.get('date', 'N/A')}</span>
            </div>
            <div class="breakdown">
                <span>Valor: R$ {next_payment.get('amount', 0):,.0f}</span>
            </div>
            {delta_html}
            <div class="status-info">
                <span class="status-badge {status_class}">
                    {'CRÍTICO' if not all_sufficient else 'OK'}
                </span>
            </div>
        </div>"""
    
    def _calculate_compliance_rate(self, summary: Dict[str, Any]) -> int:
        """Calcula taxa de compliance geral."""
        
        total_pools = summary.get('total_pools', 0)
        pools_with_violations = summary.get('pools_with_violations', 0)
        
        if total_pools == 0:
            return 100
        
        compliance_rate = ((total_pools - pools_with_violations) / total_pools) * 100
        return round(compliance_rate)
    
    def _calculate_overall_trend(self, temporal_analysis: Dict[str, Any]) -> str:
        """Calcula tendência geral do sistema."""
        
        if not temporal_analysis or temporal_analysis.get('status') != 'with_comparison':
            return "📊 Sem dados históricos"
        
        pools_data = temporal_analysis.get('pools', {})
        
        improvements = 0
        deteriorations = 0
        stable = 0
        
        for pool_data in pools_data.values():
            indicators = pool_data.get('indicators', {})
            
            for indicator_data in indicators.values():
                trend = indicator_data.get('trend', 'stable')
                
                if trend in ['better', 'up']:
                    improvements += 1
                elif trend in ['worse', 'down']:
                    deteriorations += 1
                else:
                    stable += 1
        
        if deteriorations > improvements:
            return "📉 Deterioração"
        elif improvements > deteriorations:
            return "📈 Melhoria"
        else:
            return "➡️ Estável"
    
    def _safe_id(self, text: str) -> str:
        """Converte texto para ID HTML seguro."""
        import re
        return re.sub(r'[^a-zA-Z0-9]', '_', text)
    
    def _format_date(self, date_str: str) -> str:
        """Formata data para exibição."""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%d/%m/%Y')
        except:
            return date_str
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Formata timestamp para exibição."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            return timestamp
    
    def _generate_empty_dashboard(self) -> str:
        """Gera dashboard vazio quando não há dados."""
        
        dashboard_file = self.output_path / "comprehensive_dashboard.html"
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmFi - Dashboard Operacional</title>
    <style>{self._get_comprehensive_css_styles()}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 AmFi - Dashboard Operacional</h1>
            <p class="last-updated">Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </header>
        
        <div class="empty-state">
            <h2>⚠️ Nenhum dado disponível</h2>
            <p>Execute o monitoramento para gerar dados do dashboard.</p>
        </div>
        
        <footer>
            <p>AmFi Monitoring System - {datetime.now().year}</p>
        </footer>
    </div>
</body>
</html>"""
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(dashboard_file)
    
    def _get_comprehensive_css_styles(self) -> str:
        """Retorna estilos CSS para o dashboard completo."""
        
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .last-updated {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .temporal-status {
            margin-top: 15px;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: 500;
        }
        
        .temporal-status.with-data {
            background: rgba(255,255,255,0.2);
        }
        
        .temporal-status.no-data {
            background: rgba(255,193,7,0.3);
        }
        
        .executive-summary {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .executive-summary h2 {
            color: #667eea;
            margin-bottom: 25px;
            font-size: 1.8em;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .summary-card {
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .summary-card.pools {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .summary-card.violations {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }
        
        .summary-card.compliance {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            color: #333;
        }
        
        .summary-card.trend {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .summary-card h3 {
            margin-bottom: 15px;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .summary-card .number {
            font-size: 2.5em;
            font-weight: bold;
            display: block;
            margin-bottom: 5px;
        }
        
        .summary-card .detail {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .trend-indicator {
            font-size: 1.3em;
            font-weight: 600;
        }
        
        .pools-overview {
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .pools-overview h2 {
            color: #667eea;
            padding: 25px 30px 0;
            font-size: 1.8em;
        }
        
        .pool-section {
            border-bottom: 1px solid #eee;
        }
        
        .pool-section:last-child {
            border-bottom: none;
        }
        
        .pool-header {
            padding: 20px 30px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }
        
        .pool-header:hover {
            background-color: #f8f9fa;
        }
        
        .pool-header h3 {
            color: #333;
            font-size: 1.3em;
        }
        
        .pool-status {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .badge {
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge.ok {
            background: #d4edda;
            color: #155724;
        }
        
        .badge.violation {
            background: #f8d7da;
            color: #721c24;
        }
        
        .expand-icon {
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }
        
        .pool-details {
            padding: 0 30px 30px;
            background: #f8f9fa;
        }
        
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .indicator-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 4px solid;
        }
        
        .indicator-card.ok {
            border-left-color: #28a745;
        }
        
        .indicator-card.violation {
            border-left-color: #dc3545;
        }
        
        .indicator-card h4 {
            margin-bottom: 15px;
            color: #333;
            font-size: 1.1em;
        }
        
        .indicator-value {
            margin-bottom: 15px;
        }
        
        .main-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            display: block;
        }
        
        .limit-info, .violations-info, .next-payment {
            font-size: 0.9em;
            color: #666;
            display: block;
            margin-top: 5px;
        }
        
        .breakdown {
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .breakdown span {
            display: block;
            margin-bottom: 3px;
        }
        
        .delta-info {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .delta-symbol {
            font-size: 1.2em;
        }
        
        .delta-value {
            font-weight: 600;
        }
        
        .delta-label {
            font-size: 0.8em;
            color: #666;
        }
        
        .status-info {
            text-align: center;
        }
        
        .status-badge {
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .status-badge.ok {
            background: #d4edda;
            color: #155724;
        }
        
        .status-badge.violation {
            background: #f8d7da;
            color: #721c24;
        }
        
        .empty-state {
            background: white;
            padding: 60px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .empty-state h2 {
            color: #ffc107;
            margin-bottom: 20px;
            font-size: 2em;
        }
        
        .concentration-analysis-section {
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .concentration-analysis-section h2 {
            color: #667eea;
            padding: 25px 30px;
            margin: 0;
            font-size: 1.8em;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        .concentration-content {
            padding: 0;
        }
        
        .error-message {
            padding: 30px;
            text-align: center;
            color: #dc3545;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .pool-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
            
            .indicators-grid {
                grid-template-columns: 1fr;
            }
            
            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        """
    
    def _get_comprehensive_javascript(self) -> str:
        """Retorna JavaScript para funcionalidade do dashboard."""
        
        return """
        function togglePoolDetails(poolId) {
            const element = document.getElementById('pool_' + poolId);
            const icon = element.parentElement.querySelector('.expand-icon');
            
            if (element.style.display === 'none' || element.style.display === '') {
                element.style.display = 'block';
                icon.style.transform = 'rotate(180deg)';
            } else {
                element.style.display = 'none';
                icon.style.transform = 'rotate(0deg)';
            }
        }
        
        // Auto-refresh a cada 5 minutos
        setTimeout(function() {
            location.reload();
        }, 300000);
        
        // Expandir/contrair todos os pools
        function toggleAllPools() {
            const pools = document.querySelectorAll('.pool-details');
            const allExpanded = Array.from(pools).every(pool => pool.style.display === 'block');
            
            pools.forEach(pool => {
                const poolId = pool.id.replace('pool_', '');
                togglePoolDetails(poolId);
            });
        }
        
        // Adicionar botão para expandir todos
        window.addEventListener('load', function() {
            const header = document.querySelector('.pools-overview h2');
            if (header) {
                header.innerHTML += ' <button onclick="toggleAllPools()" style="margin-left: 15px; padding: 5px 10px; border: none; background: #667eea; color: white; border-radius: 5px; cursor: pointer;">Toggle All</button>';
            }
        });
        """


def generate_comprehensive_dashboard() -> str:
    """
    Função de conveniência para gerar dashboard completo.
    
    Returns:
        str: Caminho para o arquivo HTML gerado
    """
    generator = ComprehensiveDashboardGenerator()
    return generator.generate_comprehensive_dashboard()


if __name__ == "__main__":
    # Teste básico do gerador de dashboard completo
    print("🌐 TESTE - Gerador de Dashboard Completo")
    print("=" * 60)
    
    # Gerar dashboard
    dashboard_path = generate_comprehensive_dashboard()
    
    if dashboard_path:
        print(f"✅ Dashboard completo gerado: {dashboard_path}")
        print(f"📂 Abra o arquivo em um navegador para visualizar")
    else:
        print("❌ Falha ao gerar dashboard completo")