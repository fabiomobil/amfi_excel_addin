"""
Conversores de Dados Brasileiros
================================

Responsável por:
- Converter valores monetários do formato brasileiro R$ X.XXX.XXX,XX para float
- Converter percentuais do formato brasileiro XX,X% para decimal
- Aplicar conversões em DataFrames de forma centralizada
- Garantir consistência na formatação de dados
"""

import pandas as pd
import os
from typing import List, Optional


def normalizar_nome_coluna(nome: str) -> str:
    """
    Normaliza nome de coluna para formato padronizado.
    
    Transformações aplicadas:
    - Converte para minúsculas
    - Remove (R$), (RS) e variações
    - Substitui espaços por underscore
    - Remove acentos e caracteres especiais
    - Remove underscores duplicados
    
    Examples:
        'Taxa de Juros a.m.' → 'taxa_de_juros_am'
        'Valor de Aquisição (R$)' → 'valor_de_aquisicao'
        'Valor presente (R$)' → 'valor_presente'
    """
    # Converter para minúsculas
    nome = nome.lower()
    
    # Remover (R$), (RS), etc - ANTES de substituir espaços
    nome = nome.replace('(r$)', '').replace('(rs)', '').replace('r$', '').replace('rs', '')
    
    # Substituir espaços por underscore
    nome = nome.replace(' ', '_')
    
    # Remover acentos
    nome = nome.replace('ç', 'c').replace('ã', 'a').replace('é', 'e').replace('ê', 'e')
    nome = nome.replace('á', 'a').replace('à', 'a').replace('ó', 'o').replace('í', 'i')
    nome = nome.replace('ú', 'u').replace('ô', 'o')
    
    # Remover caracteres especiais
    nome = nome.replace('(', '').replace(')', '').replace('$', '').replace('%', '')
    nome = nome.replace('.', '').replace(',', '').replace('-', '_')
    
    # Remover underscores múltiplos
    while '__' in nome:
        nome = nome.replace('__', '_')
    
    # Remover underscore inicial e final
    return nome.strip('_')


def limpar_valor_brasileiro(valor):
    """
    Converte valores no formato brasileiro R$ X.XXX.XXX,XX para float.
    LEGADO: Use convert_brazilian_currency_vectorized() para performance.
    
    Args:
        valor: Valor a ser convertido (pode ser string, float, etc.)
        
    Returns:
        float: Valor numérico convertido ou None se não conseguir converter
    """
    if pd.isna(valor) or valor == '':
        return None
    valor_str = str(valor).replace('R$', '').strip()
    
    if ',' in valor_str:
        valor_str = valor_str.replace('.', '').replace(',', '.')
    
    try:
        return float(valor_str)
    except:
        return None


def convert_brazilian_currency_vectorized(series: pd.Series) -> pd.Series:
    """
    Converte Series inteira de valores monetários brasileiros de forma vetorizada.
    Performance: 50-100x mais rápido que .apply() para datasets grandes.
    
    Args:
        series: Pandas Series com valores em formato brasileiro
        
    Returns:
        pd.Series: Series convertida para float
    """
    # Converter tudo para string, lidar com NaN
    series_str = series.astype(str).replace({'nan': '', 'None': '', '<NA>': ''})
    
    # Remover R$, RS e espaços em uma operação vetorizada
    series_clean = (series_str
                   .str.replace('R$', '', regex=False)
                   .str.replace('RS', '', regex=False) 
                   .str.replace('r$', '', regex=False)
                   .str.replace('rs', '', regex=False)
                   .str.strip())
    
    # Processar formato brasileiro: trocar . por nada e , por .
    # Usar regex para detectar padrão brasileiro (números com vírgula)
    mask_brazilian = series_clean.str.contains(',', na=False)
    
    # Para valores com vírgula (formato brasileiro)
    brazilian_values = series_clean[mask_brazilian].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    
    # Para valores sem vírgula (já no formato correto ou vazio)
    other_values = series_clean[~mask_brazilian]
    
    # Combinar de volta
    series_processed = pd.Series(index=series.index, dtype='object')
    series_processed[mask_brazilian] = brazilian_values
    series_processed[~mask_brazilian] = other_values
    
    # Converter para numérico em uma operação vetorizada
    return pd.to_numeric(series_processed, errors='coerce')


