"""
Script de Teste para JSON Loading no Spyder
===========================================

Este script testa se o sistema de descoberta de caminhos
está funcionando corretamente no Spyder.
"""

import os
import sys
import json

# Adicionar caminhos para imports
sys.path.append('/mnt/c/amfi/monitor')
sys.path.append('/mnt/c/amfi/monitor/utils')

print("=" * 60)
print("TESTE DE CARREGAMENTO JSON NO SPYDER")
print("=" * 60)

# 1. Teste direto de existência de arquivo
print("\n1. TESTE DIRETO DE ARQUIVO:")
test_paths = [
    "/mnt/c/amfi/config/pools/AFA Pool #1.json",
    r"C:\amfi\config\pools\AFA Pool #1.json",
    "config/pools/AFA Pool #1.json",
    "../../config/pools/AFA Pool #1.json"
]

for path in test_paths:
    exists = os.path.exists(path)
    print(f"   {path}: {'✅ EXISTE' if exists else '❌ NÃO EXISTE'}")

# 2. Mostrar working directory
print(f"\n2. WORKING DIRECTORY ATUAL:")
print(f"   {os.getcwd()}")

# 3. Testar importação do orchestrator
print(f"\n3. TESTE DE IMPORT DO ORCHESTRATOR:")
try:
    from orchestrator import get_possible_paths
    print("   ✅ get_possible_paths importado com sucesso")
    
    # Testar a função
    paths = get_possible_paths('escrituras', 'AFA Pool #1.json')
    print(f"\n4. CAMINHOS GERADOS PELA FUNÇÃO:")
    for i, path in enumerate(paths):
        exists = os.path.exists(path)
        print(f"   [{i}] {path}: {'✅' if exists else '❌'}")
        
except ImportError as e:
    print(f"   ❌ Erro de import: {e}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 5. Testar carregamento completo do orchestrator
print(f"\n5. TESTE COMPLETO DO ORCHESTRATOR:")
try:
    from orchestrator import run_monitoring
    print("   ✅ Orchestrator importado com sucesso")
    
    # Tentar executar para um pool
    print("\n6. EXECUTANDO MONITORAMENTO PARA AFA Pool #1:")
    resultado = run_monitoring('AFA Pool #1')
    
    if resultado['sucesso']:
        print("   ✅ SUCESSO! Monitoramento executado")
        print(f"   Pools processados: {resultado.get('pools_processados', [])}")
    else:
        print(f"   ❌ FALHA: {resultado.get('erro', 'Erro desconhecido')}")
        
except Exception as e:
    print(f"   ❌ Erro na execução: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)