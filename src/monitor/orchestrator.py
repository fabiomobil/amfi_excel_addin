"""
Orquestrador de Monitoramento
=============================

Responsável por:
- Orquestrar execução de monitores OOP via data_loader
- Enriquecimento progressivo de dados (XLSX global)
- Gerenciar logging e alertas
- Consolidar resultados com tratamento robusto de erros

Arquitetura OOP (2025-07-17):
- Monitores OOP com herança de BaseMonitor
- XLSX global enriquecido progressivamente
- Execução condicional baseada em JSONs de configuração
- Tratamento robusto: pool falha ≠ parar execução

Fluxo de Execução:
1. data_loader.load_pool_data() - centraliza tudo
2. Para cada pool: execução condicional de monitores OOP
   - Subordinação: independente
   - Inadimplência: enriquece XLSX global (dias_atraso, grupo_de_risco)
   - PDD: usa dados já enriquecidos
   - Concentração: análise de exposição
3. Campos adicionados globalmente: dias_atraso, grupo_de_risco
"""

from typing import Dict, Any, List
from datetime import datetime
import sys
import os

# Adicionar path para compatibilidade com diferentes contextos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports OOP com fallback para execução direta
try:
    from .base.monitor_subordinacao_oop import SubordinationMonitor
    from .base.monitor_inadimplencia_oop import run_delinquency_monitoring
    from .base.monitor_pdd_oop import run_pdd_monitoring
    from .base.monitor_concentracao_oop import run_concentration_monitoring
    from .cash_flow.liquidity_analyzer import LiquidityAnalyzer
    from .utils.data_loader import load_pool_data
    from .utils.alerts import log_alerta
    from .utils.daily_results_persistence import save_monitoring_results
except ImportError:
    # Fallback para execução direta
    from base.monitor_subordinacao_oop import SubordinationMonitor
    from base.monitor_inadimplencia_oop import run_delinquency_monitoring
    from base.monitor_pdd_oop import run_pdd_monitoring
    from base.monitor_concentracao_oop import run_concentration_monitoring
    from cash_flow.liquidity_analyzer import LiquidityAnalyzer
    from utils.data_loader import load_pool_data
    from utils.alerts import log_alerta
    from utils.daily_results_persistence import save_monitoring_results


