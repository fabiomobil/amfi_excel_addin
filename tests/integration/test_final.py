#!/usr/bin/env python3
"""
Teste final do data_loader
"""

# Setup básico
import sys
import os
sys.path.insert(0, 'monitor/utils')

print("=" * 50)
print("TESTE FINAL DO DATA_LOADER")
print("=" * 50)

try:
    from data_loader import load_pool_data
    print("\n✅ Import OK\n")
    
    # Executar
    resultado = load_pool_data()
    
    # Exibir resultado
    print(f"📊 RESULTADO:")
    print(f"   Sucesso: {resultado.get('sucesso')}")
    print(f"   Pools: {resultado.get('pools_processados')}")
    
    if resultado.get('monitores_debug'):
        print(f"   Modo: DEBUG")
        print(f"   Monitores: {resultado.get('monitores_debug')}")
    else:
        print(f"   Modo: NORMAL")
    
    # CSV/XLSX status
    csv_ok = resultado.get('csv_data') is not None
    xlsx_ok = resultado.get('xlsx_data') is not None
    
    print(f"\n📄 ARQUIVOS:")
    print(f"   CSV: {'✅ Carregado' if csv_ok else '❌ Falhou'}")
    print(f"   XLSX: {'✅ Carregado' if xlsx_ok else '❌ Falhou'}")
    
    # Alertas críticos
    alertas_erro = [a for a in resultado.get('alertas', []) if a.get('tipo') == 'error']
    if alertas_erro:
        print(f"\n⚠️ ERROS ({len(alertas_erro)}):")
        for alerta in alertas_erro[:3]:  # Mostrar até 3
            print(f"   - {alerta.get('mensagem')}")
    
    # Erro principal
    if resultado.get('erro'):
        print(f"\n❌ ERRO PRINCIPAL: {resultado.get('erro')}")
    
    print("\n" + "=" * 50)
    
except Exception as e:
    print(f"\n❌ FALHA TOTAL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()