#!/usr/bin/env python3
"""
Script para executar data_loader do diretório raiz
"""

import sys
import os

# Adicionar monitor/utils ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitor', 'utils'))

print("🚀 Executando data_loader...\n")

try:
    from data_loader import load_pool_data
    
    # Executar
    resultado = load_pool_data()
    
    # Resumo
    print(f"\n✅ Execução concluída!")
    print(f"Sucesso: {resultado.get('sucesso')}")
    print(f"Pools: {resultado.get('pools_processados')}")
    
    if resultado.get('erro'):
        print(f"❌ Erro: {resultado.get('erro')}")
    
    # Mostrar alertas importantes
    for alerta in resultado.get('alertas', []):
        if alerta.get('tipo') in ['error', 'warning']:
            print(f"⚠️ [{alerta['tipo']}] {alerta['mensagem']}")

except Exception as e:
    print(f"❌ Falha completa: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()