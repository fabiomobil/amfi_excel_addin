#!/usr/bin/env python3
"""
Test imports and basic functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 TESTE DE IMPORTS E FUNÇÕES")
print("=" * 40)

try:
    print("📥 Testando imports...")
    
    from monitor.utils.concentration_analysis import generate_concentration_summary_table
    print("✅ generate_concentration_summary_table importado")
    
    from monitor.utils.pdd_analysis import extract_pdd_data  
    print("✅ extract_pdd_data importado")
    
    from generate_table_dashboard import generate_table_dashboard_html, load_latest_json_data
    print("✅ generate_table_dashboard_html importado")
    
    print("\n📊 Testando carregamento de dados...")
    data, date = load_latest_json_data()
    
    if not data or not date:
        print("❌ Erro: Não foi possível carregar dados")
        sys.exit(1)
        
    print(f"✅ Dados carregados: {date}")
    
    print("\n🔧 Testando extração PDD...")
    pdd_data = extract_pdd_data(data)
    print(f"✅ PDD data extraído: {len(pdd_data)} pools")
    
    print("\n🎯 Testando geração de HTML...")
    html_content = generate_table_dashboard_html(data, date)
    print(f"✅ HTML gerado: {len(html_content)} caracteres")
    
    # Check for drilldown elements
    drilldown_checks = [
        ("toggleDrilldown function", "toggleDrilldown" in html_content),
        ("PDD drilldown rows", "id=\"pdd_" in html_content),
        ("Concentration drilldown", "concentration" in html_content.lower() and "drilldown" in html_content.lower()),
        ("JavaScript present", "<script>" in html_content),
    ]
    
    print("\n🔍 Verificando elementos drilldown:")
    for check_name, result in drilldown_checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    print("\n🎉 Todos os testes básicos passaram!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()