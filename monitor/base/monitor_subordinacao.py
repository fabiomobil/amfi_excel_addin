"""
Monitor de Subordinação
======================

Responsável por monitorar:
- Subordination Ratio (SR) mínimo e crítico
- Cálculos de adequação patrimonial

Funções principais:
- validate_data(): Validação de dados de entrada
- calculate_subordination_ratio(): Cálculo do ratio atual
"""

import pandas as pd
from typing import Dict, Any
from datetime import datetime


def _find_subordination_monitor(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Busca monitor de subordinação no JSON de configuração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com configuração do monitor de subordinação
        
    Raises:
        ValueError: Se monitor não for encontrado
    """
    if 'monitoramentos_ativos' not in config:
        raise ValueError("Configuração não contém 'monitoramentos_ativos'")
        
    for monitor in config['monitoramentos_ativos']:
        if monitor.get('id') == 'subordinacao':
            return monitor
    
    raise ValueError("Monitor de subordinação não encontrado em 'monitoramentos_ativos'")


def validate_data(df: pd.DataFrame, config: Dict[str, Any]) -> bool:
    """
    Valida se os dados de entrada estão adequados para monitoramento de subordinação.
    
    Args:
        df: DataFrame com dados da carteira (CSV)
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se dados são válidos
        
    Raises:
        ValueError: Se dados essenciais estão ausentes
    """
    try:
        # Verificar se há dados para o pool
        if df.empty:
            raise ValueError("DataFrame está vazio")
        
        # Buscar monitor de subordinação no JSON
        monitor_subordinacao = _find_subordination_monitor(config)
        
        # Verificar se monitor está ativo
        if not monitor_subordinacao.get('ativo', False):
            raise ValueError("Monitor de subordinação está inativo")
        
        # Obter campos necessários dinamicamente do JSON
        campos_necessarios = monitor_subordinacao.get('campos_necessarios', [])
        if not campos_necessarios:
            raise ValueError("Monitor de subordinação não possui 'campos_necessarios' definidos")
        
        # Verificar se colunas necessárias existem no CSV
        colunas_faltantes = [col for col in campos_necessarios if col not in df.columns]
        if colunas_faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes no CSV: {colunas_faltantes}")
        
        # Verificar se valores são numéricos (dados já convertidos pelo data_loader)
        for col in campos_necessarios:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Coluna '{col}' não é numérica")
            
            # Verificar se valores são positivos
            valores_negativos = df[col] < 0
            if valores_negativos.any():
                raise ValueError(f"Coluna '{col}' contém valores negativos")
        
        # Verificar se configuração de limites está completa
        limites = monitor_subordinacao.get('limites', {})
        if not limites:
            raise ValueError("Monitor de subordinação não possui 'limites' definidos")
        
        # Verificar limites obrigatórios
        limites_obrigatorios = ['minimo', 'critico']
        limites_faltantes = [limite for limite in limites_obrigatorios if limite not in limites]
        if limites_faltantes:
            raise ValueError(f"Limites obrigatórios ausentes: {limites_faltantes}")
        
        # Validar se limites fazem sentido (crítico <= mínimo)
        limite_minimo = limites.get('minimo')
        limite_critico = limites.get('critico')
        if limite_critico > limite_minimo:
            raise ValueError(f"Limite crítico ({limite_critico}) não pode ser maior que mínimo ({limite_minimo})")
        
        return True
        
    except Exception as e:
        return False


def calculate_subordination_ratio(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula o subordination ratio atual da carteira.
    
    Fórmula: SR = JR / (SR + JR) ou SR = Subordinada / (Senior + Subordinada)
    
    Args:
        df: DataFrame com dados da carteira (CSV)
        config: Configuração do pool com limites
        
    Returns:
        Dict com valor atual, limites, status e aportes necessários
    """
    try:
        # Obter valores financeiros do CSV (assumindo primeira linha para o pool)
        linha_pool = df.iloc[0]
        
        # Obter valores financeiros já convertidos pelo data_loader (colunas minúsculas)
        pl_atual = linha_pool['pl'] if not pd.isna(linha_pool['pl']) else 0.0
        sr_atual = linha_pool['sr'] if not pd.isna(linha_pool['sr']) else 0.0
        jr_atual = linha_pool['jr'] if not pd.isna(linha_pool['jr']) else 0.0
        
        # Validar se valores fazem sentido
        if pl_atual <= 0:
            raise ValueError(f"PL inválido: {pl_atual}")
        if sr_atual < 0 or jr_atual < 0:
            raise ValueError(f"Valores negativos: SR={sr_atual}, JR={jr_atual}")
        
        # Calcular subordination ratio atual (fórmula correta: JR / (SR + JR))
        denominador = sr_atual + jr_atual
        if denominador > 0:
            subordination_ratio = jr_atual / denominador  # Resultado em decimal (0.25 = 25%)
        else:
            raise ValueError("Denominador zero: SR + JR = 0")
        
        # Buscar monitor de subordinação no JSON
        monitor_subordinacao = _find_subordination_monitor(config)
        
        # Obter limites da configuração (em decimal: 0.25 = 25%)
        limites = monitor_subordinacao['limites']
        limite_minimo = limites['minimo']  # ex: 0.25
        limite_critico = limites['critico']  # ex: 0.20
        
        # Determinar status para cada limite (comparação em decimal)
        status_minimo = "enquadrado" if subordination_ratio >= limite_minimo else "violado"
        status_critico = "enquadrado" if subordination_ratio >= limite_critico else "violado"
        
        # Calcular aportes necessários (apenas se violado)
        # Fórmula: SR_min = (JR + x) / (PL + x)
        # Resolvendo: x = (SR_min * PL - JR) / (1 - SR_min)
        aporte_minimo = 0.0
        aporte_critico = 0.0
        
        if status_minimo == "violado":
            aporte_minimo = (limite_minimo * pl_atual - jr_atual) / (1 - limite_minimo)
            aporte_minimo = max(0.0, aporte_minimo)  # Garantir que não seja negativo
        
        if status_critico == "violado":
            aporte_critico = (limite_critico * pl_atual - jr_atual) / (1 - limite_critico)
            aporte_critico = max(0.0, aporte_critico)  # Garantir que não seja negativo
        
        resultado = {
            "subordination_ratio": round(subordination_ratio, 4),  # Decimal: 0.2517 = 25.17%
            "subordination_ratio_percent": round(subordination_ratio * 100, 2),  # Para exibição: 25.17%
            "limite_minimo": limite_minimo,
            "limite_critico": limite_critico,
            "status_limite_minimo": status_minimo,
            "status_limite_critico": status_critico,
            "aporte_necessario": {
                "para_limite_minimo": round(aporte_minimo, 2),
                "para_limite_critico": round(aporte_critico, 2)
            },
            "dados_financeiros": {
                "pl_atual": pl_atual,
                "sr_atual": sr_atual,
                "jr_atual": jr_atual,
                "denominador_calculo": denominador
            }
        }
        
        return resultado
        
    except Exception as e:
        return {
            "erro": f"Erro ao calcular subordination ratio: {str(e)}",
            "subordination_ratio": None,
            "status_limite_minimo": "erro",
            "status_limite_critico": "erro"
        }


def run_subordination_monitoring(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa monitoramento completo de subordinação.
    
    Função wrapper que combina validação + cálculo em uma chamada única.
    Ideal para uso pelo orquestrador.
    
    Args:
        df: DataFrame com dados da carteira (CSV)
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com resultado completo:
        - Se sucesso: resultado de calculate_subordination_ratio()
        - Se falha: {"erro": "mensagem", "sucesso": False}
        
    Example:
        >>> resultado = run_subordination_monitoring(pool_data, pool_config)
        >>> if resultado.get("erro"):
        ...     log_alerta(resultado["erro"])
        ... else:
        ...     print(f"SR: {resultado['subordination_ratio_percent']}%")
    """
    try:
        # 1. Validar dados de entrada
        if not validate_data(df, config):
            return {
                "erro": "Falha na validação de dados",
                "sucesso": False,
                "monitor": "subordination_ratio"
            }
        
        # 2. Calcular subordination ratio
        resultado = calculate_subordination_ratio(df, config)
        
        # 3. Verificar se houve erro no cálculo
        if "erro" in resultado:
            return {
                **resultado,
                "sucesso": False,
                "monitor": "subordination_ratio"
            }
        
        # 4. Retornar resultado de sucesso
        return {
            **resultado,
            "sucesso": True,
            "monitor": "subordination_ratio"
        }
        
    except Exception as e:
        return {
            "erro": f"Erro inesperado no monitoramento: {str(e)}",
            "sucesso": False,
            "monitor": "subordination_ratio"
        }



