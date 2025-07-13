#!/usr/bin/env python3
"""
Teste simples do data_loader - simula execução no Spyder
"""

import sys
import os

# Adicionar caminho ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitor', 'utils'))

print("🚀 Testando data_loader.py...\n")

try:
    # Import direto como seria no Spyder
    from data_loader import load_pool_data
    print("✅ Import bem-sucedido!")
    
    # Executar função
    print("\n📊 Executando load_pool_data()...")
    resultado = load_pool_data()
    
    # Mostrar resultados
    print(f"\n📋 Resultado:")
    print(f"  - Sucesso: {resultado.get('sucesso', False)}")
    print(f"  - Pools processados: {len(resultado.get('pools_processados', []))}")
    print(f"  - Alertas: {len(resultado.get('alertas', []))}")
    
    # Mostrar alertas
    if resultado.get('alertas'):
        print("\n🔔 Alertas:")
        for alerta in resultado['alertas']:
            print(f"  [{alerta.get('tipo', 'info')}] {alerta.get('mensagem', '')}")
    
    # Mostrar pools processados
    if resultado.get('pools_processados'):
        print(f"\n🏊 Pools processados: {resultado['pools_processados']}")
    
    # Verificar se carregou dados
    csv_data = resultado.get('csv_data')
    xlsx_data = resultado.get('xlsx_data')
    
    if csv_data is not None:
        print(f"\n📄 CSV carregado: {len(csv_data)} registros")
    else:
        print("\n❌ CSV não foi carregado")
        
    if xlsx_data is not None:
        print(f"📊 XLSX carregado: {len(xlsx_data)} registros")
    else:
        print("❌ XLSX não foi carregado")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro na execução: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()