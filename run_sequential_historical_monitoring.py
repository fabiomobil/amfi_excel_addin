"""
Script para processamento sequencial de dados históricos.

Estratégia:
1. Todos os arquivos estão em csv/files/ e xlsx/files/
2. Para cada data, move o arquivo correspondente para a pasta raiz
3. Executa o monitoramento (data_loader pega automaticamente o arquivo como "mais recente")
4. Deixa o arquivo na raiz e continua para próxima data
5. Evita duplicação verificando se JSON já existe
"""

import os
import sys
import shutil
import glob
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, '/mnt/c/amfi')

from monitor.orchestrator import run_monitoring

def get_target_dates():
    """Retorna as datas que queremos processar em ordem cronológica."""
    return [
        "2025-07-11",
        "2025-07-14", 
        "2025-07-15",
        "2025-07-16",
        "2025-07-17"
    ]

def find_csv_file_for_date(date_str):
    """
    Encontra o arquivo CSV para uma data específica.
    
    Args:
        date_str: Data no formato "2025-07-11"
        
    Returns:
        Caminho completo do arquivo CSV ou None se não encontrado
    """
    # Converter formato: 2025-07-11 -> 11-07-2025
    date_parts = date_str.split('-')
    formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
    
    csv_files_dir = "/mnt/c/amfi/data/input/csv/files"
    pattern = f"AcompanhamentoDeOportunidades-{formatted_date}.csv"
    file_path = os.path.join(csv_files_dir, pattern)
    
    if os.path.exists(file_path):
        return file_path
    
    # Se não encontrou o padrão exato, tentar buscar por glob
    search_pattern = os.path.join(csv_files_dir, f"*{formatted_date}*.csv")
    matches = glob.glob(search_pattern)
    
    if matches:
        return matches[0]
    
    return None

def find_xlsx_file_for_date(date_str):
    """
    Encontra o arquivo XLSX para uma data específica.
    
    Args:
        date_str: Data no formato "2025-07-11"
        
    Returns:
        Caminho completo do arquivo XLSX ou None se não encontrado
    """
    xlsx_files_dir = "/mnt/c/amfi/data/input/xlsx/files"
    
    # Procurar arquivo que comece com "Carteira Global YYYY-MM-DD"
    pattern = f"Carteira Global {date_str}*"
    search_pattern = os.path.join(xlsx_files_dir, pattern)
    matches = glob.glob(search_pattern)
    
    if matches:
        return matches[0]
    
    return None

def move_file_to_root(source_file, target_dir):
    """
    Move arquivo do subdiretório files/ para a pasta raiz.
    
    Args:
        source_file: Caminho completo do arquivo fonte
        target_dir: Diretório de destino (raiz)
        
    Returns:
        Caminho do arquivo movido
    """
    filename = os.path.basename(source_file)
    target_file = os.path.join(target_dir, filename)
    
    # Se já existe arquivo no destino, remove
    if os.path.exists(target_file):
        os.remove(target_file)
    
    shutil.move(source_file, target_file)
    return target_file

def json_already_exists(date_str):
    """
    Verifica se já existe JSON consolidado para a data.
    
    Args:
        date_str: Data no formato "2025-07-11"
        
    Returns:
        True se JSON já existe
    """
    json_path = f"/mnt/c/amfi/data/output/monitoring_results/daily_consolidated/{date_str}.json"
    return os.path.exists(json_path)

