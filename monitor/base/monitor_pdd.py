"""
Monitor de PDD (Provisão para Devedores Duvidosos)
==================================================

Responsável por:
- Cálculo de provisões PDD baseado na LÓGICA POR CEDENTE
- Identificação do ativo mais atrasado por cedente
- Aplicação do grupo de risco do pior ativo a TODAS as operações do cedente
- Análise consolidada e comparativa de provisões

LÓGICA CRÍTICA POR CEDENTE:
===========================

REGRA FUNDAMENTAL: PDD é calculado por cedente, não por título individual.

Processo:
1. Para cada cedente: identifica o ativo mais atrasado (pior grupo de risco)
2. Aplica esse grupo de risco a TODAS as operações do mesmo cedente
3. Inclusive operações em dia recebem provisão do grupo mais alto do cedente

Exemplo:
- Cedente XYZ tem:
  - Título A: 0 dias atraso → Grupo AA (0% provisão) 
  - Título B: 10 dias atraso → Grupo A (0.5% provisão)
  - Título C: 95 dias atraso → Grupo G (70% provisão) ← PIOR ATIVO
- RESULTADO: TODOS os títulos do Cedente XYZ recebem 70% provisão

ARQUITETURA INTELIGENTE:
========================

Este monitor implementa separação de responsabilidades mantendo eficiência:
- DEPENDE do enriquecimento feito pelo monitor de inadimplência
- REUTILIZA campos 'dias_atraso' e 'grupo_de_risco' já calculados
- EVITA duplicação de processamento de 79k+ registros
- IMPLEMENTA lógica PDD correta por cedente

Integração com Orquestrador:
----------------------------
```python
# Ordem de execução garantida pelo orchestrator:
if _has_delinquency_monitoring(config):
    xlsx_enriched = run_delinquency_monitoring()  # 1º: Enriquece dados
    
if _has_pdd_monitoring(config):
    pdd_result = run_pdd_monitoring(xlsx_enriched, config)  # 2º: Lógica por cedente
```

Campos Utilizados do DataFrame Enriquecido:
--------------------------------------------
- 'nome_do_cedente': str - OBRIGATÓRIO para agrupamento por cedente
- 'dias_atraso': int - Calculado pelo monitor de inadimplência
- 'grupo_de_risco': str - Classificação AA-H individual
- 'valor_presente': float - Valor do título para cálculo de provisão

Vantagens da Arquitetura:
-------------------------
✅ Lógica Correta: PDD por cedente conforme regras financeiras
✅ Performance: Zero duplicação de processamento
✅ Transparência: Análise comparativa vs cálculo individual
✅ Auditoria: Detalhamento por cedente disponível
✅ Compliance: Metodologia alinhada com normas contábeis

Cálculo de PDD (Correção 2025-07-14):
-------------------------------------
1. Agrupar títulos por cedente
2. Para cada cedente: identificar grupo_de_risco MÁXIMO (pior ativo)
3. Aplicar esse grupo a TODAS as operações do cedente
4. Provisão = Σ (valor_presente × percentual_provisao_grupo_cedente)

Fontes de Dados:
---------------
1. XLSX Enriquecido (vem do monitor de inadimplência):
   - nome_do_cedente: Identificação do cedente (obrigatório)
   - grupo_de_risco: Classificação AA-H individual
   - valor_presente: Valor do título

2. JSON Config:
   - provisoes_pdd.grupos_risco: Configuração de percentuais por grupo
   - Percentuais em decimal (ex: 0.70 = 70%)
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np


def _find_pdd_monitors(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Busca todos os monitores de PDD no JSON de configuração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Lista com configurações dos monitores de PDD
    """
    if 'monitoramentos_ativos' not in config:
        raise ValueError("Configuração não contém 'monitoramentos_ativos'")
        
    monitores = []
    for monitor in config['monitoramentos_ativos']:
        if monitor.get('tipo') == 'provisao' and monitor.get('ativo', False):
            monitores.append(monitor)
    
    return monitores