def limpar_percentual_brasileiro(valor):
    """
    Converte percentuais no formato brasileiro para float decimal.
    LEGADO: Use convert_brazilian_percentage_vectorized() para performance.
    
    Args:
        valor: Valor percentual a ser convertido (pode ser string, float, etc.)
        
    Returns:
        float: Valor decimal convertido ou None se não conseguir converter
    """
    if pd.isna(valor) or valor == '':
        return None
    valor_str = str(valor).replace('%', '').strip()
    
    if ',' in valor_str and '.' in valor_str:
        valor_str = valor_str.replace('.', '').replace(',', '.')
    elif ',' in valor_str:
        valor_str = valor_str.replace(',', '.')
    
    try:
        return float(valor_str) / 100.0
    except:
        return None


def convert_brazilian_percentage_vectorized(series: pd.Series) -> pd.Series:
    """
    Converte Series inteira de percentuais brasileiros de forma vetorizada.
    Performance: 50-100x mais rápido que .apply() para datasets grandes.
    
    Args:
        series: Pandas Series com percentuais em formato brasileiro
        
    Returns:
        pd.Series: Series convertida para float decimal (ex: 25,5% -> 0.255)
    """
    # Converter para string e limpar
    series_str = series.astype(str).replace({'nan': '', 'None': '', '<NA>': ''})
    
    # Remover % e espaços
    series_clean = series_str.str.replace('%', '', regex=False).str.strip()
    
    # Processar formato brasileiro
    # Casos: "25,5", "2.019,3", "100"
    mask_comma_and_dot = series_clean.str.contains(',', na=False) & series_clean.str.contains('\.', na=False)
    mask_comma_only = series_clean.str.contains(',', na=False) & ~series_clean.str.contains('\.', na=False)
    
    series_processed = pd.Series(index=series.index, dtype='object')
    
    # Formato "2.019,3" -> remover pontos, trocar vírgula por ponto
    if mask_comma_and_dot.any():
        series_processed[mask_comma_and_dot] = (series_clean[mask_comma_and_dot]
                                               .str.replace('.', '', regex=False)
                                               .str.replace(',', '.', regex=False))
    
    # Formato "25,5" -> trocar vírgula por ponto
    if mask_comma_only.any():
        series_processed[mask_comma_only] = series_clean[mask_comma_only].str.replace(',', '.', regex=False)
    
    # Formato "100" -> manter como está
    mask_no_comma = ~mask_comma_and_dot & ~mask_comma_only
    if mask_no_comma.any():
        series_processed[mask_no_comma] = series_clean[mask_no_comma]
    
    # Converter para numérico e dividir por 100 (percentual para decimal)
    numeric_series = pd.to_numeric(series_processed, errors='coerce')
    return numeric_series / 100.0


