"""
PDD Hierarchical Dashboard API Endpoints
========================================

Módulo de endpoints para dashboard PDD hierárquico do sistema AmFi.
Fornece APIs REST para servir dados de PDD organizados hierarquicamente.

Funcionalidades:
- Estrutura hierárquica completa grupos→cedentes→ativos
- Análise de cedentes por grupo de risco  
- Piores ativos por cedente
- Tendências históricas e indicadores
- Resumo de risco para heat maps
- Cache inteligente para performance

Endpoints implementados:
- GET /api/pdd/{pool_id}/hierarchy
- GET /api/pdd/{pool_id}/group/{group_id}/cedentes  
- GET /api/pdd/cedente/{cedente_id}/worst_assets
- GET /api/pdd/{pool_id}/trends
- GET /api/pdd/{pool_id}/risk_summary

Autor: AmFi Development Team
Data: 2025-07-22
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from functools import lru_cache
from collections import defaultdict
import pandas as pd

# Adicionar paths para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')
sys.path.insert(0, '/mnt/c/amfi/monitor/utils')

try:
    from pdd_analysis import load_historical_monitoring_data
    from data_handler import DataHandler
except ImportError as e:
    print(f"⚠️ Import warning: {e}")


class PDDHierarchicalAPI:
    """
    API para dashboard PDD hierárquico.
    
    Fornece endpoints RESTful para dados PDD organizados hierarquicamente
    com cache inteligente e otimizações de performance.
    """
    
    def __init__(self):
        """Inicializa a API PDD."""
        self.cache_ttl = 300  # 5 minutos em segundos
        self._cache = {}
        self._cache_timestamps = {}
        self.data_handler = DataHandler() if 'DataHandler' in globals() else None
        
    def _is_cache_valid(self, key: str) -> bool:
        """
        Verifica se o cache para uma chave é válido.
        
        Args:
            key: Chave do cache
            
        Returns:
            True se cache é válido
        """
        if key not in self._cache_timestamps:
            return False
            
        return (datetime.now() - self._cache_timestamps[key]).total_seconds() < self.cache_ttl
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache se válido.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor do cache ou None
        """
        if self._is_cache_valid(key):
            return self._cache.get(key)
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """
        Armazena valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
        """
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def _load_latest_pool_data(self, pool_id: str) -> Optional[Dict[str, Any]]:
        """
        Carrega dados mais recentes de um pool específico.
        
        Args:
            pool_id: ID do pool
            
        Returns:
            Dados do pool ou None se não encontrado
        """
        try:
            historical_data = load_historical_monitoring_data()
            
            if not historical_data:
                return None
            
            # Usar dados mais recentes
            latest_data = historical_data[0]['data']
            pools = latest_data.get('pools', {})
            
            if pool_id not in pools:
                return None
                
            pool_data = pools[pool_id]
            
            if not pool_data.get('sucesso', False):
                return None
                
            return pool_data.get('resultados', {}).get('pdd', {})
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados do pool {pool_id}: {e}")
            return None
    
    def _extract_risk_groups_config(self, pool_id: str) -> Dict[str, Any]:
        """
        Extrai configuração de grupos de risco para um pool.
        
        Args:
            pool_id: ID do pool
            
        Returns:
            Configuração de grupos de risco
        """
        try:
            # Carregar configuração do pool
            config_path = Path(f'/mnt/c/amfi/config/pools/{pool_id}.json')
            
            if not config_path.exists():
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config.get('provisoes_pdd', {}).get('grupos_risco', {})
            
        except Exception as e:
            print(f"❌ Erro ao carregar config do pool {pool_id}: {e}")
            return {}
    
    def get_hierarchy(self, pool_id: str) -> Dict[str, Any]:
        """
        GET /api/pdd/{pool_id}/hierarchy
        
        Retorna estrutura hierárquica completa grupos→cedentes→ativos.
        
        Args:
            pool_id: ID do pool
            
        Returns:
            Estrutura hierárquica completa
        """
        cache_key = f"hierarchy_{pool_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Carregar dados PDD do pool
            pdd_data = self._load_latest_pool_data(pool_id)
            
            if not pdd_data or not pdd_data.get('sucesso', False):
                return {
                    "success": False,
                    "error": f"Dados PDD não encontrados para pool {pool_id}",
                    "pool_id": pool_id
                }
            
            # Carregar configuração de grupos de risco
            risk_groups_config = self._extract_risk_groups_config(pool_id)
            
            # Extrair análise por cedente
            cedente_analysis = pdd_data.get('cedente_analysis', {})
            cedentes_data = cedente_analysis.get('cedentes', {})
            
            # Extrair análise por grupo
            pdd_analysis = pdd_data.get('pdd_analysis', {})
            grupos_data = pdd_analysis.get('grupos', {})
            
            # Construir hierarquia: grupos → cedentes → ativos
            hierarchy = {
                "pool_id": pool_id,
                "timestamp": datetime.now().isoformat(),
                "total_groups": len(risk_groups_config),
                "total_cedentes": len(cedentes_data),
                "metodologia": "por_cedente",
                "grupos": {}
            }
            
            # Para cada grupo de risco configurado
            for group_id in sorted(risk_groups_config.keys()):
                group_config = risk_groups_config[group_id]
                group_stats = grupos_data.get(group_id, {})
                
                # Encontrar cedentes neste grupo
                cedentes_no_grupo = []
                
                for cedente_nome, cedente_info in cedentes_data.items():
                    if cedente_info.get('grupo_pdd_aplicado') == group_id:
                        # Informações básicas do cedente para hierarquia
                        cedente_summary = {
                            "nome": cedente_nome,
                            "total_titulos": cedente_info.get('total_titulos', 0),
                            "valor_total": cedente_info.get('valor_total', 0),
                            "provisao_pct": cedente_info.get('provisao_pct', 0),
                            "provisao_valor": cedente_info.get('provisao_valor', 0),
                            "titulo_mais_atrasado": cedente_info.get('titulo_mais_atrasado', {}),
                            "ui_metadata": {
                                "color": self._get_risk_color(group_id),
                                "icon": self._get_risk_icon(group_id),
                                "status": self._get_cedente_status(cedente_info)
                            }
                        }
                        
                        cedentes_no_grupo.append(cedente_summary)
                
                # Ordenar cedentes por provisão descendente
                cedentes_no_grupo.sort(key=lambda x: x['provisao_valor'], reverse=True)
                
                # Adicionar grupo à hierarquia
                hierarchy["grupos"][group_id] = {
                    "group_id": group_id,
                    "config": {
                        "atraso_max_dias": group_config.get('atraso_max_dias', 0),
                        "provisao_pct": group_config.get('provisao_pct', 0) * 100
                    },
                    "stats": {
                        "quantidade_titulos": group_stats.get('quantidade', 0),
                        "valor_total": group_stats.get('valor_total', 0),
                        "provisao_valor": group_stats.get('provisao_valor', 0),
                        "cedentes_afetados": len(cedentes_no_grupo)
                    },
                    "cedentes": cedentes_no_grupo,
                    "ui_metadata": {
                        "color": self._get_risk_color(group_id),
                        "icon": self._get_risk_icon(group_id),
                        "severity": self._get_group_severity(group_id)
                    }
                }
            
            # Adicionar totais consolidados
            totais = pdd_analysis.get('totais', {})
            hierarchy["totals"] = {
                "carteira_valor": totais.get('carteira_valor', 0),
                "provisao_valor": totais.get('provisao_valor', 0),
                "provisao_percentual": totais.get('provisao_percentual', 0)
            }
            
            result = {
                "success": True,
                "data": hierarchy
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"❌ Erro ao obter hierarquia PDD: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "pool_id": pool_id
            }
    
    def get_group_cedentes(self, pool_id: str, group_id: str) -> Dict[str, Any]:
        """
        GET /api/pdd/{pool_id}/group/{group_id}/cedentes
        
        Retorna cedentes de um grupo específico com detalhes.
        
        Args:
            pool_id: ID do pool
            group_id: ID do grupo de risco
            
        Returns:
            Lista de cedentes do grupo com detalhes
        """
        cache_key = f"group_cedentes_{pool_id}_{group_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Carregar dados PDD do pool
            pdd_data = self._load_latest_pool_data(pool_id)
            
            if not pdd_data or not pdd_data.get('sucesso', False):
                return {
                    "success": False,
                    "error": f"Dados PDD não encontrados para pool {pool_id}",
                    "pool_id": pool_id,
                    "group_id": group_id
                }
            
            # Extrair análise por cedente
            cedente_analysis = pdd_data.get('cedente_analysis', {})
            cedentes_data = cedente_analysis.get('cedentes', {})
            
            # Filtrar cedentes do grupo específico
            cedentes_do_grupo = []
            
            for cedente_nome, cedente_info in cedentes_data.items():
                if cedente_info.get('grupo_pdd_aplicado') == group_id:
                    titulo_mais_atrasado = cedente_info.get('titulo_mais_atrasado', {})
                    
                    cedente_detail = {
                        "cedente_nome": cedente_nome,
                        "total_titulos": cedente_info.get('total_titulos', 0),
                        "valor_total": cedente_info.get('valor_total', 0),
                        "provisao_pct": cedente_info.get('provisao_pct', 0),
                        "provisao_valor": cedente_info.get('provisao_valor', 0),
                        "grupo_aplicado": group_id,
                        "titulo_mais_atrasado": {
                            "dias_atraso": titulo_mais_atrasado.get('dias_atraso', 0),
                            "grupo_original": titulo_mais_atrasado.get('grupo_original', 'N/A'),
                            "valor": titulo_mais_atrasado.get('valor', 0),
                            "data_vencimento": titulo_mais_atrasado.get('data_vencimento', 'N/A')
                        },
                        "distribuicao_grupos_originais": cedente_info.get('distribuicao_grupos_originais', {}),
                        "ranking_no_grupo": 0,  # Será atualizado após ordenação
                        "ui_metadata": {
                            "color": self._get_risk_color(group_id),
                            "status": self._get_cedente_status(cedente_info),
                            "severity_level": self._calculate_cedente_severity(cedente_info)
                        }
                    }
                    
                    cedentes_do_grupo.append(cedente_detail)
            
            # Ordenar por provisão descendente e adicionar ranking
            cedentes_do_grupo.sort(key=lambda x: x['provisao_valor'], reverse=True)
            for i, cedente in enumerate(cedentes_do_grupo):
                cedente['ranking_no_grupo'] = i + 1
            
            result = {
                "success": True,
                "data": {
                    "pool_id": pool_id,
                    "group_id": group_id,
                    "timestamp": datetime.now().isoformat(),
                    "total_cedentes": len(cedentes_do_grupo),
                    "total_valor": sum(c['valor_total'] for c in cedentes_do_grupo),
                    "total_provisao": sum(c['provisao_valor'] for c in cedentes_do_grupo),
                    "cedentes": cedentes_do_grupo
                }
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"❌ Erro ao obter cedentes do grupo {group_id}: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "pool_id": pool_id,
                "group_id": group_id
            }
    
    def get_cedente_worst_assets(self, cedente_id: str, pool_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        GET /api/pdd/cedente/{cedente_id}/worst_assets
        
        Retorna piores ativos de um cedente específico.
        
        Args:
            cedente_id: Nome/ID do cedente
            pool_id: ID do pool (opcional, busca em todos se não especificado)
            limit: Número máximo de ativos a retornar
            
        Returns:
            Lista dos piores ativos do cedente
        """
        cache_key = f"worst_assets_{cedente_id}_{pool_id}_{limit}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            historical_data = load_historical_monitoring_data()
            
            if not historical_data:
                return {
                    "success": False,
                    "error": "Dados históricos não disponíveis",
                    "cedente_id": cedente_id
                }
            
            # Usar dados mais recentes
            latest_data = historical_data[0]['data']
            pools = latest_data.get('pools', {})
            
            worst_assets = []
            pools_found = []
            
            # Buscar em pools específicos ou todos
            target_pools = [pool_id] if pool_id else pools.keys()
            
            for current_pool_id in target_pools:
                if current_pool_id not in pools:
                    continue
                    
                pool_data = pools[current_pool_id]
                
                if not pool_data.get('sucesso', False):
                    continue
                
                resultados = pool_data.get('resultados', {})
                pdd_result = resultados.get('pdd', {})
                
                if not pdd_result.get('sucesso', False):
                    continue
                
                # Verificar se cedente existe neste pool
                cedente_analysis = pdd_result.get('cedente_analysis', {})
                cedentes_data = cedente_analysis.get('cedentes', {})
                
                if cedente_id not in cedentes_data:
                    continue
                
                pools_found.append(current_pool_id)
                cedente_info = cedentes_data[cedente_id]
                
                # Extrair título mais atrasado (que determina PDD do cedente)
                titulo_mais_atrasado = cedente_info.get('titulo_mais_atrasado', {})
                
                if titulo_mais_atrasado:
                    asset_info = {
                        "pool_id": current_pool_id,
                        "cedente_nome": cedente_id,
                        "dias_atraso": titulo_mais_atrasado.get('dias_atraso', 0),
                        "grupo_risco_original": titulo_mais_atrasado.get('grupo_original', 'N/A'),
                        "grupo_pdd_aplicado": cedente_info.get('grupo_pdd_aplicado', 'N/A'),
                        "valor_titulo": titulo_mais_atrasado.get('valor', 0),
                        "data_vencimento": titulo_mais_atrasado.get('data_vencimento', 'N/A'),
                        "provisao_pct": cedente_info.get('provisao_pct', 0),
                        "provisao_valor_titulo": titulo_mais_atrasado.get('valor', 0) * cedente_info.get('provisao_pct', 0) / 100,
                        "total_titulos_cedente": cedente_info.get('total_titulos', 0),
                        "valor_total_cedente": cedente_info.get('valor_total', 0),
                        "ui_metadata": {
                            "is_worst_in_cedente": True,
                            "color": self._get_risk_color(cedente_info.get('grupo_pdd_aplicado', 'AA')),
                            "severity": self._get_atraso_severity(titulo_mais_atrasado.get('dias_atraso', 0))
                        }
                    }
                    
                    worst_assets.append(asset_info)
            
            # Ordenar por dias de atraso descendente
            worst_assets.sort(key=lambda x: x['dias_atraso'], reverse=True)
            
            # Limitar resultados
            worst_assets = worst_assets[:limit]
            
            # Adicionar ranking
            for i, asset in enumerate(worst_assets):
                asset['ranking'] = i + 1
            
            result = {
                "success": True,
                "data": {
                    "cedente_id": cedente_id,
                    "pools_searched": target_pools if pool_id else list(pools.keys()),
                    "pools_found": pools_found,
                    "timestamp": datetime.now().isoformat(),
                    "total_assets": len(worst_assets),
                    "limit_applied": limit,
                    "worst_assets": worst_assets,
                    "summary": {
                        "max_dias_atraso": max([a['dias_atraso'] for a in worst_assets]) if worst_assets else 0,
                        "total_valor_pior_titulos": sum([a['valor_titulo'] for a in worst_assets]),
                        "total_provisao_pior_titulos": sum([a['provisao_valor_titulo'] for a in worst_assets])
                    }
                }
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"❌ Erro ao obter piores ativos do cedente {cedente_id}: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "cedente_id": cedente_id
            }
    
    def get_trends(self, pool_id: str, days: int = 30) -> Dict[str, Any]:
        """
        GET /api/pdd/{pool_id}/trends
        
        Retorna tendências históricas e indicadores de PDD.
        
        Args:
            pool_id: ID do pool
            days: Número de dias históricos a analisar
            
        Returns:
            Tendências históricas e indicadores
        """
        cache_key = f"trends_{pool_id}_{days}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            historical_data = load_historical_monitoring_data()
            
            if not historical_data:
                return {
                    "success": False,
                    "error": "Dados históricos não disponíveis",
                    "pool_id": pool_id
                }
            
            # Limitar aos últimos N dias
            sorted_data = sorted(historical_data, key=lambda x: x['date'], reverse=True)[:days]
            
            trends = {
                "pool_id": pool_id,
                "timestamp": datetime.now().isoformat(),
                "period_days": len(sorted_data),
                "requested_days": days,
                "trends": {
                    "provisao_percentual": [],
                    "provisao_valor": [],
                    "cedentes_com_provisao": [],
                    "grupos_ativos": []
                },
                "indicators": {},
                "alerts": []
            }
            
            # Extrair dados históricos
            for entry in sorted_data:
                date = entry['date']
                data = entry['data']
                pools = data.get('pools', {})
                
                if pool_id not in pools:
                    continue
                
                pool_data = pools[pool_id]
                
                if not pool_data.get('sucesso', False):
                    continue
                
                resultados = pool_data.get('resultados', {})
                pdd_result = resultados.get('pdd', {})
                
                if not pdd_result.get('sucesso', False):
                    continue
                
                # Extrair métricas
                pdd_analysis = pdd_result.get('pdd_analysis', {})
                cedente_analysis = pdd_result.get('cedente_analysis', {})
                
                totais = pdd_analysis.get('totais', {})
                grupos = pdd_analysis.get('grupos', {})
                
                # Adicionar pontos de dados
                trends["trends"]["provisao_percentual"].append({
                    "date": date,
                    "value": totais.get('provisao_percentual', 0)
                })
                
                trends["trends"]["provisao_valor"].append({
                    "date": date,
                    "value": totais.get('provisao_valor', 0)
                })
                
                # Contar cedentes com provisão > 0
                cedentes_data = cedente_analysis.get('cedentes', {})
                cedentes_com_provisao = sum(1 for c in cedentes_data.values() if c.get('provisao_valor', 0) > 0)
                
                trends["trends"]["cedentes_com_provisao"].append({
                    "date": date,
                    "value": cedentes_com_provisao
                })
                
                # Contar grupos ativos (com exposição)
                grupos_ativos = sum(1 for g in grupos.values() if g.get('quantidade', 0) > 0)
                
                trends["trends"]["grupos_ativos"].append({
                    "date": date,
                    "value": grupos_ativos
                })
            
            # Calcular indicadores de tendência
            if trends["trends"]["provisao_percentual"]:
                provisao_values = [p["value"] for p in trends["trends"]["provisao_percentual"]]
                
                trends["indicators"] = {
                    "provisao_atual": provisao_values[0] if provisao_values else 0,
                    "provisao_media": sum(provisao_values) / len(provisao_values) if provisao_values else 0,
                    "provisao_max": max(provisao_values) if provisao_values else 0,
                    "provisao_min": min(provisao_values) if provisao_values else 0,
                    "tendencia": self._calculate_trend(provisao_values),
                    "volatilidade": self._calculate_volatility(provisao_values),
                    "dias_consecutivos_alta": self._count_consecutive_high_days(provisao_values, 5.0),
                    "melhor_dia": {
                        "date": trends["trends"]["provisao_percentual"][provisao_values.index(min(provisao_values))]["date"] if provisao_values else None,
                        "value": min(provisao_values) if provisao_values else 0
                    },
                    "pior_dia": {
                        "date": trends["trends"]["provisao_percentual"][provisao_values.index(max(provisao_values))]["date"] if provisao_values else None,
                        "value": max(provisao_values) if provisao_values else 0
                    }
                }
                
                # Gerar alertas baseados em tendências
                trends["alerts"] = self._generate_trend_alerts(trends["indicators"], provisao_values)
            
            result = {
                "success": True,
                "data": trends
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"❌ Erro ao obter tendências PDD: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "pool_id": pool_id
            }
    
    def get_risk_summary(self, pool_id: str) -> Dict[str, Any]:
        """
        GET /api/pdd/{pool_id}/risk_summary
        
        Retorna resumo de risco otimizado para heat maps.
        
        Args:
            pool_id: ID do pool
            
        Returns:
            Resumo de risco para visualização em heat map
        """
        cache_key = f"risk_summary_{pool_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Carregar dados PDD do pool
            pdd_data = self._load_latest_pool_data(pool_id)
            
            if not pdd_data or not pdd_data.get('sucesso', False):
                return {
                    "success": False,
                    "error": f"Dados PDD não encontrados para pool {pool_id}",
                    "pool_id": pool_id
                }
            
            # Extrair análises
            pdd_analysis = pdd_data.get('pdd_analysis', {})
            cedente_analysis = pdd_data.get('cedente_analysis', {})
            
            grupos_data = pdd_analysis.get('grupos', {})
            cedentes_data = cedente_analysis.get('cedentes', {})
            totais = pdd_analysis.get('totais', {})
            
            # Construir heat map por grupos
            risk_groups_heatmap = []
            
            for group_id in sorted(grupos_data.keys()):
                group_stats = grupos_data[group_id]
                
                # Contar cedentes neste grupo
                cedentes_no_grupo = sum(1 for c in cedentes_data.values() if c.get('grupo_pdd_aplicado') == group_id)
                
                risk_groups_heatmap.append({
                    "group_id": group_id,
                    "risk_level": self._get_group_severity(group_id),
                    "quantidade_titulos": group_stats.get('quantidade', 0),
                    "valor_total": group_stats.get('valor_total', 0),
                    "provisao_valor": group_stats.get('provisao_valor', 0),
                    "cedentes_afetados": cedentes_no_grupo,
                    "percentual_carteira": (group_stats.get('valor_total', 0) / totais.get('carteira_valor', 1)) * 100,
                    "color": self._get_risk_color(group_id),
                    "severity_score": self._calculate_group_severity_score(group_id, group_stats)
                })
            
            # Top cedentes por risco
            top_risk_cedentes = []
            
            for cedente_nome, cedente_info in cedentes_data.items():
                titulo_mais_atrasado = cedente_info.get('titulo_mais_atrasado', {})
                
                top_risk_cedentes.append({
                    "cedente_nome": cedente_nome,
                    "grupo_pdd": cedente_info.get('grupo_pdd_aplicado', 'AA'),
                    "dias_atraso_max": titulo_mais_atrasado.get('dias_atraso', 0),
                    "provisao_pct": cedente_info.get('provisao_pct', 0),
                    "provisao_valor": cedente_info.get('provisao_valor', 0),
                    "valor_total": cedente_info.get('valor_total', 0),
                    "percentual_carteira": (cedente_info.get('valor_total', 0) / totais.get('carteira_valor', 1)) * 100,
                    "risk_score": self._calculate_cedente_risk_score(cedente_info),
                    "color": self._get_risk_color(cedente_info.get('grupo_pdd_aplicado', 'AA'))
                })
            
            # Ordenar por risco descendente e limitar a top 10
            top_risk_cedentes.sort(key=lambda x: x['risk_score'], reverse=True)
            top_risk_cedentes = top_risk_cedentes[:10]
            
            # Calcular métricas de resumo
            provisao_total_pct = totais.get('provisao_percentual', 0)
            
            risk_summary = {
                "pool_id": pool_id,
                "timestamp": datetime.now().isoformat(),
                "overall_risk": {
                    "level": self._get_overall_risk_level(provisao_total_pct),
                    "score": provisao_total_pct,
                    "color": self._get_overall_risk_color(provisao_total_pct),
                    "status": "ALTO RISCO" if provisao_total_pct > 5.0 else "ATENÇÃO" if provisao_total_pct > 2.0 else "OK"
                },
                "heat_map": {
                    "risk_groups": risk_groups_heatmap,
                    "top_risk_cedentes": top_risk_cedentes
                },
                "summary_metrics": {
                    "total_carteira": totais.get('carteira_valor', 0),
                    "total_provisao": totais.get('provisao_valor', 0),
                    "provisao_percentual": provisao_total_pct,
                    "total_cedentes": len(cedentes_data),
                    "cedentes_com_risco": sum(1 for c in cedentes_data.values() if c.get('provisao_valor', 0) > 0),
                    "grupos_ativos": sum(1 for g in grupos_data.values() if g.get('quantidade', 0) > 0),
                    "pior_grupo_ativo": max([g for g in grupos_data.keys() if grupos_data[g].get('quantidade', 0) > 0], default='AA')
                },
                "ui_config": {
                    "heat_map_thresholds": [
                        {"min": 0, "max": 1, "color": "#22C55E", "label": "Baixo Risco"},
                        {"min": 1, "max": 3, "color": "#EAB308", "label": "Médio Risco"},
                        {"min": 3, "max": 7, "color": "#F97316", "label": "Alto Risco"},
                        {"min": 7, "max": 100, "color": "#EF4444", "label": "Crítico"}
                    ]
                }
            }
            
            result = {
                "success": True,
                "data": risk_summary
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"❌ Erro ao obter resumo de risco: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "pool_id": pool_id
            }
    
    # Métodos auxiliares para UI metadata
    
    def _get_risk_color(self, group_id: str) -> str:
        """Retorna cor baseada no grupo de risco."""
        color_map = {
            'AA': '#22C55E',  # Verde
            'A': '#84CC16',   # Verde claro
            'B': '#EAB308',   # Amarelo
            'C': '#F59E0B',   # Laranja claro
            'D': '#F97316',   # Laranja
            'E': '#EF4444',   # Vermelho
            'F': '#DC2626',   # Vermelho escuro
            'G': '#991B1B',   # Vermelho muito escuro
            'H': '#7F1D1D'    # Vermelho crítico
        }
        return color_map.get(group_id, '#6B7280')
    
    def _get_risk_icon(self, group_id: str) -> str:
        """Retorna ícone baseado no grupo de risco."""
        icon_map = {
            'AA': '✅', 'A': '🟢', 'B': '🟡', 'C': '🟠',
            'D': '🔶', 'E': '🔴', 'F': '⚠️', 'G': '❌', 'H': '🚨'
        }
        return icon_map.get(group_id, '❓')
    
    def _get_group_severity(self, group_id: str) -> str:
        """Retorna nível de severidade do grupo."""
        severity_map = {
            'AA': 'muito_baixo', 'A': 'baixo', 'B': 'baixo',
            'C': 'medio', 'D': 'medio', 'E': 'alto',
            'F': 'alto', 'G': 'critico', 'H': 'critico'
        }
        return severity_map.get(group_id, 'medio')
    
    def _get_cedente_status(self, cedente_info: Dict[str, Any]) -> str:
        """Determina status do cedente baseado em suas métricas."""
        provisao_pct = cedente_info.get('provisao_pct', 0)
        
        if provisao_pct >= 50:
            return 'critico'
        elif provisao_pct >= 10:
            return 'alto_risco'
        elif provisao_pct >= 3:
            return 'atencao'
        elif provisao_pct > 0:
            return 'monitoramento'
        else:
            return 'ok'
    
    def _calculate_cedente_severity(self, cedente_info: Dict[str, Any]) -> int:
        """Calcula nível de severidade numérico do cedente (1-10)."""
        provisao_pct = cedente_info.get('provisao_pct', 0)
        
        if provisao_pct >= 70:
            return 10
        elif provisao_pct >= 50:
            return 9
        elif provisao_pct >= 30:
            return 8
        elif provisao_pct >= 10:
            return 7
        elif provisao_pct >= 5:
            return 6
        elif provisao_pct >= 3:
            return 5
        elif provisao_pct >= 1:
            return 4
        elif provisao_pct > 0:
            return 3
        else:
            return 1
    
    def _get_atraso_severity(self, dias_atraso: int) -> str:
        """Determina severidade baseada em dias de atraso."""
        if dias_atraso >= 180:
            return 'critico'
        elif dias_atraso >= 90:
            return 'alto'
        elif dias_atraso >= 30:
            return 'medio'
        elif dias_atraso > 0:
            return 'baixo'
        else:
            return 'ok'
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendência dos valores."""
        if len(values) < 2:
            return 'estavel'
        
        recent_avg = sum(values[:len(values)//2]) / (len(values)//2)
        older_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if recent_avg > older_avg * 1.1:
            return 'crescente'
        elif recent_avg < older_avg * 0.9:
            return 'decrescente'
        else:
            return 'estavel'
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calcula volatilidade dos valores."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(variance ** 0.5, 2)
    
    def _count_consecutive_high_days(self, values: List[float], threshold: float) -> int:
        """Conta dias consecutivos acima do threshold."""
        count = 0
        for value in values:
            if value > threshold:
                count += 1
            else:
                break
        return count
    
    def _generate_trend_alerts(self, indicators: Dict[str, Any], values: List[float]) -> List[Dict[str, Any]]:
        """Gera alertas baseados em tendências."""
        alerts = []
        
        # Alerta de tendência crescente
        if indicators['tendencia'] == 'crescente':
            alerts.append({
                "type": "warning",
                "message": "Tendência crescente de provisão PDD detectada",
                "severity": "medium"
            })
        
        # Alerta de alta volatilidade
        if indicators['volatilidade'] > 1.0:
            alerts.append({
                "type": "info",
                "message": f"Alta volatilidade detectada: {indicators['volatilidade']:.2f}",
                "severity": "low"
            })
        
        # Alerta de dias consecutivos altos
        if indicators['dias_consecutivos_alta'] >= 3:
            alerts.append({
                "type": "error",
                "message": f"{indicators['dias_consecutivos_alta']} dias consecutivos com provisão alta",
                "severity": "high"
            })
        
        return alerts
    
    def _get_overall_risk_level(self, provisao_pct: float) -> str:
        """Determina nível de risco geral."""
        if provisao_pct >= 10:
            return 'critico'
        elif provisao_pct >= 5:
            return 'alto'
        elif provisao_pct >= 2:
            return 'medio'
        elif provisao_pct > 0:
            return 'baixo'
        else:
            return 'muito_baixo'
    
    def _get_overall_risk_color(self, provisao_pct: float) -> str:
        """Retorna cor baseada no risco geral."""
        if provisao_pct >= 10:
            return '#7F1D1D'  # Vermelho crítico
        elif provisao_pct >= 5:
            return '#EF4444'  # Vermelho
        elif provisao_pct >= 2:
            return '#F97316'  # Laranja
        elif provisao_pct > 0:
            return '#EAB308'  # Amarelo
        else:
            return '#22C55E'  # Verde
    
    def _calculate_group_severity_score(self, group_id: str, group_stats: Dict[str, Any]) -> float:
        """Calcula score de severidade para um grupo."""
        # Score baseado na provisão e na quantidade de títulos
        group_order = ['AA', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        base_score = group_order.index(group_id) if group_id in group_order else 0
        
        quantidade = group_stats.get('quantidade', 0)
        provisao = group_stats.get('provisao_valor', 0)
        
        return base_score + (quantidade * 0.1) + (provisao * 0.001)
    
    def _calculate_cedente_risk_score(self, cedente_info: Dict[str, Any]) -> float:
        """Calcula score de risco para um cedente."""
        provisao_pct = cedente_info.get('provisao_pct', 0)
        valor_total = cedente_info.get('valor_total', 0)
        titulo_mais_atrasado = cedente_info.get('titulo_mais_atrasado', {})
        dias_atraso = titulo_mais_atrasado.get('dias_atraso', 0)
        
        # Score combinado de provisão, exposição e atraso
        return (provisao_pct * 0.4) + (valor_total * 0.0001) + (dias_atraso * 0.01)


# Instância global da API
pdd_api = PDDHierarchicalAPI()

# Funções de endpoint para integração com Flask/FastAPI
def get_pdd_hierarchy(pool_id: str) -> Dict[str, Any]:
    """Endpoint wrapper para hierarquia PDD."""
    return pdd_api.get_hierarchy(pool_id)

def get_pdd_group_cedentes(pool_id: str, group_id: str) -> Dict[str, Any]:
    """Endpoint wrapper para cedentes de grupo."""
    return pdd_api.get_group_cedentes(pool_id, group_id)

def get_pdd_cedente_worst_assets(cedente_id: str, pool_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Endpoint wrapper para piores ativos de cedente."""
    return pdd_api.get_cedente_worst_assets(cedente_id, pool_id, limit)

def get_pdd_trends(pool_id: str, days: int = 30) -> Dict[str, Any]:
    """Endpoint wrapper para tendências PDD."""
    return pdd_api.get_trends(pool_id, days)

def get_pdd_risk_summary(pool_id: str) -> Dict[str, Any]:
    """Endpoint wrapper para resumo de risco."""
    return pdd_api.get_risk_summary(pool_id)


# Teste e exemplo de uso
if __name__ == "__main__":
    print("🚀 Testando PDD Hierarchical API...")
    
    # Testar com E-ctare Pool #1
    test_pool = "E-ctare Pool #1"
    
    print(f"\n1. Testando hierarquia para {test_pool}...")
    hierarchy = get_pdd_hierarchy(test_pool)
    if hierarchy["success"]:
        print(f"✅ Hierarquia carregada: {hierarchy['data']['total_groups']} grupos, {hierarchy['data']['total_cedentes']} cedentes")
    else:
        print(f"❌ Erro: {hierarchy['error']}")
    
    print(f"\n2. Testando cedentes do grupo H...")
    group_cedentes = get_pdd_group_cedentes(test_pool, "H")
    if group_cedentes["success"]:
        print(f"✅ Cedentes grupo H: {group_cedentes['data']['total_cedentes']} cedentes")
    else:
        print(f"❌ Erro: {group_cedentes['error']}")
    
    print(f"\n3. Testando tendências...")
    trends = get_pdd_trends(test_pool, 10)
    if trends["success"]:
        print(f"✅ Tendências carregadas: {trends['data']['period_days']} dias de dados")
    else:
        print(f"❌ Erro: {trends['error']}")
    
    print(f"\n4. Testando resumo de risco...")
    risk_summary = get_pdd_risk_summary(test_pool)
    if risk_summary["success"]:
        print(f"✅ Resumo de risco: {risk_summary['data']['overall_risk']['level']} - {risk_summary['data']['overall_risk']['score']:.2f}%")
    else:
        print(f"❌ Erro: {risk_summary['error']}")
    
    print("\n🎉 Teste concluído!")