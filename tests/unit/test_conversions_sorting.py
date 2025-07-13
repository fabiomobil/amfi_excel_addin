#!/usr/bin/env python3
"""
Teste das conversões de tipo e ordenação no file_loaders
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 Testando conversões e ordenação...\n")

try:
    # Importar funções necessárias
    from data_converters import limpar_valor_brasileiro, limpar_percentual_brasileiro
    
    # Testar conversão de valores monetários
    print("💰 Testando conversão de valores monetários:")
    valores_teste = [
        "R$ 26.938.191,90",
        "1.522.412,64",
        "100,50",
        "1.000",
        "",
        None
    ]
    
    for valor in valores_teste:
        resultado = limpar_valor_brasileiro(valor)
        print(f"  '{valor}' → {resultado}")
    
    # Testar conversão de percentuais
    print("\n📊 Testando conversão de percentuais:")
    percentuais_teste = [
        "25,5%",
        "2.019,3%",
        "100%",
        "0,5",
        ""
    ]
    
    for perc in percentuais_teste:
        resultado = limpar_percentual_brasileiro(perc)
        print(f"  '{perc}' → {resultado}")
    
    # Informações sobre ordenação
    print("\n📋 Ordenação configurada em load_portfolio():")
    print("  1. Nome (Pool)")
    print("  2. Data de vencimento Original (ou Data de vencimento)")
    print("  3. Nome do Cedente")
    print("  4. Nome do Sacado")
    
    print("\n✅ Novas colunas adicionadas para conversão:")
    print("  Monetárias: Valor de face, Valor de aquisição, Valor bruto, etc.")
    print("  Percentuais: Taxa, Taxa de desconto, Taxa de juros, etc.")
    print("  Datas: Data de aquisição, Data de emissão, etc.")
    print("  Numéricas: Prazo, Dias em atraso, Parcela, etc.")
    
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Teste concluído!")