def run_monitoring(pool_name: str = None, data: str = None) -> Dict[str, Any]:
    """
    Interface principal unificada do sistema de monitoramento AmFi.
    
    FUNCIONALIDADES PRINCIPAIS:
    ==========================
    
    🎯 **Monitores Executados**: TODOS os monitores configurados
    - ✅ **Subordinação**: Índice de subordinação (SR) com limites mínimo/crítico
    - ✅ **Inadimplência**: Análise por janelas customizáveis (30d, 90d, etc.)
    - ✅ **PDD**: Provisão para devedores duvidosos
    - ✅ **Concentração**: Sacados/cedentes individuais e top-N (**NOVO - Building Block 7**)
    - ✅ **Análise de Liquidez**: Disponibilidade vs próximo pagamento (3 cenários)
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
        data (str, optional):
            - None: Usa arquivos mais recentes (comportamento padrão)
            - "dd/mm/aaaa": Usa arquivos de data específica para análise histórica
        
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
                    "monitores_executados": ["subordinacao", "inadimplencia", "pdd", "liquidez"],
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
                        },
                        "liquidez": {
                            "success": bool,
                            "next_payment": {
                                "date": "YYYY-MM-DD",
                                "amount": float,
                                "percentage": float
                            },
                            "scenarios": {
                                "optimistic": {
                                    "sufficient": bool,
                                    "coverage_ratio": float,
                                    "gap": float,
                                    "surplus": float
                                },
                                "predicted": {...},
                                "conservative": {...}
                            },
                            "summary": {
                                "all_scenarios_sufficient": bool,
                                "worst_case_gap": float,
                                "best_case_surplus": float
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
        >>>
        >>> # Verificar liquidez (se configurado)
        >>> if 'liquidez' in pool_result['resultados']:
        >>>     liquidez_result = pool_result['resultados']['liquidez']
        >>>     if liquidez_result.get('success'):
        >>>         scenarios = liquidez_result['scenarios']
        >>>         print(f"Cenário otimista: {'✅' if scenarios['optimistic']['sufficient'] else '❌'}")
        >>>         print(f"Cenário conservador: {'✅' if scenarios['conservative']['sufficient'] else '❌'}")
        >>>
        >>> # Usar apenas análise de liquidez
        >>> resultado_liquidez = run_liquidity_analysis("LeCapital Pool #1")
        >>> if resultado_liquidez['sucesso']:
        >>>     pool_liquidez = resultado_liquidez['resultados_liquidez']['LeCapital Pool #1']
        >>>     print(f"Próximo pagamento: R$ {pool_liquidez['next_payment']['amount']:,.2f}")
    
    Raises:
        FileNotFoundError: Quando arquivos de dados ou configuração não são encontrados
        ValueError: Quando dados têm formato inválido ou configuração incorreta
        KeyError: Quando tentativa de acessar chaves inexistentes em configurações
        ImportError: Quando módulos de monitores não podem ser importados
        Exception: Qualquer erro não tratado é capturado e retornado na estrutura de resposta
        
    Note:
        - Falhas em pools individuais não interrompem o processamento dos demais
        - Todos os erros são capturados e incluídos na resposta final
        - Sistema projetado para máxima resiliência e continuidade de operação
    """
    try:
        # Carregar dados
        dados = load_pool_data(data)
        
        if not dados["sucesso"]:
            return dados
        
        # Filtrar pools se especifico
        if pool_name:
            if pool_name not in dados["pools_processados"]:
                return {
                    "sucesso": False,
                    "erro": f"Pool '{pool_name}' não encontrado",
                    "pools_disponiveis": dados["pools_processados"]
                }
            pools_para_processar = [pool_name]
        else:
            pools_para_processar = dados["pools_processados"]
        
        # Processar pools
        resultados_pools = {}
        pools_com_sucesso = pools_com_erro = 0
        
        for pool in pools_para_processar:
            try:
                resultado_pool = _process_single_pool(pool, dados)
                resultados_pools[pool] = resultado_pool
                
                if resultado_pool.get("sucesso", False):
                    pools_com_sucesso += 1
                else:
                    pools_com_erro += 1
                    
            except Exception as e:
                pools_com_erro += 1
                resultados_pools[pool] = {
                    "sucesso": False,
                    "erro": str(e),
                    "pool": pool,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Consolidar resultados
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
            "xlsx_enriched": dados["xlsx_data"],
            "metadados": dados.get("metadados", {})
        }
        
        # Salvar resultados automaticamente
        try:
            data_sources = {
                "csv_file": dados.get("metadados", {}).get("csv_file", ""),
                "xlsx_file": dados.get("metadados", {}).get("xlsx_file", "")
            }
            save_monitoring_results(resultado_final, data_sources)
            log_alerta({
                "tipo": "info",
                "titulo": "Persistência Automática",
                "mensagem": f"Resultados salvos automaticamente para {len(pools_para_processar)} pools"
            })
        except Exception as e:
            log_alerta({
                "tipo": "warning",
                "titulo": "Erro na Persistência",
                "mensagem": f"Falha ao salvar resultados automaticamente: {str(e)}"
            })
        
        return resultado_final
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
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
        
        # Filtrar dados do pool
        csv_data = dados["csv_data"]
        nome_col = 'nome' if 'nome' in csv_data.columns else 'Nome'
        pool_csv = csv_data[csv_data[nome_col] == pool_name]
        
        xlsx_data = dados["xlsx_data"]
        pool_xlsx = xlsx_data[xlsx_data['pool'] == pool_name]
        
        if pool_csv.empty or pool_xlsx.empty:
            return {
                "sucesso": False,
                "erro": f"Pool '{pool_name}' não encontrado nos dados",
                "pool": pool_name
            }
        
        # Resultados do pool
        resultados_monitores = {}
        
        # Executar monitores ativos
        
        # 1. Monitor de Subordinação
        sub_monitor = SubordinationMonitor(config)
        if sub_monitor.is_active():
            resultado_sub = sub_monitor.run_monitoring(pool_csv)
            resultados_monitores["subordinacao"] = resultado_sub
        
        # 2. Monitor de Inadimplência (com enriquecimento)
        if _has_delinquency_monitoring(config):
            resultado_inad = run_delinquency_monitoring(pool_csv, dados["xlsx_data"], config)
            resultados_monitores["inadimplencia"] = resultado_inad
        
        # 3. Monitor de PDD (usa dados enriquecidos)
        if _has_pdd_monitoring(config):
            pool_xlsx_enriched = dados["xlsx_data"][dados["xlsx_data"]["pool"] == pool_name]
            
            if pool_xlsx_enriched.empty:
                pool_name_alt = config.get('pool_name', config.get('pool_id', ''))
                pool_xlsx_enriched = dados["xlsx_data"][dados["xlsx_data"]["pool"] == pool_name_alt]
            
            resultado_pdd = run_pdd_monitoring(pool_xlsx_enriched, config)
            resultados_monitores["pdd"] = resultado_pdd
        
        # 4. Monitor de Concentração
        if _has_concentration_monitoring(config):
            resultado_conc = run_concentration_monitoring(pool_csv, dados["xlsx_data"], config)
            resultados_monitores["concentracao"] = resultado_conc
        
        # 5. Monitor de Liquidez (Análise de Fluxo de Caixa)
        if _has_liquidity_monitoring(config):
            resultado_liquidez = run_liquidity_monitoring(pool_csv, dados["xlsx_data"], config)
            resultados_monitores["liquidez"] = resultado_liquidez
        
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


