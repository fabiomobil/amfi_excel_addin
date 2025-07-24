#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from generate_table_dashboard import load_latest_json_data, generate_table_dashboard_html

# Load data
data, date = load_latest_json_data()
print(f"Data loaded: {date}")

# Generate HTML
html_content = generate_table_dashboard_html(data, date)
print(f"HTML generated: {len(html_content)} chars")

# Save dashboard
output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Dashboard saved: {output_path}")