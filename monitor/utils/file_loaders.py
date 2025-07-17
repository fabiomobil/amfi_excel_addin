"""
Carregadores de Arquivos
========================

Responsável por:
- Carregar arquivos CSV e XLSX com descoberta automática
- Aplicar conversões de dados automaticamente
- Suportar caminhos múltiplos (Windows/WSL/relativos)
- Gerenciar metadados de arquivos
"""

import pandas as pd
import os
import glob
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Centralized import system - eliminates complex import logic
from ..core.imports import import_function

# Import required functions using centralized system
aplicar_conversoes_csv = import_function('data_converters', 'aplicar_conversoes_csv', 'util')
aplicar_conversoes_xlsx = import_function('data_converters', 'aplicar_conversoes_xlsx', 'util')
normalize_column_name = import_function('data_converters', 'normalize_column_name', 'util')
log_alerta = import_function('alerts', 'log_alerta', 'util')
get_possible_paths = import_function('path_resolver', 'get_possible_paths', 'util')
find_existing_path = import_function('path_resolver', 'find_existing_path', 'util')


# Funções get_possible_paths e find_existing_path agora vêm do path_resolver


def read_csv_raw(arquivo_path: str) -> pd.DataFrame:
    """
    Carrega CSV preservando dados em formato string para evitar conversões incorretas.
    
    Esta função é necessária porque pandas.read_csv() tenta automaticamente converter
    valores que parecem números ou datas, causando problemas com formato brasileiro:
    
    Problemas evitados:
    - "1.234,56" seria interpretado incorretamente (ponto como separador decimal)
    - "01/01/2025" poderia ser convertido com formato americano
    - Zeros à esquerda seriam removidos ("001" → "1")
    - Células vazias seriam preenchidas com NaN
    
    Processo:
    1. Abre arquivo com csv.reader (módulo padrão Python)
    2. Lê linha por linha como strings puras
    3. Garante que todas as linhas tenham mesmo número de colunas
    4. Cria DataFrame mantendo tudo como texto
    5. Conversões são aplicadas depois por data_converters.py
    
    Args:
        arquivo_path: Caminho completo para o arquivo CSV
        
    Returns:
        pd.DataFrame: DataFrame com todos os valores como strings
        
    Example:
        >>> df = read_csv_raw('dados.csv')
        >>> df.dtypes
        Nome     object  # Tudo permanece como string
        Valor    object  # "1.234,56" não vira float
        Data     object  # "01/01/2025" não vira datetime
    """
    dados_brutos = []
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)  # Primeira linha (cabeçalho)
        
        for linha in reader:
            # Garantir que a linha tem o número correto de colunas
            while len(linha) < len(headers):
                linha.append('')
            dados_brutos.append(linha)
    
    # Criar DataFrame manualmente
    df = pd.DataFrame(dados_brutos, columns=headers)
    return df


