"""
Manipulador de Dados e Validações
=================================

Responsável por:
- Validar consistência entre diferentes fontes de dados
- Gerar alertas estruturados para inconsistências
- Verificar integridade temporal dos dados
- Validar dados carregados por pool
- Gerar metadados de carregamento
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import json
import os

# Sistema de imports compatível com Spyder e outros ambientes
import sys
import os

# Tentar imports relativos primeiro
try:
    from .alerts import log_alerta
except (ImportError, ValueError):
    # Fallback para imports diretos (Spyder)
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from alerts import log_alerta


def validar_data_d1(data_arquivo: datetime) -> Dict:
    """
    Verifica se arquivo é de D-1 (ontem).
    
    Args:
        data_arquivo: Data do arquivo
        
    Returns:
        Dict com resultado da validação e detalhes
    """
    # Calcular data de ontem
    hoje = datetime.now().date()
    ontem = hoje - timedelta(days=1)
    
    # Comparar com data do arquivo
    data_arquivo_date = data_arquivo.date() if isinstance(data_arquivo, datetime) else data_arquivo
    
    # Calcular diferença em dias
    diferenca = (hoje - data_arquivo_date).days
    
    # Determinar se é D-1
    is_d1 = data_arquivo_date == ontem
    
    return {
        "is_d1": is_d1,
        "data_arquivo": data_arquivo_date.strftime("%Y-%m-%d"),
        "data_esperada": ontem.strftime("%Y-%m-%d"),
        "diferenca_dias": diferenca,
        "tipo": "futuro" if diferenca < 0 else "passado" if diferenca > 1 else "correto"
    }


def date_check_alert(csv_date: datetime, xlsx_date: datetime) -> Dict:
    """
    Gera alerta quando datas entre CSV e XLSX não coincidem.
    
    Args:
        csv_date: Data do arquivo CSV
        xlsx_date: Data do arquivo XLSX
        
    Returns:
        Dict com estrutura de alerta padronizada
    """
    from datetime import timedelta
    
    # Calcular diferença entre datas
    if csv_date and xlsx_date:
        diferenca = abs((csv_date - xlsx_date).days)
        
        # Determinar severidade baseada na diferença
        if diferenca == 0:
            # Não deveria gerar alerta, mas por segurança
            severidade = "info"
            mensagem = "Datas dos arquivos CSV e XLSX são idênticas"
        elif diferenca <= 1:
            severidade = "warning"
            mensagem = f"Datas dos arquivos diferem em {diferenca} dia(s)"
        elif diferenca <= 3:
            severidade = "error"
            mensagem = f"Datas dos arquivos diferem em {diferenca} dias - possível inconsistência"
        else:
            severidade = "critical"
            mensagem = f"Datas dos arquivos muito diferentes: {diferenca} dias de diferença"
        
        # Formatar datas para exibição
        csv_str = csv_date.strftime("%d/%m/%Y") if csv_date else "N/A"
        xlsx_str = xlsx_date.strftime("%d/%m/%Y") if xlsx_date else "N/A"
        
        detalhes = {
            "data_csv": csv_str,
            "data_xlsx": xlsx_str,
            "diferenca_dias": diferenca,
            "impacto": "Pode afetar a consistência dos cálculos de monitoramento"
        }
        
        acoes_recomendadas = [
            "Verificar se os arquivos são da mesma data de processamento",
            "Confirmar se deseja continuar com dados inconsistentes",
            "Buscar arquivos da mesma data se disponíveis"
        ]
        
    else:
        # Uma das datas é None
        severidade = "error"
        csv_str = csv_date.strftime("%d/%m/%Y") if csv_date else "N/A"
        xlsx_str = xlsx_date.strftime("%d/%m/%Y") if xlsx_date else "N/A"
        mensagem = "Não foi possível determinar a data de um dos arquivos"
        
        detalhes = {
            "data_csv": csv_str,
            "data_xlsx": xlsx_str,
            "diferenca_dias": None,
            "impacto": "Impossível validar consistência temporal"
        }
        
        acoes_recomendadas = [
            "Verificar se os arquivos existem e são válidos",
            "Verificar permissões de acesso aos arquivos"
        ]
    
    return {
        "tipo": "inconsistencia_data",
        "severidade": severidade,
        "mensagem": mensagem,
        "detalhes": detalhes,
        "acoes_recomendadas": acoes_recomendadas,
        "timestamp": datetime.now().isoformat(),
        "requer_confirmacao": severidade in ["error", "critical"]
    }


def gerar_alerta_nao_d1(data_arquivo: datetime, diferenca_dias: int) -> Dict:
    """
    Gera alerta quando arquivo não é de D-1.
    
    Args:
        data_arquivo: Data do arquivo
        diferenca_dias: Diferença em dias vs D-1
        
    Returns:
        Dict com estrutura de alerta padronizada
    """
    # Determinar se é futuro ou passado
    tipo_temporal = "futuro" if diferenca_dias < 0 else "passado"
    
    # Calcular severidade baseada na diferença
    abs_diferenca = abs(diferenca_dias)
    if abs_diferenca == 0:
        severidade = "info"
    elif abs_diferenca == 1:
        severidade = "info" if tipo_temporal == "passado" else "warning"
    elif abs_diferenca <= 3:
        severidade = "warning"
    else:
        severidade = "error"
    
    # Gerar mensagem apropriada
    if tipo_temporal == "futuro":
        mensagem = f"Arquivo com data futura ({abs_diferenca} dias no futuro)"
    else:
        mensagem = f"Arquivo desatualizado ({abs_diferenca} dias no passado)"
    
    # Incluir impacto no monitoramento
    impactos = {
        "info": "Dados podem estar levemente desatualizados",
        "warning": "Monitoramento pode não refletir situação atual",
        "error": "Dados muito antigos, resultados não confiáveis"
    }
    
    return {
        "tipo": "data_nao_d1",
        "severidade": severidade,
        "mensagem": mensagem,
        "detalhes": {
            "data_arquivo": data_arquivo.strftime("%Y-%m-%d") if hasattr(data_arquivo, 'strftime') else str(data_arquivo),
            "diferenca_dias": diferenca_dias,
            "tipo_temporal": tipo_temporal
        },
        "impacto": impactos.get(severidade, "Impacto indeterminado"),
        "timestamp": datetime.now().isoformat()
    }


def validar_integridade_temporal(arquivo_info: Dict) -> Dict:
    """
    Valida integridade temporal do arquivo.
    
    Args:
        arquivo_info: Informações do arquivo
        
    Returns:
        Dict com resultado da validação temporal
    """
    # TODO: Verificar se data é válida
    # TODO: Verificar se não é fim de semana
    # TODO: Verificar se não é feriado
    # TODO: Validar horário de geração
    pass


def validar_sequencia_temporal(arquivos: List[Dict]) -> Dict:
    """
    Valida se há gaps na sequência temporal de arquivos.
    
    Args:
        arquivos: Lista de arquivos ordenados por data
        
    Returns:
        Dict com resultado da validação de sequência
    """
    # TODO: Verificar gaps entre datas
    # TODO: Identificar dias úteis faltantes
    # TODO: Detectar duplicatas de data
    # TODO: Calcular completude da série
    pass


def validar_horario_geracao(data_arquivo: datetime) -> Dict:
    """
    Valida se arquivo foi gerado em horário apropriado.
    
    Args:
        data_arquivo: Data e hora do arquivo
        
    Returns:
        Dict com resultado da validação de horário
    """
    # TODO: Verificar horário comercial
    # TODO: Validar fuso horário
    # TODO: Verificar padrão de geração
    # TODO: Detectar anomalias de horário
    pass


def comparar_datas_multiplas(datas: List[datetime]) -> Dict:
    """
    Compara múltiplas datas e identifica inconsistências.
    
    Args:
        datas: Lista de datas para comparar
        
    Returns:
        Dict com resultado da comparação
    """
    # TODO: Encontrar data mais comum
    # TODO: Identificar outliers
    # TODO: Calcular dispersão
    # TODO: Gerar resumo das diferenças
    pass


def validar_data_limite(data_arquivo: datetime, limite_dias: int) -> Dict:
    """
    Valida se arquivo não é mais antigo que limite permitido.
    
    Args:
        data_arquivo: Data do arquivo
        limite_dias: Limite máximo de dias no passado
        
    Returns:
        Dict com resultado da validação
    """
    # TODO: Calcular data limite
    # TODO: Comparar com data do arquivo
    # TODO: Determinar se está dentro do limite
    # TODO: Gerar alerta se necessário
    pass


def calcular_frescor_dados(data_arquivo: datetime) -> Dict:
    """
    Calcula o "frescor" dos dados (quão atuais são).
    
    Args:
        data_arquivo: Data do arquivo
        
    Returns:
        Dict com métricas de frescor
    """
    # TODO: Calcular idade dos dados
    # TODO: Classificar nível de frescor
    # TODO: Determinar impacto na confiabilidade
    # TODO: Gerar score de qualidade temporal
    pass


def data_validation(csv_df: pd.DataFrame, xlsx_df: pd.DataFrame) -> bool:
    """
    Valida e converte tipos de dados corretamente.
    Converte datas para datetime e números para numeric, preservando células vazias.
    
    Args:
        csv_df: DataFrame do CSV
        xlsx_df: DataFrame do XLSX
        
    Returns:
        bool: True se conversões foram bem-sucedidas
    """
    problemas = []
    conversoes_realizadas = []
    
    try:
        # 1. Verificar se DataFrames não estão vazios
        if csv_df.empty:
            problemas.append("CSV está vazio")
        
        if xlsx_df.empty:
            problemas.append("XLSX está vazio")
        
        # 2. Converter tipos de dados no CSV (apenas datas restantes)
        if not csv_df.empty:
            for coluna in csv_df.columns:
                tipo_original = str(csv_df[coluna].dtype)
                
                # Tentar converter colunas que parecem datas (restantes)
                if any(palavra in coluna.lower() for palavra in ['prazo']):
                    try:
                        csv_df[coluna] = pd.to_datetime(csv_df[coluna], errors='coerce', dayfirst=True)
                        conversoes_realizadas.append(f"CSV.{coluna}: {tipo_original} → datetime")
                    except Exception as e:
                        log_alerta({"tipo": "warning", "mensagem": f"Erro ao converter CSV.{coluna} para data: {str(e)}"})
        
        # 3. Converter tipos de dados no XLSX
        if not xlsx_df.empty:
            for coluna in xlsx_df.columns:
                tipo_original = str(xlsx_df[coluna].dtype)
                
                # Tentar converter colunas que parecem datas
                if any(palavra in coluna.lower() for palavra in ['data', 'date', 'vencimento', 'prazo']):
                    try:
                        xlsx_df[coluna] = pd.to_datetime(xlsx_df[coluna], errors='coerce', dayfirst=True)
                        conversoes_realizadas.append(f"XLSX.{coluna}: {tipo_original} → datetime")
                    except Exception as e:
                        log_alerta({"tipo": "warning", "mensagem": f"Erro ao converter XLSX.{coluna} para data: {str(e)}"})
                
                # Tentar converter colunas que parecem numéricas
                elif any(palavra in coluna.lower() for palavra in ['valor', 'pl', 'sr', 'jr', 'is', 'percentual', 'taxa', 'montante', 'saldo', 'presente']):
                    try:
                        xlsx_df[coluna] = pd.to_numeric(xlsx_df[coluna], errors='coerce')
                        conversoes_realizadas.append(f"XLSX.{coluna}: {tipo_original} → numeric")
                    except Exception as e:
                        log_alerta({"tipo": "warning", "mensagem": f"Erro ao converter XLSX.{coluna} para numérico: {str(e)}"})
        
        # 4. Verificar consistência de datas entre arquivos
        csv_data = csv_df.attrs.get('data_arquivo')
        xlsx_data = xlsx_df.attrs.get('data_arquivo')
        
        if csv_data and xlsx_data:
            diferenca_dias = abs((csv_data - xlsx_data).days)
            if diferenca_dias > 1:
                problemas.append(f"Datas dos arquivos muito diferentes: {diferenca_dias} dias")
        
        # 5. Log das conversões realizadas
        if conversoes_realizadas:
            log_alerta({
                "tipo": "info", 
                "mensagem": f"Conversões de tipo realizadas: {len(conversoes_realizadas)}"
            })
        
        # 6. Retornar resultado
        if problemas:
            log_alerta({
                "tipo": "warning", 
                "mensagem": f"Problemas encontrados na validação: {'; '.join(problemas)}"
            })
            return False
        
        return True
        
    except Exception as e:
        log_alerta({"tipo": "error", "mensagem": f"Erro durante validação de dados: {str(e)}"})
        return False


def gerar_metadados_carregamento(csv_info: Dict, xlsx_info: Dict, alertas: List[Dict]) -> Dict:
    """
    Gera metadados completos do processo de carregamento.
    
    Args:
        csv_info: Informações do arquivo CSV
        xlsx_info: Informações do arquivo XLSX
        alertas: Lista de alertas gerados
        
    Returns:
        Dict com metadados estruturados
    """
    return {
        "timestamp_carregamento": datetime.now().isoformat(),
        "arquivos": {
            "csv": csv_info,
            "xlsx": xlsx_info
        },
        "alertas": {
            "total": len(alertas),
            "por_tipo": {
                "info": len([a for a in alertas if a.get('tipo') == 'info']),
                "warning": len([a for a in alertas if a.get('tipo') == 'warning']),
                "error": len([a for a in alertas if a.get('tipo') == 'error'])
            }
        },
        "qualidade": {
            "arquivos_carregados": 2 if csv_info and xlsx_info else 1 if csv_info or xlsx_info else 0,
            "tem_alertas_criticos": any(a.get('tipo') == 'error' for a in alertas),
            "consistencia_temporal": "ok" if csv_info.get('data') and xlsx_info.get('data') else "desconhecida"
        }
    }


def validar_dados_por_pool(xlsx_df: pd.DataFrame, configs: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Valida dados específicos para cada pool baseado em suas configurações.
    
    Args:
        xlsx_df: DataFrame do XLSX
        configs: Configurações por pool
        
    Returns:
        Dict com validações por pool
    """
    validacoes = {}
    
    for pool_name, config in configs.items():
        try:
            if config is None:
                validacoes[pool_name] = {
                    "status": "erro",
                    "mensagem": "Configuração não encontrada",
                    "detalhes": "Arquivo JSON de configuração não existe ou está inválido",
                    "registros": 0,
                    "validacoes": {}
                }
                continue
            
            # Filtrar dados do pool no XLSX
            if 'Nome' in xlsx_df.columns:
                pool_data = xlsx_df[xlsx_df['Nome'] == pool_name]
            else:
                pool_data = pd.DataFrame()  # Vazio se não tem coluna Nome
            
            # Contar registros
            num_registros = len(pool_data)
            
            # Validações básicas
            validacoes_pool = {
                "tem_dados": num_registros > 0,
                "registros_count": num_registros
            }
            
            # Adicionar validações específicas baseadas na config
            if num_registros > 0:
                # Verificar colunas essenciais
                colunas_essenciais = ['Nome do Sacado', 'Nome do Cedente', 'Valor presente']
                colunas_faltantes = [col for col in colunas_essenciais if col not in pool_data.columns]
                validacoes_pool["colunas_completas"] = len(colunas_faltantes) == 0
                validacoes_pool["colunas_faltantes"] = colunas_faltantes
                
                # Verificar valores nulos em colunas críticas
                if 'Valor presente' in pool_data.columns:
                    valores_nulos = pool_data['Valor presente'].isna().sum()
                    validacoes_pool["valores_presentes_completos"] = valores_nulos == 0
                    validacoes_pool["valores_nulos_count"] = int(valores_nulos)
            
            # Determinar status geral
            if num_registros == 0:
                status = "aviso"
                mensagem = "Pool sem dados no XLSX"
            elif validacoes_pool.get("colunas_completas", False):
                status = "sucesso"
                mensagem = f"Pool validado com {num_registros} registros"
            else:
                status = "aviso"
                mensagem = f"Pool com {num_registros} registros mas colunas incompletas"
            
            validacoes[pool_name] = {
                "status": status,
                "mensagem": mensagem,
                "detalhes": f"Validação baseada em configuração específica do pool",
                "registros": num_registros,
                "validacoes": validacoes_pool
            }
            
        except Exception as e:
            validacoes[pool_name] = {
                "status": "erro",
                "mensagem": f"Erro na validação: {str(e)}",
                "detalhes": "Falha durante processo de validação do pool",
                "registros": 0,
                "validacoes": {}
            }
            
            log_alerta({
                "tipo": "error",
                "mensagem": f"Erro ao validar pool '{pool_name}': {str(e)}"
            })
    
    # Log resumo geral
    total_pools = len(validacoes)
    pools_sucesso = sum(1 for v in validacoes.values() if v['status'] == 'sucesso')
    pools_aviso = sum(1 for v in validacoes.values() if v['status'] == 'aviso')
    pools_erro = sum(1 for v in validacoes.values() if v['status'] == 'erro')
    
    log_alerta({
        "tipo": "info",
        "mensagem": f"Validação concluída: {total_pools} pools - {pools_sucesso} OK, {pools_aviso} avisos, {pools_erro} erros"
    })
    
    return validacoes