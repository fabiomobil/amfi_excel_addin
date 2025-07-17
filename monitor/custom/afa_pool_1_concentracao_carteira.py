"""
Monitor Customizado - AFA Pool #1 - Concentração baseada na Carteira
====================================================================

Responsável por monitorar concentração do AFA Pool #1 usando valor da carteira 
como base de cálculo (em vez do PL padrão), conforme especificado na escritura.

Diferenças vs monitor base:
- Base de cálculo: Valor da carteira (inclui PDD)
- Fonte: CSV dashboard - coluna específica do valor da carteira
- Limites específicos da AFA conforme escritura

Eventos monitorados:
- concentracao_sacados (base: carteira)
- concentracao_cedentes (base: carteira)  
- concentracao_top_n_sacados (base: carteira)
- concentracao_top_n_cedentes (base: carteira)
"""

import pandas as pd
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Centralized import system - eliminates complex import logic
from ..core.imports import import_function

# Import required functions using centralized system
try:
    log_alerta = import_function('alerts', 'log_alerta', 'util')
    validar_data_d1 = import_function('data_handler', 'validar_data_d1', 'util')
    validar_dados = import_function('concentracao', 'validar_dados')
    calcular_concentracao_individual = import_function('concentracao', 'calcular_concentracao_individual')
    calcular_concentracao_top_n = import_function('concentracao', 'calcular_concentracao_top_n')
    gerar_tabela_analise_concentracao = import_function('concentracao', 'gerar_tabela_analise_concentracao')
    verificar_limite = import_function('concentracao', 'verificar_limite')
    processar_ignore_list = import_function('concentracao', 'processar_ignore_list')
except ImportError:
    # Fallback: funções básicas sem dependências
    def log_alerta(alerta):
        print(f"ALERTA AFA: {alerta}")
    
    def validar_data_d1(data):
        return {"is_d1": True, "data_arquivo": str(data)}


def obter_valor_carteira_afa(csv_data: Dict[str, Any]) -> float:
    """
    Obtém o valor da carteira AFA do CSV dashboard.
    
    Args:
        csv_data: Dados do CSV dashboard
        
    Returns:
        float: Valor da carteira (inclui PDD)
    """
    # Prioridade de campos para valor da carteira
    campos_carteira = [
        'valor_carteira',
        'carteira_total', 
        'total_carteira',
        'valor_presente_liquido',
        'vpl_carteira'
    ]
    
    valor_carteira = 0
    campo_encontrado = None
    
    for campo in campos_carteira:
        if campo in csv_data and csv_data[campo] and csv_data[campo] > 0:
            valor_carteira = float(csv_data[campo])
            campo_encontrado = campo
            break
    
    # Fallback: usar PL se não encontrar campo específico da carteira
    if valor_carteira <= 0:
        valor_carteira = csv_data.get('pl_total', 0)
        campo_encontrado = 'pl_total (fallback)'
        
        log_alerta({
            "tipo": "warning",
            "mensagem": f"Valor da carteira não encontrado, usando PL como fallback: {valor_carteira}"
        })
    else:
        log_alerta({
            "tipo": "info",
            "mensagem": f"Valor da carteira AFA obtido de '{campo_encontrado}': {valor_carteira:,.2f}"
        })
    
    return valor_carteira


def validar_configuracao_afa(config: Dict[str, Any]) -> bool:
    """
    Valida se a configuração é específica para AFA Pool #1.
    
    Args:
        config: Configuração do pool
        
    Returns:
        bool: True se configuração é válida para AFA
    """
    pool_id = config.get('pool_id', '')
    pool_name = config.get('pool_name', '')
    
    # Verificar se é AFA
    if 'AFA' not in pool_id.upper() and 'AFA' not in pool_name.upper():
        log_alerta({
            "tipo": "warning",
            "mensagem": f"Monitor AFA aplicado a pool não-AFA: {pool_id}"
        })
        return False
    
    # Verificar se tem configuração de concentração
    concentracao_config = None
    for monitor in config.get('monitoramentos_ativos', []):
        if monitor.get('tipo') == 'concentracao':
            concentracao_config = monitor
            break
    
    if not concentracao_config:
        log_alerta({
            "tipo": "error",
            "mensagem": "Configuração de concentração ausente para AFA"
        })
        return False
    
    return True


