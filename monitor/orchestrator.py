"""
Orquestrador de Monitoramento
=============================

Responsável por:
- Orquestrar execução de monitores individuais via data_loader
- Enriquecimento progressivo de dados (XLSX global)
- Gerenciar logging e alertas
- Consolidar resultados com tratamento robusto de erros

Arquitetura Nova (2025-07-13):
- data_loader como CENTRALIZADOR (descoberta + config + carregamento)
- XLSX global (79k+ registros, 36+ pools) enriquecido progressivamente
- Execução condicional baseada em JSONs de configuração
- Tratamento robusto: pool falha ≠ parar execução

Fluxo de Execução:
1. data_loader.load_pool_data() - centraliza tudo
2. Para cada pool: execução condicional de monitores
3. Enriquecimento por pool: xlsx['pool'] == pool_name
4. Campos adicionados: dias_atraso, grupo_de_risco
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Sistema de imports compatível com Spyder e outros ambientes
try:
    from .base.monitor_subordinacao import run_subordination_monitoring, _find_subordination_monitor
    from .base.monitor_inadimplencia import run_delinquency_monitoring, _find_delinquency_monitors
    from .utils.data_loader import load_pool_data
    from .utils.alerts import log_alerta
    from .utils.file_loaders import load_dashboard, load_json_file
except (ImportError, ValueError):
    # Fallback para imports diretos (Spyder)
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    if os.path.join(os.path.dirname(__file__), 'base') not in sys.path:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'base'))
    if os.path.join(os.path.dirname(__file__), 'utils') not in sys.path:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        
    from monitor_subordinacao import run_subordination_monitoring, _find_subordination_monitor
    from monitor_inadimplencia import run_delinquency_monitoring, _find_delinquency_monitors
    from data_loader import load_pool_data
    from alerts import log_alerta
    from file_loaders import load_dashboard, load_json_file


def _has_subordination_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitor de subordinação está ativo no JSON de configuração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se monitor está configurado e ativo
    """
    try:
        monitor = _find_subordination_monitor(config)
        return monitor is not None and monitor.get('ativo', False)
    except (ValueError, KeyError):
        return False


