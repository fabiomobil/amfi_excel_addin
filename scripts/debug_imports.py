#!/usr/bin/env python3
"""
Debug de imports - verifica cada módulo individualmente
"""

import sys
import os

# Adicionar caminhos ao PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitor'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitor', 'utils'))

modules_to_test = [
    ('alerts', 'monitor.utils.alerts'),
    ('file_discovery', 'monitor.utils.file_discovery'),
    ('data_converters', 'monitor.utils.data_converters'),
    ('data_handler', 'monitor.utils.data_handler'),
    ('file_loaders', 'monitor.utils.file_loaders'),
    ('data_loader', 'monitor.utils.data_loader'),
]

print("🔍 Testando imports dos módulos...\n")

for module_name, full_path in modules_to_test:
    try:
        # Tentar import direto
        exec(f"import {module_name}")
        print(f"✅ {module_name}: Import direto OK")
    except Exception as e:
        print(f"❌ {module_name}: Import direto falhou - {type(e).__name__}: {str(e)[:50]}...")
        
    try:
        # Tentar import com caminho completo
        exec(f"import {full_path}")
        print(f"✅ {full_path}: Import completo OK")
    except Exception as e:
        print(f"❌ {full_path}: Import completo falhou - {type(e).__name__}: {str(e)[:50]}...")
    
    print("")

# Tentar importar a função principal
print("\n🔍 Testando import da função principal...")
try:
    from monitor.utils.data_loader import load_pool_data
    print("✅ load_pool_data importada com sucesso!")
except Exception as e:
    print(f"❌ Erro ao importar load_pool_data: {type(e).__name__}: {e}")

# Verificar se pandas está disponível
print("\n🔍 Verificando dependências externas...")
try:
    import pandas
    print(f"✅ pandas disponível (versão {pandas.__version__})")
except:
    print("❌ pandas não está instalado!")
    
try:
    import json
    print("✅ json disponível")
except:
    print("❌ json não disponível")
    
try:
    import xlwings
    print(f"✅ xlwings disponível")
except:
    print("❌ xlwings não está instalado!")