def executar_monitoramento_afa(df_xlsx: pd.DataFrame, csv_data: Dict, config: Dict[str, Any], 
                              pool_id: str) -> Dict[str, Any]:
    """
    Executa monitoramento de concentração específico para AFA Pool #1.
    
    Args:
        df_xlsx: DataFrame com dados da carteira
        csv_data: Dados do CSV dashboard
        config: Configuração do pool (JSON)
        pool_id: ID do pool
        
    Returns:
        Dict com resultados do monitoramento AFA
    """
    try:
        log_alerta({
            "tipo": "info", 
            "mensagem": f"Iniciando monitoramento AFA customizado para {pool_id}"
        })
        
        # Validar configuração específica AFA
        if not validar_configuracao_afa(config):
            return {
                "pool_id": pool_id,
                "status": "ERRO",
                "mensagem": "Configuração inválida para AFA",
                "timestamp": datetime.now().isoformat()
            }
        
        # Validar dados de entrada
        if not validar_dados(df_xlsx, config):
            return {
                "pool_id": pool_id,
                "status": "ERRO",
                "mensagem": "Dados inválidos para monitoramento AFA",
                "timestamp": datetime.now().isoformat()
            }
        
        # Obter valor da carteira (específico AFA)
        valor_carteira = obter_valor_carteira_afa(csv_data)
        
        if valor_carteira <= 0:
            log_alerta({
                "tipo": "error", 
                "mensagem": f"Valor da carteira inválido para AFA: {valor_carteira}"
            })
            return {
                "pool_id": pool_id,
                "status": "ERRO",
                "mensagem": "Valor da carteira inválido",
                "timestamp": datetime.now().isoformat()
            }
        
        # Obter configuração de concentração
        concentracao_config = None
        for monitor in config.get('monitoramentos_ativos', []):
            if monitor.get('tipo') == 'concentracao':
                concentracao_config = monitor
                break
        
        limites_config = concentracao_config.get('limites', [])
        
        # Executar cálculos de concentração (usando valor da carteira)
        resultado_concentracoes = {}
        
        # 1. Concentração individual
        resultado_individual = calcular_concentracao_individual(
            df_xlsx, valor_carteira, limites_config
        )
        resultado_concentracoes['individual'] = resultado_individual
        
        # 2. Concentração top N
        resultado_top_n = calcular_concentracao_top_n(
            df_xlsx, valor_carteira, limites_config
        )
        resultado_concentracoes['top_n'] = resultado_top_n
        
        # 3. Gerar tabela de análise
        tabela_analise = gerar_tabela_analise_concentracao(
            df_xlsx, valor_carteira, limites_config
        )
        
        # 4. Gerar resultado final (customizado para AFA)
        resultado_final = gerar_resultado_afa(
            resultado_concentracoes, tabela_analise, config, pool_id, valor_carteira
        )
        
        # Log do resultado
        total_violacoes = len(resultado_final.get('violacoes', []))
        log_alerta({
            "tipo": "info",
            "mensagem": f"Monitoramento AFA concluído: {pool_id} - {total_violacoes} violações (base: carteira)"
        })
        
        return resultado_final
        
    except Exception as e:
        log_alerta({
            "tipo": "error", 
            "mensagem": f"Erro no monitoramento AFA: {str(e)}"
        })
        return {
            "pool_id": pool_id,
            "status": "ERRO",
            "mensagem": f"Erro durante execução AFA: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def gerar_resultado_afa(concentracoes: Dict[str, Any], tabela_analise: List[Dict], 
                       config: Dict[str, Any], pool_id: str, valor_carteira: float) -> Dict[str, Any]:
    """
    Gera resultado específico para AFA com base na carteira.
    
    Args:
        concentracoes: Dict com todas as concentrações calculadas
        tabela_analise: Tabela de análise detalhada
        config: Configuração do pool
        pool_id: ID do pool
        valor_carteira: Valor da carteira utilizado como base
        
    Returns:
        Dict com resultado padronizado AFA
    """
    # Contar violações e alertas
    violacoes = []
    alertas = []
    
    # Coletar violações de concentração individual
    if 'individual' in concentracoes:
        if 'violacoes' in concentracoes['individual']:
            violacoes.extend(concentracoes['individual']['violacoes'])
    
    # Coletar violações de concentração top N
    if 'top_n' in concentracoes:
        if 'violacoes' in concentracoes['top_n']:
            violacoes.extend(concentracoes['top_n']['violacoes'])
    
    # Determinar status geral
    if violacoes:
        status_geral = "VIOLACAO"
        severidade = "critica"
    elif any(item['status'] == 'ATENCAO' for item in tabela_analise):
        status_geral = "ATENCAO"
        severidade = "alta"
    else:
        status_geral = "OK"
        severidade = "baixa"
    
    # Gerar recomendações específicas AFA
    recomendacoes = []
    if violacoes:
        recomendacoes.append("Reduzir exposições que violam limites da escritura AFA")
        recomendacoes.append("Verificar impacto no valor da carteira")
        recomendacoes.append("Considerar acionamento de triggers de aceleração")
    elif status_geral == "ATENCAO":
        recomendacoes.append("Monitorar exposições próximas aos limites AFA")
        recomendacoes.append("Evitar novas aquisições de entidades em atenção")
    else:
        recomendacoes.append("Continuar monitoramento normal AFA")
    
    # Calcular estatísticas
    total_entidades = len(tabela_analise)
    entidades_violacao = len([item for item in tabela_analise if item['status'] == 'VIOLACAO'])
    entidades_atencao = len([item for item in tabela_analise if item['status'] == 'ATENCAO'])
    entidades_ok = len([item for item in tabela_analise if item['status'] == 'OK'])
    
    return {
        "pool_id": pool_id,
        "tipo_monitoramento": "concentracao_afa_customizado",
        "timestamp": datetime.now().isoformat(),
        "status_geral": status_geral,
        "severidade": severidade,
        "base_calculo": {
            "tipo": "valor_carteira",  # Específico AFA
            "valor": float(valor_carteira),
            "descricao": "Valor da carteira conforme escritura AFA (inclui PDD)"
        },
        "resumo": {
            "total_entidades": total_entidades,
            "entidades_ok": entidades_ok,
            "entidades_atencao": entidades_atencao,
            "entidades_violacao": entidades_violacao,
            "total_violacoes": len(violacoes)
        },
        "concentracao_individual": concentracoes.get('individual', {}),
        "concentracao_top_n": concentracoes.get('top_n', {}),
        "tabela_analise": tabela_analise,
        "violacoes": violacoes,
        "recomendacoes": recomendacoes,
        "metadata": {
            "versao_monitor": "1.0_afa_custom",
            "base_dados": "xlsx_carteira",
            "configuracao": config.get('pool_id', 'AFA Pool #1'),
            "especificidade": "Cálculo baseado no valor da carteira conforme escritura AFA",
            "diferenca_monitor_base": "Base de cálculo = carteira (não PL)"
        }
    }


