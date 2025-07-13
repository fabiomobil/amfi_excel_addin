#!/usr/bin/env python3
"""
Analisar Arquivo Real - Ver Colunas Exatas
==========================================

Vou carregar o arquivo XLSX real e mostrar TODAS as colunas
com seus tipos e amostras para definir as listas corretas.
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 ANALISANDO ARQUIVO REAL")
print("=" * 60)

try:
    # Importar apenas o que preciso
    import pandas as pd
    from file_loaders import find_existing_path
    from data_converters import normalizar_nome_coluna
    import glob
    
    # Encontrar pasta XLSX
    pasta_xlsx = find_existing_path('xlsx')
    print(f"📂 Pasta XLSX encontrada: {pasta_xlsx}")
    
    # Procurar arquivo mais recente
    padrao = f"{pasta_xlsx}/Carteira Global *.xlsx"
    arquivos = glob.glob(padrao)
    
    if not arquivos:
        print(f"❌ Nenhum arquivo encontrado em {padrao}")
        exit()
    
    arquivo_escolhido = max(arquivos, key=os.path.getmtime)
    print(f"📄 Arquivo: {os.path.basename(arquivo_escolhido)}")
    
    # Carregar arquivo RAW (sem conversões)
    print("⏳ Carregando arquivo...")
    df_raw = pd.read_excel(arquivo_escolhido, engine='openpyxl')
    
    print(f"📊 Dataset: {len(df_raw):,} registros, {len(df_raw.columns)} colunas")
    
    # Mostrar colunas ORIGINAIS
    print(f"\n📋 COLUNAS ORIGINAIS (antes da normalização):")
    print("-" * 60)
    for i, col in enumerate(df_raw.columns):
        dtype = str(df_raw[col].dtype)
        amostra = list(df_raw[col].dropna().head(3).values)
        print(f"{i+1:2d}. '{col}' → {dtype}")
        print(f"    Amostra: {amostra}")
    
    # Normalizar colunas
    df_raw.columns = [normalizar_nome_coluna(col) for col in df_raw.columns]
    
    print(f"\n🔄 COLUNAS APÓS NORMALIZAÇÃO:")
    print("-" * 60)
    for i, col in enumerate(df_raw.columns):
        dtype = str(df_raw[col].dtype)
        amostra = list(df_raw[col].dropna().head(3).values)
        print(f"{i+1:2d}. '{col}' → {dtype}")
        print(f"    Amostra: {amostra}")
    
    # Identificar colunas que precisam de conversão
    print(f"\n🔍 ANÁLISE DE TIPOS:")
    print("-" * 60)
    
    colunas_texto = []
    colunas_numericas = []
    
    for col in df_raw.columns:
        dtype = str(df_raw[col].dtype)
        if dtype == 'object':
            # Analisar se parece numérico
            amostra = df_raw[col].dropna().head(10)
            parece_numero = False
            parece_percentual = False
            
            for valor in amostra:
                valor_str = str(valor)
                if any(char in valor_str for char in ['R$', ',', '%']):
                    if '%' in valor_str:
                        parece_percentual = True
                    else:
                        parece_numero = True
                    break
            
            if parece_numero:
                colunas_texto.append(f"{col} → MONETÁRIO")
            elif parece_percentual:
                colunas_texto.append(f"{col} → PERCENTUAL")
            else:
                colunas_texto.append(f"{col} → TEXTO")
        else:
            colunas_numericas.append(col)
    
    print("📝 COLUNAS QUE PRECISAM DE CONVERSÃO:")
    for col in colunas_texto:
        if "MONETÁRIO" in col or "PERCENTUAL" in col:
            print(f"   {col}")
    
    print(f"\n🔢 COLUNAS JÁ NUMÉRICAS ({len(colunas_numericas)}):")
    for col in colunas_numericas:
        print(f"   {col}")

except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 60)