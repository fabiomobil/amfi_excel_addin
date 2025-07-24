#!/usr/bin/env python3

# Direct dashboard creation
import os
import json
import glob
from datetime import datetime

# Load latest JSON data
daily_dir = "C:\\amfi\\data\\output\\monitoring_results\\daily_consolidated"
json_files = glob.glob(os.path.join(daily_dir, "*.json"))
latest_file = max(json_files)
latest_date = os.path.basename(latest_file).replace('.json', '')

with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ Loaded: {latest_date}")

# Import functions
import sys
sys.path.insert(0, os.path.dirname(__file__))

from generate_table_dashboard import generate_table_dashboard_html

# Generate HTML
html_content = generate_table_dashboard_html(data, latest_date)

# Create directory and save
output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Dashboard created: {output_path}")
print("🌐 Ready for http://localhost:8080")