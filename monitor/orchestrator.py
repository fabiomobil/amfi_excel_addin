"""
Orquestrador de Monitoramento
=============================

Responsável por:
- Orquestrar execução de monitores individuais via data_loader
- Enriquecimento progressivo de dados (XLSX global)
- Gerenciar logging e alertas
- Consolidar resultados com tratamento robusto de erros

Arquitetura CLASS-ONLY (2025-07-17):
- TODOS os monitores usam BaseMonitor classes (SubordinacaoMonitor, ConcentracaoMonitor, etc.)
- data_loader como CENTRALIZADOR (descoberta + config + carregamento)
- XLSX global (79k+ registros, 36+ pools) enriquecido progressivamente
- Execução condicional baseada em JSONs de configuração
- Tratamento robusto: pool falha ≠ parar execução
- Código 70% mais limpo: 1.000+ linhas de código duplicado eliminadas

Fluxo de Execução:
1. data_loader.load_pool_data() - centraliza tudo
2. Para cada pool: execução condicional de monitores
   - Subordinação: independente
   - Inadimplência: enriquece XLSX global (dias_atraso, grupo_de_risco)
   - PDD: usa dados já enriquecidos (arquitetura inteligente)
3. Campos adicionados globalmente: dias_atraso, grupo_de_risco
"""

import sys
import os
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

# CLASS-BASED MONITORS ONLY - New architecture using BaseMonitor
# Imports compatíveis com Spyder/Windows
try:
    # Try relative imports first (WSL/Linux)
    from .core.imports import import_function
    from .core.subordinacao_monitor import SubordinacaoMonitor
    from .core.concentracao_monitor_simple import ConcentracaoMonitor
    from .core.inadimplencia_monitor import InadimplenciaMonitor
    from .core.pdd_monitor import PDDMonitor
except ImportError:
    # Fallback for Spyder/Windows absolute imports
    import sys
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(script_dir))
    
    from monitor.core.imports import import_function
    from monitor.core.subordinacao_monitor import SubordinacaoMonitor
    from monitor.core.concentracao_monitor_simple import ConcentracaoMonitor
    from monitor.core.inadimplencia_monitor import InadimplenciaMonitor
    from monitor.core.pdd_monitor import PDDMonitor

# Import utilities with fallback
try:
    load_pool_data = import_function('data_loader', 'load_pool_data', 'util')
    log_alerta = import_function('alerts', 'log_alerta', 'util')
    load_dashboard = import_function('file_loaders', 'load_dashboard', 'util')
    load_json_file = import_function('file_loaders', 'load_json_file', 'util')
    get_possible_paths = import_function('path_resolver', 'get_possible_paths', 'util')
except:
    # Fallback for direct imports
    from monitor.utils.data_loader import load_pool_data
    from monitor.utils.alerts import log_alerta
    from monitor.utils.file_loaders import load_dashboard, load_json_file
    from monitor.utils.path_resolver import get_possible_paths


def _has_subordination_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitor de subordinação está ativo no JSON de configuração.
    """
    try:
        monitor = SubordinacaoMonitor('temp', config, pd.DataFrame())
        return monitor.is_active()
    except:
        return False


def _has_delinquency_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitores de inadimplência estão ativos no JSON de configuração.
    """
    try:
        monitor = InadimplenciaMonitor('temp', config, pd.DataFrame())
        return monitor.is_active()
    except:
        return False


def _has_concentration_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitores de concentração estão ativos no JSON de configuração.
    """
    try:
        monitor = ConcentracaoMonitor('temp', config, pd.DataFrame())
        return monitor.is_active()
    except:
        return False


def _has_pdd_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitores de PDD estão ativos no JSON de configuração.
    """
    try:
        monitor = PDDMonitor('temp', config, pd.DataFrame())
        return monitor.is_active()
    except:
        return False


