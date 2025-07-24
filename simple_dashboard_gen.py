import sys, os, json, glob
sys.path.insert(0, os.path.dirname(__file__))

# Load data
daily_dir = "C:\\amfi\\data\\output\\monitoring_results\\daily_consolidated"
json_files = glob.glob(os.path.join(daily_dir, "*.json"))
latest_file = max(json_files)
date = os.path.basename(latest_file).replace('.json', '')

with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Data loaded: {date}")

# Generate HTML
from generate_table_dashboard import generate_table_dashboard_html
html = generate_table_dashboard_html(data, date)

# Save
with open("C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html", 'w', encoding='utf-8') as f:
    f.write(html)

print("Dashboard generated successfully!")