# Funções auxiliares simplificadas
def _has_delinquency_monitoring(config: Dict[str, Any]) -> bool:
    """Verifica se o pool tem monitoramento de inadimplência."""
    monitoramentos = config.get('monitoramentos_ativos', [])
    return any(monitor.get('tipo') == 'inadimplencia' and monitor.get('ativo', False) 
               for monitor in monitoramentos)

def _has_pdd_monitoring(config: Dict[str, Any]) -> bool:
    """Verifica se o pool tem monitoramento de PDD."""
    return bool(config.get('provisoes_pdd', {}).get('grupos_risco', {}))

def _has_concentration_monitoring(config: Dict[str, Any]) -> bool:
    """Verifica se o pool tem monitoramento de concentração."""
    monitoramentos = config.get('monitoramentos_ativos', [])
    return any(monitor.get('tipo') == 'concentracao' and monitor.get('ativo', False) 
               for monitor in monitoramentos)

def _has_liquidity_monitoring(config: Dict[str, Any]) -> bool:
    """Verifica se o pool tem cronograma de pagamentos para análise de liquidez."""
    cronograma_pagamentos = config.get('cronograma_pagamentos', {})
    cronograma = cronograma_pagamentos.get('cronograma_amortizacao', [])
    return bool(cronograma)

def run_liquidity_monitoring(pool_csv, xlsx_data, config):
    """Executa análise de liquidez usando o LiquidityAnalyzer."""
    try:
        analyzer = LiquidityAnalyzer(config, pool_csv, xlsx_data)
        return analyzer.run_full_analysis()
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e),
            'pool': config.get('pool_name', 'Unknown'),
            'timestamp': datetime.now().isoformat()
        }