def load_dashboard(data: str = None, pool: str = None) -> pd.DataFrame:
    """
    Carrega arquivo CSV de dashboard (dados dos pools).
    Por padrão carrega o mais recente, ou data específica se solicitada.
    
    Args:
        data: Data no formato dd/mm/aaaa (opcional)
        pool: Nome do pool para filtrar (opcional)
        
    Returns:
        DataFrame com dados do CSV, com conversões aplicadas
        
    Raises:
        FileNotFoundError: Se arquivo para data específica não for encontrado
    """
    try:
        # Encontrar pasta CSV
        pasta_csv = find_existing_path('csv')
        
        # Escolher arquivo baseado na data ou mais recente
        if data:
            # Converter data e procurar arquivo específico
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            data_arquivo = data_obj.strftime("%Y-%m-%d")
            
            padrao = f"{pasta_csv}/AcompanhamentoDeOportunidades-{data_arquivo}*.csv"
            arquivos = glob.glob(padrao)
            
            if not arquivos:
                raise FileNotFoundError(f"Arquivo CSV não encontrado para data {data} (procurado: {padrao})")
            
            arquivo_escolhido = arquivos[0]
        else:
            # Procurar arquivo mais recente
            padrao = f"{pasta_csv}/AcompanhamentoDeOportunidades-*.csv"
            arquivos = glob.glob(padrao)
            
            if not arquivos:
                raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {pasta_csv}")
            
            arquivo_escolhido = max(arquivos, key=os.path.getmtime)
        
        # Carregar arquivo usando leitura manual
        df = read_csv_raw(arquivo_escolhido)
        
        # Adicionar metadados ao DataFrame
        df.attrs['arquivo'] = arquivo_escolhido
        df.attrs['data_arquivo'] = datetime.fromtimestamp(os.path.getmtime(arquivo_escolhido))
        
        # Aplicar conversões automaticamente
        df = aplicar_conversoes_csv(df)
        
        # Filtrar por pool se especificado (usando nome normalizado)
        if pool:
            if 'nome' in df.columns:
                # Normalizar o nome do pool para comparação
                pool_normalizado = normalizar_nome_coluna(pool)
                df_filtrado = df[df['nome'] == pool_normalizado]
                if df_filtrado.empty:
                    raise ValueError(f"Pool '{pool}' não encontrado no CSV")
                df = df_filtrado
                log_alerta({"tipo": "info", "mensagem": f"CSV filtrado para pool: {pool}"})
            else:
                raise ValueError("Coluna 'nome' não encontrada no CSV para filtrar por pool")
        
        log_alerta({"tipo": "info", "mensagem": f"CSV carregado: {os.path.basename(arquivo_escolhido)} ({len(df)} registros)"})
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao carregar CSV {arquivo_escolhido if 'arquivo_escolhido' in locals() else 'desconhecido'}: {str(e)}")


def load_portfolio(data: str = None, pool: str = None) -> pd.DataFrame:
    """
    Carrega arquivo XLSX de portfolio (carteira detalhada).
    Por padrão carrega o mais recente, ou data específica se solicitada.
    
    Args:
        data: Data no formato dd/mm/aaaa (opcional)
        pool: Nome do pool para filtrar (opcional)
        
    Returns:
        DataFrame com dados do XLSX, com conversões aplicadas
        
    Raises:
        FileNotFoundError: Se arquivo para data específica não for encontrado
    """
    try:
        # Encontrar pasta XLSX
        pasta_xlsx = find_existing_path('xlsx')
        
        # Escolher arquivo baseado na data ou mais recente
        if data:
            # Converter data e procurar arquivo específico
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            data_arquivo = data_obj.strftime("%Y-%m-%d")
            
            padrao = f"{pasta_xlsx}/Carteira Global {data_arquivo}*.xlsx"
            arquivos = glob.glob(padrao)
            
            if not arquivos:
                raise FileNotFoundError(f"Arquivo XLSX não encontrado para data {data} (procurado: {padrao})")
            
            arquivo_escolhido = arquivos[0]
        else:
            # Procurar arquivo mais recente
            padrao = f"{pasta_xlsx}/Carteira Global *.xlsx"
            arquivos = glob.glob(padrao)
            
            if not arquivos:
                raise FileNotFoundError(f"Nenhum arquivo XLSX encontrado em {pasta_xlsx}")
            
            arquivo_escolhido = max(arquivos, key=os.path.getmtime)
        
        # Carregar arquivo
        df = pd.read_excel(arquivo_escolhido, engine='openpyxl')
        
        # Adicionar metadados ao DataFrame
        df.attrs['arquivo'] = arquivo_escolhido
        df.attrs['data_arquivo'] = datetime.fromtimestamp(os.path.getmtime(arquivo_escolhido))
        
        # Aplicar conversões automaticamente
        df = aplicar_conversoes_xlsx(df)
        
        # Ordenar DataFrame por: pool, data de vencimento, cedente, sacado (nomes normalizados)
        colunas_ordenacao = []
        if 'nome' in df.columns:
            colunas_ordenacao.append('nome')  # Pool
        if 'data_de_vencimento_original' in df.columns:
            colunas_ordenacao.append('data_de_vencimento_original')
        elif 'data_de_vencimento' in df.columns:
            colunas_ordenacao.append('data_de_vencimento')
        if 'nome_do_cedente' in df.columns:
            colunas_ordenacao.append('nome_do_cedente')
        if 'nome_do_sacado' in df.columns:
            colunas_ordenacao.append('nome_do_sacado')
        
        if colunas_ordenacao:
            df = df.sort_values(by=colunas_ordenacao, na_position='last')
            log_alerta({"tipo": "info", "mensagem": f"XLSX ordenado por: {', '.join(colunas_ordenacao)}"})
        
        # Filtrar por pool se especificado (usando nome normalizado)
        if pool:
            if 'nome' in df.columns:
                # Normalizar o nome do pool para comparação
                pool_normalizado = normalizar_nome_coluna(pool)
                df_filtrado = df[df['nome'] == pool_normalizado]
                if df_filtrado.empty:
                    raise ValueError(f"Pool '{pool}' não encontrado no XLSX")
                df = df_filtrado
                log_alerta({"tipo": "info", "mensagem": f"XLSX filtrado para pool: {pool}"})
            else:
                raise ValueError("Coluna 'nome' não encontrada no XLSX para filtrar por pool")
        
        log_alerta({"tipo": "info", "mensagem": f"XLSX carregado: {os.path.basename(arquivo_escolhido)} ({len(df)} registros)"})
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao carregar XLSX {arquivo_escolhido if 'arquivo_escolhido' in locals() else 'desconhecido'}: {str(e)}")


