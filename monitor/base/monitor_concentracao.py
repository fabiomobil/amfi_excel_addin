"""
Monitor de Concentração
======================

Responsável por monitorar:
- Concentração individual por sacado/cedente
- Concentração agregada top N (10, 15, 30, etc.)
- Verificação de grupos econômicos
- Limites específicos por entidade

Eventos monitorados:
- concentracao_sacados
- concentracao_cedentes
- concentracao_top_n_sacados
- concentracao_top_n_cedentes
"""

import pandas as pd
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Sistema de imports robusto para compatibilidade com Spyder e outros ambientes
import_success = False

# Método 1: Tentar imports relativos (execução como módulo)
try:
    from ..utils.alerts import log_alerta
    from ..utils.data_handler import validar_data_d1
    import_success = True
except (ImportError, ValueError):
    pass

# Método 2: Tentar imports diretos (Spyder/execução direta)
if not import_success:
    try:
        # Adicionar diretório utils ao path se necessário
        utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
        if utils_path not in sys.path:
            sys.path.insert(0, utils_path)
            
        from alerts import log_alerta
        from data_handler import validar_data_d1
        import_success = True
    except ImportError:
        # Fallback: funções básicas sem dependências
        def log_alerta(alerta):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tipo = alerta.get('tipo', 'info').upper()
            mensagem = alerta.get('mensagem', str(alerta))
            print(f"📝 [{timestamp}] {tipo}: {mensagem}")
        
        def validar_data_d1(data):
            return {"is_d1": True, "data_arquivo": str(data)}


def validar_dados(df: pd.DataFrame, config: Dict[str, Any]) -> bool:
    """
    Valida se os dados de entrada estão adequados para monitoramento de concentração.
    
    Args:
        df: DataFrame com dados da carteira
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se dados são válidos
        
    Raises:
        ValueError: Se dados essenciais estão ausentes
    """
    erros = []
    
    # Verificar se DataFrame não está vazio
    if df.empty:
        erros.append("DataFrame da carteira está vazio")
        
    # Verificar colunas essenciais (nomes normalizados pelo data_loader)
    colunas_obrigatorias = ['nome_do_sacado', 'nome_do_cedente', 'valor_presente']
    colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    
    if colunas_faltantes:
        erros.append(f"Colunas obrigatórias ausentes: {colunas_faltantes}")
    
    # Verificar se há dados válidos
    if 'valor_presente' in df.columns:
        valores_validos = df['valor_presente'].notna() & (df['valor_presente'] > 0)
        if not valores_validos.any():
            erros.append("Nenhum valor presente válido encontrado")
    
    # Verificar configuração de concentração
    if 'monitoramentos_ativos' in config:
        tem_concentracao = any(m.get('tipo') == 'concentracao' for m in config.get('monitoramentos_ativos', []))
        if not tem_concentracao:
            erros.append("Configuração de concentração ausente no JSON")
    else:
        erros.append("Configuração de monitoramentos_ativos ausente no JSON")
    
    # Log de erros encontrados
    if erros:
        for erro in erros:
            log_alerta({"tipo": "error", "mensagem": f"Validação concentração: {erro}"})
        return False
    
    log_alerta({"tipo": "info", "mensagem": "Dados validados para monitoramento de concentração"})
    return True


