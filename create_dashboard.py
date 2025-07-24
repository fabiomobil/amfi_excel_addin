#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from generate_table_dashboard import load_latest_json_data, generate_table_dashboard_html

# Load data
data, date = load_latest_json_data()
if not data:
    print("❌ Erro ao carregar dados")
    sys.exit(1)

print(f"📊 Dados carregados: {date}")

# Generate HTML
html_content = generate_table_dashboard_html(data, date)

# Save dashboard
output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Dashboard gerado: {output_path}")
print("🌐 Acesse: http://localhost:8080")