def _find_pdd_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Busca configuração de grupos de risco PDD no JSON.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com grupos de risco e percentuais de provisão
    """
    if 'provisoes_pdd' not in config:
        return {}
    
    return config['provisoes_pdd'].get('grupos_risco', {})


def validate_enriched_data(xlsx_df: pd.DataFrame, config: Dict[str, Any]) -> bool:
    """
    Valida se os dados enriquecidos estão adequados para cálculo de PDD.
    
    Args:
        xlsx_df: DataFrame enriquecido (deve ter campos calculados pelo monitor de inadimplência)
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se dados são válidos
        
    Raises:
        ValueError: Se dados essenciais estão ausentes
    """
    # Verificar se há dados
    if xlsx_df.empty:
        raise ValueError("DataFrame XLSX enriquecido está vazio")
    
    # Verificar se há monitores de PDD ativos
    monitores = _find_pdd_monitors(config)
    if not monitores:
        raise ValueError("Nenhum monitor de PDD ativo encontrado")
    
    # Verificar se dados foram enriquecidos pelo monitor de inadimplência
    campos_obrigatorios_enriquecidos = ['dias_atraso', 'grupo_de_risco', 'valor_presente', 'nome_do_cedente']
    for campo in campos_obrigatorios_enriquecidos:
        if campo not in xlsx_df.columns:
            raise ValueError(f"Campo obrigatório '{campo}' ausente. {campo} é necessário para cálculo PDD por cedente.")
    
    # Verificar se configuração PDD existe
    pdd_config = _find_pdd_config(config)
    if not pdd_config:
        raise ValueError("Configuração 'provisoes_pdd.grupos_risco' não encontrada no JSON")
    
    # Verificar se grupos de risco estão válidos
    grupos_validos = set(pdd_config.keys())
    grupos_nos_dados = set(xlsx_df['grupo_de_risco'].unique())
    grupos_invalidos = grupos_nos_dados - grupos_validos
    
    if grupos_invalidos:
        raise ValueError(f"Grupos de risco inválidos nos dados: {grupos_invalidos}. Válidos: {grupos_validos}")
    
    # Verificar se valores_presente são numéricos
    if not pd.api.types.is_numeric_dtype(xlsx_df['valor_presente']):
        raise ValueError("Coluna 'valor_presente' não é numérica")
    
    return True


def calculate_pdd_provisions(xlsx_df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula provisões PDD baseado na LÓGICA POR CEDENTE.
    
    REGRA CRÍTICA: PDD é calculado por cedente, não por título individual.
    - Para cada cedente: identifica o ativo mais atrasado (pior grupo de risco)
    - Aplica esse grupo de risco a TODAS as operações do mesmo cedente
    - Inclusive operações em dia recebem provisão do grupo mais alto do cedente
    
    Args:
        xlsx_df: DataFrame enriquecido com 'grupo_de_risco' calculado
        config: Configuração do pool com grupos de PDD
        
    Returns:
        Dict com análise completa de PDD por grupo (baseado na lógica por cedente)
    """
    grupos_risco = _find_pdd_config(config)
    if not grupos_risco:
        return {"erro": "Configuração de PDD não encontrada"}
    
    # Verificar se coluna 'nome_do_cedente' existe
    if 'nome_do_cedente' not in xlsx_df.columns:
        return {"erro": "Coluna 'nome_do_cedente' não encontrada. PDD requer dados por cedente."}
    
    df = xlsx_df.copy()
    
    # LÓGICA CORRETA POR CEDENTE
    # 1. Para cada cedente, identificar o MAIOR ATRASO (título mais atrasado)
    def get_grupo_from_dias_atraso(dias_atraso):
        """Classifica grupo de risco baseado em dias de atraso"""
        for grupo, params in sorted(grupos_risco.items(), key=lambda x: x[1]['atraso_max_dias']):
            if dias_atraso <= params['atraso_max_dias']:
                return grupo
        return 'H'  # Grupo mais alto por default
    
    # Agrupar por cedente e encontrar o MAIOR ATRASO (não grupo máximo)
    cedente_max_atraso = df.groupby('nome_do_cedente')['dias_atraso'].max().reset_index()
    cedente_max_atraso['grupo_pdd_cedente'] = cedente_max_atraso['dias_atraso'].apply(get_grupo_from_dias_atraso)
    
    # Mapear de volta para o DataFrame principal
    df = df.merge(
        cedente_max_atraso[['nome_do_cedente', 'grupo_pdd_cedente']], 
        on='nome_do_cedente', 
        how='left'
    )
    
    # DEBUG: Análise condensada por cedente (pode ser removido em produção)
    cedentes_com_pdd = cedente_max_atraso[cedente_max_atraso['dias_atraso'] > 0]
    if len(cedentes_com_pdd) > 0:
        print(f"✅ PDD aplicada a {len(cedentes_com_pdd)} cedentes com atraso (de {len(cedente_max_atraso)} total)")
    
    # Calcular provisão usando o grupo PDD do cedente (não do título individual)
    df['provisao_pct'] = df['grupo_pdd_cedente'].map(
        {g: v['provisao_pct'] for g, v in grupos_risco.items()}
    )
    df['provisao_valor'] = df['valor_presente'] * df['provisao_pct']
    
    # Análise por grupo PDD (baseado no grupo aplicado por cedente)
    analise_grupos = {}
    for grupo in sorted(grupos_risco.keys()):
        # Usar grupo_pdd_cedente (não grupo_de_risco individual)
        titulos_grupo = df[df['grupo_pdd_cedente'] == grupo]
        
        if len(titulos_grupo) > 0:
            analise_grupos[grupo] = {
                "quantidade": len(titulos_grupo),
                "valor_total": round(float(titulos_grupo['valor_presente'].sum()), 2),
                "provisao_pct": grupos_risco[grupo]['provisao_pct'] * 100,
                "provisao_valor": round(float(titulos_grupo['provisao_valor'].sum()), 2),
                "atraso_max_dias": grupos_risco[grupo]['atraso_max_dias'],
                "cedentes_afetados": len(titulos_grupo['nome_do_cedente'].unique())
            }
        else:
            # Grupo sem títulos
            analise_grupos[grupo] = {
                "quantidade": 0,
                "valor_total": 0.0,
                "provisao_pct": grupos_risco[grupo]['provisao_pct'] * 100,
                "provisao_valor": 0.0,
                "atraso_max_dias": grupos_risco[grupo]['atraso_max_dias'],
                "cedentes_afetados": 0
            }
    
    # Totais consolidados
    total_carteira = df['valor_presente'].sum()
    total_provisao = df['provisao_valor'].sum()
    
    # Estatísticas adicionais (baseadas na lógica por cedente)
    estatisticas = {
        "titulos_total": len(df),
        "titulos_com_provisao": len(df[df['provisao_valor'] > 0]),
        "cedentes_total": len(df['nome_do_cedente'].unique()),
        "cedentes_com_provisao": len(df[df['provisao_valor'] > 0]['nome_do_cedente'].unique()),
        "grupo_pdd_modal": df['grupo_pdd_cedente'].mode().iloc[0] if len(df) > 0 else None,
        "provisao_media_por_titulo": round(float(total_provisao / len(df)) if len(df) > 0 else 0, 2),
        "provisao_media_por_cedente": round(float(total_provisao / len(df['nome_do_cedente'].unique())) if len(df['nome_do_cedente'].unique()) > 0 else 0, 2)
    }
    
    # Análise comparativa: mostrar diferença vs cálculo individual
    df_individual = df.copy()
    df_individual['provisao_individual'] = df_individual['grupo_de_risco'].map(
        {g: v['provisao_pct'] for g, v in grupos_risco.items()}
    ) * df_individual['valor_presente']
    
    total_provisao_individual = df_individual['provisao_individual'].sum()
    diferenca_metodologia = total_provisao - total_provisao_individual
    
    estatisticas.update({
        "comparacao_vs_individual": {
            "provisao_por_cedente": round(float(total_provisao), 2),
            "provisao_individual": round(float(total_provisao_individual), 2),
            "diferenca_valor": round(float(diferenca_metodologia), 2),
            "diferenca_percentual": round(float(diferenca_metodologia / total_provisao_individual * 100) if total_provisao_individual > 0 else 0, 2)
        }
    })
    
    return {
        "grupos": analise_grupos,
        "totais": {
            "carteira_valor": round(float(total_carteira), 2),
            "provisao_valor": round(float(total_provisao), 2),
            "provisao_percentual": round((total_provisao / total_carteira * 100) if total_carteira > 0 else 0, 2)
        },
        "estatisticas": estatisticas
    }


