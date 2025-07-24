#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 DEBUG - Testing imports")

try:
    print("1. Testing load_latest_json_data...")
    from generate_table_dashboard import load_latest_json_data
    
    data, date = load_latest_json_data()
    print(f"   ✅ Data loaded: {date}, pools: {len(data.get('pools', {}))}")
    
    print("2. Testing generate_table_dashboard_html...")
    from generate_table_dashboard import generate_table_dashboard_html
    
    html = generate_table_dashboard_html(data, date)
    print(f"   ✅ HTML generated: {len(html)} chars")
    
    print("3. Testing concentration_analysis...")
    from monitor.utils.concentration_analysis import generate_concentration_summary_table
    
    conc_html = generate_concentration_summary_table(data)
    print(f"   ✅ Concentration HTML: {len(conc_html)} chars")
    
    print("4. Saving complete dashboard...")
    output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"   ✅ Dashboard saved: {output_path}")
    print("🎉 SUCCESS: All imports working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()