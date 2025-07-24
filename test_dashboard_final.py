#!/usr/bin/env python3
"""
Final test - verify drilldown functionality is working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🎯 TESTE FINAL - DRILLDOWN FUNCTIONALITY")
print("=" * 50)

try:
    # Test the import resolution
    from generate_table_dashboard import generate_table_dashboard_html, load_latest_json_data
    print("✅ Função principal importada")
    
    # Load data
    data, date = load_latest_json_data()
    if not data:
        print("❌ No data loaded")
        sys.exit(1)
    
    print(f"📊 Data loaded: {date}")
    
    # Generate HTML
    html_content = generate_table_dashboard_html(data, date)
    print(f"✅ HTML generated: {len(html_content)} chars")
    
    # Test critical drilldown elements
    critical_tests = [
        ("JavaScript toggleDrilldown function", "function toggleDrilldown(elementId)" in html_content),
        ("PDD drilldown rows", 'id="pdd_' in html_content and 'class="drilldown-row"' in html_content),
        ("Concentration drilldown rows", 'id="conc_' in html_content and 'class="drilldown-row"' in html_content), 
        ("Subordinacao drilldown rows", 'id="sub_' in html_content and 'class="drilldown-row"' in html_content),
        ("Click handlers", "onclick=\"toggleDrilldown(" in html_content),
        ("Drilldown CSS", ".drilldown-row" in html_content and ".drilldown-content" in html_content),
    ]
    
    print("\n🔍 DRILLDOWN FUNCTIONALITY CHECK:")
    all_passed = True
    for test_name, result in critical_tests:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if not result:
            all_passed = False
    
    # Save final output
    with open("C:\\amfi\\final_dashboard_test.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    if all_passed:
        print("\n🎉 SUCCESS: All drilldown functionality is present!")
        print("📄 Dashboard saved as: final_dashboard_test.html")
    else:
        print("\n⚠️  FAILURE: Some drilldown elements are missing")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()