def generate_cedente_analysis(xlsx_df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera análise detalhada por cedente mostrando como a lógica PDD funciona.
    
    Args:
        xlsx_df: DataFrame enriquecido com campos calculados
        config: Configuração do pool
        
    Returns:
        Dict com análise detalhada por cedente
    """
    grupos_risco = _find_pdd_config(config)
    if not grupos_risco:
        return {"erro": "Configuração de PDD não encontrada"}
    
    if 'nome_do_cedente' not in xlsx_df.columns:
        return {"erro": "Coluna 'nome_do_cedente' não encontrada"}
    
    df = xlsx_df.copy()
    
    # Mapear grupos para ordem
    def map_grupo_to_order(grupo):
        ordem = {'AA': 0, 'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}
        return ordem.get(grupo, 0)
    
    def map_order_to_grupo(ordem):
        grupos = ['AA', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        return grupos[min(ordem, len(grupos)-1)]
    
    df['grupo_ordem'] = df['grupo_de_risco'].apply(map_grupo_to_order)
    
    # Análise por cedente (usar mesma lógica da função principal)
    def get_grupo_from_dias_atraso_local(dias_atraso):
        """Classifica grupo de risco baseado em dias de atraso"""
        for grupo, params in sorted(grupos_risco.items(), key=lambda x: x[1]['atraso_max_dias']):
            if dias_atraso <= params['atraso_max_dias']:
                return grupo
        return 'H'
    
    analise_cedentes = {}
    
    for cedente in df['nome_do_cedente'].unique():
        if pd.isna(cedente) or cedente == '':
            continue
            
        titulos_cedente = df[df['nome_do_cedente'] == cedente].copy()
        
        # Identificar maior atraso (usar mesma lógica corrigida)
        max_atraso_cedente = titulos_cedente['dias_atraso'].max()
        grupo_pdd = get_grupo_from_dias_atraso_local(max_atraso_cedente)
        
        # Título mais atrasado (baseado em dias_atraso, não grupo_ordem)
        idx_mais_atrasado = titulos_cedente['dias_atraso'].idxmax()
        titulo_mais_atrasado = titulos_cedente.loc[idx_mais_atrasado]
        
        # Estatísticas do cedente
        total_valor = titulos_cedente['valor_presente'].sum()
        provisao_pct = grupos_risco[grupo_pdd]['provisao_pct']
        provisao_valor = total_valor * provisao_pct
        
        # Distribuição por grupo original (antes da aplicação PDD)
        distribuicao_original = titulos_cedente['grupo_de_risco'].value_counts().to_dict()
        
        analise_cedentes[cedente] = {
            "total_titulos": len(titulos_cedente),
            "valor_total": round(float(total_valor), 2),
            "grupo_pdd_aplicado": grupo_pdd,
            "provisao_pct": provisao_pct * 100,
            "provisao_valor": round(float(provisao_valor), 2),
            "titulo_mais_atrasado": {
                "dias_atraso": int(titulo_mais_atrasado['dias_atraso']),
                "data_vencimento": titulo_mais_atrasado['vencimento_original'].strftime('%Y-%m-%d') if pd.notna(titulo_mais_atrasado['vencimento_original']) else None,
                "grupo_original": titulo_mais_atrasado['grupo_de_risco'],
                "valor": round(float(titulo_mais_atrasado['valor_presente']), 2),
                "sacado": titulo_mais_atrasado.get('sacado', 'N/A'),
                "status": titulo_mais_atrasado.get('status', 'N/A')
            },
            "distribuicao_grupos_originais": distribuicao_original
        }
    
    return {
        "total_cedentes": len(analise_cedentes),
        "cedentes": analise_cedentes
    }


def run_pdd_monitoring(
    carteira_xlsx: pd.DataFrame,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Interface principal para o orquestrador - Monitor de PDD.
    
    REQUISITO: DataFrame deve estar enriquecido pelo monitor de inadimplência.
    
    Args:
        carteira_xlsx: DataFrame enriquecido com campos calculados (dias_atraso, grupo_de_risco)
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com resultados completos de análise PDD
        
    Note:
        Este monitor DEPENDE do enriquecimento feito pelo monitor de inadimplência.
        Execute monitor de inadimplência primeiro para garantir dados corretos.
    """
    try:
        # Validar dados enriquecidos de entrada
        validate_enriched_data(carteira_xlsx, config)
        
        # Resultado base
        resultado = {
            "sucesso": True,
            "monitor": "pdd",
            "pool_id": config.get('pool_id', 'desconhecido'),
            "data_analise": datetime.now().isoformat(),
            "dependencias": {
                "monitor_inadimplencia": "OK - Dados enriquecidos presentes",
                "campos_utilizados": ["dias_atraso", "grupo_de_risco", "valor_presente"]
            }
        }
        
        # Calcular provisões PDD (lógica por cedente)
        analise_pdd = calculate_pdd_provisions(carteira_xlsx, config)
        
        # Verificar se houve erro no cálculo
        if "erro" in analise_pdd:
            return {
                "sucesso": False,
                "monitor": "pdd",
                "erro": analise_pdd["erro"],
                "tipo_erro": "ConfiguracaoInvalida"
            }
        
        # Gerar análise detalhada por cedente
        analise_cedentes = generate_cedente_analysis(carteira_xlsx, config)
        
        # Consolidar resultados
        resultado.update({
            "pdd_analysis": analise_pdd,
            "cedente_analysis": analise_cedentes,
            "metodologia": {
                "calculo": "por_cedente",
                "regra": "Provisão baseada no ativo mais atrasado de cada cedente",
                "explicacao": "Todas as operações do cedente recebem a provisão do grupo mais alto (pior ativo)"
            },
            "compliance": {
                "grupos_configurados": len(_find_pdd_config(config)),
                "grupos_com_exposicao": len([g for g in analise_pdd["grupos"].values() if g["quantidade"] > 0]),
                "provisao_total_percentual": analise_pdd["totais"]["provisao_percentual"]
            }
        })
        
        return resultado
        
    except Exception as e:
        return {
            "sucesso": False,
            "monitor": "pdd",
            "erro": str(e),
            "tipo_erro": type(e).__name__
        }


def _has_pdd_monitoring(config: Dict[str, Any]) -> bool:
    """
    Verifica se monitores de PDD estão ativos no JSON de configuração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se há pelo menos um monitor PDD ativo
    """
    try:
        monitors = _find_pdd_monitors(config)
        return len(monitors) > 0
    except ValueError:
        return False


if __name__ == "__main__":
    # Exemplo de uso para testes
    print("Monitor de PDD carregado com sucesso")
    print("Use run_pdd_monitoring() como interface principal")
    print("IMPORTANTE: Execute monitor de inadimplência primeiro para enriquecer dados")