def calcular_concentracao_individual(df: pd.DataFrame, base_calculo: float, 
                                     limites_config: List[Dict], 
                                     incluir_grupos: bool = True) -> Dict[str, Any]:
    """
    Calcula concentração individual por sacado ou cedente.
    
    Args:
        df: DataFrame com dados da carteira
        base_calculo: Valor base para cálculo de percentuais (PL ou carteira)
        limites_config: Lista de configurações de limites
        incluir_grupos: Se deve considerar agrupamento por grupo econômico
        
    Returns:
        Dict com concentrações individuais e status de cada entidade
    """
    resultado = {
        "sacados": {},
        "cedentes": {},
        "violacoes": [],
        "alertas": []
    }
    
    try:
        # Filtrar dados válidos
        df_valido = df[df['valor_presente'].notna() & (df['valor_presente'] > 0)].copy()
        
        if df_valido.empty:
            log_alerta({"tipo": "warning", "mensagem": "Nenhum dado válido para concentração individual"})
            return resultado
        
        # Processar sacados
        for limite in limites_config:
            if limite.get('tipo') == 'individual' and limite.get('entidade') == 'sacado':
                concentracoes_sacados = df_valido.groupby('nome_do_sacado')['valor_presente'].sum().sort_values(ascending=False)
                
                for sacado, valor in concentracoes_sacados.items():
                    pct_concentracao = valor / base_calculo
                    limite_max = limite.get('limite', 1.0)
                    
                    status_limite = verificar_limite(pct_concentracao, limite)
                    
                    resultado["sacados"][sacado] = {
                        "valor_financeiro": float(valor),
                        "percentual": float(pct_concentracao),
                        "limite": float(limite_max),
                        "status": status_limite["status"],
                        "margem_disponivel": float(limite_max - pct_concentracao),
                        "violacao": pct_concentracao > limite_max
                    }
                    
                    if pct_concentracao > limite_max:
                        resultado["violacoes"].append({
                            "tipo": "concentracao_individual_sacado",
                            "entidade": sacado,
                            "valor_atual": pct_concentracao,
                            "limite": limite_max,
                            "excesso": pct_concentracao - limite_max
                        })
        
        # Processar cedentes
        for limite in limites_config:
            if limite.get('tipo') == 'individual' and limite.get('entidade') == 'cedente':
                concentracoes_cedentes = df_valido.groupby('nome_do_cedente')['valor_presente'].sum().sort_values(ascending=False)
                
                for cedente, valor in concentracoes_cedentes.items():
                    pct_concentracao = valor / base_calculo
                    limite_max = limite.get('limite', 1.0)
                    
                    status_limite = verificar_limite(pct_concentracao, limite)
                    
                    resultado["cedentes"][cedente] = {
                        "valor_financeiro": float(valor),
                        "percentual": float(pct_concentracao),
                        "limite": float(limite_max),
                        "status": status_limite["status"],
                        "margem_disponivel": float(limite_max - pct_concentracao),
                        "violacao": pct_concentracao > limite_max
                    }
                    
                    if pct_concentracao > limite_max:
                        resultado["violacoes"].append({
                            "tipo": "concentracao_individual_cedente",
                            "entidade": cedente,
                            "valor_atual": pct_concentracao,
                            "limite": limite_max,
                            "excesso": pct_concentracao - limite_max
                        })
        
        # Log do resultado
        total_sacados = len(resultado["sacados"])
        total_cedentes = len(resultado["cedentes"])
        total_violacoes = len(resultado["violacoes"])
        
        log_alerta({
            "tipo": "info",
            "mensagem": f"Concentração individual calculada: {total_sacados} sacados, {total_cedentes} cedentes, {total_violacoes} violações"
        })
        
    except Exception as e:
        log_alerta({"tipo": "error", "mensagem": f"Erro no cálculo de concentração individual: {str(e)}"})
        resultado["alertas"].append(f"Erro: {str(e)}")
    
    return resultado