def _has_delinquency_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitores de inadimplência estão ativos no JSON de configuração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se pelo menos um monitor de inadimplência está ativo
    """
    try:
        monitors = _find_delinquency_monitors(config)
        return len(monitors) > 0
    except (ValueError, KeyError):
        return False


def run_monitoring(pool_name: str = None) -> Dict[str, Any]:
    """
    Interface principal unificada do orquestrador.
    
    Características:
    - Usa data_loader como centralizador (descoberta + config + carregamento)
    - XLSX global (79k+ registros, 36+ pools) enriquecido progressivamente
    - Execução condicional baseada em JSONs de configuração
    - Tratamento robusto de erros (pool falha ≠ parar tudo)
    
    Args:
        pool_name: Nome específico do pool ou None para todos os pools
        
    Returns:
        Dict com resultados consolidados de todos os pools processados
        
    Example:
        >>> # Processar todos os pools (modo normal ou debug)
        >>> resultado = run_monitoring()
        >>> 
        >>> # Processar pool específico
        >>> resultado = run_monitoring("LeCapital Pool #1")
    """
    log_alerta({
        "tipo": "info", 
        "mensagem": f"🎯 Iniciando orquestração integrada",
        "pool_especifico": pool_name
    })
    
    try:
        # 1. CENTRALIZADOR: data_loader faz toda descoberta/config/carregamento
        log_alerta({"tipo": "info", "mensagem": "Chamando data_loader como centralizador"})
        dados = load_pool_data()
        
        if not dados["sucesso"]:
            log_alerta({
                "tipo": "erro", 
                "mensagem": f"Falha crítica no data_loader: {dados.get('erro', 'Desconhecido')}"
            })
            return dados  # Propagar erro crítico do data_loader
        
        log_alerta({
            "tipo": "info", 
            "mensagem": f"✅ Data loader concluído: {len(dados['pools_processados'])} pools descobertos"
        })
        
        # 2. FILTRAR pools se específico
        if pool_name:
            if pool_name not in dados["pools_processados"]:
                erro_msg = f"Pool '{pool_name}' não encontrado nos pools descobertos: {dados['pools_processados']}"
                log_alerta({"tipo": "erro", "mensagem": erro_msg})
                return {
                    "sucesso": False,
                    "erro": erro_msg,
                    "pools_disponiveis": dados["pools_processados"]
                }
            pools_para_processar = [pool_name]
        else:
            pools_para_processar = dados["pools_processados"]
        
        log_alerta({
            "tipo": "info", 
            "mensagem": f"Processando {len(pools_para_processar)} pools: {pools_para_processar}"
        })
        
        # 3. LOOP por pool com tratamento robusto de erros
        resultados_pools = {}
        pools_com_sucesso = 0
        pools_com_erro = 0
        
        for pool in pools_para_processar:
            log_alerta({
                "tipo": "info", 
                "pool": pool,
                "mensagem": f"Processando pool {pool}"
            })
            
            try:
                resultado_pool = _process_single_pool(pool, dados)
                resultados_pools[pool] = resultado_pool
                
                if resultado_pool.get("sucesso", False):
                    pools_com_sucesso += 1
                    log_alerta({
                        "tipo": "info", 
                        "pool": pool,
                        "mensagem": f"✅ Pool processado com sucesso"
                    })
                else:
                    pools_com_erro += 1
                    log_alerta({
                        "tipo": "warning", 
                        "pool": pool,
                        "mensagem": f"⚠️ Pool processado com erros: {resultado_pool.get('erro', 'Desconhecido')}"
                    })
                    
            except Exception as e:
                # Pool específico falha ≠ parar tudo
                pools_com_erro += 1
                erro_msg = f"Falha crítica no pool: {str(e)}"
                
                log_alerta({
                    "tipo": "erro", 
                    "pool": pool,
                    "mensagem": erro_msg
                })
                
                resultados_pools[pool] = {
                    "sucesso": False,
                    "erro": erro_msg,
                    "pool": pool,
                    "timestamp": datetime.now().isoformat()
                }
        
        # 4. CONSOLIDAR resultados finais
        resultado_final = {
            "sucesso": True,
            "timestamp": datetime.now().isoformat(),
            "pools_processados": pools_para_processar,
            "estatisticas": {
                "total": len(pools_para_processar),
                "sucesso": pools_com_sucesso,
                "erro": pools_com_erro,
                "taxa_sucesso": round(pools_com_sucesso / len(pools_para_processar) * 100, 1) if pools_para_processar else 0
            },
            "resultados": resultados_pools,
            "xlsx_enriched": dados["xlsx_data"],  # DataFrame globalmente enriquecido
            "metadados": dados.get("metadados", {})
        }
        
        log_alerta({
            "tipo": "info", 
            "mensagem": f"🎯 Orquestração concluída",
            "total_pools": len(pools_para_processar),
            "sucesso": pools_com_sucesso,
            "erro": pools_com_erro,
            "taxa_sucesso": resultado_final["estatisticas"]["taxa_sucesso"]
        })
        
        return resultado_final
        
    except Exception as e:
        erro_msg = f"Erro crítico na orquestração: {str(e)}"
        log_alerta({
            "tipo": "erro", 
            "mensagem": erro_msg
        })
        
        return {
            "sucesso": False,
            "erro": erro_msg,
            "timestamp": datetime.now().isoformat()
        }


def _process_single_pool(pool_name: str, dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa um pool individual com todos os monitores configurados.
    
    Args:
        pool_name: Nome do pool
        dados: Dados carregados pelo data_loader
        
    Returns:
        Dict com resultados do pool específico
    """
    try:
        # Obter configuração do pool
        config = dados["pools_configs"].get(pool_name)
        if not config:
            return {
                "sucesso": False,
                "erro": f"Configuração JSON não encontrada para pool '{pool_name}'",
                "pool": pool_name
            }
        
        # Filtrar CSV para o pool específico
        csv_data = dados["csv_data"]
        nome_col = 'nome' if 'nome' in csv_data.columns else 'Nome'
        pool_csv = csv_data[csv_data[nome_col] == pool_name]
        
        if pool_csv.empty:
            return {
                "sucesso": False,
                "erro": f"Pool '{pool_name}' não encontrado nos dados CSV",
                "pool": pool_name
            }
        
        # Filtrar XLSX para o pool específico (para cálculos)
        xlsx_data = dados["xlsx_data"]
        pool_xlsx = xlsx_data[xlsx_data['pool'] == pool_name]
        
        if pool_xlsx.empty:
            return {
                "sucesso": False,
                "erro": f"Pool '{pool_name}' não encontrado nos dados XLSX",
                "pool": pool_name
            }
        
        log_alerta({
            "tipo": "info",
            "pool": pool_name,
            "mensagem": f"Dados do pool: CSV {len(pool_csv)} registros, XLSX {len(pool_xlsx)} registros"
        })
        
        # Resultados do pool
        resultados_monitores = {}
        
        # EXECUÇÃO CONDICIONAL baseada no JSON de configuração
        
        # 1. Monitor de Subordinação
        if _has_subordination_monitoring(config):
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": "Executando monitor de subordinação"
            })
            
            resultado_sub = run_subordination_monitoring(pool_csv, config)
            resultados_monitores["subordinacao"] = resultado_sub
        
        # 2. Monitor de Inadimplência (com enriquecimento)
        if _has_delinquency_monitoring(config):
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": "Executando monitor de inadimplência (com enriquecimento)"
            })
            
            # ENRIQUECIMENTO: modificar XLSX global in-place
            resultado_inad = run_delinquency_monitoring(pool_csv, dados["xlsx_data"], config)
            resultados_monitores["inadimplencia"] = resultado_inad
            
            # Log do enriquecimento
            if "dias_atraso" in dados["xlsx_data"].columns:
                log_alerta({
                    "tipo": "info",
                    "pool": pool_name,
                    "mensagem": "✅ XLSX enriquecido com campo 'dias_atraso'"
                })
            
            if "grupo_de_risco" in dados["xlsx_data"].columns:
                log_alerta({
                    "tipo": "info",
                    "pool": pool_name,
                    "mensagem": "✅ XLSX enriquecido com campo 'grupo_de_risco'"
                })
        
        return {
            "sucesso": True,
            "pool": pool_name,
            "monitores_executados": list(resultados_monitores.keys()),
            "resultados": resultados_monitores,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "pool": pool_name,
            "timestamp": datetime.now().isoformat()
        }