def run_liquidity_analysis(pool_name: str = None, data: str = None) -> Dict[str, Any]:
    """
    Interface principal para análise de liquidez apenas.
    
    Args:
        pool_name (str, optional): Nome do pool para análise
        data (str, optional): Data específica no formato dd/mm/aaaa
        
    Returns:
        Dict[str, Any]: Resultados da análise de liquidez
    """
    try:
        # Carregar dados
        dados = load_pool_data(data)
        
        if not dados["sucesso"]:
            return dados
        
        # Filtrar pools se específico
        if pool_name:
            if pool_name not in dados["pools_processados"]:
                return {
                    "sucesso": False,
                    "erro": f"Pool '{pool_name}' não encontrado",
                    "pools_disponiveis": dados["pools_processados"]
                }
            pools_para_processar = [pool_name]
        else:
            pools_para_processar = dados["pools_processados"]
        
        # Processar análise de liquidez
        resultados_liquidez = {}
        pools_com_sucesso = pools_com_erro = 0
        
        for pool in pools_para_processar:
            try:
                # Obter configuração do pool
                config = dados["pools_configs"].get(pool)
                if not config:
                    pools_com_erro += 1
                    continue
                
                # Verificar se tem cronograma de amortização
                if not _has_liquidity_monitoring(config):
                    pools_com_erro += 1
                    resultados_liquidez[pool] = {
                        "sucesso": False,
                        "erro": "Pool não possui cronograma de pagamentos",
                        "pool": pool
                    }
                    continue
                
                # Filtrar dados do pool
                csv_data = dados["csv_data"]
                nome_col = 'nome' if 'nome' in csv_data.columns else 'Nome'
                pool_csv = csv_data[csv_data[nome_col] == pool]
                
                xlsx_data = dados["xlsx_data"]
                pool_xlsx = xlsx_data[xlsx_data['pool'] == pool]
                
                if pool_csv.empty or pool_xlsx.empty:
                    pools_com_erro += 1
                    resultados_liquidez[pool] = {
                        "sucesso": False,
                        "erro": f"Pool '{pool}' não encontrado nos dados",
                        "pool": pool
                    }
                    continue
                
                # Enriquecer dados se necessário (para conservative scenario)
                if 'dias_atraso' not in xlsx_data.columns:
                    # Trigger enrichment via delinquency monitoring
                    _ = run_delinquency_monitoring(pool_csv, xlsx_data, config)
                
                # Executar análise de liquidez
                resultado = run_liquidity_monitoring(pool_csv, xlsx_data, config)
                
                if resultado.get('success', False):
                    pools_com_sucesso += 1
                else:
                    pools_com_erro += 1
                
                resultados_liquidez[pool] = resultado
                
            except Exception as e:
                pools_com_erro += 1
                resultados_liquidez[pool] = {
                    "sucesso": False,
                    "erro": str(e),
                    "pool": pool,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Consolidar resultados
        return {
            "sucesso": True,
            "timestamp": datetime.now().isoformat(),
            "pools_processados": pools_para_processar,
            "estatisticas": {
                "total": len(pools_para_processar),
                "sucesso": pools_com_sucesso,
                "erro": pools_com_erro,
                "taxa_sucesso": round(pools_com_sucesso / len(pools_para_processar) * 100, 1) if pools_para_processar else 0
            },
            "resultados_liquidez": resultados_liquidez
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Exemplo de uso direto
    print("🎯 ORQUESTRADOR DE MONITORAMENTO - Todos os Monitores")
    print("=" * 60)
    
    # Executar para pools de teste (NOVO: inclui inadimplência + liquidez)
    resultado = run_monitoring()
    
    # Exemplo de análise de liquidez apenas
    print("\n💧 ANÁLISE DE LIQUIDEZ APENAS")
    print("=" * 60)
    resultado_liquidez = run_liquidity_analysis()
    
    if resultado_liquidez.get("sucesso"):
        print(f"✅ Análise de liquidez concluída para {resultado_liquidez['estatisticas']['total']} pools")
        print(f"   📊 Taxa de sucesso: {resultado_liquidez['estatisticas']['taxa_sucesso']}%")
        
        # Mostrar resumo de liquidez
        for pool_name, pool_result in resultado_liquidez["resultados_liquidez"].items():
            print(f"\n🏦 {pool_name}:")
            if pool_result.get('success', False):
                scenarios = pool_result.get('scenarios', {})
                summary = pool_result.get('summary', {})
                
                all_sufficient = summary.get('all_scenarios_sufficient', False)
                status = "✅ Todos os cenários suficientes" if all_sufficient else "⚠️ Alguns cenários insuficientes"
                print(f"   {status}")
                
                if not all_sufficient:
                    worst_gap = summary.get('worst_case_gap', 0)
                    print(f"   📉 Pior gap: R$ {worst_gap:,.2f}")
                else:
                    best_surplus = summary.get('best_case_surplus', 0)
                    print(f"   📈 Melhor sobra: R$ {best_surplus:,.2f}")
            else:
                print(f"   ❌ Erro: {pool_result.get('error', 'N/A')}")
    else:
        print(f"❌ Erro na análise de liquidez: {resultado_liquidez.get('erro', 'N/A')}")
    
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
            
            # Resultados de Liquidez
            if 'liquidez' in pool_result.get('resultados', {}):
                liquidez_result = pool_result['resultados']['liquidez']
                print(f"   💧 Análise de Liquidez:")
                if 'success' in liquidez_result and liquidez_result['success']:
                    if 'next_payment' in liquidez_result:
                        next_payment = liquidez_result['next_payment']
                        print(f"     - Próximo pagamento: R$ {next_payment.get('amount', 0):,.2f} ({next_payment.get('date', 'N/A')})")
                    
                    if 'scenarios' in liquidez_result:
                        scenarios = liquidez_result['scenarios']
                        print(f"     - Cenários de liquidez:")
                        for scenario_name, scenario_data in scenarios.items():
                            sufficient = scenario_data.get('sufficient', False)
                            status = '✅ Suficiente' if sufficient else '❌ Insuficiente'
                            coverage = scenario_data.get('coverage_ratio', 0)
                            print(f"       • {scenario_name.capitalize()}: {status} (cobertura: {coverage:.2f}x)")
                            
                            if not sufficient and scenario_data.get('gap', 0) > 0:
                                gap = scenario_data.get('gap', 0)
                                print(f"         Gap: R$ {gap:,.2f}")
                            elif sufficient and scenario_data.get('surplus', 0) > 0:
                                surplus = scenario_data.get('surplus', 0)
                                print(f"         Sobra: R$ {surplus:,.2f}")
                else:
                    print(f"     - Erro na análise: {liquidez_result.get('error', 'N/A')}")
        
    else:
        print(f"❌ Falha na orquestração: {resultado.get('erro', 'Erro desconhecido')}")
        
        # Tentar pelo menos a análise de liquidez
        print("\n🔧 Tentando análise de liquidez isolada...")
        resultado_liquidez = run_liquidity_analysis()
        
        if resultado_liquidez.get("sucesso"):
            print(f"✅ Análise de liquidez funcionou isoladamente")
            print(f"   📊 {resultado_liquidez['estatisticas']['sucesso']} pools com sucesso")
        else:
            print(f"❌ Análise de liquidez também falhou: {resultado_liquidez.get('erro', 'N/A')}")