def calcular_concentracao_top_n(df: pd.DataFrame, base_calculo: float, 
                                limites_config: List[Dict]) -> Dict[str, Any]:
    """
    Calcula concentração agregada dos top N maiores sacados/cedentes.
    
    Args:
        df: DataFrame com dados da carteira
        base_calculo: Valor base para cálculo de percentuais
        limites_config: Lista de configurações de limites top N
        
    Returns:
        Dict com concentração agregada e lista dos top N
    """
    resultado = {
        "top_n_sacados": {},
        "top_n_cedentes": {},
        "violacoes": [],
        "detalhes": {}
    }
    
    try:
        # Filtrar dados válidos
        df_valido = df[df['valor_presente'].notna() & (df['valor_presente'] > 0)].copy()
        
        if df_valido.empty:
            log_alerta({"tipo": "warning", "mensagem": "Nenhum dado válido para concentração top N"})
            return resultado
        
        # Processar top N sacados
        for limite in limites_config:
            if limite.get('tipo') == 'top_n' and limite.get('entidade') == 'sacado':
                n = limite.get('n', 10)
                limite_max = limite.get('limite', 1.0)
                
                concentracoes_sacados = df_valido.groupby('nome_do_sacado')['valor_presente'].sum().sort_values(ascending=False)
                top_n_sacados = concentracoes_sacados.head(n)
                
                valor_total_top_n = top_n_sacados.sum()
                pct_total_top_n = valor_total_top_n / base_calculo
                
                # Detalhes dos top N
                top_n_detalhes = []
                for i, (sacado, valor) in enumerate(top_n_sacados.items(), 1):
                    top_n_detalhes.append({
                        "posicao": i,
                        "entidade": sacado,
                        "valor_financeiro": float(valor),
                        "percentual": float(valor / base_calculo)
                    })
                
                resultado["top_n_sacados"][f"top_{n}"] = {
                    "n": n,
                    "valor_total": float(valor_total_top_n),
                    "percentual_total": float(pct_total_top_n),
                    "limite": float(limite_max),
                    "margem_disponivel": float(limite_max - pct_total_top_n),
                    "violacao": pct_total_top_n > limite_max,
                    "detalhes": top_n_detalhes
                }
                
                if pct_total_top_n > limite_max:
                    resultado["violacoes"].append({
                        "tipo": f"concentracao_top_{n}_sacados",
                        "valor_atual": pct_total_top_n,
                        "limite": limite_max,
                        "excesso": pct_total_top_n - limite_max
                    })
        
        # Processar top N cedentes
        for limite in limites_config:
            if limite.get('tipo') == 'top_n' and limite.get('entidade') == 'cedente':
                n = limite.get('n', 10)
                limite_max = limite.get('limite', 1.0)
                
                concentracoes_cedentes = df_valido.groupby('nome_do_cedente')['valor_presente'].sum().sort_values(ascending=False)
                top_n_cedentes = concentracoes_cedentes.head(n)
                
                valor_total_top_n = top_n_cedentes.sum()
                pct_total_top_n = valor_total_top_n / base_calculo
                
                # Detalhes dos top N
                top_n_detalhes = []
                for i, (cedente, valor) in enumerate(top_n_cedentes.items(), 1):
                    top_n_detalhes.append({
                        "posicao": i,
                        "entidade": cedente,
                        "valor_financeiro": float(valor),
                        "percentual": float(valor / base_calculo)
                    })
                
                resultado["top_n_cedentes"][f"top_{n}"] = {
                    "n": n,
                    "valor_total": float(valor_total_top_n),
                    "percentual_total": float(pct_total_top_n),
                    "limite": float(limite_max),
                    "margem_disponivel": float(limite_max - pct_total_top_n),
                    "violacao": pct_total_top_n > limite_max,
                    "detalhes": top_n_detalhes
                }
                
                if pct_total_top_n > limite_max:
                    resultado["violacoes"].append({
                        "tipo": f"concentracao_top_{n}_cedentes",
                        "valor_atual": pct_total_top_n,
                        "limite": limite_max,
                        "excesso": pct_total_top_n - limite_max
                    })
        
        # Log do resultado
        total_violacoes = len(resultado["violacoes"])
        log_alerta({
            "tipo": "info",
            "mensagem": f"Concentração top N calculada com {total_violacoes} violações"
        })
        
    except Exception as e:
        log_alerta({"tipo": "error", "mensagem": f"Erro no cálculo de concentração top N: {str(e)}"})
    
    return resultado


