#!/usr/bin/env python3
"""
Test dashboard generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from generate_table_dashboard import load_latest_json_data, generate_table_dashboard_html
    
    print("🧪 Testando geração do dashboard...")
    
    # Load data
    data, date = load_latest_json_data()
    if not data:
        print("❌ Erro ao carregar dados")
        sys.exit(1)
    
    print(f"📊 Dados carregados: {date}")
    
    # Generate HTML
    html_content = generate_table_dashboard_html(data, date)
    print(f"✅ HTML gerado: {len(html_content)} caracteres")
    
    # Save to test file
    with open("C:\\amfi\\test_dashboard.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("📄 Dashboard salvo em: test_dashboard.html")
    
    # Check for drilldown elements
    has_drilldown = "toggleDrilldown" in html_content
    has_concentration = "concentration" in html_content.lower()
    
    print(f"🔍 Drilldown JS: {'✅' if has_drilldown else '❌'}")
    print(f"🎯 Concentration: {'✅' if has_concentration else '❌'}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()