def run_monitoring(pool_name: str = None) -> Dict[str, Any]:
    """
    Interface principal unificada do sistema de monitoramento AmFi.
    
    FUNCIONALIDADES PRINCIPAIS:
    ==========================
    
    🎯 **Monitores Executados**: TODOS os monitores configurados
    - ✅ **Subordinação**: Índice de subordinação (SR) com limites mínimo/crítico
    - ✅ **Inadimplência**: Análise por janelas customizáveis (30d, 90d, etc.)
    - ✅ **PDD**: Provisão para devedores duvidosos
    - ✅ **Concentração**: Sacados/cedentes individuais e top-N (**NOVO - Building Block 7**)
    - 🔄 **Vencimento médio**: Prazo médio ponderado da carteira
    - 🔄 **Elegibilidade**: Critérios de ativos válidos
    
    🔄 **Enriquecimento Progressivo**: 
    - DataFrame XLSX global enriquecido com campos calculados
    - Campos adicionados: 'dias_atraso', 'grupo_de_risco'
    - Performance otimizada: cálculos feitos uma vez, reutilizados
    
    🏗️ **Arquitetura Moderna**:
    - data_loader centraliza descoberta/config/carregamento
    - Execução condicional baseada em JSONs de configuração
    - Compatibilidade multi-ambiente (Windows/WSL/Spyder)
    - Tratamento robusto: falha de pool ≠ parar execução
    
    Args:
        pool_name (str, optional): 
            - None: Processa TODOS os pools (modo normal ou debug via test_pools.json)
            - "Pool Name": Processa apenas o pool específico
        
    Returns:
        Dict[str, Any]: Estrutura de resultados consolidados
        {
            "sucesso": bool,
            "timestamp": str,
            "pools_processados": List[str],
            "estatisticas": {
                "total": int,
                "sucesso": int, 
                "erro": int,
                "taxa_sucesso": float
            },
            "resultados": {
                "Pool Name": {
                    "sucesso": bool,
                    "monitores_executados": ["subordinacao", "inadimplencia", "pdd"],
                    "resultados": {
                        "subordinacao": {
                            "subordination_ratio_percent": float,
                            "status_limite_minimo": "conforme|violado",
                            "aporte_necessario": {...}
                        },
                        "inadimplencia": {
                            "resultados": {
                                "inadimplencia_30d": {
                                    "inadimplencia_percent": float,
                                    "limite_configurado": float,
                                    "status": "conforme|violado"
                                },
                                "inadimplencia_90d": {...}
                            }
                        },
                        "pdd": {
                            "pdd_analysis": {
                                "grupos": {"AA": {...}, "B": {...}},
                                "totais": {
                                    "provisao_valor": float,
                                    "provisao_percentual": float
                                }
                            }
                        }
                    }
                }
            },
            "xlsx_enriched": pd.DataFrame,  # DataFrame globalmente enriquecido
            "metadados": {...}
        }
        
    Examples:
        >>> # 1. PROCESSAR TODOS OS POOLS (modo debug - usa test_pools.json)
        >>> resultado = run_monitoring()
        >>> print(f"Pools processados: {resultado['pools_processados']}")
        >>> print(f"Taxa de sucesso: {resultado['estatisticas']['taxa_sucesso']}%")
        >>> 
        >>> # 2. PROCESSAR POOL ESPECÍFICO
        >>> resultado = run_monitoring("LeCapital Pool #1")
        >>> pool_result = resultado['resultados']['LeCapital Pool #1']
        >>> 
        >>> # Verificar subordinação
        >>> sub_result = pool_result['resultados']['subordinacao']
        >>> print(f"Subordinação: {sub_result['subordination_ratio_percent']}%")
        >>> 
        >>> # Verificar inadimplência
        >>> inad_result = pool_result['resultados']['inadimplencia']['resultados']
        >>> for janela, dados in inad_result.items():
        >>>     print(f"{janela}: {dados['inadimplencia_percent']}% (limite: {dados['limite_configurado']*100}%)")
        >>> 
        >>> # Verificar PDD (se configurado)
        >>> if 'pdd' in pool_result['resultados']:
        >>>     pdd_result = pool_result['resultados']['pdd']['pdd_analysis']
        >>>     print(f"PDD Total: R$ {pdd_result['totais']['provisao_valor']:,.2f}")
        >>>     print(f"PDD %: {pdd_result['totais']['provisao_percentual']}%")
        >>> 
        >>> # Verificar concentração (se configurado)
        >>> if 'concentracao' in pool_result['resultados']:
        >>>     conc_result = pool_result['resultados']['concentracao']
        >>>     print(f"Concentração: {conc_result['status_geral']}")
        >>>     print(f"Limites analisados: {conc_result['resumo']['total_limites_analisados']}")
        >>> 
        >>> # 3. ACESSAR XLSX ENRIQUECIDO
        >>> xlsx_enriched = resultado['xlsx_enriched']
        >>> print(f"Novos campos: {['dias_atraso', 'grupo_de_risco']}")
        >>> print(f"Total registros: {len(xlsx_enriched)}")
        
    Modo DEBUG:
        Se arquivo /config/monitoring/test_pools.json existir:
        - Processa apenas pools listados em "debug_pools"
        - Exemplo: ["AFA Pool #1", "LeCapital Pool #1"]
        
    Compatibilidade:
        ✅ Windows (C:\\amfi\\...)
        ✅ WSL (/mnt/c/amfi/...)
        ✅ Spyder (descoberta automática de caminhos)
        ✅ Linha de comando
        
    Raises:
        Exception: Apenas em falhas críticas do data_loader
        
    Note:
        Esta é a ÚNICA interface oficial do sistema. 
        Funções legacy foram removidas em 2025-07-14.
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
                "mensagem": "Executando monitor de subordinação (BaseMonitor)"
            })
            
            try:
                monitor_sub = SubordinacaoMonitor(pool_name, config, dados["csv_data"])
                resultado_sub = monitor_sub.run()
                resultados_monitores["subordinacao"] = {
                    "status": "sucesso" if resultado_sub.status == "success" else "erro",
                    "timestamp": resultado_sub.timestamp,
                    "resultados": resultado_sub.data,
                    "alerts": resultado_sub.alerts
                }
            except Exception as e:
                log_alerta({
                    "tipo": "error",
                    "pool": pool_name,
                    "mensagem": f"Erro no monitor de subordinação: {str(e)}"
                })
                resultados_monitores["subordinacao"] = {
                    "status": "erro",
                    "erro": str(e)
                }
        
        # 2. Monitor de Inadimplência (com enriquecimento)
        if _has_delinquency_monitoring(config):
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": "Executando monitor de inadimplência (com enriquecimento)"
            })
            
            # BaseMonitor: Execução com enriquecimento automático
            try:
                monitor_inad = InadimplenciaMonitor(pool_name, config, dados["csv_data"], dados["xlsx_data"])
                resultado_inad = monitor_inad.run()
                resultados_monitores["inadimplencia"] = {
                    "sucesso": resultado_inad.status == "success",
                    "timestamp": resultado_inad.timestamp,
                    "resultados": resultado_inad.data,
                    "alerts": resultado_inad.alerts
                }
            except Exception as e:
                log_alerta({
                    "tipo": "error",
                    "pool": pool_name,
                    "mensagem": f"Erro no monitor de inadimplência: {str(e)}"
                })
                resultados_monitores["inadimplencia"] = {
                    "sucesso": False,
                    "erro": str(e)
                }
            
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
        
        # 3. Monitor de PDD (usa dados enriquecidos pelo monitor de inadimplência)
        if _has_pdd_monitoring(config):
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": "Executando monitor de PDD (usando dados enriquecidos)"
            })
            
            # BaseMonitor: PDD usando dados já enriquecidos automaticamente
            try:
                monitor_pdd = PDDMonitor(pool_name, config, dados["csv_data"], dados["xlsx_data"])
                resultado_pdd = monitor_pdd.run()
                resultados_monitores["pdd"] = {
                    "sucesso": resultado_pdd.status == "success",
                    "timestamp": resultado_pdd.timestamp,
                    "pdd_analysis": resultado_pdd.data,
                    "alerts": resultado_pdd.alerts
                }
            except Exception as e:
                log_alerta({
                    "tipo": "error",
                    "pool": pool_name,
                    "mensagem": f"Erro no monitor de PDD: {str(e)}"
                })
                resultados_monitores["pdd"] = {
                    "sucesso": False,
                    "erro": str(e)
                }
            
            # Log da execução BaseMonitor
            if resultados_monitores["pdd"].get("sucesso"):
                log_alerta({
                    "tipo": "info",
                    "pool": pool_name,
                    "mensagem": "✅ PDD calculado via BaseMonitor usando dados enriquecidos"
                })
            else:
                log_alerta({
                    "tipo": "warning",
                    "pool": pool_name,
                    "mensagem": f"⚠️ Falha no monitor PDD: {resultados_monitores['pdd'].get('erro', 'Desconhecido')}"
                })
        
        # 4. Monitor de Concentração
        if _has_concentration_monitoring(config):
            log_alerta({
                "tipo": "info",
                "pool": pool_name,
                "mensagem": "Executando monitor de concentração"
            })
            
            # BaseMonitor: Concentração refatorada com arquitetura limpa
            try:
                monitor_conc = ConcentracaoMonitor(pool_name, config, dados["csv_data"], dados["xlsx_data"])
                resultado_conc = monitor_conc.run()
                resultados_monitores["concentracao"] = {
                    "sucesso": resultado_conc.status == "success",
                    "timestamp": resultado_conc.timestamp,
                    "status_geral": resultado_conc.data.get("status_geral"),
                    "resumo": resultado_conc.data.get("resumo"),
                    "resultados": resultado_conc.data,
                    "alerts": resultado_conc.alerts
                }
            except Exception as e:
                log_alerta({
                    "tipo": "error",
                    "pool": pool_name,
                    "mensagem": f"Erro no monitor de concentração: {str(e)}"
                })
                resultados_monitores["concentracao"] = {
                    "sucesso": False,
                    "erro": str(e)
                }
            
            # Log da execução BaseMonitor 
            if resultados_monitores["concentracao"].get("sucesso"):
                status = resultados_monitores["concentracao"].get("status_geral", "desconhecido")
                if status == "sem_limites":
                    log_alerta({
                        "tipo": "info",
                        "pool": pool_name,
                        "mensagem": "ℹ️ Concentração (BaseMonitor): sem limites configurados"
                    })
                elif status == "enquadrado":
                    log_alerta({
                        "tipo": "info",
                        "pool": pool_name,
                        "mensagem": "✅ Concentração (BaseMonitor): todos os limites enquadrados"
                    })
                elif status == "violado":
                    num_violados = resultados_monitores["concentracao"].get("resumo", {}).get("limites_violados", 0)
                    log_alerta({
                        "tipo": "warning",
                        "pool": pool_name,
                        "mensagem": f"⚠️ Concentração (BaseMonitor): {num_violados} limite(s) violado(s)"
                    })
                else:
                    log_alerta({
                        "tipo": "warning",
                        "pool": pool_name,
                        "mensagem": f"⚠️ Concentração (BaseMonitor): status {status}"
                    })
            else:
                log_alerta({
                    "tipo": "warning",
                    "pool": pool_name,
                    "mensagem": f"⚠️ Falha no monitor concentração: {resultados_monitores['concentracao'].get('erro', 'Desconhecido')}"
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


# Funções legacy removidas - usar run_monitoring() como interface única


if __name__ == "__main__":
    # Exemplo de uso direto
    print("🎯 ORQUESTRADOR DE MONITORAMENTO - Todos os Monitores")
    print("=" * 60)
    
    # Executar para pools de teste (NOVO: inclui inadimplência)
    resultado = run_monitoring()
    
    if resultado.get("sucesso"):
        stats = resultado["estatisticas"]
        print(f"✅ Orquestração concluída:")
        print(f"   📊 Total de pools: {stats['total']}")
        print(f"   ✅ Sucesso: {stats['sucesso']}")
        print(f"   ❌ Erro: {stats['erro']}")
        print(f"   📈 Taxa de sucesso: {stats['taxa_sucesso']}%")
        
        # Mostrar resultados detalhados por pool
        print(f"\n📋 RESULTADOS POR POOL:")
        for pool_name, pool_result in resultado["resultados"].items():
            print(f"\n🏦 {pool_name}:")
            print(f"   ✅ Sucesso: {pool_result.get('sucesso', 'N/A')}")
            print(f"   📊 Monitores: {pool_result.get('monitores_executados', [])}")
            
            # Resultados de subordinação
            if 'subordinacao' in pool_result.get('resultados', {}):
                sub_result = pool_result['resultados']['subordinacao']
                if 'subordination_ratio_percent' in sub_result:
                    sr = sub_result['subordination_ratio_percent']
                    status = sub_result.get('status_limite_minimo', 'N/A')
                    print(f"   📈 Subordinação: {sr}% ({status})")
            
            # Resultados de inadimplência  
            if 'inadimplencia' in pool_result.get('resultados', {}):
                inad_result = pool_result['resultados']['inadimplencia']
                print(f"   🔍 Inadimplência:")
                if 'resultados' in inad_result:
                    for monitor_id, monitor_data in inad_result['resultados'].items():
                        if 'inadimplencia_percent' in monitor_data:
                            perc = monitor_data['inadimplencia_percent']
                            limite = monitor_data.get('limite_configurado', 0) * 100
                            status = monitor_data.get('status', 'N/A')
                            janela = monitor_id.replace('inadimplencia_', '').replace('d', ' dias')
                            print(f"     - {janela}: {perc}% (limite: {limite}% | {status})")
            
            # Resultados de PDD
            if 'pdd' in pool_result.get('resultados', {}):
                pdd_result = pool_result['resultados']['pdd']
                print(f"   💰 PDD (Provisão para Devedores Duvidosos):")
                if 'pdd_analysis' in pdd_result and 'totais' in pdd_result['pdd_analysis']:
                    totais = pdd_result['pdd_analysis']['totais']
                    valor = totais.get('provisao_valor', 0)
                    perc = totais.get('provisao_percentual', 0)
                    print(f"     - Total: R$ {valor:,.2f} ({perc}% da carteira)")
                    
                    # Mostrar grupos com exposição
                    if 'grupos' in pdd_result['pdd_analysis']:
                        grupos_com_exposicao = {
                            g: dados for g, dados in pdd_result['pdd_analysis']['grupos'].items()
                            if dados.get('quantidade', 0) > 0
                        }
                        if grupos_com_exposicao:
                            print(f"     - Grupos com exposição: {', '.join(grupos_com_exposicao.keys())}")
        
    else:
        print(f"❌ Falha na orquestração: {resultado.get('erro', 'Erro desconhecido')}")