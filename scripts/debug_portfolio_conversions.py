#!/usr/bin/env python3
"""
Debug script para rastrear por que conversões não estão funcionando no load_portfolio
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 Debugando conversões no load_portfolio...\n")

try:
    from file_loaders import load_portfolio
    from data_converters import normalizar_nome_coluna
    import pandas as pd
    
    # Habilitar debug mode
    os.environ['AMFI_DEBUG'] = 'true'
    
    print("📂 Carregando portfolio...")
    df = load_portfolio()
    
    print(f"\n📊 DataFrame carregado: {len(df)} registros, {len(df.columns)} colunas")
    
    # Verificar colunas específicas do screenshot
    colunas_problema = [
        'Taxa de Juros a.m.',
        'Valor de Aquisição (R$)', 
        'Valor presente (R$)',
        'Valor Recebido (RS)'
    ]
    
    print("\n🔍 VERIFICANDO COLUNAS ORIGINAIS:")
    print("-" * 50)
    for col in colunas_problema:
        if col in df.columns:
            dtype = df[col].dtype
            status = "✅ NUMÉRICO" if pd.api.types.is_numeric_dtype(df[col]) else "❌ TEXTO"
            amostra = list(df[col].dropna().head(3).values)
            print(f"'{col}': {dtype} {status}")
            print(f"   Amostra: {amostra}")
        else:
            # Verificar versão normalizada
            col_norm = normalizar_nome_coluna(col)
            if col_norm in df.columns:
                dtype = df[col_norm].dtype
                status = "✅ NUMÉRICO" if pd.api.types.is_numeric_dtype(df[col_norm]) else "❌ TEXTO"
                amostra = list(df[col_norm].dropna().head(3).values)
                print(f"'{col}' → '{col_norm}': {dtype} {status}")
                print(f"   Amostra: {amostra}")
            else:
                print(f"'{col}': ⚠️ NÃO ENCONTRADA (nem original nem normalizada)")
    
    print("\n🔤 TODAS AS COLUNAS NO DATAFRAME:")
    print("-" * 50)
    for i, col in enumerate(df.columns):
        dtype = df[col].dtype
        status = "✅" if pd.api.types.is_numeric_dtype(df[col]) else "❌"
        print(f"{i+1:2d}. '{col}': {dtype} {status}")
    
    print("\n🧪 TESTANDO CONVERSÃO MANUAL:")
    print("-" * 50)
    
    # Testar conversão manual nas colunas problema
    from data_converters import limpar_valor_brasileiro, limpar_percentual_brasileiro
    
    for col_original in colunas_problema:
        col_norm = normalizar_nome_coluna(col_original)
        
        if col_norm in df.columns:
            print(f"\n🔧 Testando '{col_norm}':")
            
            # Pegar amostra
            amostra = df[col_norm].dropna().head(3)
            
            for idx, valor in amostra.items():
                print(f"   Valor original: '{valor}' (tipo: {type(valor).__name__})")
                
                # Testar conversão monetária
                conv_monetaria = limpar_valor_brasileiro(valor)
                print(f"   Conversão monetária: {conv_monetaria} (tipo: {type(conv_monetaria).__name__})")
                
                # Testar conversão percentual
                conv_percentual = limpar_percentual_brasileiro(valor)
                print(f"   Conversão percentual: {conv_percentual} (tipo: {type(conv_percentual).__name__})")
                
                break  # Só testar primeiro valor
    
    print("\n✨ Debug concluído!")
    print("\nSe as conversões manuais funcionaram mas as automáticas não,")
    print("então o problema está na lógica de detecção de colunas em aplicar_conversoes_xlsx()")

except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()