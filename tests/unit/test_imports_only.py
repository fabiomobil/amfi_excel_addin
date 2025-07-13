#!/usr/bin/env python3
"""
Teste simples dos imports renomeados
"""

import sys
import os
sys.path.insert(0, 'monitor/utils')

print("🔍 Testando imports das funções renomeadas...\n")

# Testar se o arquivo pode ser importado
try:
    import file_loaders
    print("✅ file_loaders importado com sucesso")
    
    # Verificar se as funções existem
    funções_esperadas = [
        'get_possible_paths',
        'find_existing_path', 
        'read_csv_raw',
        'load_json_file',
        'get_file_metadata',
        'load_dashboard',
        'load_portfolio'
    ]
    
    for func in funções_esperadas:
        if hasattr(file_loaders, func):
            print(f"✅ {func} encontrada")
        else:
            print(f"❌ {func} NÃO encontrada")
    
    # Verificar se as antigas não existem mais
    funções_antigas = [
        'obter_caminhos_multiplos',
        'encontrar_pasta_existente',
        'carregar_csv_manual',
        'carregar_arquivo_json',
        'obter_metadados_arquivo'
    ]
    
    print("\n🔍 Verificando se funções antigas foram removidas:")
    for func in funções_antigas:
        if hasattr(file_loaders, func):
            print(f"⚠️ {func} ainda existe (deveria ter sido renomeada)")
        else:
            print(f"✅ {func} removida corretamente")
    
    # Testar get_possible_paths sem pandas
    try:
        caminhos = file_loaders.get_possible_paths('csv')
        print(f"\n✅ get_possible_paths funciona: {len(caminhos)} caminhos")
        print(f"   Exemplo: {caminhos[0]}")
    except Exception as e:
        print(f"\n❌ get_possible_paths falhou: {e}")
    
except Exception as e:
    print(f"❌ Erro ao importar file_loaders: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Teste de imports concluído!")