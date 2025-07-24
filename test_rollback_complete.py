#!/usr/bin/env python3
"""
Test complete rollback functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🔄 TESTE COMPLETO - ROLLBACK PARA VERSÃO FUNCIONANDO")
print("=" * 60)

try:
    # 1. Test imports
    print("1️⃣ Testando imports...")
    
    from generate_table_dashboard import (
        load_latest_json_data, 
        generate_table_dashboard_html,
        extract_subordinacao_data,
        extract_concentracao_data
    )
    print("   ✅ Funções principais importadas")
    
    from monitor.utils.concentration_analysis import generate_concentration_summary_table
    print("   ✅ Função de concentração importada")
    
    # 2. Test data loading
    print("\n2️⃣ Testando carregamento de dados...")
    data, date = load_latest_json_data()
    
    if not data:
        print("   ❌ Erro ao carregar dados")
        sys.exit(1)
    
    print(f"   ✅ Dados carregados: {date}")
    print(f"   📊 Total pools: {data.get('summary', {}).get('total_pools', 'N/A')}")
    
    # 3. Test HTML generation
    print("\n3️⃣ Testando geração HTML...")
    html_content = generate_table_dashboard_html(data, date)
    
    if not html_content:
        print("   ❌ HTML não foi gerado")
        sys.exit(1)
    
    print(f"   ✅ HTML gerado: {len(html_content):,} caracteres")
    
    # 4. Test for critical elements
    print("\n4️⃣ Verificando elementos críticos...")
    
    critical_elements = [
        ("JavaScript toggleDrilldown", "function toggleDrilldown" in html_content),
        ("Concentration header", "concentração" in html_content.lower()),
        ("Subordinação table", "subordinação" in html_content.lower()),
        ("Drilldown CSS classes", ".drilldown-row" in html_content),
        ("Click handlers", "onclick=" in html_content),
        ("Modal functionality", "modal" in html_content.lower()),
    ]
    
    all_good = True
    for element_name, test_result in critical_elements:
        status = "✅" if test_result else "❌"
        print(f"   {status} {element_name}")
        if not test_result:
            all_good = False
    
    # 5. Create dashboard file
    print("\n5️⃣ Criando arquivo dashboard...")
    
    output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"   ✅ Dashboard salvo: {output_path}")
    
    # 6. Final result
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 SUCESSO: Rollback completo - tudo funcionando!")
        print("🌐 Servidor disponível em: http://localhost:8080")
    else:
        print("⚠️  ATENÇÃO: Alguns elementos podem estar faltando")
    
    print("📄 Dashboard criado e pronto para uso")
    
except Exception as e:
    print(f"❌ Erro durante teste: {e}")
    import traceback
    traceback.print_exc()