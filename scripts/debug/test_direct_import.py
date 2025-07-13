#!/usr/bin/env python3
"""
Teste direto de import - simula execução do Spyder
"""

print("🔍 Testando imports diretos (como no Spyder)...\n")

# Teste 1: Import direto sem modificar sys.path
try:
    from file_loaders import load_dashboard, load_portfolio
    print("✅ Import direto de file_loaders OK")
except ImportError as e:
    print(f"❌ Import direto de file_loaders falhou: {e}")

# Teste 2: Import de data_handler
try:
    from data_handler import data_validation
    print("✅ Import direto de data_handler OK")
except ImportError as e:
    print(f"❌ Import direto de data_handler falhou: {e}")

# Teste 3: Import de alerts
try:
    from alerts import log_alerta
    print("✅ Import direto de alerts OK")
except ImportError as e:
    print(f"❌ Import direto de alerts falhou: {e}")

# Teste 4: Import de data_loader
try:
    from data_loader import load_pool_data
    print("✅ Import direto de data_loader OK")
    
    # Tentar executar
    print("\n🚀 Tentando executar load_pool_data()...")
    resultado = load_pool_data()
    print(f"✅ Execução completada! Sucesso: {resultado.get('sucesso', False)}")
    
except ImportError as e:
    print(f"❌ Import direto de data_loader falhou: {e}")
except Exception as e:
    print(f"❌ Erro na execução: {type(e).__name__}: {e}")