def aplicar_conversoes_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas as conversões necessárias para CSV de dashboard.
    
    Args:
        df: DataFrame do CSV a ser convertido
        
    Returns:
        pd.DataFrame: DataFrame com conversões aplicadas e colunas normalizadas
    """
    # NOVO: Normalizar nomes das colunas primeiro
    df.columns = [normalizar_nome_coluna(col) for col in df.columns]
    
    # Listas simplificadas com nomes base normalizados
    colunas_monetarias_base = ['pl', 'sr', 'jr', 'carteira', 'caixa_livre', 
                               'fundo_de_reserva', 'rg', 'saldo_em_aplicacoes']
    
    colunas_percentuais_base = ['is', 'is_tranche', 'de_atraso', 'de_pdd', 
                                'rentabilidade_media_ativos']
    
    colunas_data_base = ['data_de_vencimento', 'proximo_pagamento']
    
    # Aplicar conversões baseadas em nomes normalizados
    for coluna in df.columns:
        # Verificar se é monetária
        if any(base in coluna for base in colunas_monetarias_base):
            df[coluna] = df[coluna].apply(limpar_valor_brasileiro)
        # Verificar se é percentual
        elif any(base in coluna for base in colunas_percentuais_base):
            df[coluna] = df[coluna].apply(limpar_percentual_brasileiro)
        # Verificar se é data
        elif any(base in coluna for base in colunas_data_base):
            if df[coluna].dtype != 'datetime64[ns]':
                df[coluna] = pd.to_datetime(df[coluna], errors='coerce', dayfirst=True)
    
    return df


def tentar_conversao_automatica(df: pd.DataFrame, coluna: str) -> pd.Series:
    """
    Tenta converter uma coluna automaticamente para numérico.
    
    Args:
        df: DataFrame
        coluna: Nome da coluna
        
    Returns:
        pd.Series: Coluna convertida ou original se falhar
    """
    serie = df[coluna].copy()
    
    # Se já for numérica, retornar
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    
    # Tentar conversão direta primeiro
    try:
        return pd.to_numeric(serie, errors='coerce')
    except:
        pass
    
    # Se falhar, tentar limpar formato brasileiro
    try:
        # Remover espaços e caracteres especiais comuns
        serie_limpa = serie.astype(str).str.replace(' ', '').str.replace('R$', '')
        
        # Verificar se tem vírgula (formato brasileiro)
        if serie_limpa.str.contains(',').any():
            return serie_limpa.apply(limpar_valor_brasileiro)
        else:
            return pd.to_numeric(serie_limpa, errors='coerce')
    except:
        return serie  # Retornar original se tudo falhar


def aplicar_conversoes_xlsx(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas as conversões necessárias para XLSX de portfolio.
    Otimizado para performance em datasets grandes.
    
    Args:
        df: DataFrame do XLSX a ser convertido
        
    Returns:
        pd.DataFrame: DataFrame com conversões aplicadas e colunas normalizadas
    """
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # Estratégia baseada no tamanho do dataset
    is_large_dataset = num_rows > 1000
    
    # Log macro inicial
    print(f"📊 Processando portfolio: {num_rows:,} registros, {num_cols} colunas")
    if is_large_dataset:
        print("⚡ Modo performance ativado para dataset grande")
    
    # Normalizar nomes das colunas
    df.columns = [normalizar_nome_coluna(col) for col in df.columns]
    
    # Identificar colunas por palavras-chave (mais flexível e abrangente)
    palavras_monetarias = ['valor', 'preco', 'montante', 'saldo', 'presente', 'aquisicao', 'recebido']
    palavras_percentuais = ['taxa', 'percentual', 'percent']
    
    # Aplicar conversões com estratégia apropriada
    conversoes_aplicadas = {'monetarias': [], 'percentuais': []}
    
    # Analisar cada coluna
    for coluna in df.columns:
        coluna_lower = coluna.lower()
        
        # Pular colunas que devem permanecer como texto
        if any(exclusao in coluna_lower for exclusao in ['nome', 'cnpj', 'cpf', 'endereco', 'cidade', 'estado', 'cedente', 'sacado']):
            continue
            
        # Verificar se coluna já é numérica
        if pd.api.types.is_numeric_dtype(df[coluna]):
            continue
            
        # Verificar se tem dados para converter
        if df[coluna].dropna().empty:
            continue
        
        # Conversões monetárias (baseado em palavras-chave)
        if any(palavra in coluna_lower for palavra in palavras_monetarias):
            try:
                if is_large_dataset:
                    # Tentar conversão vetorizada primeiro
                    resultado = convert_brazilian_currency_vectorized(df[coluna])
                    # Verificar se a conversão funcionou
                    if pd.api.types.is_numeric_dtype(resultado) and resultado.notna().sum() > 0:
                        df[coluna] = resultado
                    else:
                        # Fallback para método tradicional
                        df[coluna] = df[coluna].apply(limpar_valor_brasileiro)
                else:
                    df[coluna] = df[coluna].apply(limpar_valor_brasileiro)
                conversoes_aplicadas['monetarias'].append(coluna)
            except Exception as e:
                # Em caso de erro, tentar método tradicional
                df[coluna] = df[coluna].apply(limpar_valor_brasileiro)
                conversoes_aplicadas['monetarias'].append(f"{coluna} (fallback)")
            
        # Conversões percentuais (baseado em palavras-chave)
        elif any(palavra in coluna_lower for palavra in palavras_percentuais):
            try:
                if is_large_dataset:
                    # Tentar conversão vetorizada primeiro
                    resultado = convert_brazilian_percentage_vectorized(df[coluna])
                    # Verificar se a conversão funcionou
                    if pd.api.types.is_numeric_dtype(resultado) and resultado.notna().sum() > 0:
                        df[coluna] = resultado
                    else:
                        # Fallback para método tradicional
                        df[coluna] = df[coluna].apply(limpar_percentual_brasileiro)
                else:
                    df[coluna] = df[coluna].apply(limpar_percentual_brasileiro)
                conversoes_aplicadas['percentuais'].append(coluna)
            except Exception as e:
                # Em caso de erro, tentar método tradicional
                df[coluna] = df[coluna].apply(limpar_percentual_brasileiro)
                conversoes_aplicadas['percentuais'].append(f"{coluna} (fallback)")
    
    # Log macro de resultados
    print(f"✅ Conversões aplicadas: {len(conversoes_aplicadas['monetarias'])} monetárias, {len(conversoes_aplicadas['percentuais'])} percentuais")
    
    # Conversões de data (sempre vetorizadas)
    colunas_data_base = [
        'data_vencimento', 'data_vencimento_original', 'data_aquisicao',
        'data_emissao', 'data_pagamento', 'data_liquidacao',
        'data_ultimo_pagamento', 'data_proximo_pagamento'
    ]
    
    data_conversions = 0
    for coluna in df.columns:
        if any(base in coluna for base in colunas_data_base):
            if df[coluna].dtype != 'datetime64[ns]':
                df[coluna] = pd.to_datetime(df[coluna], errors='coerce', dayfirst=True)
                data_conversions += 1
    
    if data_conversions > 0:
        print(f"📅 {data_conversions} colunas de data convertidas")
    
    # Conversões numéricas simples (sempre vetorizadas)
    colunas_numericas_base = ['prazo', 'dias_atraso', 'parcela', 'numero_parcelas', 'id', 'codigo']
    
    numeric_conversions = 0
    for coluna in df.columns:
        if any(base in coluna for base in colunas_numericas_base):
            df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
            numeric_conversions += 1
    
    if numeric_conversions > 0:
        print(f"🔢 {numeric_conversions} colunas numéricas convertidas")
    
    return df


