#!/usr/bin/env python3
"""
Teste das funções renomeadas no file_loaders.py
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 Testando funções renomeadas...\n")

try:
    # Testar imports
    from file_loaders import (
        get_possible_paths, 
        find_existing_path, 
        read_csv_raw,
        load_json_file,
        get_file_metadata,
        load_dashboard,
        load_portfolio
    )
    print("✅ Imports bem-sucedidos!")
    
    # Testar get_possible_paths
    caminhos = get_possible_paths('csv')
    print(f"✅ get_possible_paths('csv'): {len(caminhos)} caminhos retornados")
    
    # Testar find_existing_path
    try:
        caminho = find_existing_path('csv')
        print(f"✅ find_existing_path('csv'): {caminho}")
    except FileNotFoundError as e:
        print(f"⚠️ find_existing_path('csv'): {e}")
    
    # Testar load_json_file
    try:
        config = load_json_file('test_pools.json')
        print(f"✅ load_json_file('test_pools.json'): {len(config)} chaves")
    except FileNotFoundError as e:
        print(f"⚠️ load_json_file: {e}")
    
    # Testar data_loader principal
    print("\n🚀 Testando data_loader com funções renomeadas...")
    from data_loader import load_pool_data
    
    resultado = load_pool_data()
    print(f"✅ data_loader executado: sucesso = {resultado.get('sucesso')}")
    
    if resultado.get('csv_data') is not None:
        print(f"✅ CSV carregado: {len(resultado['csv_data'])} registros")
    
    print(f"\n📊 Pools processados: {resultado.get('pools_processados', [])}")
    
except ImportError as e:
    print(f"❌ Erro de import: {e}")
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Teste concluído!")