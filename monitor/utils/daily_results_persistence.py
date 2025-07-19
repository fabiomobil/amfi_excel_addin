"""
Sistema de Persistência de Resultados Diários
===========================================

Responsável por:
- Salvar resultados diários consolidados em JSON
- Gerar índices para dashboard HTML
- Extrair violações ativas
- Preparar dados de drill-down
- Gerenciar histórico e compressão

Arquitetura:
- Arquivo principal: daily_consolidated/{YYYY-MM-DD}.json
- Índices para performance: violations_index/active_violations.json
- Archive comprimido: archive/{YYYY-MM}.json.gz
"""

import json
import gzip
import os
from datetime import datetime, date
from typing import Dict, Any, List
from pathlib import Path

# Compatibilidade Spyder vs módulo
try:
    from .alerts import log_alerta
except (ImportError, ValueError):
    import sys
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from alerts import log_alerta


class DailyResultsPersistence:
    """
    Sistema de persistência para resultados de monitoramento diário.
    
    Funcionalidades:
    - Salvamento consolidado por dia
    - Geração de índices para dashboard
    - Extração de violações ativas
    - Preparação de dados de drill-down
    """
    
    def __init__(self, base_path: str = "/mnt/c/amfi/data/output/monitoring_results"):
        """
        Inicializa o sistema de persistência.
        
        Args:
            base_path: Diretório base para armazenamento
        """
        self.base_path = Path(base_path)
        self.daily_path = self.base_path / "daily_consolidated"
        self.index_path = self.base_path / "violations_index"
        self.archive_path = self.base_path / "archive"
        
        # Criar diretórios se não existem
        for path in [self.daily_path, self.index_path, self.archive_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_daily_results(self, monitoring_results: Dict[str, Any], 
                          data_sources: Dict[str, str] = None) -> bool:
        """
        Salva resultados do monitoramento do dia.
        
        Args:
            monitoring_results: Resultado completo do run_monitoring()
            data_sources: Informações sobre arquivos CSV/XLSX usados
            
        Returns:
            bool: True se salvamento foi bem-sucedido
        """
        try:
            # Obter data de execução dos metadados (extraída dos arquivos) ou usar data atual
            execution_date = self._get_execution_date_from_metadata(monitoring_results)
            
            # 1. Obter dados do dia anterior para comparação
            previous_data = self._get_previous_day_data()
            
            # 2. Preparar dados consolidados com análise temporal
            consolidated_data = self._prepare_consolidated_data(
                monitoring_results, data_sources, execution_date, previous_data
            )
            
            # 3. Salvar arquivo diário
            daily_file = self.daily_path / f"{execution_date}.json"
            self._save_json_file(consolidated_data, daily_file)
            
            # 4. Extrair e salvar violações ativas
            violations = self._extract_violations(monitoring_results)
            self._update_violation_indices(violations)
            
            # 5. Gerar dashboard HTML
            dashboard_path = self._generate_html_dashboard()
            
            # 6. Log sucesso
            log_alerta({
                "tipo": "info",
                "titulo": "Persistência de Dados",
                "mensagem": f"Resultados salvos para {execution_date}",
                "detalhes": {
                    "arquivo_diario": str(daily_file),
                    "dashboard_html": dashboard_path,
                    "total_pools": len(monitoring_results.get('resultados', {})),
                    "total_violations": len(violations)
                }
            })
            
            return True
            
        except Exception as e:
            log_alerta({
                "tipo": "erro",
                "titulo": "Erro na Persistência",
                "mensagem": f"Falha ao salvar resultados: {str(e)}"
            })
            return False
    
    def _prepare_consolidated_data(self, monitoring_results: Dict[str, Any], 
                                 data_sources: Dict[str, str], 
                                 execution_date: str,
                                 previous_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepara dados consolidados para salvamento."""
        
        # Calcular estatísticas de violações
        violations = self._extract_violations(monitoring_results)
        
        # Calcular análise temporal com dados anteriores
        temporal_analysis = self._calculate_temporal_analysis(
            monitoring_results, previous_data
        )
        
        return {
            "execution_date": execution_date,
            "execution_timestamp": datetime.now().isoformat(),
            "data_sources": data_sources or {},
            "summary": {
                "total_pools": monitoring_results.get('estatisticas', {}).get('total', 0),
                "pools_with_violations": len(set(v['pool'] for v in violations)),
                "total_violations": len(violations),
                "critical_violations": len([v for v in violations if v.get('criticidade') == 'critica'])
            },
            "pools": monitoring_results.get('resultados', {}),
            "violations": violations,
            "temporal_analysis": temporal_analysis,
            "execution_stats": monitoring_results.get('estatisticas', {}),
            "metadata": {
                "version": "1.0",
                "generated_by": "AmFi Monitoring System",
                "data_retention_days": 90,
                "has_previous_data": previous_data is not None
            }
        }
    
    def _extract_violations(self, monitoring_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai todas as violações dos resultados de monitoramento.
        
        Returns:
            Lista de violações com dados para drill-down
        """
        violations = []
        
        pools_results = monitoring_results.get('resultados', {})
        
        for pool_name, pool_result in pools_results.items():
            if not pool_result.get('sucesso', False):
                continue
                
            pool_violations = pool_result.get('resultados', {})
            
            # Extrair violações de subordinação
            violations.extend(self._extract_subordinacao_violations(pool_name, pool_violations))
            
            # Extrair violações de concentração
            violations.extend(self._extract_concentracao_violations(pool_name, pool_violations))
            
            # Extrair violações de inadimplência
            violations.extend(self._extract_inadimplencia_violations(pool_name, pool_violations))
            
            # Extrair violações de liquidez
            violations.extend(self._extract_liquidez_violations(pool_name, pool_violations))
        
        return violations
    
    def _extract_subordinacao_violations(self, pool_name: str, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai violações de subordinação."""
        violations = []
        
        sub_result = results.get('subordinacao', {})
        if not sub_result:
            return violations
        
        # Verificar violação do limite mínimo
        if sub_result.get('status_limite_minimo') == 'violado':
            violations.append({
                "pool": pool_name,
                "tipo": "subordinacao",
                "subtipo": "limite_minimo",
                "status": "violado",
                "valor_atual": sub_result.get('subordination_ratio_percent', 0),
                "limite_configurado": sub_result.get('limite_minimo', 0) * 100,
                "criticidade": "alta",
                "aporte_necessario": sub_result.get('aporte_necessario', {}).get('para_limite_minimo', 0),
                "dados_financeiros": sub_result.get('dados_financeiros', {}),
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar violação do limite crítico
        if sub_result.get('status_limite_critico') == 'violado':
            violations.append({
                "pool": pool_name,
                "tipo": "subordinacao",
                "subtipo": "limite_critico",
                "status": "violado",
                "valor_atual": sub_result.get('subordination_ratio_percent', 0),
                "limite_configurado": sub_result.get('limite_critico', 0) * 100,
                "criticidade": "critica",
                "aporte_necessario": sub_result.get('aporte_necessario', {}).get('para_limite_critico', 0),
                "dados_financeiros": sub_result.get('dados_financeiros', {}),
                "timestamp": datetime.now().isoformat()
            })
        
        return violations
    
    def _extract_concentracao_violations(self, pool_name: str, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai violações de concentração."""
        violations = []
        
        conc_result = results.get('concentracao', {})
        if not conc_result or not conc_result.get('sucesso', False):
            return violations
        
        # Violações individuais
        individual = conc_result.get('concentracao_individual', {})
        for entity_type in ['sacados', 'cedentes']:
            entity_violations = individual.get(entity_type, {}).get('violacoes', [])
            
            for violation in entity_violations:
                violations.append({
                    "pool": pool_name,
                    "tipo": "concentracao",
                    "subtipo": f"individual_{entity_type[:-1]}",  # Remove 's' final
                    "entity": violation.get('entidade', ''),
                    "status": "violado",
                    "valor_atual": violation.get('percentual_atual', 0),
                    "limite_configurado": violation.get('limite_configurado', 0) * 100,
                    "amount": violation.get('valor_absoluto', 0),
                    "criticidade": "alta",
                    "drill_down_data": violation,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Violações top-N
        top_n = conc_result.get('concentracao_top_n', {})
        for entity_type in ['sacados', 'cedentes']:
            entity_data = top_n.get(entity_type, {})
            if entity_data.get('violacao', False):
                violations.append({
                    "pool": pool_name,
                    "tipo": "concentracao",
                    "subtipo": f"top_n_{entity_type[:-1]}",  # Remove 's' final
                    "status": "violado",
                    "valor_atual": entity_data.get('percentual_atual', 0),
                    "limite_configurado": entity_data.get('limite_configurado', 0) * 100,
                    "amount": entity_data.get('valor_absoluto', 0),
                    "criticidade": "alta",
                    "top_n_breakdown": entity_data.get('detalhes', []),
                    "timestamp": datetime.now().isoformat()
                })
        
        return violations
    
    def _extract_inadimplencia_violations(self, pool_name: str, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai violações de inadimplência."""
        violations = []
        
        inad_result = results.get('inadimplencia', {})
        if not inad_result or not inad_result.get('sucesso', False):
            return violations
        
        inad_results = inad_result.get('resultados', {})
        
        for monitor_id, monitor_data in inad_results.items():
            if monitor_data.get('status') == 'violado':
                violations.append({
                    "pool": pool_name,
                    "tipo": "inadimplencia",
                    "subtipo": monitor_id,
                    "status": "violado",
                    "valor_atual": monitor_data.get('inadimplencia_percent', 0),
                    "limite_configurado": monitor_data.get('limite_configurado', 0) * 100,
                    "amount": monitor_data.get('valor_inadimplente', 0),
                    "criticidade": "alta",
                    "janela_dias": monitor_data.get('prazo_dias', 0),
                    "matriz_atrasos": inad_result.get('matriz_atrasos', {}),
                    "timestamp": datetime.now().isoformat()
                })
        
        return violations
    
    def _extract_liquidez_violations(self, pool_name: str, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai violações de liquidez."""
        violations = []
        
        liquidez_result = results.get('liquidez', {})
        if not liquidez_result or not liquidez_result.get('success', False):
            return violations
        
        summary = liquidez_result.get('summary', {})
        scenarios = liquidez_result.get('scenarios', {})
        
        # Se nem todos os cenários são suficientes, há problema de liquidez
        if not summary.get('all_scenarios_sufficient', True):
            # Encontrar o pior cenário
            worst_scenario = None
            worst_gap = 0
            
            for scenario_name, scenario_data in scenarios.items():
                if not scenario_data.get('sufficient', True):
                    gap = scenario_data.get('gap', 0)
                    if gap > worst_gap:
                        worst_gap = gap
                        worst_scenario = scenario_name
            
            if worst_scenario:
                violations.append({
                    "pool": pool_name,
                    "tipo": "liquidez",
                    "subtipo": "insuficiencia_cenarios",
                    "status": "violado",
                    "worst_scenario": worst_scenario,
                    "worst_gap": worst_gap,
                    "next_payment": liquidez_result.get('next_payment', {}),
                    "criticidade": "critica",
                    "scenarios_detail": scenarios,
                    "timestamp": datetime.now().isoformat()
                })
        
        return violations
    
    def _update_violation_indices(self, violations: List[Dict[str, Any]]) -> None:
        """Atualiza índices de violações para dashboard."""
        
        # Agrupar violações por tipo
        violations_by_type = {
            "subordinacao": [],
            "concentracao": [],
            "inadimplencia": [],
            "liquidez": []
        }
        
        for violation in violations:
            tipo = violation.get('tipo', '')
            if tipo in violations_by_type:
                violations_by_type[tipo].append(violation)
        
        # Ordenar por criticidade e data
        for tipo in violations_by_type:
            violations_by_type[tipo].sort(
                key=lambda x: (
                    0 if x.get('criticidade') == 'critica' else 1,  # Críticas primeiro
                    x.get('timestamp', '')  # Mais antigas primeiro
                )
            )
        
        # Preparar dados para dashboard
        active_violations = {
            "last_updated": datetime.now().isoformat(),
            "summary": {
                "total_violations": len(violations),
                "critical_violations": len([v for v in violations if v.get('criticidade') == 'critica']),
                "by_type": {tipo: len(viols) for tipo, viols in violations_by_type.items()}
            },
            "subordinacao": violations_by_type["subordinacao"],
            "concentracao": violations_by_type["concentracao"],
            "inadimplencia": violations_by_type["inadimplencia"],
            "liquidez": violations_by_type["liquidez"]
        }
        
        # Salvar índice principal
        index_file = self.index_path / "active_violations.json"
        self._save_json_file(active_violations, index_file)
        
        # Salvar índices específicos por tipo
        for tipo, viols in violations_by_type.items():
            if viols:  # Só salvar se tiver violações
                type_file = self.index_path / f"{tipo}_violations.json"
                self._save_json_file({
                    "tipo": tipo,
                    "last_updated": datetime.now().isoformat(),
                    "violations": viols
                }, type_file)
    
    def _save_json_file(self, data: Dict[str, Any], file_path: Path) -> None:
        """Salva dados em arquivo JSON com formatação legível."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _generate_html_dashboard(self) -> str:
        """
        Gera dashboard HTML automaticamente.
        
        Returns:
            str: Caminho para o dashboard HTML gerado
        """
        try:
            # Import local para evitar dependência circular
            from .html_dashboard_generator import HTMLDashboardGenerator
            from .comprehensive_dashboard_generator import ComprehensiveDashboardGenerator
            
            # Gerar dashboard de violações (original)
            violations_generator = HTMLDashboardGenerator(self)
            violations_path = violations_generator.generate_dashboard()
            
            # Gerar dashboard completo (novo)
            comprehensive_generator = ComprehensiveDashboardGenerator(self)
            comprehensive_path = comprehensive_generator.generate_comprehensive_dashboard()
            
            return comprehensive_path  # Retornar o dashboard completo como principal
            
        except Exception as e:
            log_alerta({
                "tipo": "warning",
                "titulo": "Dashboard HTML",
                "mensagem": f"Falha ao gerar dashboard HTML: {str(e)}"
            })
            return ""
    
    def _get_execution_date_from_metadata(self, monitoring_results: Dict[str, Any]) -> str:
        """
        Obtém data de execução dos metadados (extraída dos arquivos) ou usa data atual.
        
        Args:
            monitoring_results: Resultados do monitoramento com metadados
            
        Returns:
            str: Data de execução no formato ISO (YYYY-MM-DD)
        """
        try:
            # PRIORIDADE 1: Verificar se há data forçada via variável de ambiente
            forced_date = os.environ.get('FORCE_EXECUTION_DATE')
            if forced_date:
                log_alerta({
                    "tipo": "info",
                    "titulo": "Data de Execução",
                    "mensagem": f"📅 Usando data forçada: {forced_date}",
                    "detalhes": {
                        "fonte": "environment_variable",
                        "variable": "FORCE_EXECUTION_DATE"
                    }
                })
                return forced_date
            
            # PRIORIDADE 2: Tentar obter data dos metadados (validação de arquivos)
            metadados = monitoring_results.get('metadados', {})
            execution_date = metadados.get('execution_date')
            
            if execution_date:
                log_alerta({
                    "tipo": "info",
                    "titulo": "Data de Execução",
                    "mensagem": f"📅 Usando data extraída dos arquivos: {execution_date}",
                    "detalhes": {
                        "fonte": "metadados_validacao",
                        "date_validation": metadados.get('date_validation', {})
                    }
                })
                return execution_date
            else:
                # PRIORIDADE 3: Fallback para data atual
                current_date = date.today().isoformat()
                log_alerta({
                    "tipo": "warning",
                    "titulo": "Data de Execução",
                    "mensagem": f"⚠️ Data não encontrada nos metadados, usando data atual: {current_date}"
                })
                return current_date
                
        except Exception as e:
            # Em caso de erro, usar data atual
            current_date = date.today().isoformat()
            log_alerta({
                "tipo": "warning",
                "titulo": "Erro na Data de Execução",
                "mensagem": f"Erro ao obter data dos metadados: {str(e)}, usando data atual: {current_date}"
            })
            return current_date
    
    def _get_previous_day_data(self) -> Dict[str, Any]:
        """
        Obtém dados do dia anterior para análise temporal.
        
        Returns:
            Dict com dados do dia anterior ou dict vazio se não encontrado
        """
        from datetime import timedelta
        
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        previous_file = self.daily_path / f"{yesterday}.json"
        
        if not previous_file.exists():
            return {}
        
        try:
            with open(previous_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_alerta({
                "tipo": "warning",
                "titulo": "Dados Anteriores",
                "mensagem": f"Falha ao carregar dados de {yesterday}: {str(e)}"
            })
            return {}
    
    def _calculate_temporal_analysis(self, current_results: Dict[str, Any], 
                                   previous_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula análise temporal comparando dados atuais com D-1.
        
        Args:
            current_results: Resultados do monitoramento atual
            previous_data: Dados do dia anterior
            
        Returns:
            Dict com análise temporal por pool e indicador
        """
        if not previous_data:
            return {"status": "no_previous_data", "pools": {}}
        
        temporal_analysis = {
            "status": "with_comparison",
            "comparison_date": previous_data.get('execution_date', 'unknown'),
            "pools": {}
        }
        
        current_pools = current_results.get('resultados', {})
        previous_pools = previous_data.get('pools', {})
        
        for pool_name, current_pool in current_pools.items():
            if not current_pool.get('sucesso', False):
                continue
                
            previous_pool = previous_pools.get(pool_name, {})
            if not previous_pool:
                temporal_analysis['pools'][pool_name] = {
                    "status": "new_pool",
                    "indicators": {}
                }
                continue
            
            # Análise de indicadores
            pool_analysis = {
                "status": "compared",
                "indicators": {}
            }
            
            current_indicators = current_pool.get('resultados', {})
            previous_indicators = previous_pool.get('resultados', {})
            
            # Análise de Subordinação
            if 'subordinacao' in current_indicators and 'subordinacao' in previous_indicators:
                pool_analysis['indicators']['subordinacao'] = self._analyze_subordinacao_delta(
                    current_indicators['subordinacao'],
                    previous_indicators['subordinacao']
                )
            
            # Análise de Concentração
            if 'concentracao' in current_indicators and 'concentracao' in previous_indicators:
                pool_analysis['indicators']['concentracao'] = self._analyze_concentracao_delta(
                    current_indicators['concentracao'],
                    previous_indicators['concentracao']
                )
            
            # Análise de Inadimplência
            if 'inadimplencia' in current_indicators and 'inadimplencia' in previous_indicators:
                pool_analysis['indicators']['inadimplencia'] = self._analyze_inadimplencia_delta(
                    current_indicators['inadimplencia'],
                    previous_indicators['inadimplencia']
                )
            
            # Análise de Liquidez
            if 'liquidez' in current_indicators and 'liquidez' in previous_indicators:
                pool_analysis['indicators']['liquidez'] = self._analyze_liquidez_delta(
                    current_indicators['liquidez'],
                    previous_indicators['liquidez']
                )
            
            temporal_analysis['pools'][pool_name] = pool_analysis
        
        return temporal_analysis
    
    def _analyze_subordinacao_delta(self, current: Dict[str, Any], 
                                  previous: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa delta de subordinação entre D-1 e hoje."""
        
        current_ratio = current.get('subordination_ratio_percent', 0)
        previous_ratio = previous.get('subordination_ratio_percent', 0)
        delta = current_ratio - previous_ratio
        
        return {
            "type": "subordinacao",
            "current_value": current_ratio,
            "previous_value": previous_ratio,
            "delta": delta,
            "delta_percent": (delta / previous_ratio * 100) if previous_ratio != 0 else 0,
            "trend": "up" if delta > 0 else "down" if delta < 0 else "stable",
            "status_current": current.get('status_limite_minimo', 'unknown'),
            "status_previous": previous.get('status_limite_minimo', 'unknown'),
            "status_changed": current.get('status_limite_minimo') != previous.get('status_limite_minimo')
        }
    
    def _analyze_concentracao_delta(self, current: Dict[str, Any], 
                                  previous: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa delta de concentração entre D-1 e hoje."""
        
        # Análise simplificada - pode ser expandida
        current_violations = len(current.get('concentracao_individual', {}).get('sacados', {}).get('violacoes', []))
        previous_violations = len(previous.get('concentracao_individual', {}).get('sacados', {}).get('violacoes', []))
        delta_violations = current_violations - previous_violations
        
        return {
            "type": "concentracao",
            "current_violations": current_violations,
            "previous_violations": previous_violations,
            "delta_violations": delta_violations,
            "trend": "worse" if delta_violations > 0 else "better" if delta_violations < 0 else "stable",
            "status_changed": delta_violations != 0
        }
    
    def _analyze_inadimplencia_delta(self, current: Dict[str, Any], 
                                   previous: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa delta de inadimplência entre D-1 e hoje."""
        
        # Comparar inadimplência 30d como principal indicador
        current_results = current.get('resultados', {})
        previous_results = previous.get('resultados', {})
        
        current_30d = None
        previous_30d = None
        
        # Encontrar monitor de 30 dias
        for monitor_id, data in current_results.items():
            if '30' in monitor_id:
                current_30d = data.get('inadimplencia_percent', 0)
                break
        
        for monitor_id, data in previous_results.items():
            if '30' in monitor_id:
                previous_30d = data.get('inadimplencia_percent', 0)
                break
        
        if current_30d is None or previous_30d is None:
            return {"type": "inadimplencia", "status": "insufficient_data"}
        
        delta = current_30d - previous_30d
        
        return {
            "type": "inadimplencia",
            "current_value": current_30d,
            "previous_value": previous_30d,
            "delta": delta,
            "delta_percent": (delta / previous_30d * 100) if previous_30d != 0 else 0,
            "trend": "worse" if delta > 0 else "better" if delta < 0 else "stable"
        }
    
    def _analyze_liquidez_delta(self, current: Dict[str, Any], 
                              previous: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa delta de liquidez entre D-1 e hoje."""
        
        current_sufficient = current.get('summary', {}).get('all_scenarios_sufficient', True)
        previous_sufficient = previous.get('summary', {}).get('all_scenarios_sufficient', True)
        
        return {
            "type": "liquidez",
            "current_sufficient": current_sufficient,
            "previous_sufficient": previous_sufficient,
            "status_changed": current_sufficient != previous_sufficient,
            "trend": "better" if current_sufficient and not previous_sufficient else 
                    "worse" if not current_sufficient and previous_sufficient else "stable"
        }
    
    def get_historical_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Carrega dados históricos dos últimos N dias.
        
        Args:
            days: Número de dias para carregar
            
        Returns:
            Lista de dados diários ordenados por data
        """
        historical_data = []
        
        for json_file in sorted(self.daily_path.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historical_data.append(data)
            except Exception as e:
                log_alerta({
                    "tipo": "warning",
                    "titulo": "Erro ao Carregar Histórico",
                    "mensagem": f"Falha ao carregar {json_file.name}: {str(e)}"
                })
        
        # Retornar apenas os últimos N dias
        return historical_data[-days:] if len(historical_data) > days else historical_data
    
    def get_active_violations(self) -> Dict[str, Any]:
        """
        Carrega violações ativas do índice.
        
        Returns:
            Dados de violações ativas ou dict vazio se não encontrado
        """
        index_file = self.index_path / "active_violations.json"
        
        if not index_file.exists():
            return {}
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_alerta({
                "tipo": "warning",
                "titulo": "Erro ao Carregar Violações",
                "mensagem": f"Falha ao carregar índice de violações: {str(e)}"
            })
            return {}


def save_monitoring_results(monitoring_results: Dict[str, Any], 
                          data_sources: Dict[str, str] = None) -> bool:
    """
    Função de conveniência para salvar resultados de monitoramento.
    
    Args:
        monitoring_results: Resultado completo do run_monitoring()
        data_sources: Informações sobre arquivos CSV/XLSX usados
        
    Returns:
        bool: True se salvamento foi bem-sucedido
    """
    persistence = DailyResultsPersistence()
    return persistence.save_daily_results(monitoring_results, data_sources)


if __name__ == "__main__":
    # Teste básico do sistema de persistência
    print("🗄️ TESTE - Sistema de Persistência de Resultados")
    print("=" * 60)
    
    # Criar instância
    persistence = DailyResultsPersistence()
    
    # Dados de teste
    test_results = {
        "sucesso": True,
        "timestamp": datetime.now().isoformat(),
        "pools_processados": ["LeCapital Pool #1"],
        "estatisticas": {
            "total": 1,
            "sucesso": 1,
            "erro": 0,
            "taxa_sucesso": 100.0
        },
        "resultados": {
            "LeCapital Pool #1": {
                "sucesso": True,
                "pool": "LeCapital Pool #1",
                "monitores_executados": ["subordinacao"],
                "resultados": {
                    "subordinacao": {
                        "subordination_ratio_percent": 25.18,
                        "status_limite_minimo": "enquadrado",
                        "limite_minimo": 0.25
                    }
                }
            }
        }
    }
    
    test_sources = {
        "csv_file": "AcompanhamentoDeOportunidades-2025-07-18.csv",
        "xlsx_file": "Carteira Global 2025-07-18.xlsx"
    }
    
    # Testar salvamento
    success = persistence.save_daily_results(test_results, test_sources)
    
    if success:
        print("✅ Teste de salvamento bem-sucedido")
        
        # Testar carregamento
        violations = persistence.get_active_violations()
        print(f"📊 Violações carregadas: {len(violations.get('subordinacao', []))}")
        
    else:
        print("❌ Teste de salvamento falhou")