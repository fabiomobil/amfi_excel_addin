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

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import monitor.orchestrator as orchestrator
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Erro ao importar módulo de monitoramento",
        "timestamp": datetime.now().isoformat()
    }))
    sys.exit(1)

def check_if_already_run_today():
    """Verifica se o monitoramento já foi executado hoje."""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = f"/mnt/c/amfi/data/output/monitoring_results/daily_consolidated/{today}.json"
    
    if os.path.exists(daily_file):
        # Verificar se o arquivo foi modificado hoje
        file_mtime = datetime.fromtimestamp(os.path.getmtime(daily_file))
        if file_mtime.date() == datetime.now().date():
            return True, daily_file
    
    return False, daily_file

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
    
    # Verificar se já foi executado hoje
    already_run, daily_file = check_if_already_run_today()
    
    response = {
        "already_run_today": already_run,
        "daily_file": daily_file,
        "force_run": force_run
    }
    
    if already_run and not force_run:
        response.update({
            "success": False,
            "message": "Monitoramento já foi executado hoje",
            "action_required": "confirm_overwrite",
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Executar monitoramento
        result = run_monitoring()
        response.update(result)
        
        # Se foi bem-sucedido, gerar dashboard
        if result.get("success", False):
            try:
                print("🎨 Gerando dashboard atualizado...")
                import subprocess
                subprocess.run([
                    sys.executable, 
                    "/mnt/c/amfi/generate_table_dashboard.py"
                ], check=True, capture_output=True, text=True)
                response["dashboard_updated"] = True
                print("✅ Dashboard atualizado!")
            except Exception as e:
                response["dashboard_updated"] = False
                response["dashboard_error"] = str(e)
                print(f"⚠️ Erro ao atualizar dashboard: {e}")
    
    # Retornar JSON para o frontend
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()