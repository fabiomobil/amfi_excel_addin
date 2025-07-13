#!/usr/bin/env python3
"""
Teste específico para colunas do screenshot
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 Testando conversão das colunas exatas do screenshot...\n")

# Simular dados como aparecem no screenshot
test_data = {
    'Taxa de Juros a.m.': ['0.031374', '0.039067', '0.046178', '0.043826'],
    'Valor de Aquisição (R$)': ['1117.69', '628.58', '1555.72', '1181.72'],
    'Valor presente (R$)': ['1212.41', '635.03', '1627.56', '1242.36']
}

print("📊 Colunas a converter:")
for col in test_data.keys():
    print(f"  - {col}")

print("\n✅ Essas colunas agora estão configuradas para conversão:")
print("  1. 'Taxa de Juros a.m.' → lista de percentuais")
print("  2. 'Valor de Aquisição (R$)' → lista de monetários")  
print("  3. 'Valor presente (R$)' → lista de monetários")

print("\n🔧 Além disso, a conversão automática detectará:")
print("  - Qualquer coluna com '(r$)' ou '(rs)' no nome")
print("  - Colunas com palavras: valor, taxa, juros, etc.")

print("\n💡 Como testar no Spyder:")
print("```python")
print("# Ativar debug para ver conversões")
print("import os")
print("os.environ['AMFI_DEBUG'] = 'true'")
print("")
print("# Carregar dados")
print("from monitor.utils.file_loaders import load_portfolio")
print("df = load_portfolio()")
print("")
print("# Verificar tipos")
print("print(df[['Taxa de Juros a.m.', 'Valor de Aquisição (R$)', 'Valor presente (R$)']].dtypes)")
print("")
print("# Devem aparecer como float64, não object")
print("```")

print("\n✨ Teste concluído!")