def process_date(date_str, force_reprocess=True):
    """
    Processa uma data específica.
    
    Args:
        date_str: Data no formato "2025-07-11"
        force_reprocess: Se True, reprocessa mesmo que JSON já exista
        
    Returns:
        True se processamento foi bem-sucedido
    """
    print(f"\n{'='*70}")
    print(f"🔄 Processando data: {date_str}")
    print(f"{'='*70}")
    
    # Verificar se JSON já existe
    if json_already_exists(date_str) and not force_reprocess:
        print(f"⚠️  JSON já existe para {date_str}. Pulando... (use force_reprocess=True para reprocessar)")
        return True
    
    # Encontrar arquivos para a data
    csv_file = find_csv_file_for_date(date_str)
    xlsx_file = find_xlsx_file_for_date(date_str)
    
    if not csv_file:
        print(f"❌ CSV não encontrado para {date_str}")
        return False
        
    if not xlsx_file:
        print(f"❌ XLSX não encontrado para {date_str}")
        return False
    
    print(f"📁 CSV encontrado: {os.path.basename(csv_file)}")
    print(f"📊 XLSX encontrado: {os.path.basename(xlsx_file)}")
    
    try:
        # Mover arquivos para pasta raiz
        csv_target_dir = "/mnt/c/amfi/data/input/csv"
        xlsx_target_dir = "/mnt/c/amfi/data/input/xlsx"
        
        print(f"📦 Movendo CSV para pasta raiz...")
        moved_csv = move_file_to_root(csv_file, csv_target_dir)
        
        print(f"📦 Movendo XLSX para pasta raiz...")
        moved_xlsx = move_file_to_root(xlsx_file, xlsx_target_dir)
        
        # Executar monitoramento
        print(f"🔄 Executando monitoramento...")
        results = run_monitoring()
        
        # Verificar resultado
        if isinstance(results, dict) and results.get('sucesso', False):
            stats = results.get('estatisticas', {})
            print(f"✅ Monitoramento concluído com sucesso!")
            print(f"📊 Pools processados: {stats.get('total', 0)}")
            print(f"✅ Pools com sucesso: {stats.get('sucesso', 0)}")
            print(f"❌ Pools com erro: {stats.get('erro', 0)}")
            print(f"📈 Taxa de sucesso: {stats.get('taxa_sucesso', 0)}%")
            
            # Verificar se JSON foi criado
            if json_already_exists(date_str):
                print(f"✅ JSON consolidado criado: {date_str}.json")
                return True
            else:
                print(f"⚠️  JSON não foi criado para {date_str}")
                return False
        else:
            print(f"❌ Erro no monitoramento: {results}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {date_str}: {e}")
        print(f"💡 Detalhes do erro: {type(e).__name__}")
        return False

def main():
    """Função principal."""
    print("🚀 Iniciando processamento sequencial de dados históricos")
    print("📋 Estratégia: mover arquivos sequencialmente para pasta raiz")
    print("="*70)
    
    dates = get_target_dates()
    success_count = 0
    processed_dates = []
    failed_dates = []
    
    for date_str in dates:
        print(f"\n🎯 Iniciando processamento de {date_str}...")
        
        if process_date(date_str, force_reprocess=False):
            success_count += 1
            processed_dates.append(date_str)
            print(f"✅ {date_str} processado com sucesso!")
        else:
            failed_dates.append(date_str)
            print(f"❌ Falha no processamento de {date_str}")
    
    # Resumo final
    print(f"\n{'='*70}")
    print(f"📈 RESUMO FINAL DO PROCESSAMENTO")
    print(f"{'='*70}")
    print(f"✅ Datas processadas com sucesso: {success_count}/{len(dates)}")
    print(f"📅 Datas processadas: {', '.join(processed_dates)}")
    
    if failed_dates:
        print(f"❌ Datas com falha: {', '.join(failed_dates)}")
    
    if success_count == len(dates):
        print("🎉 Todos os dias foram processados com sucesso!")
        print("🔄 Execute o dashboard: python3 generate_table_dashboard.py")
    else:
        print(f"⚠️  {len(failed_dates)} dias tiveram problemas no processamento.")
    
    print(f"\n📁 Resultados salvos em: /mnt/c/amfi/data/output/monitoring_results/daily_consolidated/")
    
    # Mostrar status dos arquivos na raiz
    csv_root = "/mnt/c/amfi/data/input/csv"
    xlsx_root = "/mnt/c/amfi/data/input/xlsx"
    
    csv_files = [f for f in os.listdir(csv_root) if f.endswith('.csv')]
    xlsx_files = [f for f in os.listdir(xlsx_root) if f.endswith('.xlsx')]
    
    print(f"\n📁 Arquivos atualmente na pasta raiz:")
    print(f"   CSV: {csv_files}")
    print(f"   XLSX: {xlsx_files}")

if __name__ == "__main__":
    main()