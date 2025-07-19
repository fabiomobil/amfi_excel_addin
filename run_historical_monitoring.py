"""
Script para executar monitoramento histórico dos últimos 5 dias
usando os CSVs e XLSXs específicos de cada data.
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, '/mnt/c/amfi')

from monitor.orchestrator import run_monitoring

def get_last_5_business_days():
    """Retorna as últimas 5 datas com dados disponíveis."""
    # Baseado nos arquivos disponíveis
    available_dates = [
        "2025-07-11",
        "2025-07-14", 
        "2025-07-15",
        "2025-07-16",
        "2025-07-17"
    ]
    return available_dates

def find_files_for_date(date_str):
    """Encontra os arquivos CSV e XLSX para uma data específica."""
    # Converter formato de data: 2025-07-11 -> 11-07-2025
    date_parts = date_str.split('-')
    formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
    
    csv_dir = "/mnt/c/amfi/data/input/csv"
    xlsx_dir = "/mnt/c/amfi/data/input/xlsx"
    
    # Procurar CSV
    csv_pattern = f"AcompanhamentoDeOportunidades-{formatted_date}.csv"
    csv_file = os.path.join(csv_dir, csv_pattern)
    
    # Procurar XLSX
    xlsx_pattern = f"Carteira Global {date_str}"
    xlsx_file = None
    
    for filename in os.listdir(xlsx_dir):
        if filename.startswith(xlsx_pattern):
            xlsx_file = os.path.join(xlsx_dir, filename)
            break
    
    return csv_file, xlsx_file

def create_temp_data_structure(date_str, csv_file, xlsx_file):
    """Cria estrutura temporária de dados para a data específica."""
    # Criar diretório temporário para a data
    temp_dir = f"/tmp/amfi_monitoring_{date_str}"
    temp_csv_dir = os.path.join(temp_dir, "csv")
    temp_xlsx_dir = os.path.join(temp_dir, "xlsx")
    
    os.makedirs(temp_csv_dir, exist_ok=True)
    os.makedirs(temp_xlsx_dir, exist_ok=True)
    
    # Copiar arquivos para estrutura temporária
    csv_dest = os.path.join(temp_csv_dir, os.path.basename(csv_file))
    xlsx_dest = os.path.join(temp_xlsx_dir, os.path.basename(xlsx_file))
    
    shutil.copy2(csv_file, csv_dest)
    shutil.copy2(xlsx_file, xlsx_dest)
    
    return temp_dir, csv_dest, xlsx_dest

def cleanup_temp_structure(temp_dir):
    """Remove estrutura temporária."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def run_monitoring_for_date(date_str, csv_file, xlsx_file):
    """Executa o monitoramento para uma data específica."""
    print(f"\n{'='*60}")
    print(f"🔄 Executando monitoramento para {date_str}")
    print(f"📁 CSV: {os.path.basename(csv_file) if csv_file else 'NÃO ENCONTRADO'}")
    print(f"📊 XLSX: {os.path.basename(xlsx_file) if xlsx_file else 'NÃO ENCONTRADO'}")
    print(f"{'='*60}")
    
    if not csv_file or not os.path.exists(csv_file):
        print(f"❌ CSV não encontrado para {date_str}")
        return False
        
    if not xlsx_file or not os.path.exists(xlsx_file):
        print(f"❌ XLSX não encontrado para {date_str}")
        return False
    
    temp_dir = None
    try:
        # Converter data para formato dd/mm/aaaa
        date_parts = date_str.split('-')
        date_formatted = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        
        # Criar estrutura temporária
        print(f"📋 Preparando ambiente temporário...")
        temp_dir, csv_temp, xlsx_temp = create_temp_data_structure(date_str, csv_file, xlsx_file)
        
        # Modificar temporariamente variáveis de ambiente se necessário
        original_data_path = os.environ.get('AMFI_DATA_PATH')
        os.environ['AMFI_DATA_PATH'] = temp_dir
        
        # Executar monitoramento com data específica
        print(f"🔄 Executando monitoramento...")
        results = run_monitoring()
        
        print(f"✅ Monitoramento concluído para {date_str}")
        
        # Mostrar estatísticas
        if isinstance(results, dict) and results.get('sucesso', False):
            stats = results.get('estatisticas', {})
            print(f"📊 Pools processados: {stats.get('total', 0)}")
            print(f"✅ Pools com sucesso: {stats.get('sucesso', 0)}")
            print(f"❌ Pools com erro: {stats.get('erro', 0)}")
            print(f"📈 Taxa de sucesso: {stats.get('taxa_sucesso', 0)}%")
        else:
            print(f"⚠️  Resultado inesperado: {results}")
        
        # Restaurar variável de ambiente
        if original_data_path:
            os.environ['AMFI_DATA_PATH'] = original_data_path
        elif 'AMFI_DATA_PATH' in os.environ:
            del os.environ['AMFI_DATA_PATH']
        
        # Cleanup
        cleanup_temp_structure(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {date_str}: {e}")
        print(f"💡 Detalhes do erro: {type(e).__name__}")
        
        # Garantir cleanup mesmo com erro
        if temp_dir:
            try:
                cleanup_temp_structure(temp_dir)
            except:
                pass
        
        # Restaurar variável de ambiente
        try:
            if original_data_path:
                os.environ['AMFI_DATA_PATH'] = original_data_path
            elif 'AMFI_DATA_PATH' in os.environ:
                del os.environ['AMFI_DATA_PATH']
        except:
            pass
            
        return False

def main():
    """Função principal."""
    print("🚀 Iniciando monitoramento histórico dos últimos 5 dias")
    print("="*60)
    
    dates = get_last_5_business_days()
    success_count = 0
    
    for date_str in dates:
        csv_file, xlsx_file = find_files_for_date(date_str)
        
        if run_monitoring_for_date(date_str, csv_file, xlsx_file):
            success_count += 1
        else:
            print(f"⚠️  Falha no processamento de {date_str}")
    
    print(f"\n{'='*60}")
    print(f"📈 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"✅ Datas processadas com sucesso: {success_count}/{len(dates)}")
    print(f"📊 Datas: {', '.join(dates)}")
    
    if success_count == len(dates):
        print("🎉 Todos os dias foram processados com sucesso!")
    else:
        print("⚠️  Alguns dias tiveram problemas no processamento.")
    
    print(f"\n📁 Resultados salvos em: /mnt/c/amfi/data/output/monitoring_results/daily_consolidated/")
    print("🔄 Execute o dashboard: python3 generate_table_dashboard.py")

if __name__ == "__main__":
    main()