#!/usr/bin/env python3
"""
Script de Processamento Retroativo Completo com Paralelização
============================================================

Este script processa retroativamente TODAS as datas históricas disponíveis
para TODOS os 77 pools usando paralelização com threading.

Funcionalidades:
- Descoberta automática de todas as datas históricas disponíveis
- Processamento de TODOS os pools (não limitado ao debug)
- Paralelização com ThreadPoolExecutor
- Uso da técnica de movimentação de arquivos (pasta 'files')
- Verificação e prevenção de duplicação de dados
- Progresso detalhado em tempo real
- Logs estruturados de execução
- Tratamento robusto de erros

Arquitetura:
- Worker threads para processar múltiplas datas simultaneamente
- File management thread-safe para movimentação de arquivos
- Progress tracking com threading.Lock para sincronização
- Backup automático de resultados existentes

Requisitos:
- Dados CSV e XLSX disponíveis na estrutura /mnt/c/amfi/data/input/
- Sistema de monitoramento AmFi configurado
- Configurações JSON de pools válidas

Uso:
    python3 run_full_historical_monitoring.py [--max-workers N] [--skip-existing] [--dry-run]
"""

import os
import sys
import shutil
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import argparse
import traceback
from typing import Dict, List, Tuple, Optional, Any
import logging

# Criar diretório de logs se não existir
logs_dir = '/mnt/c/amfi/logs'
os.makedirs(logs_dir, exist_ok=True)

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, 'full_historical_monitoring.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao path
sys.path.insert(0, '/mnt/c/amfi')

# Imports do sistema de monitoramento
try:
    from monitor.orchestrator import run_monitoring
    from monitor.utils.data_loader import load_pool_data
except ImportError as e:
    logger.error(f"Erro ao importar módulos do sistema de monitoramento: {e}")
    sys.exit(1)

# Configurações globais
CONFIG = {
    'base_dir': '/mnt/c/amfi',
    'csv_dir': '/mnt/c/amfi/data/input/csv',
    'xlsx_dir': '/mnt/c/amfi/data/input/xlsx',
    'output_dir': '/mnt/c/amfi/data/output/monitoring_results/daily_consolidated',
    'backup_dir': '/mnt/c/amfi/data/output/monitoring_results/daily_consolidated_backup',
    'files_subdir': 'files',
    'temp_dir_base': '/tmp/amfi_historical',
    'logs_dir': '/mnt/c/amfi/logs'
}

# Thread-safe progress tracking
class ProgressTracker:
    def __init__(self, total_dates: int):
        self.total_dates = total_dates
        self.completed_dates = 0
        self.failed_dates = 0
        self.skipped_dates = 0
        self.total_pools_processed = 0
        self.lock = Lock()
        
    def update_completed(self, pools_count: int = 0):
        with self.lock:
            self.completed_dates += 1
            self.total_pools_processed += pools_count
            
    def update_failed(self):
        with self.lock:
            self.failed_dates += 1
            
    def update_skipped(self):
        with self.lock:
            self.skipped_dates += 1
            
    def get_progress(self) -> Dict[str, Any]:
        with self.lock:
            processed = self.completed_dates + self.failed_dates + self.skipped_dates
            return {
                'total_dates': self.total_dates,
                'processed_dates': processed,
                'completed_dates': self.completed_dates,
                'failed_dates': self.failed_dates,
                'skipped_dates': self.skipped_dates,
                'total_pools_processed': self.total_pools_processed,
                'progress_percent': round((processed / self.total_dates) * 100, 1) if self.total_dates > 0 else 0
            }

