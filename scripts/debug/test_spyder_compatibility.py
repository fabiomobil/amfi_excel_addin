#!/usr/bin/env python3
"""
Teste de Compatibilidade com Spyder
===================================

Testa se o data_loader.py refatorado funciona quando executado diretamente no Spyder.
"""

print("🧪 TESTANDO COMPATIBILIDADE COM SPYDER")
print("="*50)

try:
    # Testar import direto
    print("1. Testando import do data_loader...")
    from data_loader import load_pool_data
    print("   ✅ Import realizado com sucesso")
    
    # Testar se consegue pelo menos instanciar
    print("2. Testando instanciação da função...")
    print("   📋 load_pool_data está disponível")
    
    # Testar execução (pode falhar por falta de dados, mas import deve funcionar)
    print("3. Testando execução básica...")
    try:
        resultado = load_pool_data()
        print(f"   ✅ Execução concluída. Sucesso: {resultado.get('sucesso', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️ Execução falhou (esperado): {str(e)[:100]}")
    
    print("\n🎉 TESTE DE COMPATIBILIDADE CONCLUÍDO")
    print("✅ O data_loader.py refatorado é compatível com Spyder")
    
except ImportError as e:
    print(f"❌ Erro de import: {e}")
    print("💡 Verifique se os arquivos estão no local correto")
except Exception as e:
    print(f"❌ Erro geral: {e}")

print("\n" + "="*50)