def obter_limites_afa() -> Dict[str, Any]:
    """
    Retorna os limites específicos da AFA Pool #1 conforme escritura.
    
    Returns:
        Dict com limites AFA
    """
    return {
        "concentracao_individual": {
            "sacado": 0.27,  # 27% sobre valor da carteira
            "cedente": 0.30  # 30% sobre valor da carteira
        },
        "concentracao_top_n": {
            "top_10_sacados": 1.00,  # 100% sobre valor da carteira
            "top_10_cedentes": 0.70  # 70% sobre valor da carteira
        },
        "base_calculo": "valor_carteira",
        "fonte": "Escritura AFA Pool #1"
    }


if __name__ == "__main__":
    # Exemplo de uso específico AFA
    print("Monitor AFA Pool #1 - Concentração baseada na Carteira")
    print("=" * 55)
    print("")
    print("Uso: Integrar com sistema de carregamento de dados")
    print("")
    print("Exemplo:")
    print("from monitor.utils.data_loader import load_pool_data")
    print("from monitor.custom.afa_pool_1_concentracao_carteira import executar_monitoramento_afa")
    print("")
    print("# Carregar dados")
    print("data = load_pool_data()")
    print("pool_data = data['pools']['AFA Pool #1']")
    print("")
    print("# Executar monitoramento AFA")
    print("resultado = executar_monitoramento_afa(")
    print("    pool_data['xlsx_df'],")
    print("    pool_data['csv_data'],")
    print("    pool_data['config'],")
    print("    'AFA Pool #1'")
    print(")")
    print("")
    print("print(json.dumps(resultado, indent=2, ensure_ascii=False))")
    print("")
    print("Limites AFA:")
    limites = obter_limites_afa()
    print(json.dumps(limites, indent=2, ensure_ascii=False))