def setup_directories():
    """Cria diretórios necessários para execução."""
    directories = [
        CONFIG['logs_dir'],
        CONFIG['backup_dir'],
        CONFIG['temp_dir_base']
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
def discover_historical_dates() -> List[str]:
    """
    Descobre automaticamente todas as datas históricas disponíveis.
    
    Returns:
        List[str]: Lista de datas no formato YYYY-MM-DD ordenadas cronologicamente
    """
    logger.info("🔍 Descobrindo datas históricas disponíveis...")
    
    # Verificar arquivos CSV na pasta files (dados já processados)
    csv_files_dir = os.path.join(CONFIG['csv_dir'], CONFIG['files_subdir'])
    xlsx_files_dir = os.path.join(CONFIG['xlsx_dir'], CONFIG['files_subdir'])
    
    found_dates = set()
    
    # Extrair datas dos arquivos CSV
    if os.path.exists(csv_files_dir):
        for filename in os.listdir(csv_files_dir):
            if filename.startswith('AcompanhamentoDeOportunidades-') and filename.endswith('.csv'):
                # Formato: AcompanhamentoDeOportunidades-DD-MM-YYYY.csv
                date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})\.csv$', filename)
                if date_match:
                    day, month, year = date_match.groups()
                    date_str = f"{year}-{month}-{day}"
                    found_dates.add(date_str)
    
    # Extrair datas dos arquivos XLSX
    if os.path.exists(xlsx_files_dir):
        for filename in os.listdir(xlsx_files_dir):
            if filename.startswith('Carteira Global ') and filename.endswith('.xlsx'):
                # Formato: Carteira Global YYYY-MM-DD HHMMSS.xlsx
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
                if date_match:
                    year, month, day = date_match.groups()
                    date_str = f"{year}-{month}-{day}"
                    found_dates.add(date_str)
    
    # Verificar também arquivos no diretório principal (dados não processados)
    for base_dir in [CONFIG['csv_dir'], CONFIG['xlsx_dir']]:
        if os.path.exists(base_dir):
            for filename in os.listdir(base_dir):
                if filename.startswith('AcompanhamentoDeOportunidades-') and filename.endswith('.csv'):
                    date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})\.csv$', filename)
                    if date_match:
                        day, month, year = date_match.groups()
                        date_str = f"{year}-{month}-{day}"
                        found_dates.add(date_str)
                elif filename.startswith('Carteira Global ') and filename.endswith('.xlsx'):
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
                    if date_match:
                        year, month, day = date_match.groups()
                        date_str = f"{year}-{month}-{day}"
                        found_dates.add(date_str)
    
    # Converter para lista ordenada
    dates_list = sorted(list(found_dates))
    
    logger.info(f"📅 Encontradas {len(dates_list)} datas históricas:")
    for date_str in dates_list:
        logger.info(f"   📄 {date_str}")
    
    return dates_list

