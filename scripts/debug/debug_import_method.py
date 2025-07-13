#!/usr/bin/env python3
"""
Debug detalhado do método de import usado
"""

import sys
import os

print("🔍 Debug de métodos de import\n")

# Mostrar estado inicial
print("📁 Diretório atual:", os.getcwd())
print("📄 Arquivo executado:", __file__)
print("🐍 Python path inicial:", sys.path[:3], "...\n")

# Testar cada método individualmente
print("=== TESTE 1: Import relativo ===")
try:
    from .file_loaders import load_dashboard
    print("✅ Método 1 funcionou (import relativo)")
except (ImportError, ValueError) as e:
    print(f"❌ Método 1 falhou: {type(e).__name__}: {e}")

print("\n=== TESTE 2: Import direto ===")
try:
    # Resetar para tentar novamente
    if 'file_loaders' in sys.modules:
        del sys.modules['file_loaders']
    
    from file_loaders import load_dashboard
    print("✅ Método 2 funcionou (import direto)")
except ImportError as e:
    print(f"❌ Método 2 falhou: {e}")

print("\n=== TESTE 3: Import com caminho absoluto ===")
try:
    # Resetar para tentar novamente
    if 'monitor.utils.file_loaders' in sys.modules:
        del sys.modules['monitor.utils.file_loaders']
    
    # Adicionar caminho raiz ao path
    root_path = os.path.join(os.path.dirname(__file__), '..', '..')
    if root_path not in sys.path:
        sys.path.insert(0, root_path)
    
    from monitor.utils.file_loaders import load_dashboard
    print("✅ Método 3 funcionou (caminho absoluto)")
except ImportError as e:
    print(f"❌ Método 3 falhou: {e}")

print("\n=== TESTE 4: Import do data_loader completo ===")
try:
    # Limpar imports anteriores
    for module in list(sys.modules.keys()):
        if module.startswith('file_loaders') or module.startswith('data_loader'):
            del sys.modules[module]
    
    from data_loader import load_pool_data
    print("✅ data_loader importado com sucesso!")
    
    # Verificar se está usando funções mock
    import data_loader
    if hasattr(data_loader, 'import_success'):
        print(f"📊 Status de import no data_loader: import_success = {data_loader.import_success}")
    
except ImportError as e:
    print(f"❌ Import do data_loader falhou: {e}")

print("\n🐍 Python path final:", sys.path[:5], "...")