def orchestrate_subordination_monitoring(pool_name: str, data_referencia: str = None) -> Dict[str, Any]:
    """
    Orquestra monitoramento de subordinação para um pool específico.
    
    Args:
        pool_name: Nome do pool (ex: "LeCapital Pool #1")
        data_referencia: Data específica ou None para dados mais recentes
        
    Returns:
        Dict com resultado completo do monitoramento
        
    Example:
        >>> resultado = orchestrate_subordination_monitoring("LeCapital Pool #1")
        >>> if resultado.get("sucesso"):
        ...     print(f"SR: {resultado['subordination_ratio_percent']}%")
    """
    log_alerta({
        "tipo": "info",
        "pool": pool_name,
        "monitor": "subordination_ratio",
        "mensagem": f"Iniciando monitoramento de subordinação",
        "data_referencia": data_referencia
    })
    
    try:
        # 1. Carregar dados do dashboard (CSV)
        log_alerta({
            "tipo": "info", 
            "pool": pool_name,
            "mensagem": "Carregando dados do CSV"
        })
        
        csv_data = load_dashboard(data=data_referencia)
        
        # Filtrar dados do pool específico
        pool_data = csv_data[csv_data['nome'] == pool_name]
        
        if pool_data.empty:
            erro_msg = f"Pool '{pool_name}' não encontrado no CSV"
            log_alerta({
                "tipo": "erro",
                "pool": pool_name,
                "monitor": "subordination_ratio", 
                "mensagem": erro_msg
            })
            return {
                "sucesso": False,
                "pool": pool_name,
                "monitor": "subordination_ratio",
                "erro": erro_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        log_alerta({
            "tipo": "info",
            "pool": pool_name,
            "mensagem": f"Dados CSV carregados: {len(pool_data)} registro(s)"
        })
        
        # 2. Carregar configuração JSON do pool
        log_alerta({
            "tipo": "info",
            "pool": pool_name, 
            "mensagem": "Carregando configuração JSON"
        })
        
        try:
            # Tentar carregar JSON do pool
            import json
            json_path = f"/mnt/c/amfi/data/escrituras/{pool_name}.json"
            
            with open(json_path, 'r', encoding='utf-8') as f:
                pool_config = json.load(f)
                
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": f"JSON carregado: {json_path}"
            })
            
        except FileNotFoundError:
            erro_msg = f"Configuração JSON não encontrada: {json_path}"
            log_alerta({
                "tipo": "erro",
                "pool": pool_name,
                "monitor": "subordination_ratio",
                "mensagem": erro_msg
            })
            return {
                "sucesso": False,
                "pool": pool_name,
                "monitor": "subordination_ratio", 
                "erro": erro_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        # 3. Executar monitoramento (delegando para o monitor)
        log_alerta({
            "tipo": "info",
            "pool": pool_name,
            "monitor": "subordination_ratio",
            "mensagem": "Executando cálculo de subordination ratio"
        })
        
        resultado = run_subordination_monitoring(pool_data, pool_config)
        
        # 4. Processar resultado e logging detalhado
        if resultado.get("sucesso"):
            # Sucesso - log detalhado
            sr_percent = resultado.get('subordination_ratio_percent', 0)
            status_min = resultado.get('status_limite_minimo', 'desconhecido')
            status_crit = resultado.get('status_limite_critico', 'desconhecido')
            
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "monitor": "subordination_ratio",
                "valor": sr_percent,
                "status_minimo": status_min,
                "status_critico": status_crit,
                "mensagem": f"Subordination ratio calculado: {sr_percent}% (Status: {status_min})"
            })
            
            # Alertas específicos para violações
            if status_min == 'violado':
                aporte_necessario = resultado.get('aporte_necessario', {}).get('para_limite_minimo', 0)
                limite_min = resultado.get('limite_minimo', 0) * 100
                
                log_alerta({
                    "tipo": "alerta",
                    "pool": pool_name,
                    "monitor": "subordination_ratio",
                    "severidade": "critica" if status_crit == 'violado' else "alta",
                    "valor_atual": sr_percent,
                    "limite_minimo": limite_min,
                    "aporte_necessario": aporte_necessario,
                    "mensagem": f"🚨 SUBORDINAÇÃO VIOLADA: {sr_percent}% < {limite_min}% (Aporte: R$ {aporte_necessario:,.2f})"
                })
                
                # Alerta crítico se ambos os limites estão violados
                if status_crit == 'violado':
                    log_alerta({
                        "tipo": "alerta",
                        "pool": pool_name,
                        "monitor": "subordination_ratio",
                        "severidade": "critica",
                        "mensagem": f"🔥 LIMITE CRÍTICO VIOLADO: Ação imediata necessária"
                    })
            
            # 5. Salvar resultado (se necessário)
            # TODO: Implementar save_monitoring_result() quando definir formato de persistência
            
            # 6. Consolidar resultado final
            resultado_final = {
                **resultado,
                "pool": pool_name,
                "timestamp": datetime.now().isoformat(),
                "data_referencia": data_referencia or "atual"
            }
            
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "monitor": "subordination_ratio",
                "mensagem": "Monitoramento de subordinação concluído com sucesso"
            })
            
            return resultado_final
            
        else:
            # Erro no monitor - log do erro
            erro_monitor = resultado.get('erro', 'Erro desconhecido no monitor')
            
            log_alerta({
                "tipo": "erro",
                "pool": pool_name,
                "monitor": "subordination_ratio",
                "erro": erro_monitor,
                "mensagem": f"Falha no cálculo: {erro_monitor}"
            })
            
            return {
                **resultado,
                "pool": pool_name,
                "timestamp": datetime.now().isoformat(),
                "data_referencia": data_referencia or "atual"
            }
            
    except Exception as e:
        # Erro inesperado no orquestrador
        erro_msg = f"Erro inesperado na orquestração: {str(e)}"
        
        log_alerta({
            "tipo": "erro",
            "pool": pool_name,
            "monitor": "subordination_ratio",
            "erro": erro_msg,
            "mensagem": "Falha crítica na orquestração"
        })
        
        return {
            "sucesso": False,
            "pool": pool_name,
            "monitor": "subordination_ratio",
            "erro": erro_msg,
            "timestamp": datetime.now().isoformat(),
            "data_referencia": data_referencia or "atual"
        }


