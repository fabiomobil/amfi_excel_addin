#!/usr/bin/env python3
"""
Generate dashboard HTML using the restored version
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from generate_table_dashboard import main
    print("🔧 Gerando dashboard com versão restaurada...")
    main()
    print("✅ Dashboard gerado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()