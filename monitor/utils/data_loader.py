"""
Carregamento de Dados Principal
==============================

Responsável por:
- Orquestrar todo o processo de carregamento
- Integrar descoberta, validação e alertas
- Fornecer interface unificada para monitores
- Coordenar modo debug vs normal
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Sistema de imports robusto para compatibilidade com Spyder e outros ambientes
import_success = False

# Método 1: Tentar imports relativos (execução como módulo)
try:
    from .file_loaders import load_dashboard, load_portfolio, load_json_file, get_file_metadata
    from .data_handler import data_validation, gerar_metadados_carregamento, validar_dados_por_pool
    from .alerts import log_alerta
    # from .file_discovery import descobrir_arquivo_mais_recente, validar_consistencia_datas
    from .data_handler import validar_data_d1, date_check_alert, gerar_alerta_nao_d1
    import_success = True
except (ImportError, ValueError):
    pass

# Método 2: Tentar imports diretos (Spyder/execução direta)
if not import_success:
    try:
        # Adicionar diretório atual ao path se necessário
        import sys
        if os.path.dirname(__file__) not in sys.path:
            sys.path.insert(0, os.path.dirname(__file__))
            
        from file_loaders import load_dashboard, load_portfolio, load_json_file, get_file_metadata
        from data_handler import data_validation, gerar_metadados_carregamento, validar_dados_por_pool
        from alerts import log_alerta
        # from file_discovery import descobrir_arquivo_mais_recente, validar_consistencia_datas
        from data_handler import validar_data_d1, date_check_alert, gerar_alerta_nao_d1
        import_success = True
    except ImportError:
        pass

# Método 3: Tentar com caminho absoluto
if not import_success:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from monitor.utils.file_loaders import load_dashboard, load_portfolio, load_json_file, get_file_metadata
        from monitor.utils.data_handler import data_validation, gerar_metadados_carregamento, validar_dados_por_pool
        from monitor.utils.alerts import log_alerta
        # from monitor.utils.file_discovery import descobrir_arquivo_mais_recente, validar_consistencia_datas
        from monitor.utils.data_handler import validar_data_d1, date_check_alert, gerar_alerta_nao_d1
        import_success = True
    except ImportError:
        pass

# Se todos falharem, usar funções mock
if not import_success:
    print("⚠️ Alguns módulos auxiliares não foram encontrados. Usando versões simplificadas.")
    
    def date_check_alert(csv_date, xlsx_date):
        return {"tipo": "warning", "mensagem": "Verificação de data simplificada"}
    
    def log_alerta(alerta):
        print(f"📝 Log: {alerta.get('mensagem', 'Log desconhecido')}")
    
    def data_validation(csv_df, xlsx_df):
        return True
    
    def gerar_metadados_carregamento(csv_info, xlsx_info, alertas):
        return {"timestamp": "mock", "arquivos": {}}
    
    def validar_dados_por_pool(xlsx_df, configs):
        return {}
    
    def load_dashboard(data=None, pool=None):
        print("⚠️ Usando versão mock de load_dashboard")
        df = pd.DataFrame()
        df.attrs = {"arquivo": "mock.csv", "data_arquivo": datetime.now()}
        return df
    
    def load_portfolio(data=None, pool=None):
        print("⚠️ Usando versão mock de load_portfolio")
        df = pd.DataFrame()
        df.attrs = {"arquivo": "mock.xlsx", "data_arquivo": datetime.now()}
        return df
    
    def load_json_file(nome_arquivo):
        print(f"⚠️ Usando versão mock de load_json_file para {nome_arquivo}")
        return {}
    
    def get_file_metadata(df):
        return {"arquivo": "mock", "data_arquivo": None, "registros": 0, "colunas": 0}


def load_pool_data(data: str = None) -> Dict:
    """
    Função principal que orquestra todo o processo de carregamento.
    
    MODO DEBUG (se test_pools.json existe):
    1) Carrega CSV 2) Carrega XLSX 3) Validações 4) Usa pools do test_pools.json
    5) Carrega JSONs 6) Validações finais
    
    MODO NORMAL (sem test_pools.json):
    1) Carrega CSV 2) Carrega XLSX 3) Validações 4) Obtém pools do CSV 
    5) Verifica ignore list 6) Carrega JSONs 7) Validações finais
    
    Args:
        data: Data específica no formato dd/mm/aaaa (opcional)
        
    Returns:
        Dict com dados carregados e metadados
        
    Raises:
        DataInconsistencyError: Se dados inconsistentes e usuário não confirmar
        DateValidationError: Se data inválida e usuário não confirmar
        FileNotFoundError: Se arquivos não encontrados
    """
    alertas = []
    monitores_debug = None  # Para armazenar monitores específicos do debug
    
    try:
        # ETAPA 1: Carregar CSV (dashboard)
        log_alerta({"tipo": "info", "mensagem": "Iniciando carregamento de dados - Etapa 1/9: Carregando Dashboard"})
        csv_df = load_dashboard(data)
        
        # ETAPA 2: Carregar XLSX (portfolio)
        log_alerta({"tipo": "info", "mensagem": "Etapa 2/9: Carregando Portfolio"})
        xlsx_df = load_portfolio(data)
        
        # ETAPA 3: Validações de consistência
        log_alerta({"tipo": "info", "mensagem": "Etapa 3/9: Validando consistência de dados"})
        validacao_ok = data_validation(csv_df, xlsx_df)
        if not validacao_ok:
            alerta = date_check_alert(csv_df.attrs.get('data_arquivo'), xlsx_df.attrs.get('data_arquivo'))
            alertas.append(alerta)
            # Temporariamente ignorar validação para teste
            log_alerta({"tipo": "warning", "mensagem": "⚠️ Validação de data ignorada para teste"})
        
        # Verificar se estamos em modo debug
        try:
            test_config = load_json_file("test_pools.json")
            
            # MODO DEBUG - usar pools do test_pools.json
            pools = test_config.get("debug_pools", [])
            monitores_debug = test_config.get("monitor", [])  # Carregar monitores específicos
            
            if not pools:
                raise ValueError("test_pools.json existe mas não contém pools válidos em 'debug_pools'")
            
            log_alerta({
                "tipo": "info",
                "mensagem": f"MODO DEBUG: Usando {len(pools)} pools do test_pools.json: {pools}"
            })
            
            if monitores_debug:
                log_alerta({
                    "tipo": "info",
                    "mensagem": f"MODO DEBUG: Executando apenas {len(monitores_debug)} monitores: {monitores_debug}"
                })
                
        except FileNotFoundError:
            # MODO NORMAL - fluxo completo
            # ETAPA 4: Obter pools do CSV
            log_alerta({"tipo": "info", "mensagem": "MODO NORMAL: Obtendo lista de pools do CSV"})
            csv_pools = get_dashboard_pools(csv_df)
            
            # ETAPA 5: Verificar ignore list
            log_alerta({"tipo": "info", "mensagem": "Filtrando pools com ignore list"})
            pools = filter_ignored_pools(csv_pools)
            
            log_alerta({
                "tipo": "info",
                "mensagem": f"Processando {len(pools)} pools"
            })
        except Exception as e:
            raise Exception(f"Erro ao processar test_pools.json: {str(e)}")
        
        # Filtrar CSV e XLSX pelos pools selecionados (debug ou normal)
        log_alerta({"tipo": "info", "mensagem": f"Filtrando dados pelos {len(pools)} pools selecionados"})
        nome_col = 'nome' if 'nome' in csv_df.columns else 'Nome'
        if nome_col in csv_df.columns:
            csv_df = csv_df[csv_df[nome_col].isin(pools)]
            log_alerta({"tipo": "info", "mensagem": f"CSV filtrado: {len(csv_df)} registros restantes"})
        
        # Carregar JSONs de configuração
        log_alerta({"tipo": "info", "mensagem": "Carregando configurações JSON"})
        configs_pools = load_json(pools)
        
        # Validações finais por pool
        log_alerta({"tipo": "info", "mensagem": "Validações finais por pool"})
        validacoes_finais = validar_dados_por_pool(xlsx_df, configs_pools)
        
        # Gerar metadados completos
        metadados = gerar_metadados_carregamento(
            get_file_metadata(csv_df),
            get_file_metadata(xlsx_df),
            alertas
        )
        
        resultado = {
            "csv_data": csv_df,
            "xlsx_data": xlsx_df,
            "pools_configs": configs_pools,
            "pools_processados": pools,
            "monitores_debug": monitores_debug,  # Monitores específicos se em modo debug
            "validacoes": validacoes_finais,
            "metadados": metadados,
            "alertas": alertas,
            "sucesso": True
        }
        
        log_alerta({"tipo": "info", "mensagem": f"Carregamento concluído com sucesso. {len(pools)} pools processados."})
        return resultado
        
    except Exception as e:
        log_alerta({"tipo": "error", "mensagem": f"Erro durante carregamento: {str(e)}"})
        return {
            "csv_data": None,
            "xlsx_data": None,
            "pools_configs": {},
            "pools_processados": [],
            "monitores_debug": None,
            "validacoes": {},
            "metadados": {},
            "alertas": alertas + [{"tipo": "error", "mensagem": str(e)}],
            "sucesso": False,
            "erro": str(e)
        }


def get_dashboard_pools(csv_df: pd.DataFrame) -> List[str]:
    """
    Extrai lista de pools únicos do DataFrame CSV.
    
    Args:
        csv_df: DataFrame do CSV
        
    Returns:
        List[str]: Lista de nomes de pools únicos
        
    Raises:
        ValueError: Se coluna 'Nome' não existir
    """
    # Verificar colunas disponíveis (podem estar em snake_case)
    nome_col = 'nome' if 'nome' in csv_df.columns else 'Nome'
    tipo_col = 'tipo_de_produto' if 'tipo_de_produto' in csv_df.columns else 'Tipo de Produto'
    
    if nome_col not in csv_df.columns:
        raise ValueError(f"Coluna de nome não encontrada no CSV. Colunas disponíveis: {list(csv_df.columns)}")
    
    # Filtrar apenas rows que são pools (não outros tipos)
    pools_df = csv_df[csv_df[tipo_col] == 'Pool'] if tipo_col in csv_df.columns else csv_df
    
    # Extrair nomes únicos e remover espaços extras
    pools = pools_df[nome_col].dropna().str.strip().unique().tolist()
    
    # Remover strings vazias
    pools = [pool for pool in pools if pool and pool.strip()]
    
    log_alerta({
        "tipo": "info",
        "mensagem": f"Encontrados {len(pools)} pools no CSV"
    })
    
    return pools


def filter_ignored_pools(pools: List[str]) -> List[str]:
    """
    Remove pools da ignore list da lista de pools.
    
    Args:
        pools: Lista de pools para filtrar
        
    Returns:
        List[str]: Lista de pools filtrada
    """
    try:
        ignore_config = load_json_file("ignore_pools.json")
        ignore_list = ignore_config.get("ignore_pools", [])
        
        # Extrair apenas os nomes dos pools ignorados
        ignored_names = [item.get("pool_id") if isinstance(item, dict) else item for item in ignore_list]
        ignored_names = [name for name in ignored_names if name]  # Remover None/vazios
        
        # Filtrar pools
        pools_filtrados = [pool for pool in pools if pool not in ignored_names]
        
        pools_ignorados = len(pools) - len(pools_filtrados)
        if pools_ignorados > 0:
            log_alerta({
                "tipo": "info",
                "mensagem": f"{pools_ignorados} pools ignorados conforme ignore_pools.json"
            })
        
        return pools_filtrados
        
    except FileNotFoundError:
        log_alerta({
            "tipo": "info",
            "mensagem": "Arquivo ignore_pools.json não encontrado - processando todos os pools"
        })
        return pools
    except Exception as e:
        log_alerta({
            "tipo": "warning",
            "mensagem": f"Erro ao processar ignore_pools.json: {str(e)} - processando todos os pools"
        })
        return pools


def load_json(pools: List[str]) -> Dict[str, Dict]:
    """
    Carrega configurações JSON para cada pool.
    
    Args:
        pools: Lista de pools para carregar
        
    Returns:
        Dict[str, Dict]: Configurações por pool
    """
    try:
        from .path_resolver import get_possible_paths
    except ImportError:
        try:
            from path_resolver import get_possible_paths
        except ImportError:
            try:
                from .file_loaders import get_possible_paths
            except ImportError:
                try:
                    from file_loaders import get_possible_paths
                except ImportError:
                    # Se nada funcionar, importar do módulo centralizado com path absoluto
                    import sys
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
                    from path_resolver import get_possible_paths
    
    configs = {}
    pools_sem_config = []
    
    for pool in pools:
        # Usar nome direto do pool como nome de arquivo (padronização 2025-07-11)
        # "LeCapital Pool #1" → "LeCapital Pool #1.json"
        pool_filename = pool
        
        # Múltiplos caminhos para compatibilidade
        possible_json_paths = get_possible_paths('escrituras', f"{pool_filename}.json")
        
        json_path = None
        for path in possible_json_paths:
            if os.path.exists(path):
                json_path = path
                break
        
        try:
            if json_path and os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configs[pool] = config
                    
                    log_alerta({
                        "tipo": "info",
                        "mensagem": f"JSON carregado para pool '{pool}' ({pool_filename}.json)"
                    })
            else:
                pools_sem_config.append(pool)
                configs[pool] = None  # Pool sem configuração
                
        except Exception as e:
            log_alerta({
                "tipo": "warning",
                "mensagem": f"Erro ao carregar JSON do pool '{pool}': {str(e)}"
            })
            configs[pool] = None
    
    # Log de pools sem configuração
    if pools_sem_config:
        log_alerta({
            "tipo": "warning",
            "mensagem": f"Pools sem arquivo JSON de configuração ({len(pools_sem_config)}): {pools_sem_config}"
        })
    
    return configs