def obter_colunas_por_tipo():
    """
    Retorna dicionário com listas de colunas por tipo de conversão.
    
    Returns:
        dict: Dicionário com tipos de colunas
    """
    return {
        'csv_monetarias': ['PL', 'SR', 'JR', 'Carteira', 'Caixa Livre', 'Fundo de Reserva', 'R.G.', 'Saldo em Aplicações'],
        'csv_percentuais': ['I.S.', 'I.S. (Tranche)', '% de Atraso', '% de PDD', 'Rentabilidade Média Ativos %'],
        'csv_datas': ['Data de vencimento', 'Próximo Pagamento'],
        'xlsx_monetarias': [
            'Valor presente', 'Valor do título', 'Valor nominal', 'Valor pago', 'Saldo devedor',
            'Valor de face', 'Valor de aquisição', 'Valor bruto', 'Valor líquido',
            'Valor da parcela', 'Valor total', 'Valor contábil', 'Valor de mercado',
            'Principal', 'Juros', 'Multa', 'Desconto', 'Acréscimo'
        ],
        'xlsx_percentuais': ['Taxa', 'Taxa de desconto', 'Taxa de juros', 'Percentual', 'Desconto %'],
        'xlsx_datas': [
            'Data de vencimento', 'Data de vencimento Original', 'Data de aquisição',
            'Data de emissão', 'Data de pagamento', 'Data de liquidação',
            'Data do último pagamento', 'Data do próximo pagamento'
        ],
        'xlsx_numericas': ['Prazo', 'Dias em atraso', 'Parcela', 'Número de parcelas', 'ID', 'Código']
    }