#!/usr/bin/env python3
"""
Script de teste para verificar se data_loader funciona
"""

import sys
import os

# Adicionar o diretório ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitor', 'utils'))

try:
    from data_loader import load_pool_data
    print("✅ Import do data_loader bem-sucedido!")
    
    # Tentar executar a função
    print("\n🔄 Tentando executar load_pool_data()...")
    resultado = load_pool_data()
    
    if resultado:
        print(f"\n✅ Função executada! Sucesso: {resultado.get('sucesso', False)}")
        print(f"Pools processados: {len(resultado.get('pools_processados', []))}")
        print(f"Alertas: {len(resultado.get('alertas', []))}")
        
        # Mostrar alertas
        for alerta in resultado.get('alertas', []):
            print(f"  - [{alerta.get('tipo', 'info')}] {alerta.get('mensagem', '')}")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print(f"Módulo específico que falhou: {e.name if hasattr(e, 'name') else 'desconhecido'}")
    
except Exception as e:
    print(f"❌ Erro geral: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()