def orchestrate_multiple_pools_monitoring(pools: List[str] = None, data_referencia: str = None) -> Dict[str, Any]:
    """
    Orquestra monitoramento de subordinação para múltiplos pools.
    
    Args:
        pools: Lista de pools ou None para usar test_pools.json
        data_referencia: Data específica ou None para dados mais recentes
        
    Returns:
        Dict com resultados consolidados de todos os pools
        
    Example:
        >>> resultado = orchestrate_multiple_pools_monitoring()
        >>> print(f"Pools processados: {resultado['total_pools']}")
    """
    log_alerta({
        "tipo": "info",
        "mensagem": "Iniciando orquestração de múltiplos pools",
        "data_referencia": data_referencia
    })
    
    try:
        # 1. Definir pools a serem processados
        if pools is None:
            # Usar configuração de teste
            try:
                test_config = load_json_file('test_pools.json')
                pools_para_processar = test_config.get('debug_pools', [])
                log_alerta({
                    "tipo": "info",
                    "mensagem": f"Usando test_pools.json: {pools_para_processar}"
                })
            except Exception as e:
                log_alerta({
                    "tipo": "erro",
                    "mensagem": f"Erro ao carregar test_pools.json: {str(e)}"
                })
                return {
                    "sucesso": False,
                    "erro": "Falha ao carregar configuração de pools",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            pools_para_processar = pools
            
        log_alerta({
            "tipo": "info",
            "mensagem": f"Processando {len(pools_para_processar)} pools: {pools_para_processar}"
        })
        
        # 2. Executar monitoramento para cada pool
        resultados = {}
        pools_com_sucesso = 0
        pools_com_erro = 0
        pools_violados = 0
        
        for pool_name in pools_para_processar:
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": f"Processando pool {pool_name}"
            })
            
            resultado_pool = orchestrate_subordination_monitoring(pool_name, data_referencia)
            resultados[pool_name] = resultado_pool
            
            # Estatísticas
            if resultado_pool.get("sucesso"):
                pools_com_sucesso += 1
                if resultado_pool.get("status_limite_minimo") == "violado":
                    pools_violados += 1
            else:
                pools_com_erro += 1
        
        # 3. Consolidar estatísticas
        resultado_consolidado = {
            "sucesso": True,
            "timestamp": datetime.now().isoformat(),
            "data_referencia": data_referencia or "atual",
            "estatisticas": {
                "total_pools": len(pools_para_processar),
                "pools_com_sucesso": pools_com_sucesso,
                "pools_com_erro": pools_com_erro,
                "pools_violados": pools_violados,
                "taxa_sucesso": round(pools_com_sucesso / len(pools_para_processar) * 100, 1)
            },
            "resultados": resultados
        }
        
        # 4. Log consolidado
        log_alerta({
            "tipo": "info",
            "mensagem": f"Orquestração concluída",
            "total_pools": len(pools_para_processar),
            "sucesso": pools_com_sucesso,
            "erro": pools_com_erro,
            "violados": pools_violados,
            "taxa_sucesso": resultado_consolidado["estatisticas"]["taxa_sucesso"]
        })
        
        # Alerta se houver violações
        if pools_violados > 0:
            pools_violados_nomes = [
                pool for pool, resultado in resultados.items() 
                if resultado.get("status_limite_minimo") == "violado"
            ]
            
            log_alerta({
                "tipo": "alerta",
                "severidade": "alta",
                "mensagem": f"🚨 {pools_violados} pools com subordinação violada: {pools_violados_nomes}"
            })
        
        return resultado_consolidado
        
    except Exception as e:
        erro_msg = f"Erro crítico na orquestração múltipla: {str(e)}"
        
        log_alerta({
            "tipo": "erro",
            "mensagem": erro_msg
        })
        
        return {
            "sucesso": False,
            "erro": erro_msg,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Exemplo de uso direto
    print("🎯 ORQUESTRADOR DE MONITORAMENTO - Subordinação")
    print("=" * 60)
    
    # Executar para pools de teste
    resultado = orchestrate_multiple_pools_monitoring()
    
    if resultado.get("sucesso"):
        stats = resultado["estatisticas"]
        print(f"✅ Orquestração concluída:")
        print(f"   📊 Total de pools: {stats['total_pools']}")
        print(f"   ✅ Sucesso: {stats['pools_com_sucesso']}")
        print(f"   ❌ Erro: {stats['pools_com_erro']}")
        print(f"   🚨 Violados: {stats['pools_violados']}")
        print(f"   📈 Taxa de sucesso: {stats['taxa_sucesso']}%")
        
        # Mostrar detalhes dos pools violados
        if stats['pools_violados'] > 0:
            print(f"\n🚨 Pools com subordinação violada:")
            for pool_name, resultado_pool in resultado["resultados"].items():
                if resultado_pool.get("status_limite_minimo") == "violado":
                    sr = resultado_pool.get("subordination_ratio_percent", 0)
                    limite = resultado_pool.get("limite_minimo", 0) * 100
                    aporte = resultado_pool.get("aporte_necessario", {}).get("para_limite_minimo", 0)
                    print(f"   - {pool_name}: {sr}% < {limite}% (Aporte: R$ {aporte:,.2f})")
    else:
        print(f"❌ Falha na orquestração: {resultado.get('erro', 'Erro desconhecido')}")