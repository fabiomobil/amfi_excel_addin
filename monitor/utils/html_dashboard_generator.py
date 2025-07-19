"""
Gerador de Dashboard HTML
========================

Responsável por:
- Gerar dashboard HTML operacional
- Criar drill-down funcional por tipo de violação
- Organizar violações por antiguidade
- Fornecer acesso rápido a informações críticas

Funcionalidades:
- Dashboard principal com resumo de violações
- Seções por tipo: subordinação, concentração, inadimplência, liquidez
- Drill-down com detalhes específicos de cada violação
- Ordenação por criticidade e antiguidade
- Interface responsiva e profissional
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
except (ImportError, ValueError):
    import sys
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from daily_results_persistence import DailyResultsPersistence
    from alerts import log_alerta


class HTMLDashboardGenerator:
    """
    Gerador de dashboard HTML para monitoramento de violações.
    
    Funcionalidades:
    - Dashboard principal com overview
    - Seções detalhadas por tipo de violação
    - Drill-down com informações específicas
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
    
    def generate_dashboard(self) -> str:
        """
        Gera dashboard HTML completo.
        
        Returns:
            str: Caminho para o arquivo HTML gerado
        """
        try:
            # Carregar dados de violações
            violations_data = self.persistence.get_active_violations()
            
            if not violations_data:
                log_alerta({
                    "tipo": "warning",
                    "titulo": "Dashboard HTML",
                    "mensagem": "Nenhuma violação encontrada para dashboard"
                })
                return self._generate_empty_dashboard()
            
            # Gerar HTML
            html_content = self._generate_html_content(violations_data)
            
            # Salvar arquivo
            dashboard_file = self.output_path / "violations_dashboard.html"
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log_alerta({
                "tipo": "info",
                "titulo": "Dashboard HTML",
                "mensagem": f"Dashboard gerado: {dashboard_file}",
                "detalhes": {
                    "total_violations": violations_data.get('summary', {}).get('total_violations', 0),
                    "critical_violations": violations_data.get('summary', {}).get('critical_violations', 0)
                }
            })
            
            return str(dashboard_file)
            
        except Exception as e:
            log_alerta({
                "tipo": "erro",
                "titulo": "Erro no Dashboard",
                "mensagem": f"Falha ao gerar dashboard HTML: {str(e)}"
            })
            return ""
    
    def _generate_html_content(self, violations_data: Dict[str, Any]) -> str:
        """Gera conteúdo HTML completo do dashboard."""
        
        summary = violations_data.get('summary', {})
        last_updated = violations_data.get('last_updated', datetime.now().isoformat())
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmFi - Dashboard de Violações</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚨 AmFi - Dashboard de Violações</h1>
            <p class="last-updated">Última atualização: {self._format_timestamp(last_updated)}</p>
        </header>
        
        <div class="summary-section">
            <h2>📊 Resumo Executivo</h2>
            <div class="summary-cards">
                <div class="card critical">
                    <h3>Críticas</h3>
                    <span class="number">{summary.get('critical_violations', 0)}</span>
                </div>
                <div class="card total">
                    <h3>Total</h3>
                    <span class="number">{summary.get('total_violations', 0)}</span>
                </div>
                <div class="card by-type">
                    <h3>Por Tipo</h3>
                    <div class="type-breakdown">
                        {self._generate_type_breakdown(summary.get('by_type', {}))}
                    </div>
                </div>
            </div>
        </div>
        
        {self._generate_violations_sections(violations_data)}
        
        <footer>
            <p>AmFi Monitoring System - {datetime.now().year}</p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_violations_sections(self, violations_data: Dict[str, Any]) -> str:
        """Gera seções de violações por tipo."""
        
        sections = []
        
        # Seção de Subordinação
        if violations_data.get('subordinacao'):
            sections.append(self._generate_subordinacao_section(violations_data['subordinacao']))
        
        # Seção de Concentração
        if violations_data.get('concentracao'):
            sections.append(self._generate_concentracao_section(violations_data['concentracao']))
        
        # Seção de Inadimplência
        if violations_data.get('inadimplencia'):
            sections.append(self._generate_inadimplencia_section(violations_data['inadimplencia']))
        
        # Seção de Liquidez
        if violations_data.get('liquidez'):
            sections.append(self._generate_liquidez_section(violations_data['liquidez']))
        
        return '\n'.join(sections)
    
    def _generate_subordinacao_section(self, violations: List[Dict[str, Any]]) -> str:
        """Gera seção de violações de subordinação."""
        
        html = """
        <div class="violation-section">
            <h2>📈 Subordinação</h2>
            <div class="violations-list">"""
        
        for violation in violations:
            pool = violation.get('pool', '')
            subtipo = violation.get('subtipo', '')
            valor_atual = violation.get('valor_atual', 0)
            limite = violation.get('limite_configurado', 0)
            aporte = violation.get('aporte_necessario', 0)
            criticidade = violation.get('criticidade', 'alta')
            
            criticidade_class = 'critical' if criticidade == 'critica' else 'high'
            
            html += f"""
                <div class="violation-item {criticidade_class}" onclick="toggleDetails('sub_{hash(pool + subtipo)}')">
                    <div class="violation-header">
                        <h3>{pool}</h3>
                        <span class="violation-type">{subtipo.replace('_', ' ').title()}</span>
                        <span class="status-badge {criticidade_class}">{criticidade.upper()}</span>
                    </div>
                    <div class="violation-summary">
                        <span class="current-value">{valor_atual:.2f}%</span>
                        <span class="vs">vs</span>
                        <span class="limit-value">{limite:.2f}%</span>
                        <span class="gap">Gap: R$ {aporte:,.2f}</span>
                    </div>
                    <div class="violation-details" id="sub_{hash(pool + subtipo)}" style="display: none;">
                        <h4>💰 Dados Financeiros</h4>
                        {self._format_financial_data(violation.get('dados_financeiros', {}))}
                        <h4>🔧 Ação Requerida</h4>
                        <p>Aporte necessário: <strong>R$ {aporte:,.2f}</strong></p>
                        <p>Prazo de cura: <strong>5 dias úteis</strong></p>
                    </div>
                </div>"""
        
        html += """
            </div>
        </div>"""
        
        return html
    
    def _generate_concentracao_section(self, violations: List[Dict[str, Any]]) -> str:
        """Gera seção de violações de concentração."""
        
        html = """
        <div class="violation-section">
            <h2>🎯 Concentração</h2>
            <div class="violations-list">"""
        
        for violation in violations:
            pool = violation.get('pool', '')
            subtipo = violation.get('subtipo', '')
            entity = violation.get('entity', '')
            valor_atual = violation.get('valor_atual', 0)
            limite = violation.get('limite_configurado', 0)
            amount = violation.get('amount', 0)
            
            html += f"""
                <div class="violation-item high" onclick="toggleDetails('conc_{hash(pool + entity)}')">
                    <div class="violation-header">
                        <h3>{pool}</h3>
                        <span class="violation-type">{subtipo.replace('_', ' ').title()}</span>
                        <span class="status-badge high">ALTA</span>
                    </div>
                    <div class="violation-summary">
                        <span class="entity-name">{entity}</span>
                        <span class="current-value">{valor_atual:.2f}%</span>
                        <span class="vs">vs</span>
                        <span class="limit-value">{limite:.2f}%</span>
                        <span class="amount">R$ {amount:,.2f}</span>
                    </div>
                    <div class="violation-details" id="conc_{hash(pool + entity)}" style="display: none;">
                        <h4>📊 Detalhes da Concentração</h4>
                        <p>Entidade: <strong>{entity}</strong></p>
                        <p>Tipo: <strong>{subtipo.replace('_', ' ').title()}</strong></p>
                        <p>Valor absoluto: <strong>R$ {amount:,.2f}</strong></p>
                        <p>Percentual atual: <strong>{valor_atual:.2f}%</strong></p>
                        <p>Limite configurado: <strong>{limite:.2f}%</strong></p>
                        
                        {self._format_concentration_drilldown(violation)}
                    </div>
                </div>"""
        
        html += """
            </div>
        </div>"""
        
        return html
    
    def _generate_inadimplencia_section(self, violations: List[Dict[str, Any]]) -> str:
        """Gera seção de violações de inadimplência."""
        
        html = """
        <div class="violation-section">
            <h2>⏰ Inadimplência</h2>
            <div class="violations-list">"""
        
        for violation in violations:
            pool = violation.get('pool', '')
            subtipo = violation.get('subtipo', '')
            valor_atual = violation.get('valor_atual', 0)
            limite = violation.get('limite_configurado', 0)
            amount = violation.get('amount', 0)
            janela = violation.get('janela_dias', 0)
            
            html += f"""
                <div class="violation-item high" onclick="toggleDetails('inad_{hash(pool + subtipo)}')">
                    <div class="violation-header">
                        <h3>{pool}</h3>
                        <span class="violation-type">Inadimplência {janela}+ dias</span>
                        <span class="status-badge high">ALTA</span>
                    </div>
                    <div class="violation-summary">
                        <span class="current-value">{valor_atual:.2f}%</span>
                        <span class="vs">vs</span>
                        <span class="limit-value">{limite:.2f}%</span>
                        <span class="amount">R$ {amount:,.2f}</span>
                    </div>
                    <div class="violation-details" id="inad_{hash(pool + subtipo)}" style="display: none;">
                        <h4>📈 Análise de Inadimplência</h4>
                        <p>Janela: <strong>{janela}+ dias de atraso</strong></p>
                        <p>Percentual atual: <strong>{valor_atual:.2f}%</strong></p>
                        <p>Limite configurado: <strong>{limite:.2f}%</strong></p>
                        <p>Valor inadimplente: <strong>R$ {amount:,.2f}</strong></p>
                        
                        {self._format_aging_analysis(violation.get('matriz_atrasos', {}))}
                    </div>
                </div>"""
        
        html += """
            </div>
        </div>"""
        
        return html
    
    def _generate_liquidez_section(self, violations: List[Dict[str, Any]]) -> str:
        """Gera seção de violações de liquidez."""
        
        html = """
        <div class="violation-section">
            <h2>💧 Liquidez</h2>
            <div class="violations-list">"""
        
        for violation in violations:
            pool = violation.get('pool', '')
            worst_scenario = violation.get('worst_scenario', '')
            worst_gap = violation.get('worst_gap', 0)
            next_payment = violation.get('next_payment', {})
            
            html += f"""
                <div class="violation-item critical" onclick="toggleDetails('liq_{hash(pool)}')">
                    <div class="violation-header">
                        <h3>{pool}</h3>
                        <span class="violation-type">Insuficiência de Liquidez</span>
                        <span class="status-badge critical">CRÍTICA</span>
                    </div>
                    <div class="violation-summary">
                        <span class="scenario">Pior cenário: {worst_scenario.title()}</span>
                        <span class="gap">Gap: R$ {worst_gap:,.2f}</span>
                        <span class="next-payment">Próximo: {next_payment.get('date', 'N/A')}</span>
                    </div>
                    <div class="violation-details" id="liq_{hash(pool)}" style="display: none;">
                        <h4>💰 Próximo Pagamento</h4>
                        <p>Data: <strong>{next_payment.get('date', 'N/A')}</strong></p>
                        <p>Valor: <strong>R$ {next_payment.get('amount', 0):,.2f}</strong></p>
                        <p>Percentual: <strong>{next_payment.get('percentage', 0):.2f}%</strong></p>
                        
                        <h4>📊 Análise por Cenário</h4>
                        {self._format_liquidity_scenarios(violation.get('scenarios_detail', {}))}
                    </div>
                </div>"""
        
        html += """
            </div>
        </div>"""
        
        return html
    
    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Formata dados financeiros para exibição."""
        
        if not financial_data:
            return "<p>Dados financeiros não disponíveis</p>"
        
        return f"""
        <div class="financial-data">
            <p>PL Atual: <strong>R$ {financial_data.get('pl_atual', 0):,.2f}</strong></p>
            <p>SR Atual: <strong>R$ {financial_data.get('sr_atual', 0):,.2f}</strong></p>
            <p>JR Atual: <strong>R$ {financial_data.get('jr_atual', 0):,.2f}</strong></p>
        </div>"""
    
    def _format_concentration_drilldown(self, violation: Dict[str, Any]) -> str:
        """Formata drill-down de concentração."""
        
        drill_down = violation.get('drill_down_data', {})
        top_n = violation.get('top_n_breakdown', [])
        
        if not drill_down and not top_n:
            return "<p>Detalhes de drill-down não disponíveis</p>"
        
        html = "<h4>🔍 Drill-down</h4>"
        
        if top_n:
            html += "<div class='top-n-breakdown'>"
            for i, item in enumerate(top_n[:5], 1):  # Top 5
                html += f"""
                <p>{i}. {item.get('entidade', 'N/A')}: 
                   <strong>{item.get('percentual', 0):.2f}%</strong> 
                   (R$ {item.get('valor', 0):,.2f})</p>"""
            html += "</div>"
        
        return html
    
    def _format_aging_analysis(self, matriz_atrasos: Dict[str, Any]) -> str:
        """Formata análise de aging."""
        
        if not matriz_atrasos:
            return "<p>Matriz de atrasos não disponível</p>"
        
        stats = matriz_atrasos.get('estatisticas_gerais', {})
        
        return f"""
        <h4>📊 Estatísticas de Atraso</h4>
        <div class="aging-stats">
            <p>Total de títulos atrasados: <strong>{stats.get('total_titulos_atrasados', 0)}</strong></p>
            <p>Valor total em atraso: <strong>R$ {stats.get('valor_total_em_atraso', 0):,.2f}</strong></p>
            <p>Atraso médio: <strong>{stats.get('atraso_medio_dias', 0):.1f} dias</strong></p>
            <p>Cedentes afetados: <strong>{stats.get('quantidade_cedentes_afetados', 0)}</strong></p>
            <p>Sacados afetados: <strong>{stats.get('quantidade_sacados_afetados', 0)}</strong></p>
        </div>"""
    
    def _format_liquidity_scenarios(self, scenarios: Dict[str, Any]) -> str:
        """Formata cenários de liquidez."""
        
        if not scenarios:
            return "<p>Detalhes de cenários não disponíveis</p>"
        
        html = "<div class='scenarios-breakdown'>"
        
        for scenario_name, scenario_data in scenarios.items():
            sufficient = scenario_data.get('sufficient', False)
            coverage = scenario_data.get('coverage_ratio', 0)
            status = '✅ Suficiente' if sufficient else '❌ Insuficiente'
            
            html += f"""
            <div class='scenario-item'>
                <p><strong>{scenario_name.title()}:</strong> {status}</p>
                <p>Cobertura: {coverage:.2f}x</p>
            </div>"""
        
        html += "</div>"
        return html
    
    def _generate_type_breakdown(self, by_type: Dict[str, int]) -> str:
        """Gera breakdown por tipo de violação."""
        
        html = ""
        for tipo, count in by_type.items():
            if count > 0:
                html += f'<span class="type-item">{tipo.title()}: {count}</span>'
        
        return html or '<span class="type-item">Nenhuma violação</span>'
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Formata timestamp para exibição."""
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            return timestamp
    
    def _generate_empty_dashboard(self) -> str:
        """Gera dashboard vazio quando não há violações."""
        
        dashboard_file = self.output_path / "violations_dashboard.html"
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AmFi - Dashboard de Violações</title>
    <style>{self._get_css_styles()}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✅ AmFi - Dashboard de Violações</h1>
            <p class="last-updated">Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </header>
        
        <div class="empty-state">
            <h2>🎉 Nenhuma violação encontrada!</h2>
            <p>Todos os pools estão em conformidade com suas respectivas escrituras.</p>
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
    
    def _get_css_styles(self) -> str:
        """Retorna estilos CSS para o dashboard."""
        
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .last-updated {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .summary-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
        }
        
        .card.critical {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        }
        
        .card.total {
            background: linear-gradient(135deg, #4ecdc4, #44a08d);
        }
        
        .card.by-type {
            background: linear-gradient(135deg, #a8edea, #fed6e3);
            color: #333;
        }
        
        .card h3 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .card .number {
            font-size: 2.5em;
            font-weight: bold;
            display: block;
        }
        
        .type-breakdown {
            margin-top: 10px;
        }
        
        .type-item {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            margin: 2px;
            font-size: 0.9em;
        }
        
        .violation-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .violation-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .violation-item {
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 15px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .violation-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        .violation-item.critical {
            border-left: 5px solid #ff6b6b;
        }
        
        .violation-item.high {
            border-left: 5px solid #ffa726;
        }
        
        .violation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .violation-header h3 {
            color: #333;
            font-size: 1.3em;
        }
        
        .violation-type {
            background: #f0f0f0;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }
        
        .status-badge.critical {
            background: #ff6b6b;
        }
        
        .status-badge.high {
            background: #ffa726;
        }
        
        .violation-summary {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 1.1em;
        }
        
        .current-value {
            font-weight: bold;
            color: #ff6b6b;
        }
        
        .vs {
            color: #999;
        }
        
        .limit-value {
            font-weight: bold;
            color: #333;
        }
        
        .gap, .amount {
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .entity-name {
            background: #e3f2fd;
            padding: 5px 10px;
            border-radius: 5px;
            color: #1976d2;
            font-weight: bold;
        }
        
        .violation-details {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
            border-top: 2px solid #667eea;
        }
        
        .violation-details h4 {
            color: #667eea;
            margin-bottom: 15px;
            margin-top: 20px;
        }
        
        .violation-details h4:first-child {
            margin-top: 0;
        }
        
        .financial-data p, .aging-stats p, .scenario-item p {
            margin-bottom: 8px;
        }
        
        .scenarios-breakdown {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .scenario-item {
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
        
        .empty-state {
            background: white;
            padding: 60px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .empty-state h2 {
            color: #4caf50;
            margin-bottom: 20px;
            font-size: 2em;
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
            
            .violation-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .violation-summary {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """Retorna JavaScript para funcionalidade do dashboard."""
        
        return """
        function toggleDetails(elementId) {
            const element = document.getElementById(elementId);
            if (element.style.display === 'none' || element.style.display === '') {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        }
        
        // Auto-refresh a cada 5 minutos (se executado em servidor)
        setTimeout(function() {
            location.reload();
        }, 300000);
        """


def generate_dashboard() -> str:
    """
    Função de conveniência para gerar dashboard HTML.
    
    Returns:
        str: Caminho para o arquivo HTML gerado
    """
    generator = HTMLDashboardGenerator()
    return generator.generate_dashboard()


if __name__ == "__main__":
    # Teste básico do gerador de dashboard
    print("🌐 TESTE - Gerador de Dashboard HTML")
    print("=" * 60)
    
    # Gerar dashboard
    dashboard_path = generate_dashboard()
    
    if dashboard_path:
        print(f"✅ Dashboard gerado: {dashboard_path}")
        print(f"📂 Abra o arquivo em um navegador para visualizar")
    else:
        print("❌ Falha ao gerar dashboard")