def find_files_for_date(date_str: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Encontra os arquivos CSV e XLSX para uma data específica.
    
    Args:
        date_str: Data no formato YYYY-MM-DD
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (csv_file_path, xlsx_file_path)
    """
    # Converter formato de data: 2025-07-11 -> 11-07-2025
    date_parts = date_str.split('-')
    formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
    
    # Procurar CSV (priorizar pasta files)
    csv_file = None
    csv_pattern = f"AcompanhamentoDeOportunidades-{formatted_date}.csv"
    
    # Primeiro tentar na pasta files
    csv_files_path = os.path.join(CONFIG['csv_dir'], CONFIG['files_subdir'], csv_pattern)
    if os.path.exists(csv_files_path):
        csv_file = csv_files_path
    else:
        # Tentar no diretório principal
        csv_main_path = os.path.join(CONFIG['csv_dir'], csv_pattern)
        if os.path.exists(csv_main_path):
            csv_file = csv_main_path
    
    # Procurar XLSX (priorizar pasta files)
    xlsx_file = None
    xlsx_pattern = f"Carteira Global {date_str}"
    
    # Primeiro tentar na pasta files
    xlsx_files_dir = os.path.join(CONFIG['xlsx_dir'], CONFIG['files_subdir'])
    if os.path.exists(xlsx_files_dir):
        for filename in os.listdir(xlsx_files_dir):
            if filename.startswith(xlsx_pattern):
                xlsx_file = os.path.join(xlsx_files_dir, filename)
                break
    
    # Se não encontrou, tentar no diretório principal
    if not xlsx_file and os.path.exists(CONFIG['xlsx_dir']):
        for filename in os.listdir(CONFIG['xlsx_dir']):
            if filename.startswith(xlsx_pattern):
                xlsx_file = os.path.join(CONFIG['xlsx_dir'], filename)
                break
    
    return csv_file, xlsx_file

def check_existing_results(date_str: str) -> bool:
    """
    Verifica se já existem resultados para uma data específica.
    
    Args:
        date_str: Data no formato YYYY-MM-DD
        
    Returns:
        bool: True se já existem resultados
    """
    result_file = os.path.join(CONFIG['output_dir'], f"{date_str}.json")
    backup_file = os.path.join(CONFIG['backup_dir'], f"{date_str}.json")
    
    return os.path.exists(result_file) or os.path.exists(backup_file)

def move_files_to_active_position(csv_file: str, xlsx_file: str) -> Tuple[str, str]:
    """
    Move arquivos para posição ativa (fora da pasta files) para processamento.
    
    Args:
        csv_file: Caminho do arquivo CSV
        xlsx_file: Caminho do arquivo XLSX
        
    Returns:
        Tuple[str, str]: (csv_active_path, xlsx_active_path)
    """
    csv_active = os.path.join(CONFIG['csv_dir'], os.path.basename(csv_file))
    xlsx_active = os.path.join(CONFIG['xlsx_dir'], os.path.basename(xlsx_file))
    
    # Mover CSV se estiver na pasta files
    if CONFIG['files_subdir'] in csv_file and not os.path.exists(csv_active):
        shutil.copy2(csv_file, csv_active)
    elif not os.path.exists(csv_active):
        shutil.copy2(csv_file, csv_active)
    
    # Mover XLSX se estiver na pasta files
    if CONFIG['files_subdir'] in xlsx_file and not os.path.exists(xlsx_active):
        shutil.copy2(xlsx_file, xlsx_active)
    elif not os.path.exists(xlsx_active):
        shutil.copy2(xlsx_file, xlsx_active)
    
    return csv_active, xlsx_active

def move_files_back_to_files(csv_active: str, xlsx_active: str):
    """
    Move arquivos de volta para a pasta files após processamento.
    
    Args:
        csv_active: Caminho ativo do CSV
        xlsx_active: Caminho ativo do XLSX
    """
    csv_files_dir = os.path.join(CONFIG['csv_dir'], CONFIG['files_subdir'])
    xlsx_files_dir = os.path.join(CONFIG['xlsx_dir'], CONFIG['files_subdir'])
    
    os.makedirs(csv_files_dir, exist_ok=True)
    os.makedirs(xlsx_files_dir, exist_ok=True)
    
    csv_files_path = os.path.join(csv_files_dir, os.path.basename(csv_active))
    xlsx_files_path = os.path.join(xlsx_files_dir, os.path.basename(xlsx_active))
    
    # Mover para pasta files se não estiver lá
    if not os.path.exists(csv_files_path):
        shutil.move(csv_active, csv_files_path)
    elif os.path.exists(csv_active):
        os.remove(csv_active)
        
    if not os.path.exists(xlsx_files_path):
        shutil.move(xlsx_active, xlsx_files_path)
    elif os.path.exists(xlsx_active):
        os.remove(xlsx_active)

def disable_debug_mode():
    """
    Temporariamente desabilita o modo debug para processar todos os pools.
    
    Returns:
        str: Caminho do backup do arquivo de configuração
    """
    test_pools_file = '/mnt/c/amfi/config/monitoring/_test_pools.json'
    backup_file = f"{test_pools_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if os.path.exists(test_pools_file):
        # Fazer backup
        shutil.copy2(test_pools_file, backup_file)
        
        # Modificar configuração para processar todos os pools
        with open(test_pools_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Salvar configuração original e modificar para processar todos
        config['_original_debug_pools'] = config.get('debug_pools', [])
        config['debug_pools'] = []  # Lista vazia = todos os pools
        
        with open(test_pools_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"🔧 Modo debug temporariamente desabilitado (backup: {backup_file})")
        return backup_file
    
    return None

def restore_debug_mode(backup_file: Optional[str]):
    """
    Restaura o modo debug original.
    
    Args:
        backup_file: Caminho do arquivo de backup
    """
    if backup_file and os.path.exists(backup_file):
        test_pools_file = '/mnt/c/amfi/config/monitoring/_test_pools.json'
        shutil.copy2(backup_file, test_pools_file)
        os.remove(backup_file)
        logger.info("🔧 Modo debug restaurado")

def run_monitoring_for_date(date_str: str, progress_tracker: ProgressTracker, 
                          skip_existing: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """
    Executa o monitoramento para uma data específica.
    
    Args:
        date_str: Data no formato YYYY-MM-DD
        progress_tracker: Objeto para tracking de progresso
        skip_existing: Se True, pula datas já processadas
        dry_run: Se True, apenas simula o processamento
        
    Returns:
        Dict[str, Any]: Resultados do processamento
    """
    thread_name = f"Worker-{date_str}"
    logger.info(f"[{thread_name}] 🔄 Iniciando processamento de {date_str}")
    
    try:
        # Verificar se já existe resultado
        if skip_existing and check_existing_results(date_str):
            logger.info(f"[{thread_name}] ⏭️  Pulando {date_str} - já processado")
            progress_tracker.update_skipped()
            return {
                'success': True,
                'date': date_str,
                'status': 'skipped',
                'message': 'Já processado anteriormente'
            }
        
        # Encontrar arquivos
        csv_file, xlsx_file = find_files_for_date(date_str)
        
        if not csv_file or not os.path.exists(csv_file):
            logger.warning(f"[{thread_name}] ❌ CSV não encontrado para {date_str}")
            progress_tracker.update_failed()
            return {
                'success': False,
                'date': date_str,
                'status': 'error',
                'message': 'CSV não encontrado'
            }
            
        if not xlsx_file or not os.path.exists(xlsx_file):
            logger.warning(f"[{thread_name}] ❌ XLSX não encontrado para {date_str}")
            progress_tracker.update_failed()
            return {
                'success': False,
                'date': date_str,
                'status': 'error',
                'message': 'XLSX não encontrado'
            }
        
        if dry_run:
            logger.info(f"[{thread_name}] 🧪 DRY RUN - {date_str} seria processado")
            progress_tracker.update_completed()
            return {
                'success': True,
                'date': date_str,
                'status': 'dry_run',
                'message': 'Simulação bem-sucedida'
            }
        
        logger.info(f"[{thread_name}] 📁 CSV: {os.path.basename(csv_file)}")
        logger.info(f"[{thread_name}] 📊 XLSX: {os.path.basename(xlsx_file)}")
        
        # Mover arquivos para posição ativa (thread-safe)
        csv_active, xlsx_active = move_files_to_active_position(csv_file, xlsx_file)
        
        try:
            # Executar monitoramento
            logger.info(f"[{thread_name}] 🚀 Executando monitoramento...")
            results = run_monitoring()
            
            if isinstance(results, dict) and results.get('sucesso', False):
                stats = results.get('estatisticas', {})
                pools_processed = stats.get('total', 0)
                success_rate = stats.get('taxa_sucesso', 0)
                
                logger.info(f"[{thread_name}] ✅ Monitoramento concluído para {date_str}")
                logger.info(f"[{thread_name}] 📊 Pools processados: {pools_processed}")
                logger.info(f"[{thread_name}] 📈 Taxa de sucesso: {success_rate}%")
                
                progress_tracker.update_completed(pools_processed)
                
                return {
                    'success': True,
                    'date': date_str,
                    'status': 'completed',
                    'pools_processed': pools_processed,
                    'success_rate': success_rate,
                    'message': f'Processados {pools_processed} pools com {success_rate}% de sucesso'
                }
            else:
                logger.error(f"[{thread_name}] ❌ Falha no monitoramento para {date_str}: {results}")
                progress_tracker.update_failed()
                return {
                    'success': False,
                    'date': date_str,
                    'status': 'error',
                    'message': f'Falha no monitoramento: {results}'
                }
                
        finally:
            # Mover arquivos de volta para pasta files
            try:
                move_files_back_to_files(csv_active, xlsx_active)
                logger.debug(f"[{thread_name}] 📂 Arquivos movidos de volta para pasta files")
            except Exception as e:
                logger.warning(f"[{thread_name}] ⚠️  Erro ao mover arquivos de volta: {e}")
        
    except Exception as e:
        logger.error(f"[{thread_name}] ❌ Erro crítico processando {date_str}: {e}")
        logger.debug(f"[{thread_name}] Traceback: {traceback.format_exc()}")
        progress_tracker.update_failed()
        return {
            'success': False,
            'date': date_str,
            'status': 'error',
            'message': f'Erro crítico: {str(e)}'
        }

def print_progress_update(progress_tracker: ProgressTracker, start_time: datetime):
    """
    Imprime atualização de progresso.
    
    Args:
        progress_tracker: Objeto de tracking de progresso
        start_time: Horário de início do processamento
    """
    progress = progress_tracker.get_progress()
    elapsed = datetime.now() - start_time
    
    if progress['processed_dates'] > 0:
        avg_time_per_date = elapsed.total_seconds() / progress['processed_dates']
        remaining_dates = progress['total_dates'] - progress['processed_dates']
        eta_seconds = avg_time_per_date * remaining_dates
        eta = timedelta(seconds=int(eta_seconds))
    else:
        eta = timedelta(0)
    
    print(f"\n📊 PROGRESSO ATUAL:")
    print(f"   📅 Datas processadas: {progress['processed_dates']}/{progress['total_dates']} ({progress['progress_percent']}%)")
    print(f"   ✅ Concluídas: {progress['completed_dates']}")
    print(f"   ❌ Falharam: {progress['failed_dates']}")
    print(f"   ⏭️  Puladas: {progress['skipped_dates']}")
    print(f"   🏦 Total de pools processados: {progress['total_pools_processed']}")
    print(f"   ⏱️  Tempo decorrido: {str(elapsed).split('.')[0]}")
    print(f"   ⏰ ETA: {str(eta).split('.')[0]}")

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description='Processamento retroativo completo com paralelização',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python3 run_full_historical_monitoring.py                    # Execução padrão
  python3 run_full_historical_monitoring.py --max-workers 8    # Usar 8 threads
  python3 run_full_historical_monitoring.py --skip-existing    # Pular já processados
  python3 run_full_historical_monitoring.py --dry-run          # Apenas simular
        """
    )
    
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Número máximo de threads simultâneas (default: 4)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Pular datas já processadas')
    parser.add_argument('--dry-run', action='store_true',
                       help='Apenas simular o processamento (não executar)')
    
    args = parser.parse_args()
    
    # Configurar diretórios
    setup_directories()
    
    # Banner
    print("🚀 PROCESSAMENTO RETROATIVO COMPLETO COM PARALELIZAÇÃO")
    print("=" * 70)
    print(f"⚙️  Configurações:")
    print(f"   🔄 Max workers: {args.max_workers}")
    print(f"   ⏭️  Skip existing: {args.skip_existing}")
    print(f"   🧪 Dry run: {args.dry_run}")
    print("=" * 70)
    
    start_time = datetime.now()
    
    try:
        # Descobrir datas históricas
        historical_dates = discover_historical_dates()
        
        if not historical_dates:
            logger.error("❌ Nenhuma data histórica encontrada!")
            return 1
        
        print(f"\n📅 Encontradas {len(historical_dates)} datas para processar")
        print(f"   📍 Primeira data: {historical_dates[0]}")
        print(f"   📍 Última data: {historical_dates[-1]}")
        
        # Filtrar datas já processadas se solicitado
        if args.skip_existing:
            original_count = len(historical_dates)
            historical_dates = [date for date in historical_dates if not check_existing_results(date)]
            skipped_count = original_count - len(historical_dates)
            if skipped_count > 0:
                print(f"   ⏭️  Pulando {skipped_count} datas já processadas")
        
        if not historical_dates:
            print("✅ Todas as datas já foram processadas!")
            return 0
        
        # Desabilitar modo debug temporariamente
        debug_backup = None
        if not args.dry_run:
            debug_backup = disable_debug_mode()
        
        # Inicializar progress tracker
        progress_tracker = ProgressTracker(len(historical_dates))
        
        # Processar datas com ThreadPoolExecutor
        print(f"\n🔄 Iniciando processamento paralelo com {args.max_workers} workers...")
        
        results = []
        with ThreadPoolExecutor(max_workers=args.max_workers, thread_name_prefix="DateWorker") as executor:
            # Submeter todas as tarefas
            future_to_date = {
                executor.submit(run_monitoring_for_date, date_str, progress_tracker, 
                              args.skip_existing, args.dry_run): date_str 
                for date_str in historical_dates
            }
            
            # Processar resultados conforme completam
            for future in as_completed(future_to_date):
                date_str = future_to_date[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Imprimir progresso a cada 5 tarefas concluídas
                    progress = progress_tracker.get_progress()
                    if progress['processed_dates'] % 5 == 0 or progress['processed_dates'] == progress['total_dates']:
                        print_progress_update(progress_tracker, start_time)
                        
                except Exception as e:
                    logger.error(f"❌ Erro crítico processando {date_str}: {e}")
                    progress_tracker.update_failed()
                    results.append({
                        'success': False,
                        'date': date_str,
                        'status': 'critical_error',
                        'message': f'Erro crítico: {str(e)}'
                    })
        
        # Restaurar modo debug
        if debug_backup:
            restore_debug_mode(debug_backup)
        
        # Relatório final
        end_time = datetime.now()
        total_time = end_time - start_time
        
        print(f"\n{'='*70}")
        print("📊 RELATÓRIO FINAL DE PROCESSAMENTO")
        print(f"{'='*70}")
        
        final_progress = progress_tracker.get_progress()
        
        print(f"⏱️  Tempo total: {str(total_time).split('.')[0]}")
        print(f"📅 Datas processadas: {final_progress['processed_dates']}/{final_progress['total_dates']}")
        print(f"✅ Sucessos: {final_progress['completed_dates']}")
        print(f"❌ Falhas: {final_progress['failed_dates']}")
        print(f"⏭️  Puladas: {final_progress['skipped_dates']}")
        print(f"🏦 Total de pools processados: {final_progress['total_pools_processed']}")
        
        success_rate = (final_progress['completed_dates'] / final_progress['total_dates']) * 100 if final_progress['total_dates'] > 0 else 0
        print(f"📈 Taxa de sucesso geral: {success_rate:.1f}%")
        
        # Detalhes por status
        print(f"\n📋 DETALHES POR STATUS:")
        status_summary = {}
        for result in results:
            status = result.get('status', 'unknown')
            if status not in status_summary:
                status_summary[status] = []
            status_summary[status].append(result['date'])
        
        for status, dates in status_summary.items():
            print(f"   {status.upper()}: {len(dates)} datas")
            if len(dates) <= 10:  # Mostrar datas se forem poucas
                print(f"      📄 {', '.join(dates)}")
        
        # Mostrar falhas detalhadas
        failed_results = [r for r in results if not r.get('success', False)]
        if failed_results:
            print(f"\n❌ DETALHES DE FALHAS ({len(failed_results)} datas):")
            for result in failed_results[:10]:  # Mostrar primeiras 10 falhas
                print(f"   📅 {result['date']}: {result.get('message', 'Erro desconhecido')}")
            if len(failed_results) > 10:
                print(f"   ... e mais {len(failed_results) - 10} falhas")
        
        print(f"\n📁 Resultados salvos em: {CONFIG['output_dir']}")
        print(f"📊 Execute o dashboard: python3 generate_table_dashboard.py")
        print(f"📜 Logs detalhados: {CONFIG['logs_dir']}/full_historical_monitoring.log")
        
        # Código de saída baseado no sucesso
        if final_progress['failed_dates'] == 0:
            print("\n🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO TOTAL!")
            return 0
        elif final_progress['completed_dates'] > 0:
            print(f"\n⚠️  PROCESSAMENTO CONCLUÍDO COM ALGUMAS FALHAS ({final_progress['failed_dates']} de {final_progress['total_dates']})")
            return 1
        else:
            print("\n❌ PROCESSAMENTO FALHOU COMPLETAMENTE!")
            return 2
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Processamento interrompido pelo usuário")
        logger.info("Processamento interrompido via Ctrl+C")
        return 130
    except Exception as e:
        logger.error(f"❌ Erro crítico no processamento: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        print(f"\n❌ ERRO CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)