def load_json_file(nome_arquivo: str) -> Dict:
    """
    Carrega arquivo JSON usando descoberta automática de caminho.
    
    Esta função combina o sistema de caminhos múltiplos com carregamento de JSON,
    permitindo que arquivos de configuração sejam encontrados automaticamente
    independente do ambiente de execução.
    
    Processo:
    1. Usa get_possible_paths('config', nome_arquivo) para obter variantes
    2. Testa cada caminho até encontrar arquivo existente
    3. Carrega JSON com encoding UTF-8 (suporte a caracteres especiais)
    4. Retorna dicionário Python
    
    Args:
        nome_arquivo: Nome do arquivo JSON (ex: "test_pools.json")
        
    Returns:
        Dict: Conteúdo do arquivo JSON como dicionário Python
        
    Raises:
        FileNotFoundError: Se arquivo não for encontrado em nenhum caminho
        json.JSONDecodeError: Se arquivo não for JSON válido
        
    Example:
        >>> config = load_json_file('test_pools.json')
        >>> config['debug_pools']
        ['AFA Pool #1', 'LeCapital Pool #1']
    """
    import json
    
    possible_paths = get_possible_paths('config', nome_arquivo)
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"Arquivo {nome_arquivo} não encontrado. Tentados: {possible_paths}")


def get_file_metadata(df: pd.DataFrame) -> Dict:
    """
    Extrai metadados de um DataFrame para auditoria e rastreamento.
    
    Esta função padroniza a extração de informações sobre arquivos carregados,
    essencial para logs de auditoria e debugging. Os metadados são armazenados
    no atributo .attrs do DataFrame pelas funções de carregamento.
    
    Metadados extraídos:
    - Caminho completo do arquivo original
    - Data/hora de modificação do arquivo
    - Número de registros carregados
    - Número de colunas
    
    Args:
        df: DataFrame com metadados armazenados em df.attrs
        
    Returns:
        Dict: Metadados estruturados do arquivo
        {
            'arquivo': 'caminho/completo/arquivo.csv',
            'data_arquivo': datetime object,
            'registros': 1234,
            'colunas': 15
        }
        
    Example:
        >>> df = load_dashboard()
        >>> meta = get_file_metadata(df)
        >>> meta['registros']
        156
        >>> meta['arquivo']
        '/mnt/c/amfi/data/input/csv/AcompanhamentoDeOportunidades-2025-07-07.csv'
    """
    return {
        "arquivo": df.attrs.get('arquivo', 'desconhecido'),
        "data_arquivo": df.attrs.get('data_arquivo'),
        "registros": len(df),
        "colunas": len(df.columns) if not df.empty else 0
    }

if __name__ == "__main__":
    df = load_dashboard()