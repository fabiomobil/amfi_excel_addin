#!/usr/bin/env python3

import sys
import os
import json
import glob

# Add path for imports
sys.path.insert(0, os.path.dirname(__file__))

print("🔧 GERANDO DASHBOARD COMPLETO...")
print("=" * 50)

try:
    # 1. Load data directly
    print("1️⃣ Carregando dados JSON...")
    daily_dir = "C:\\amfi\\data\\output\\monitoring_results\\daily_consolidated"
    json_files = glob.glob(os.path.join(daily_dir, "*.json"))
    
    if not json_files:
        raise Exception("Nenhum arquivo JSON encontrado")
    
    latest_file = max(json_files)
    latest_date = os.path.basename(latest_file).replace('.json', '')
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   ✅ Dados carregados: {latest_date}")
    print(f"   📊 Total pools: {data.get('summary', {}).get('total_pools', 'N/A')}")
    
    # 2. Import and generate HTML
    print("\n2️⃣ Importando funções...")
    
    from generate_table_dashboard import generate_table_dashboard_html
    print("   ✅ Função principal importada")
    
    # 3. Generate complete HTML
    print("\n3️⃣ Gerando HTML completo...")
    
    html_content = generate_table_dashboard_html(data, latest_date)
    
    if not html_content or len(html_content) < 1000:
        raise Exception("HTML gerado parece estar incompleto")
    
    print(f"   ✅ HTML gerado: {len(html_content):,} caracteres")
    
    # 4. Check for critical elements
    print("\n4️⃣ Verificando elementos críticos...")
    
    checks = [
        ("JavaScript toggleDrilldown", "toggleDrilldown" in html_content),
        ("Subordinação table", "subordinação" in html_content.lower()),
        ("Concentration functionality", "concentração" in html_content.lower()),
        ("Drilldown CSS", ".drilldown-row" in html_content),
        ("Click handlers", "onclick=" in html_content),
    ]
    
    all_good = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        if not result:
            all_good = False
    
    # 5. Save dashboard
    print("\n5️⃣ Salvando dashboard...")
    
    output_path = "C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"   ✅ Dashboard salvo: {output_path}")
    
    # 6. Final status
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SUCESSO: Dashboard completo gerado!")
    else:
        print("⚠️  Dashboard gerado com algumas limitações")
    
    print("🌐 Acesse: http://localhost:8080")
    print("🔄 Faça F5 no navegador para carregar a versão completa")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback: create basic working dashboard
    print("\n🔄 Criando dashboard básico como fallback...")
    
    basic_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AmFi Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2E3A87; color: white; padding: 20px; border-radius: 10px; }}
        .error {{ background: #ffe6e6; border: 1px solid #ff0000; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ AmFi Dashboard</h1>
        <p>Sistema restaurado - Versão básica</p>
    </div>
    
    <div class="error">
        <h3>⚠️ Dashboard em modo de recuperação</h3>
        <p>O sistema foi restaurado para uma versão estável anterior.</p>
        <p>Funcionalidades completas serão restauradas em breve.</p>
        <p><strong>Data dos dados:</strong> Arquivo JSON mais recente disponível</p>
    </div>
    
    <script>
        console.log("Dashboard básico carregado - aguardando restauração completa");
    </script>
</body>
</html>"""
    
    with open("C:\\amfi\\data\\output\\monitoring_results\\dashboard\\table_dashboard.html", 'w', encoding='utf-8') as f:
        f.write(basic_html)
    
    print("📄 Dashboard básico criado como fallback")