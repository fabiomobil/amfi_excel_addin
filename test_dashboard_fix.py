#!/usr/bin/env python3
"""
Test script para verificar se o dashboard está funcionando
"""

import json
import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from generate_table_dashboard import generate_table_dashboard_html, load_latest_json_data
    
    print("🧪 TESTE DO DASHBOARD - DRILLDOWN FIX")
    print("=" * 50)
    
    # Load latest data
    print("📥 Carregando dados mais recentes...")
    data, date = load_latest_json_data()
    
    if not data or not date:
        print("❌ Erro: Não foi possível carregar dados")
        sys.exit(1)
    
    print(f"✅ Dados carregados: {date}")
    print(f"📊 Total de pools: {data.get('summary', {}).get('total_pools', 'N/A')}")
    
    # Generate HTML
    print("\n🔧 Gerando HTML dashboard...")
    html_content = generate_table_dashboard_html(data, date)
    
    # Check for key drilldown elements
    print("\n🔍 Verificando elementos de drilldown:")
    
    checks = [
        ("toggleDrilldown function", "toggleDrilldown" in html_content),
        ("Subordinacao drilldown", "toggleDrilldown('sub_" in html_content),
        ("PDD drilldown", "toggleDrilldown('pdd_" in html_content), 
        ("Concentration drilldown", "toggleDrilldown('conc_" in html_content),
        ("JavaScript functions", "function toggle" in html_content or "const toggle" in html_content),
        ("CSS drilldown styles", ".drilldown-row" in html_content)
    ]
    
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
    
    # Save test output
    test_output = "C:\\amfi\\test_dashboard_output.html"
    with open(test_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n💾 Dashboard salvo em: {test_output}")
    
    all_passed = all(check[1] for check in checks)
    if all_passed:
        print("🎉 SUCESSO: Todos os elementos de drilldown estão presentes!")
    else:
        print("⚠️  ATENÇÃO: Alguns elementos de drilldown podem estar ausentes")
    
except Exception as e:
    print(f"❌ Erro durante teste: {e}")
    import traceback
    traceback.print_exc()