#!/usr/bin/env python3
"""
Para executar no SPYDER - Mostrar Colunas Reais do Arquivo
==========================================================

INSTRUÇÕES:
1. Abra o Spyder
2. Execute este script linha por linha
3. Vou mostrar TODAS as colunas reais com amostras
"""

import sys
sys.path.insert(0, 'monitor/utils')

print("🔍 ANALISANDO ARQUIVO REAL NO SPYDER")
print("=" * 60)

# Importar módulos
import pandas as pd
from file_loaders import find_existing_path
from data_converters import normalizar_nome_coluna
import glob
import os

# Encontrar e carregar arquivo
pasta_xlsx = find_existing_path('xlsx')
padrao = f"{pasta_xlsx}/Carteira Global *.xlsx"
arquivos = glob.glob(padrao)
arquivo_escolhido = max(arquivos, key=os.path.getmtime)

print(f"📄 Carregando: {os.path.basename(arquivo_escolhido)}")

# Carregar arquivo RAW (sem conversões)
df_raw = pd.read_excel(arquivo_escolhido, engine='openpyxl')

print(f"📊 Dataset: {len(df_raw):,} registros, {len(df_raw.columns)} colunas")

print(f"\n📋 COLUNAS ORIGINAIS:")
print("-" * 60)

for i, col in enumerate(df_raw.columns):
    dtype = str(df_raw[col].dtype)
    amostra = list(df_raw[col].dropna().head(3).values)
    print(f"{i+1:2d}. ORIGINAL: '{col}'")
    print(f"    TIPO: {dtype}")
    print(f"    AMOSTRA: {amostra}")
    
    # Mostrar versão normalizada
    col_normalizada = normalizar_nome_coluna(col)
    print(f"    NORMALIZADA: '{col_normalizada}'")
    print()

print(f"\n🎯 IDENTIFICAÇÃO DE TIPOS:")
print("-" * 60)

# Listas para as diferentes categorias
monetarias_encontradas = []
percentuais_encontradas = []
texto_puro = []
ja_numericas = []

for col in df_raw.columns:
    col_norm = normalizar_nome_coluna(col)
    dtype = str(df_raw[col].dtype)
    
    if dtype == 'object':
        # Analisar amostra para ver o tipo
        amostra = df_raw[col].dropna().head(10)
        tem_rs = False
        tem_percentual = False
        
        for valor in amostra:
            valor_str = str(valor)
            if 'R$' in valor_str or any(c in valor_str for c in [',', '.']):
                # Verificar se é formato brasileiro de número
                if any(char.isdigit() for char in valor_str):
                    tem_rs = True
            if '%' in valor_str:
                tem_percentual = True
        
        if tem_percentual:
            percentuais_encontradas.append(col_norm)
            print(f"📊 PERCENTUAL: '{col_norm}' (original: '{col}')")
        elif tem_rs:
            monetarias_encontradas.append(col_norm)
            print(f"💰 MONETÁRIO: '{col_norm}' (original: '{col}')")
        else:
            texto_puro.append(col_norm)
            print(f"📝 TEXTO: '{col_norm}' (original: '{col}')")
    else:
        ja_numericas.append(col_norm)
        print(f"🔢 JÁ NUMÉRICO: '{col_norm}' (original: '{col}')")

print(f"\n🎯 LISTAS PARA USAR NO CÓDIGO:")
print("-" * 60)
print(f"💰 MONETÁRIAS ({len(monetarias_encontradas)}):")
print(f"   {monetarias_encontradas}")
print(f"\n📊 PERCENTUAIS ({len(percentuais_encontradas)}):")
print(f"   {percentuais_encontradas}")
print(f"\n🔢 JÁ NUMÉRICAS ({len(ja_numericas)}):")
print(f"   {ja_numericas[:10]}...")  # Mostrar só as primeiras 10

print(f"\n✅ AGORA POSSO USAR AS LISTAS EXATAS DO SEU ARQUIVO!")