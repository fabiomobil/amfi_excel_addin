#!/usr/bin/env python3
"""
Teste que simula execução no Spyder - executar DESTE diretório
"""

print("🔍 Teste de execução direta (simulando Spyder)\n")
print(f"Diretório atual: {__file__}")
print(f"Diretório de trabalho: {import os; os.getcwd()}")

# Tentar executar como seria no Spyder
try:
    from data_loader import load_pool_data
    print("\n✅ Import direto funcionou!")
    
    print("\n🚀 Executando load_pool_data()...")
    resultado = load_pool_data()
    
    print(f"\n📊 Resultado:")
    print(f"  - Sucesso: {resultado.get('sucesso')}")
    print(f"  - Pools para processar: {resultado.get('pools_processados')}")
    
    # Verificar se entrou em modo debug
    if resultado.get('monitores_debug'):
        print(f"  - MODO DEBUG ATIVO")
        print(f"  - Monitores específicos: {resultado.get('monitores_debug')}")
    
except Exception as e:
    print(f"\n❌ Erro: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()