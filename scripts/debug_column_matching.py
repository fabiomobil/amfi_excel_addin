#!/usr/bin/env python3
"""
Debug: Por que as conversões não estão funcionando em arquivos grandes
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 DEBUGANDO MATCHING DE COLUNAS")
print("=" * 50)

try:
    from file_loaders import load_portfolio
    from data_converters import normalizar_nome_coluna
    
    # Carregar dados
    print("📂 Carregando portfolio...")
    df = load_portfolio()
    
    print(f"📊 Dataset: {len(df):,} registros, {len(df.columns)} colunas")
    print(f"🔍 Threshold para arquivo grande: 1000 (atual: {'GRANDE' if len(df) > 1000 else 'PEQUENO'})")
    
    # Mostrar todas as colunas normalizadas
    print(f"\n📋 TODAS AS COLUNAS APÓS NORMALIZAÇÃO:")
    print("-" * 50)
    for i, col in enumerate(df.columns):
        dtype = str(df[col].dtype)
        is_text = dtype == 'object'
        status = "📝 TEXTO" if is_text else f"🔢 {dtype}"
        print(f"{i+1:2d}. '{col}' → {status}")
    
    # Verificar colunas-alvo específicas
    print(f"\n🎯 VERIFICANDO MATCHING COM LISTAS DE CONVERSÃO:")
    print("-" * 50)
    
    colunas_monetarias_procuradas = [
        'prazo_dias', 'valor_de_aquisicao', 'valor_presente', 'valor_recebido'
    ]
    
    colunas_percentuais_procuradas = [
        'taxa_de_juros_am'
    ]
    
    print("💰 MONETÁRIAS:")
    for target in colunas_monetarias_procuradas:
        matches = [col for col in df.columns if target in col]
        if matches:
            print(f"   '{target}' → ENCONTRADA: {matches}")
            for match in matches:
                dtype = str(df[match].dtype)
                amostra = list(df[match].dropna().head(3).values)
                print(f"      {match}: {dtype} | Amostra: {amostra}")
        else:
            print(f"   '{target}' → ❌ NÃO ENCONTRADA")
    
    print("\n📊 PERCENTUAIS:")
    for target in colunas_percentuais_procuradas:
        matches = [col for col in df.columns if target in col]
        if matches:
            print(f"   '{target}' → ENCONTRADA: {matches}")
            for match in matches:
                dtype = str(df[match].dtype)
                amostra = list(df[match].dropna().head(3).values)
                print(f"      {match}: {dtype} | Amostra: {amostra}")
        else:
            print(f"   '{target}' → ❌ NÃO ENCONTRADA")
    
    # Buscar colunas suspeitas que podem ser numéricas
    print(f"\n🔍 COLUNAS SUSPEITAS (contêm palavras-chave):")
    print("-" * 50)
    palavras_chave = ['valor', 'taxa', 'juros', 'percentual', 'presente', 'aquisicao', 'recebido']
    
    for palavra in palavras_chave:
        matches = [col for col in df.columns if palavra in col.lower()]
        if matches:
            print(f"\n'{palavra}':")
            for match in matches:
                dtype = str(df[match].dtype)
                is_text = dtype == 'object'
                status = "⚠️ TEXTO" if is_text else f"✅ {dtype}"
                if is_text:
                    amostra = list(df[match].dropna().head(2).values)
                    print(f"   {match}: {status} | {amostra}")
                else:
                    print(f"   {match}: {status}")

except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 50)