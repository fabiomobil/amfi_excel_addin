#!/usr/bin/env python3
"""
Script simples para testar conversões no Spyder

Instruções:
1. Abra o Spyder
2. Execute este script linha por linha ou copie o código para o console
3. O debug será exibido mostrando exatamente o que está acontecendo
"""

# Configurar debug mode
import os
os.environ['AMFI_DEBUG'] = 'true'

# Importar função de carregamento
import sys
sys.path.insert(0, 'monitor/utils')

print("🔍 Testando conversões com debug habilitado...")
print("=" * 60)

try:
    from file_loaders import load_portfolio
    
    # Carregar portfolio com debug
    print("📂 Carregando portfolio...")
    df = load_portfolio()
    
    print(f"\n✅ Portfolio carregado: {len(df)} registros, {len(df.columns)} colunas")
    
    # Verificar tipos específicos das colunas problemáticas
    colunas_teste = [
        'taxa_de_juros_am',
        'valor_de_aquisicao', 
        'valor_presente',
        'valor_recebido'
    ]
    
    print(f"\n🔍 VERIFICAÇÃO FINAL:")
    print("-" * 30)
    
    for col in colunas_teste:
        if col in df.columns:
            dtype = df[col].dtype
            is_numeric = str(dtype).startswith(('int', 'float'))
            status = "✅ NUMÉRICO" if is_numeric else "❌ TEXTO"
            amostra = list(df[col].dropna().head(3).values)
            
            print(f"'{col}':")
            print(f"  Tipo: {dtype} {status}")
            print(f"  Amostra: {amostra}")
        else:
            print(f"'{col}': ⚠️ NÃO ENCONTRADA")
    
    print(f"\n💡 Se ainda houver colunas como TEXTO, verifique o debug acima")
    print(f"para entender por que as conversões não foram aplicadas.")
    
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)