def _organizar_limites_por_tipo(limites_config: List[Dict]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Organiza limites de configuração por tipo (individual vs top_n).
    
    Args:
        limites_config: Lista de configurações de limites
        
    Returns:
        Tuple com (limites_individuais, limites_top_n)
    """
    limites_individuais = {}
    limites_top_n = {}
    
    for limite in limites_config:
        if limite.get('tipo') == 'individual':
            entidade = limite.get('entidade')
            limites_individuais[entidade] = limite
        elif limite.get('tipo') == 'top_n':
            entidade = limite.get('entidade')
            n = limite.get('n', 10)
            limites_top_n[f"{entidade}_top_{n}"] = limite
    
    return limites_individuais, limites_top_n


def _calcular_espaco_top_n(entidade: str, valor_entidade: float, concentracoes_ordenadas: pd.Series, 
                          top_n_config: Dict) -> Tuple[float, str]:
    """
    Calcula espaço disponível considerando limite top N.
    
    Args:
        entidade: Nome da entidade
        valor_entidade: Valor financeiro da entidade
        concentracoes_ordenadas: Series com concentrações ordenadas
        top_n_config: Configuração do limite top N
        
    Returns:
        Tuple com (espaco_top_n, info_top_n)
    """
    if not top_n_config:
        return 0, "N/A"
    
    n = top_n_config.get('n', 10)
    limite_top_n_pct = top_n_config.get('limite', 1.0)
    base_calculo = top_n_config.get('_base_calculo', 1)  # Será injetado pela função principal
    
    # Calcular top N atual
    top_n_atual = concentracoes_ordenadas.head(n)
    valor_top_n_atual = top_n_atual.sum()
    
    # Se está no top N
    if entidade in top_n_atual.index:
        # Folga total do top N
        folga_top_n = max(0, (limite_top_n_pct * base_calculo) - valor_top_n_atual)
        # Adicionar valor atual da entidade (pode crescer até consumir toda folga)
        espaco_top_n = folga_top_n + valor_entidade
        top_n_info = f"Top {n} (dentro)"
    else:
        # Não está no top N - calcular espaço para entrar
        menor_do_top_n = top_n_atual.min() if len(top_n_atual) == n else 0
        espaco_top_n = max(0, menor_do_top_n - valor_entidade)
        top_n_info = f"Top {n} (fora)"
    
    return espaco_top_n, top_n_info


def _determinar_status_entidade(pct_base: float, limite_individual: float) -> str:
    """
    Determina status da entidade baseado no percentual vs limite.
    
    Args:
        pct_base: Percentual atual da entidade
        limite_individual: Limite individual configurado
        
    Returns:
        Status: "VIOLACAO", "ATENCAO" ou "OK"
    """
    if pct_base > limite_individual:
        return "VIOLACAO"
    elif pct_base > limite_individual * 0.8:  # 80% do limite
        return "ATENCAO"
    else:
        return "OK"


def _processar_sacados(df_valido: pd.DataFrame, base_calculo: float, 
                      limites_individuais: Dict, limites_top_n: Dict) -> List[Dict]:
    """
    Processa sacados para tabela de análise de concentração.
    
    Args:
        df_valido: DataFrame com dados válidos da carteira
        base_calculo: Valor base para cálculo de percentuais
        limites_individuais: Dict com limites individuais por entidade
        limites_top_n: Dict com limites top N
        
    Returns:
        Lista com análise de sacados
    """
    tabela_sacados = []
    
    if 'sacado' not in limites_individuais:
        return tabela_sacados
    
    limite_sacado = limites_individuais['sacado']
    concentracoes_sacados = df_valido.groupby('nome_do_sacado')['valor_presente'].sum().sort_values(ascending=False)
    
    # Encontrar top N aplicável para sacados
    top_n_sacado = None
    for key, limite_top in limites_top_n.items():
        if 'sacado' in key:
            top_n_sacado = limite_top.copy()
            top_n_sacado['_base_calculo'] = base_calculo  # Injetar base de cálculo
            break
    
    for sacado, valor in concentracoes_sacados.items():
        pct_base = valor / base_calculo
        limite_individual = limite_sacado.get('limite', 1.0)
        
        # Espaço individual
        espaco_individual = max(0, (limite_individual * base_calculo) - valor)
        
        # Espaço top N
        espaco_top_n, top_n_info = _calcular_espaco_top_n(
            sacado, valor, concentracoes_sacados, top_n_sacado
        )
        
        # Status
        status = _determinar_status_entidade(pct_base, limite_individual)
        
        tabela_sacados.append({
            "entidade": sacado,
            "tipo": "Sacado",
            "valor_financeiro": float(valor),
            "pct_base": float(pct_base),
            "limite_individual": float(limite_individual),
            "espaco_individual": float(espaco_individual),
            "top_n_aplicavel": top_n_info,
            "espaco_top_n": float(espaco_top_n),
            "status": status
        })
    
    return tabela_sacados


def _processar_cedentes(df_valido: pd.DataFrame, base_calculo: float, 
                       limites_individuais: Dict, limites_top_n: Dict) -> List[Dict]:
    """
    Processa cedentes para tabela de análise de concentração.
    
    Args:
        df_valido: DataFrame com dados válidos da carteira
        base_calculo: Valor base para cálculo de percentuais
        limites_individuais: Dict com limites individuais por entidade
        limites_top_n: Dict com limites top N
        
    Returns:
        Lista com análise de cedentes
    """
    tabela_cedentes = []
    
    if 'cedente' not in limites_individuais:
        return tabela_cedentes
    
    limite_cedente = limites_individuais['cedente']
    concentracoes_cedentes = df_valido.groupby('nome_do_cedente')['valor_presente'].sum().sort_values(ascending=False)
    
    # Encontrar top N aplicável para cedentes
    top_n_cedente = None
    for key, limite_top in limites_top_n.items():
        if 'cedente' in key:
            top_n_cedente = limite_top.copy()
            top_n_cedente['_base_calculo'] = base_calculo  # Injetar base de cálculo
            break
    
    for cedente, valor in concentracoes_cedentes.items():
        pct_base = valor / base_calculo
        limite_individual = limite_cedente.get('limite', 1.0)
        
        # Espaço individual
        espaco_individual = max(0, (limite_individual * base_calculo) - valor)
        
        # Espaço top N
        espaco_top_n, top_n_info = _calcular_espaco_top_n(
            cedente, valor, concentracoes_cedentes, top_n_cedente
        )
        
        # Status
        status = _determinar_status_entidade(pct_base, limite_individual)
        
        tabela_cedentes.append({
            "entidade": cedente,
            "tipo": "Cedente",
            "valor_financeiro": float(valor),
            "pct_base": float(pct_base),
            "limite_individual": float(limite_individual),
            "espaco_individual": float(espaco_individual),
            "top_n_aplicavel": top_n_info,
            "espaco_top_n": float(espaco_top_n),
            "status": status
        })
    
    return tabela_cedentes


def gerar_tabela_analise_concentracao(df: pd.DataFrame, base_calculo: float, 
                                     limites_config: List[Dict]) -> List[Dict]:
    """
    Gera tabela completa de análise de concentração com espaços disponíveis.
    
    Args:
        df: DataFrame com dados da carteira
        base_calculo: Valor base para cálculo de percentuais
        limites_config: Lista de configurações de limites
        
    Returns:
        Lista de dicionários com análise detalhada por entidade
    """
    tabela = []
    
    try:
        # Filtrar dados válidos
        df_valido = df[df['valor_presente'].notna() & (df['valor_presente'] > 0)].copy()
        
        if df_valido.empty:
            log_alerta({"tipo": "warning", "mensagem": "Nenhum dado válido para tabela de análise"})
            return tabela
        
        # Organizar limites por tipo usando função de suporte
        limites_individuais, limites_top_n = _organizar_limites_por_tipo(limites_config)
        
        # Processar sacados usando função especializada
        tabela_sacados = _processar_sacados(df_valido, base_calculo, limites_individuais, limites_top_n)
        tabela.extend(tabela_sacados)
        
        # Processar cedentes usando função especializada
        tabela_cedentes = _processar_cedentes(df_valido, base_calculo, limites_individuais, limites_top_n)
        tabela.extend(tabela_cedentes)
        
        # Ordenar por valor financeiro decrescente
        tabela.sort(key=lambda x: x['valor_financeiro'], reverse=True)
        
        log_alerta({
            "tipo": "info",
            "mensagem": f"Tabela de análise gerada com {len(tabela)} entidades ({len(tabela_sacados)} sacados, {len(tabela_cedentes)} cedentes)"
        })
        
    except Exception as e:
        log_alerta({"tipo": "error", "mensagem": f"Erro ao gerar tabela de análise: {str(e)}"})
    
    return tabela


def verificar_limite(valor: float, limite_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica se concentração está dentro dos limites configurados.
    
    Args:
        valor: Valor da concentração (0.0 a 1.0)
        limite_config: Configuração dos limites
        
    Returns:
        Dict com status de compliance e detalhes
    """
    limite_max = limite_config.get('limite', 1.0)
    limite_atencao = limite_config.get('limite_atencao', limite_max * 0.8)  # 80% do limite como atenção
    
    # Determinar status
    if valor > limite_max:
        status = "VIOLACAO"
        severidade = "critica"
        mensagem = f"Concentração de {valor:.2%} excede limite de {limite_max:.2%}"
        acoes = [
            "Reduzir exposição imediatamente",
            "Avaliar impacto no pool",
            "Considerar acionamento de triggers"
        ]
    elif valor > limite_atencao:
        status = "ATENCAO"
        severidade = "alta"
        mensagem = f"Concentração de {valor:.2%} próxima ao limite de {limite_max:.2%}"
        acoes = [
            "Monitorar proximamente",
            "Evitar novas aquisições desta entidade",
            "Preparar plano de redução"
        ]
    else:
        status = "OK"
        severidade = "baixa"
        mensagem = f"Concentração de {valor:.2%} dentro do limite de {limite_max:.2%}"
        acoes = ["Continuar monitoramento normal"]
    
    # Calcular margens
    margem_disponivel = max(0, limite_max - valor)
    margem_atencao = max(0, limite_atencao - valor)
    
    return {
        "status": status,
        "severidade": severidade,
        "mensagem": mensagem,
        "valor_atual": valor,
        "limite_maximo": limite_max,
        "limite_atencao": limite_atencao,
        "margem_disponivel": margem_disponivel,
        "margem_atencao": margem_atencao,
        "acoes_recomendadas": acoes,
        "em_violacao": valor > limite_max,
        "requer_atencao": valor > limite_atencao
    }


def gerar_resultado(concentracoes: Dict[str, Any], tabela_analise: List[Dict], 
                   config: Dict[str, Any], pool_id: str, base_calculo: float) -> Dict[str, Any]:
    """
    Gera resultado padronizado para monitoramento de concentração.
    
    Args:
        concentracoes: Dict com todas as concentrações calculadas
        tabela_analise: Tabela de análise detalhada
        config: Configuração do pool
        pool_id: ID do pool
        base_calculo: Valor base utilizado
        
    Returns:
        Dict com resultado padronizado JSON
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
    
    # Gerar recomendações
    recomendacoes = []
    if violacoes:
        recomendacoes.append("Reduzir exposições que violam limites")
        recomendacoes.append("Revisar estratégia de aquisição")
        recomendacoes.append("Considerar acionamento de triggers")
    elif status_geral == "ATENCAO":
        recomendacoes.append("Monitorar exposições próximas aos limites")
        recomendacoes.append("Evitar novas aquisições de entidades em atenção")
    else:
        recomendacoes.append("Continuar monitoramento normal")
    
    # Calcular estatísticas
    total_entidades = len(tabela_analise)
    entidades_violacao = len([item for item in tabela_analise if item['status'] == 'VIOLACAO'])
    entidades_atencao = len([item for item in tabela_analise if item['status'] == 'ATENCAO'])
    entidades_ok = len([item for item in tabela_analise if item['status'] == 'OK'])
    
    return {
        "pool_id": pool_id,
        "tipo_monitoramento": "concentracao",
        "timestamp": datetime.now().isoformat(),
        "status_geral": status_geral,
        "severidade": severidade,
        "base_calculo": {
            "tipo": "pl_total",  # Para AFA será "carteira"
            "valor": float(base_calculo)
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
            "versao_monitor": "1.0",
            "base_dados": "xlsx_carteira",
            "configuracao": config.get('pool_id', 'desconhecido')
        }
    }


def executar_monitoramento(df_xlsx: pd.DataFrame, csv_data: Dict, config: Dict[str, Any], 
                          pool_id: str) -> Dict[str, Any]:
    """
    Executa monitoramento completo de concentração para um pool.
    
    Args:
        df_xlsx: DataFrame com dados da carteira
        csv_data: Dados do CSV dashboard
        config: Configuração do pool (JSON)
        pool_id: ID do pool a ser monitorado
        
    Returns:
        Dict com resultados de todos os monitores de concentração
    """
    try:
        log_alerta({"tipo": "info", "mensagem": f"Iniciando monitoramento de concentração para {pool_id}"})
        
        # Validar dados de entrada
        if not validar_dados(df_xlsx, config):
            return {
                "pool_id": pool_id,
                "status": "ERRO",
                "mensagem": "Dados inválidos para monitoramento",
                "timestamp": datetime.now().isoformat()
            }
        
        # Obter base de cálculo (PL total do CSV)
        base_calculo = csv_data.get('pl_total', 0)
        if base_calculo <= 0:
            log_alerta({"tipo": "error", "mensagem": f"Base de cálculo inválida: {base_calculo}"})
            return {
                "pool_id": pool_id,
                "status": "ERRO",
                "mensagem": "Base de cálculo inválida",
                "timestamp": datetime.now().isoformat()
            }
        
        # Obter configuração de concentração
        concentracao_config = None
        for monitor in config.get('monitoramentos_ativos', []):
            if monitor.get('tipo') == 'concentracao':
                concentracao_config = monitor
                break
        
        if not concentracao_config:
            log_alerta({"tipo": "warning", "mensagem": "Configuração de concentração não encontrada"})
            return {
                "pool_id": pool_id,
                "status": "ERRO",
                "mensagem": "Configuração de concentração ausente",
                "timestamp": datetime.now().isoformat()
            }
        
        limites_config = concentracao_config.get('limites', [])
        
        # Executar cálculos de concentração
        resultado_concentracoes = {}
        
        # 1. Concentração individual
        resultado_individual = calcular_concentracao_individual(
            df_xlsx, base_calculo, limites_config
        )
        resultado_concentracoes['individual'] = resultado_individual
        
        # 2. Concentração top N
        resultado_top_n = calcular_concentracao_top_n(
            df_xlsx, base_calculo, limites_config
        )
        resultado_concentracoes['top_n'] = resultado_top_n
        
        # 3. Gerar tabela de análise
        tabela_analise = gerar_tabela_analise_concentracao(
            df_xlsx, base_calculo, limites_config
        )
        
        # 4. Gerar resultado final
        resultado_final = gerar_resultado(
            resultado_concentracoes, tabela_analise, config, pool_id, base_calculo
        )
        
        # Log do resultado
        total_violacoes = len(resultado_final.get('violacoes', []))
        log_alerta({
            "tipo": "info",
            "mensagem": f"Monitoramento de concentração concluído: {pool_id} - {total_violacoes} violações"
        })
        
        return resultado_final
        
    except Exception as e:
        log_alerta({"tipo": "error", "mensagem": f"Erro no monitoramento de concentração: {str(e)}"})
        return {
            "pool_id": pool_id,
            "status": "ERRO",
            "mensagem": f"Erro durante execução: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Exemplo de uso - teste básico
    print("Monitor de Concentração - Versão Base")
    print("Uso: Integrar com sistema de carregamento de dados")
    print("Exemplo:")
    print("from monitor.utils.data_loader import load_pool_data")
    print("from monitor.base.monitor_concentracao import executar_monitoramento")
    print("")
    print("# Carregar dados")
    print("data = load_pool_data()")
    print("pool_data = data['pools']['LeCapital Pool #1']")
    print("")
    print("# Executar monitoramento")
    print("resultado = executar_monitoramento(")
    print("    pool_data['xlsx_df'],")
    print("    pool_data['csv_data'],")
    print("    pool_data['config'],")
    print("    'LeCapital Pool #1'")
    print(")")
    print("")
    print("print(json.dumps(resultado, indent=2, ensure_ascii=False))")