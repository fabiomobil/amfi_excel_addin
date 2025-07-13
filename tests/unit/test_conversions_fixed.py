#!/usr/bin/env python3
"""
Teste das Conversões Corrigidas
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔧 TESTE DAS CONVERSÕES CORRIGIDAS")
print("=" * 50)

try:
    from file_loaders import load_portfolio
    
    print("📂 Carregando portfolio com conversões corrigidas...")
    df = load_portfolio()
    
    print(f"📊 Dataset: {len(df):,} registros, {len(df.columns)} colunas")
    
    # Verificar colunas que contêm palavras-chave importantes
    print(f"\n🔍 COLUNAS COM PALAVRAS-CHAVE:")
    print("-" * 40)
    
    palavras_teste = ['valor', 'taxa', 'presente', 'aquisicao', 'recebido', 'juros']
    colunas_encontradas = []
    
    for palavra in palavras_teste:
        matches = [col for col in df.columns if palavra in col.lower()]
        if matches:
            print(f"\n'{palavra}':")
            for col in matches:
                dtype = str(df[col].dtype)
                is_numeric = pd.api.types.is_numeric_dtype(df[col])
                status = "✅ NUMÉRICO" if is_numeric else "❌ TEXTO"
                
                if not is_numeric:
                    # Mostrar amostra para debug
                    amostra = list(df[col].dropna().head(3).values)
                    print(f"   {col}: {dtype} {status} | {amostra}")
                    colunas_encontradas.append((col, amostra))
                else:
                    print(f"   {col}: {dtype} {status}")
    
    # Testar conversões manuais nas colunas que falharam
    if colunas_encontradas:
        print(f"\n🧪 TESTE MANUAL DE CONVERSÕES:")
        print("-" * 40)
        
        from data_converters import convert_brazilian_currency_vectorized, limpar_valor_brasileiro
        
        for col, amostra in colunas_encontradas[:3]:  # Testar até 3 colunas
            print(f"\n🔧 Testando '{col}':")
            
            # Testar função vetorizada
            try:
                resultado_vet = convert_brazilian_currency_vectorized(df[col].head(5))
                print(f"   Vetorizada: {list(resultado_vet.values)} (tipo: {resultado_vet.dtype})")
            except Exception as e:
                print(f"   Vetorizada: ERRO - {e}")
            
            # Testar função tradicional
            try:
                resultado_trad = df[col].head(5).apply(limpar_valor_brasileiro)
                print(f"   Tradicional: {list(resultado_trad.values)} (tipo: {resultado_trad.dtype})")
            except Exception as e:
                print(f"   Tradicional: ERRO - {e}")
    
    # Contar sucessos
    total_colunas = len(df.columns)
    colunas_numericas = len(df.select_dtypes(include=['number']).columns)
    colunas_texto = len(df.select_dtypes(include=['object']).columns)
    
    print(f"\n📈 RESUMO FINAL:")
    print(f"   Total de colunas: {total_colunas}")
    print(f"   Colunas numéricas: {colunas_numericas}")
    print(f"   Colunas texto: {colunas_texto}")
    print(f"   Taxa de conversão: {colunas_numericas/total_colunas*100:.1f}%")

except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 50)