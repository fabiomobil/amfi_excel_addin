#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 TESTE DAS FUNÇÕES PDD")
print("=" * 40)

try:
    print("1️⃣ Testando importações...")
    
    from monitor.utils.pdd_analysis import (
        load_historical_monitoring_data,
        get_pdd_pool_historical_analysis,
        get_pdd_cedente_breakdown_for_date,
        get_pdd_methodology_comparison,
        extract_pdd_data
    )
    print("✅ Todas as funções PDD importadas")
    
    print("\n2️⃣ Testando carregamento de dados históricos...")
    historical_data = load_historical_monitoring_data()
    print(f"✅ Dados históricos: {len(historical_data)} registros")
    
    if historical_data:
        print(f"📅 Data mais recente: {historical_data[0]['date']}")
        
        print("\n3️⃣ Testando análise de pool...")
        pool_history = get_pdd_pool_historical_analysis(
            'E-ctare Pool #1', 'pdd', '', historical_data
        )
        print(f"✅ Histórico pool: {len(pool_history)} registros")
        
        print("\n4️⃣ Testando breakdown cedentes...")
        cedente_breakdown = get_pdd_cedente_breakdown_for_date(
            'E-ctare Pool #1', 'latest', historical_data
        )
        print(f"✅ Breakdown cedentes: {len(cedente_breakdown)} registros")
        
        print("\n5️⃣ Testando comparação metodológica...")
        methodology_data = get_pdd_methodology_comparison(
            'E-ctare Pool #1', 'latest', historical_data
        )
        print(f"✅ Metodologia: {'Dados encontrados' if methodology_data else 'Sem dados'}")
    
    print("\n🎉 Todos os testes passaram!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()