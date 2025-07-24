#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 TESTE FINAL - Dashboard pós rollback")
print("=" * 50)

try:
    # 1. Test imports
    from generate_table_dashboard import generate_table_dashboard_html, load_latest_json_data
    print("✅ Função principal importada")
    
    # 2. Load data
    data, date = load_latest_json_data()
    if not data:
        print("❌ Erro ao carregar dados")
        sys.exit(1)
    
    print(f"✅ Dados carregados: {date}")
    
    # 3. Generate HTML
    html_content = generate_table_dashboard_html(data, date)
    print(f"✅ HTML gerado: {len(html_content):,} caracteres")
    
    # 4. Save dashboard
    output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard salvo: {output_path}")
    
    # 5. Check critical elements
    checks = [
        ("JavaScript drilldown", "toggleDrilldown" in html_content),
        ("Subordinação", "subordinação" in html_content.lower()),
        ("Concentration", "concentration" in html_content.lower()),
        ("PDD dashboard", "pdd" in html_content.lower()),
        ("API calls", "/api/" in html_content),
    ]
    
    print("\n🔍 Verificando elementos críticos:")
    all_good = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        if not result:
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SUCESSO: Dashboard completamente funcional!")
        print("🌐 Acesse: http://localhost:8080")
    else:
        print("⚠️  Alguns elementos podem estar faltando")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()