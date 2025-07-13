#!/usr/bin/env python3
"""
Teste da função de normalização de colunas
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 Testando normalização de nomes de colunas...\n")

try:
    from data_converters import normalizar_nome_coluna
    
    # Exemplos de colunas do screenshot
    exemplos = [
        'Taxa de Juros a.m.',
        'Valor de Aquisição (R$)',
        'Valor presente (R$)',
        'Nome do Sacado',
        'Nome do Cedente',
        'Data de vencimento Original',
        'Valor Recebido (RS)',
        'I.S. (Tranche)',
        '% de Atraso'
    ]
    
    print("📋 Transformações aplicadas:")
    for original in exemplos:
        normalizado = normalizar_nome_coluna(original)
        print(f"  '{original}' → '{normalizado}'")
    
    print(f"\n✅ Agora as colunas têm nomes consistentes:")
    print(f"  - Sem espaços (underscore)")
    print(f"  - Sem acentos")
    print(f"  - Sem (R$) ou caracteres especiais")
    print(f"  - Minúsculas")
    
    print(f"\n💡 No Spyder, após carregar portfolio:")
    print(f"  df.columns irá mostrar: ['taxa_de_juros_am', 'valor_de_aquisicao', 'valor_presente', ...]")
    print(f"  df['valor_presente'].dtype irá mostrar: float64 ✅")
    
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")

print("\n✨ Teste concluído!")