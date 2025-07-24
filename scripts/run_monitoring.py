#!/usr/bin/env python3
"""
API Simples para Execução do Monitoramento AmFi via Dashboard
=============================================================

Script que funciona como endpoint para o dashboard executar monitoramento.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
import platform
import re
import glob

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

try:
    import src.monitor.orchestrator as orchestrator
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Erro ao importar módulo de monitoramento",
        "timestamp": datetime.now().isoformat()
    }))
    sys.exit(1)

def get_data_base_from_files():
    """Extrai a data base dos arquivos CSV e XLSX atuais."""
    project_root = Path(__file__).parent
    
    dates_found = []
    
    # Verificar CSV - formato DD-MM-YYYY
    csv_path = project_root / "data" / "input" / "csv"
    csv_files = list(csv_path.glob("*.csv"))
    for csv_file in csv_files:
        filename = csv_file.name
        # Padrão para CSV: DD-MM-YYYY
        csv_pattern = r'(\d{2}-\d{2}-\d{4})'
        match = re.search(csv_pattern, filename)
        if match:
            date_str = match.group(1)
            # Converter DD-MM-YYYY -> YYYY-MM-DD
            parts = date_str.split('-')
            normalized_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
            dates_found.append(normalized_date)
            print(f"📅 CSV: {filename} -> Data extraída: {normalized_date}")
            break
    
    # Verificar XLSX - formato YYYY-MM-DD
    xlsx_path = project_root / "data" / "input" / "xlsx"
    xlsx_files = list(xlsx_path.glob("*.xlsx"))
    for xlsx_file in xlsx_files:
        filename = xlsx_file.name
        # Padrão para XLSX: YYYY-MM-DD
        xlsx_pattern = r'(\d{4}-\d{2}-\d{2})'
        match = re.search(xlsx_pattern, filename)
        if match:
            date_str = match.group(1)
            # Já está no formato correto YYYY-MM-DD
            dates_found.append(date_str)
            print(f"📅 XLSX: {filename} -> Data extraída: {date_str}")
            break
    
    # Validar se as datas são consistentes
    if len(set(dates_found)) > 1:
        print(f"⚠️ Datas inconsistentes encontradas: {dates_found}")
        print("🔄 Usando a data mais recente encontrada...")
        return max(dates_found)
    elif dates_found:
        return dates_found[0]
    
    # Fallback para hoje se não encontrar datas
    fallback_date = datetime.now().strftime('%Y-%m-%d')
    print(f"⚠️ Nenhuma data encontrada nos arquivos, usando data atual: {fallback_date}")
    return fallback_date

def check_if_already_run_for_data_base():
    """Verifica se o monitoramento já foi executado para a data base atual."""
    # Obter a data base dos arquivos atuais
    data_base = get_data_base_from_files()
    
    # Usar caminhos relativos baseados na localização do script
    project_root = Path(__file__).parent
    daily_dir = project_root / "data" / "output" / "monitoring_results" / "daily_consolidated"
    daily_file = daily_dir / f"{data_base}.json"
    
    if daily_file.exists():
        # Retornar True se o arquivo existe para esta data base
        return True, str(daily_file), data_base
    
    return False, str(daily_file), data_base

def run_monitoring():
    """Executa o monitoramento completo."""
    try:
        print("🚀 Iniciando monitoramento AmFi...")
        
        # Executar monitoramento via orchestrator
        resultado = orchestrator.run_monitoring()
        
        if resultado.get("sucesso", False):
            print("✅ Monitoramento executado com sucesso!")
            return {
                "success": True,
                "message": "Monitoramento executado com sucesso",
                "stats": resultado.get("estatisticas", {}),
                "pools_processados": resultado.get("pools_processados", []),
                "timestamp": datetime.now().isoformat()
            }
        else:
            print("❌ Erro no monitoramento")
            return {
                "success": False,
                "error": resultado.get("erro", "Erro desconhecido"),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"💥 Erro crítico: {str(e)}")
        return {
            "success": False,
            "error": f"Erro crítico na execução: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Função principal da API."""
    
    # Verificar argumentos
    force_run = "--force" in sys.argv
    
    # Verificar se já foi executado para a data base atual
    already_run, daily_file, data_base = check_if_already_run_for_data_base()
    data_execucao = datetime.now().strftime('%Y-%m-%d')
    
    response = {
        "already_run_for_data_base": already_run,
        "data_base": data_base,
        "data_execucao": data_execucao,
        "daily_file": daily_file,
        "force_run": force_run
    }
    
    if already_run and not force_run:
        response.update({
            "success": False,
            "message": f"Monitoramento já foi executado para a data base {data_base}",
            "action_required": "confirm_overwrite",
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Executar monitoramento
        result = run_monitoring()
        response.update(result)
        
        # Adicionar informações de data
        response["data_base"] = data_base
        response["data_execucao"] = data_execucao
        
        # Se foi bem-sucedido, verificar se o arquivo foi gerado
        if result.get("success", False):
            # Verificar se o arquivo JSON foi criado para a data base
            project_root = Path(__file__).parent
            daily_dir = project_root / "data" / "output" / "monitoring_results" / "daily_consolidated"
            expected_file = daily_dir / f"{data_base}.json"
            
            # Aguardar um momento para o arquivo ser criado
            import time
            time.sleep(2)
            
            if expected_file.exists():
                print(f"✅ Arquivo JSON confirmado: {expected_file}")
                response["json_file_created"] = True
                response["json_file_path"] = str(expected_file)
                
                # Verificar se o arquivo tem conteúdo válido
                try:
                    with open(expected_file, 'r', encoding='utf-8') as f:
                        json_content = json.load(f)
                    file_size = expected_file.stat().st_size
                    response["json_file_size"] = file_size
                    response["json_validation"] = "valid"
                    print(f"📊 Arquivo JSON validado: {file_size} bytes")
                except Exception as e:
                    response["json_validation"] = f"invalid: {str(e)}"
                    print(f"⚠️ Erro na validação do JSON: {e}")
            else:
                print(f"❌ Arquivo JSON NÃO foi criado: {expected_file}")
                response["json_file_created"] = False
                response["json_file_path"] = str(expected_file)
                response["error"] = f"Arquivo JSON não foi gerado para a data base {data_base}"
                response["success"] = False
            
            # Gerar dashboard apenas se o JSON foi criado corretamente
            if response.get("json_file_created", False):
                try:
                    print("🎨 Gerando dashboard atualizado...")
                    import subprocess
                    
                    dashboard_script = project_root / "scripts" / "generate_dashboard.py"
                    
                    subprocess.run([
                        sys.executable, 
                        str(dashboard_script)
                    ], check=True, capture_output=True, text=True, cwd=str(project_root))
                    response["dashboard_updated"] = True
                    print("✅ Dashboard atualizado!")
                except Exception as e:
                    response["dashboard_updated"] = False
                    response["dashboard_error"] = str(e)
                    print(f"⚠️ Erro ao atualizar dashboard: {e}")
            else:
                response["dashboard_updated"] = False
                print("⚠️ Dashboard não foi atualizado pois o JSON não foi criado")
    
    # Retornar JSON para o frontend
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()