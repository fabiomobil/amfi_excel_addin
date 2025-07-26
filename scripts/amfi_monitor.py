#!/usr/bin/env python3
"""
Monitor Unificado AmFi - Interface única para todos os cenários de monitoramento

Este script consolida 6 cenários diferentes de análise de pools em uma interface única:
1. Rotina diária (todos os pools, data atual)
2. Pool específico (data atual)  
3. Pool específico + data específica
4. Pool específico + múltiplas datas
5. Múltiplos pools + múltiplas datas
6. Carga histórica completa

Características Principais:
✅ Modo Preview: Gerar JSON temporário para análise
✅ Modo Commit: Aplicar mudanças aos JSONs diários definitivos
✅ Enriquecimento Inteligente: Adiciona dados sem substituir outros pools
✅ Backup Automático: Proteção antes de modificar arquivos existentes
✅ Interface Híbrida: CLI + Programática

Usage:
    Programática (Recomendada para Spyder):
    >>> from scripts.amfi_monitor import AmFiMonitor
    >>> monitor = AmFiMonitor()
    >>> 
    >>> # Preview primeiro
    >>> preview = monitor.run_single_pool("Baru Pool #2", mode='preview')
    >>> print(f"Preview: {preview['preview_file']}")
    >>> 
    >>> # Commit após análise
    >>> commit = monitor.run_single_pool("Baru Pool #2", mode='commit')
    
    CLI:
    python scripts/amfi_monitor.py --pool "Baru Pool #2" --preview
    python scripts/amfi_monitor.py --pool "Baru Pool #2" --commit
"""

import sys
import os
import json
import argparse
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

# Adicionar src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from src.monitor.orchestrator import run_monitoring
    from src.monitor.utils.data_loader import load_pool_data
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que está executando do diretório C:\\amfi")
    sys.exit(1)


class JsonManagerAmFi:
    """Gerenciador inteligente de JSONs diários para enriquecimento sem substituição"""
    
    def __init__(self, daily_dir: str = None, backup_enabled: bool = True):
        self.daily_dir = Path(daily_dir) if daily_dir else Path("data/output/monitoring_results/daily_consolidated")
        self.backup_dir = self.daily_dir / "backups"
        self.backup_enabled = backup_enabled
        
        # Criar diretórios se não existirem
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        if self.backup_enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_backup(self, json_path: Path) -> Optional[str]:
        """Criar backup do arquivo antes de modificar"""
        if not self.backup_enabled or not json_path.exists():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{json_path.stem}_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(json_path, backup_path)
        return str(backup_path)
    
    def load_existing_json(self, date: str) -> Dict:
        """Carregar JSON existente ou retornar estrutura vazia"""
        date_obj = datetime.strptime(date, "%d/%m/%Y")
        json_path = self.daily_dir / f"{date_obj.strftime('%Y-%m-%d')}.json"
        
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️ Erro ao carregar {json_path}: {e}")
                return {}
        
        return {}
    
    def enrich_json_data(self, existing_data: Dict, new_results: Dict, date: str) -> Dict:
        """Enriquecer JSON existente com novos resultados, preservando outros pools"""
        # Se não há dados existentes, usar estrutura nova
        if not existing_data:
            return new_results
        
        # Copiar dados existentes
        enriched_data = existing_data.copy()
        
        # Atualizar apenas os pools processados nos novos resultados
        if 'resultados' in new_results:
            if 'resultados' not in enriched_data:
                enriched_data['resultados'] = {}
            
            for pool_name, pool_results in new_results['resultados'].items():
                enriched_data['resultados'][pool_name] = pool_results
                print(f"  ✅ Pool '{pool_name}' atualizado no JSON")
        
        # Atualizar metadados globais
        for key in ['execution_date', 'timestamp', 'estatisticas']:
            if key in new_results:
                enriched_data[key] = new_results[key]
        
        return enriched_data
    
    def save_json_data(self, data: Dict, date: str, mode: str = 'commit') -> str:
        """Salvar dados JSON no local apropriado baseado no modo"""
        date_obj = datetime.strptime(date, "%d/%m/%Y")
        
        if mode == 'preview':
            # Salvar em diretório temporário
            preview_dir = Path("temp/previews")
            preview_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{date_obj.strftime('%Y-%m-%d')}_preview.json"
            file_path = preview_dir / filename
        else:
            # Salvar no diretório oficial
            filename = f"{date_obj.strftime('%Y-%m-%d')}.json"
            file_path = self.daily_dir / filename
            
            # Fazer backup se arquivo existir
            if file_path.exists():
                backup_path = self._create_backup(file_path)
                if backup_path:
                    print(f"  💾 Backup criado: {backup_path}")
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)


class AmFiMonitor:
    """
    Monitor Unificado AmFi - Interface única para todos os cenários de monitoramento
    
    Este monitor consolida 6 cenários diferentes de análise de pools:
    1. Rotina diária (todos os pools, data atual)
    2. Pool específico (data atual)  
    3. Pool específico + data específica
    4. Pool específico + múltiplas datas
    5. Múltiplos pools + múltiplas datas
    6. Carga histórica completa
    
    Características Principais:
    ✅ Modo Preview: Gerar JSON temporário para análise
    ✅ Modo Commit: Aplicar mudanças aos JSONs diários definitivos
    ✅ Enriquecimento Inteligente: Adiciona dados sem substituir outros pools
    ✅ Backup Automático: Proteção antes de modificar arquivos existentes
    ✅ Interface Híbrida: CLI + Programática
    
    Examples:
        Uso Básico no Spyder:
        >>> from scripts.amfi_monitor import AmFiMonitor
        >>> monitor = AmFiMonitor()
        >>> 
        >>> # Preview de rotina diária
        >>> resultado = monitor.run_daily_routine(mode='preview')
        >>> print(f"Arquivo preview: {resultado['preview_file']}")
        >>> 
        >>> # Commit após aprovação
        >>> resultado = monitor.run_daily_routine(mode='commit')
        >>> print(f"Pools processados: {resultado['pools_processados']}")
        
        Pool Específico:
        >>> # Testar Baru Pool #2 antes de aplicar
        >>> preview = monitor.run_single_pool("Baru Pool #2", mode='preview')
        >>> # Analisar temp/previews/2025-07-26_preview.json
        >>> 
        >>> # Aplicar se aprovado  
        >>> commit = monitor.run_single_pool("Baru Pool #2", mode='commit')
        
        Análise Histórica:
        >>> # Carregar dados de múltiplas datas
        >>> historico = monitor.run_date_range(
        ...     pool_name="Baru Pool #2",
        ...     start_date="14/07/2025",
        ...     end_date="18/07/2025", 
        ...     mode='preview'
        ... )
        
        Casos de Uso Avançados:
        >>> # Comparar antes e depois
        >>> preview = monitor.run_single_pool("AFA Pool #1", mode='preview')
        >>> diff = monitor.compare_with_existing(preview['preview_file'])
        >>> print(f"Mudanças detectadas: {diff['changes_summary']}")
        >>> 
        >>> # Aplicar apenas se diff for aprovado
        >>> if user_approves(diff):
        ...     commit = monitor.run_single_pool("AFA Pool #1", mode='commit')
    
    Arguments:
        backup_enabled (bool): Fazer backup automático antes de modificar JSONs (default: True)
        preview_dir (str): Diretório para arquivos de preview (default: 'temp/previews')
        dry_run (bool): Simular execução sem modificar arquivos (default: False)
        
    Returns:
        Dict contendo:
        - success (bool): Status da operação
        - mode (str): 'preview' ou 'commit'  
        - pools_processados (List[str]): Pools que foram processados
        - files_generated (List[str]): Arquivos JSON gerados/modificados
        - preview_file (str): Caminho do arquivo de preview (se mode='preview')
        - backup_files (List[str]): Arquivos de backup criados (se mode='commit')
        - execution_summary (Dict): Estatísticas da execução
        - errors (List[str]): Erros encontrados durante a execução
        
    Raises:
        ValueError: Quando argumentos são inválidos ou conflitantes
        FileNotFoundError: Quando arquivos de dados não são encontrados
        PermissionError: Quando não há permissão para criar/modificar arquivos
        
    Notes:
        - O modo 'preview' NUNCA modifica arquivos existentes
        - O modo 'commit' sempre faz backup antes de modificar
        - Todos os JSONs seguem a estrutura: data/output/monitoring_results/daily_consolidated/
        - Arquivos de preview ficam em: temp/previews/
        - Sistema reutiliza run_monitoring() e data_loader existentes
        
    See Also:
        - src.monitor.orchestrator.run_monitoring(): Interface de monitoramento base
        - Descoberta automática de datas históricas integrada  
        - docs/user-guide/getting-started.md: Guia completo de uso
    """
    
    def __init__(self, backup_enabled: bool = True, preview_dir: str = 'temp/previews', dry_run: bool = False):
        """
        Inicializar o monitor com configurações personalizáveis
        
        Args:
            backup_enabled: Habilitar backup automático
            preview_dir: Diretório para arquivos de preview
            dry_run: Modo simulação (não modifica arquivos)
        """
        self.backup_enabled = backup_enabled
        self.preview_dir = Path(preview_dir)
        self.dry_run = dry_run
        self.json_manager = JsonManagerAmFi(backup_enabled=backup_enabled)
        
        # Criar diretório de preview
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 AmFi Monitor inicializado")
        print(f"   📁 Preview dir: {self.preview_dir}")
        print(f"   💾 Backup: {'✅' if backup_enabled else '❌'}")
        print(f"   🔍 Dry run: {'✅' if dry_run else '❌'}")
    
    def _validate_date_format(self, date: str) -> bool:
        """Validar formato de data dd/mm/yyyy"""
        try:
            datetime.strptime(date, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def _validate_pool_name(self, pool_name: str) -> bool:
        """Validar se pool existe no sistema"""
        try:
            # Carregar dados para verificar pools disponíveis
            dados = load_pool_data()
            return pool_name in dados.get('pools_processados', [])
        except Exception:
            return False
    
    def _get_current_date(self) -> str:
        """Obter data atual no formato dd/mm/yyyy"""
        return datetime.now().strftime("%d/%m/%Y")
    
    def _execute_monitoring(self, pool_name: Optional[str] = None, date: Optional[str] = None) -> Dict:
        """Executar monitoramento usando a interface existente"""
        try:
            print(f"⏳ Executando monitoramento...")
            if pool_name and date:
                print(f"   🎯 Pool: {pool_name}")
                print(f"   📅 Data: {date}")
            elif pool_name:
                print(f"   🎯 Pool: {pool_name}")
                print(f"   📅 Data: atual")
            elif date:
                print(f"   🎯 Pools: todos")
                print(f"   📅 Data: {date}")
            else:
                print(f"   🎯 Pools: todos")
                print(f"   📅 Data: atual")
            
            resultado = run_monitoring(pool_name=pool_name, data=date)
            
            if resultado.get('sucesso'):
                print(f"   ✅ Monitoramento concluído")
                print(f"   📊 Pools processados: {len(resultado.get('pools_processados', []))}")
                return resultado
            else:
                print(f"   ❌ Falha no monitoramento: {resultado.get('erro', 'Erro desconhecido')}")
                return resultado
                
        except Exception as e:
            print(f"   ❌ Exceção durante monitoramento: {str(e)}")
            return {
                'sucesso': False,
                'erro': f"Exceção: {str(e)}",
                'pools_processados': [],
                'resultados': {}
            }
    
    def _process_results(self, monitoring_result: Dict, date: str, mode: str) -> Dict:
        """Processar resultados do monitoramento baseado no modo"""
        if not monitoring_result.get('sucesso'):
            return {
                'success': False,
                'mode': mode,
                'error': monitoring_result.get('erro', 'Monitoramento falhou'),
                'pools_processados': [],
                'files_generated': []
            }
        
        # Preparar dados para persistência
        execution_date = date if date else self._get_current_date()
        
        if mode == 'preview':
            print(f"📋 Modo Preview - Gerando arquivo temporário...")
            
            # Gerar arquivo de preview
            preview_file = self.json_manager.save_json_data(
                monitoring_result, execution_date, mode='preview'
            )
            
            print(f"   💾 Preview salvo: {preview_file}")
            print(f"   ⚠️  ATENÇÃO: Este é um arquivo temporário!")
            print(f"   ⚠️  Para aplicar as mudanças, execute com mode='commit'")
            
            return {
                'success': True,
                'mode': 'preview',
                'pools_processados': monitoring_result.get('pools_processados', []),
                'preview_file': preview_file,
                'files_generated': [preview_file],
                'execution_summary': {
                    'total_pools': len(monitoring_result.get('pools_processados', [])),
                    'taxa_sucesso': monitoring_result.get('estatisticas', {}).get('taxa_sucesso', 0),
                    'execution_date': execution_date
                },
                'errors': []
            }
        
        else:  # mode == 'commit'
            print(f"💾 Modo Commit - Aplicando mudanças definitivas...")
            
            if self.dry_run:
                print(f"   🔍 Dry run ativo - Simulando sem modificar arquivos")
                return {
                    'success': True,
                    'mode': 'commit',
                    'dry_run': True,
                    'pools_processados': monitoring_result.get('pools_processados', []),
                    'files_generated': [],
                    'would_generate': [f"data/output/monitoring_results/daily_consolidated/{datetime.strptime(execution_date, '%d/%m/%Y').strftime('%Y-%m-%d')}.json"]
                }
            
            # Carregar dados existentes
            existing_data = self.json_manager.load_existing_json(execution_date)
            
            # Enriquecer com novos dados
            enriched_data = self.json_manager.enrich_json_data(
                existing_data, monitoring_result, execution_date
            )
            
            # Salvar dados definitivos
            final_file = self.json_manager.save_json_data(
                enriched_data, execution_date, mode='commit'
            )
            
            print(f"   ✅ JSON definitivo atualizado: {final_file}")
            
            return {
                'success': True,
                'mode': 'commit',
                'pools_processados': monitoring_result.get('pools_processados', []),
                'files_generated': [final_file],
                'execution_summary': {
                    'total_pools': len(monitoring_result.get('pools_processados', [])),
                    'taxa_sucesso': monitoring_result.get('estatisticas', {}).get('taxa_sucesso', 0),
                    'execution_date': execution_date,
                    'enriched_existing_data': len(existing_data) > 0
                },
                'errors': []
            }
    
    def run_daily_routine(self, mode: str = 'preview', **kwargs) -> Dict:
        """
        Executar rotina diária completa (todos os pools, data atual)
        
        Args:
            mode (str): 'preview' ou 'commit'
            **kwargs: Argumentos adicionais para personalização
            
        Returns:
            Dict: Resultado da execução com arquivos gerados
            
        Example:
            >>> monitor = AmFiMonitor()
            >>> resultado = monitor.run_daily_routine(mode='preview')
            >>> print(f"Preview gerado: {resultado['preview_file']}")
        """
        if mode not in ['preview', 'commit']:
            raise ValueError("mode deve ser 'preview' ou 'commit'")
        
        print(f"🌅 Executando Rotina Diária - Modo: {mode.upper()}")
        print("=" * 50)
        
        # Executar monitoramento de todos os pools na data atual
        monitoring_result = self._execute_monitoring(pool_name=None, date=None)
        
        # Processar resultados
        return self._process_results(monitoring_result, None, mode)
    
    def run_single_pool(self, pool_name: str, date: Optional[str] = None, mode: str = 'preview', **kwargs) -> Dict:
        """
        Executar monitoramento de pool específico
        
        Args:
            pool_name (str): Nome exato do pool (ex: "Baru Pool #2")
            date (str, optional): Data específica no formato dd/mm/yyyy
            mode (str): 'preview' ou 'commit'
            
        Returns:
            Dict: Resultado da execução
            
        Example:
            >>> # Pool específico, data atual
            >>> resultado = monitor.run_single_pool("Baru Pool #2", mode='preview')
            >>> 
            >>> # Pool específico, data histórica
            >>> resultado = monitor.run_single_pool(
            ...     "Baru Pool #2", 
            ...     date="14/07/2025", 
            ...     mode='preview'
            ... )
        """
        if mode not in ['preview', 'commit']:
            raise ValueError("mode deve ser 'preview' ou 'commit'")
        
        if date and not self._validate_date_format(date):
            raise ValueError(f"Data inválida: {date}. Use formato dd/mm/yyyy")
        
        date_display = date if date else "atual"
        print(f"🎯 Executando Pool Específico - Modo: {mode.upper()}")
        print(f"   Pool: {pool_name}")
        print(f"   Data: {date_display}")
        print("=" * 50)
        
        # Executar monitoramento do pool específico
        monitoring_result = self._execute_monitoring(pool_name=pool_name, date=date)
        
        # Processar resultados
        return self._process_results(monitoring_result, date, mode)
    
    def run_date_range(self, pool_name: Optional[str] = None, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None, mode: str = 'preview', **kwargs) -> Dict:
        """
        Executar monitoramento para múltiplas datas
        
        Args:
            pool_name (str, optional): Pool específico ou None para todos
            start_date (str): Data inicial (dd/mm/yyyy)
            end_date (str): Data final (dd/mm/yyyy)  
            mode (str): 'preview' ou 'commit'
            
        Returns:
            Dict: Resultado da execução com estatísticas por data
            
        Example:
            >>> # Múltiplas datas para pool específico
            >>> resultado = monitor.run_date_range(
            ...     pool_name="Baru Pool #2",
            ...     start_date="14/07/2025",
            ...     end_date="18/07/2025",
            ...     mode='preview'
            ... )
        """
        if mode not in ['preview', 'commit']:
            raise ValueError("mode deve ser 'preview' ou 'commit'")
        
        if not start_date or not end_date:
            raise ValueError("start_date e end_date são obrigatórios")
        
        if not self._validate_date_format(start_date) or not self._validate_date_format(end_date):
            raise ValueError("Datas inválidas. Use formato dd/mm/yyyy")
        
        pool_display = pool_name if pool_name else "todos os pools"
        print(f"📅 Executando Período - Modo: {mode.upper()}")
        print(f"   Pool(s): {pool_display}")
        print(f"   Período: {start_date} até {end_date}")
        print("=" * 50)
        
        # Gerar lista de datas no período
        start_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_obj = datetime.strptime(end_date, "%d/%m/%Y")
        
        dates_to_process = []
        current_date = start_obj
        while current_date <= end_obj:
            dates_to_process.append(current_date.strftime("%d/%m/%Y"))
            current_date += timedelta(days=1)
        
        print(f"📋 {len(dates_to_process)} datas para processar")
        
        # Processar cada data
        all_results = []
        files_generated = []
        errors = []
        
        for i, date in enumerate(dates_to_process, 1):
            print(f"\n[{i}/{len(dates_to_process)}] Processando {date}...")
            
            try:
                monitoring_result = self._execute_monitoring(pool_name=pool_name, date=date)
                result = self._process_results(monitoring_result, date, mode)
                
                all_results.append({
                    'date': date,
                    'result': result
                })
                
                if result.get('files_generated'):
                    files_generated.extend(result['files_generated'])
                
                if not result.get('success'):
                    errors.append(f"{date}: {result.get('error', 'Erro desconhecido')}")
                    
            except Exception as e:
                error_msg = f"{date}: Exceção - {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
        
        # Consolidar resultados
        successful_dates = [r for r in all_results if r['result'].get('success')]
        
        print(f"\n📊 RESUMO DO PERÍODO:")
        print(f"   ✅ Sucessos: {len(successful_dates)}/{len(dates_to_process)}")
        print(f"   ❌ Erros: {len(errors)}")
        
        return {
            'success': len(successful_dates) > 0,
            'mode': mode,
            'dates_processed': len(successful_dates),
            'total_dates': len(dates_to_process),
            'files_generated': files_generated,
            'errors': errors,
            'detailed_results': all_results,
            'execution_summary': {
                'pool_name': pool_name,
                'start_date': start_date,
                'end_date': end_date,
                'success_rate': len(successful_dates) / len(dates_to_process) * 100
            }
        }
    
    def run_historical_load(self, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                           mode: str = 'preview', **kwargs) -> Dict:
        """
        Executar carga histórica completa
        
        Args:
            start_date (str, optional): Data inicial ou None para auto-descoberta
            end_date (str, optional): Data final ou None para auto-descoberta
            mode (str): 'preview' ou 'commit'
            
        Returns:
            Dict: Resultado da carga histórica
            
        Example:
            >>> # Carga histórica completa com auto-descoberta
            >>> resultado = monitor.run_historical_load(mode='preview')
            >>> 
            >>> # Período específico
            >>> resultado = monitor.run_historical_load(
            ...     start_date="14/07/2025",
            ...     end_date="18/07/2025", 
            ...     mode='commit'
            ... )
        """
        if mode not in ['preview', 'commit']:
            raise ValueError("mode deve ser 'preview' ou 'commit'")
        
        print(f"⏳ Executando Carga Histórica - Modo: {mode.upper()}")
        print("=" * 50)
        
        if start_date and end_date:
            # Usar período específico
            print(f"📅 Usando período específico: {start_date} até {end_date}")
            return self.run_date_range(
                pool_name=None, 
                start_date=start_date, 
                end_date=end_date, 
                mode=mode, 
                **kwargs
            )
        else:
            # Auto-descoberta de datas históricas disponíveis
            print(f"🔍 Auto-descobrindo datas históricas disponíveis...")
            
            try:
                # Descoberta automática integrada
                csv_dir = Path("data/input/csv")
                csv_pattern = csv_dir / "AcompanhamentoDeOportunidades-*-*-*.csv"
                csv_files = glob.glob(str(csv_pattern))
                
                datas_encontradas = set()
                for arquivo in csv_files:
                    nome = Path(arquivo).name
                    partes = nome.replace("AcompanhamentoDeOportunidades-", "").replace(".csv", "")
                    
                    if partes.count("-") == 2:
                        try:
                            datetime.strptime(partes, "%d-%m-%Y")
                            data_formatada = partes.replace("-", "/")
                            datas_encontradas.add(data_formatada)
                        except ValueError:
                            continue
                
                datas_disponiveis = sorted(list(datas_encontradas), 
                                        key=lambda x: datetime.strptime(x, "%d/%m/%Y"))
                
                if not datas_disponiveis:
                    return {
                        'success': False,
                        'mode': mode,
                        'error': 'Nenhuma data histórica encontrada',
                        'files_generated': []
                    }
                
                # Usar primeira e última data descobertas
                start_discovered = datas_disponiveis[0]
                end_discovered = datas_disponiveis[-1]
                
                print(f"📅 Datas descobertas: {start_discovered} até {end_discovered} ({len(datas_disponiveis)} datas)")
                
                return self.run_date_range(
                    pool_name=None,
                    start_date=start_discovered,
                    end_date=end_discovered,
                    mode=mode,
                    **kwargs
                )
                
            except Exception as e:
                return {
                    'success': False,
                    'mode': mode,
                    'error': f'Erro na auto-descoberta: {str(e)}',
                    'files_generated': []
                }
    
    def compare_with_existing(self, preview_file_path: str) -> Dict:
        """
        Comparar arquivo de preview com JSON existente
        
        Args:
            preview_file_path (str): Caminho do arquivo de preview
            
        Returns:
            Dict: Análise das diferenças encontradas
            
        Example:
            >>> preview = monitor.run_single_pool("AFA Pool #1", mode='preview')
            >>> diff = monitor.compare_with_existing(preview['preview_file'])
            >>> if diff['has_changes']:
            ...     print(f"Mudanças: {diff['changes_summary']}")
        """
        preview_path = Path(preview_file_path)
        
        if not preview_path.exists():
            return {
                'success': False,
                'error': f'Arquivo de preview não encontrado: {preview_file_path}'
            }
        
        try:
            # Carregar dados do preview
            with open(preview_path, 'r', encoding='utf-8') as f:
                preview_data = json.load(f)
            
            # Extrair data do nome do arquivo de preview
            # Formato esperado: YYYY-MM-DD_preview.json
            date_match = preview_path.stem.split('_')[0]  # Remove '_preview'
            date_obj = datetime.strptime(date_match, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%d/%m/%Y")
            
            # Carregar dados existentes
            existing_data = self.json_manager.load_existing_json(date_formatted)
            
            if not existing_data:
                return {
                    'success': True,
                    'has_changes': True,
                    'changes_summary': ['Arquivo JSON não existe - seria criado novo arquivo'],
                    'preview_pools': list(preview_data.get('resultados', {}).keys()),
                    'existing_pools': []
                }
            
            # Comparar pools
            preview_pools = set(preview_data.get('resultados', {}).keys())
            existing_pools = set(existing_data.get('resultados', {}).keys())
            
            changes = []
            
            # Pools novos
            new_pools = preview_pools - existing_pools
            if new_pools:
                changes.extend([f"Novo pool: {pool}" for pool in new_pools])
            
            # Pools atualizados
            updated_pools = preview_pools & existing_pools
            for pool in updated_pools:
                changes.append(f"Pool atualizado: {pool}")
            
            # Pools que seriam mantidos (não no preview)
            maintained_pools = existing_pools - preview_pools
            if maintained_pools:
                changes.extend([f"Pool mantido: {pool}" for pool in maintained_pools])
            
            return {
                'success': True,
                'has_changes': len(changes) > 0,
                'changes_summary': changes,
                'preview_pools': list(preview_pools),
                'existing_pools': list(existing_pools),
                'new_pools': list(new_pools),
                'updated_pools': list(updated_pools),
                'maintained_pools': list(maintained_pools)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao comparar arquivos: {str(e)}'
            }


def main():
    """Interface CLI para o monitor unificado"""
    parser = argparse.ArgumentParser(
        description="Monitor Unificado AmFi - Interface única para todos os cenários",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  Rotina diária (todos os pools, data atual):
    python scripts/amfi_monitor.py --routine daily --preview
    python scripts/amfi_monitor.py --routine daily --commit

  Pool específico:
    python scripts/amfi_monitor.py --pool "Baru Pool #2" --preview
    python scripts/amfi_monitor.py --pool "Baru Pool #2" --commit

  Pool específico + data histórica:
    python scripts/amfi_monitor.py --pool "Baru Pool #2" --date "14/07/2025" --preview

  Múltiplas datas:
    python scripts/amfi_monitor.py --pool "Baru Pool #2" --date-range "14/07/2025:18/07/2025" --preview

  Carga histórica:
    python scripts/amfi_monitor.py --historical --preview
    python scripts/amfi_monitor.py --historical --start-date "14/07/2025" --end-date "18/07/2025" --commit

Recomendação: Use sempre --preview primeiro para analisar antes de --commit
        """
    )
    
    # Argumentos mutuamente exclusivos para diferentes modos
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--routine', choices=['daily'], help='Rotina completa diária')
    mode_group.add_argument('--pool', help='Pool específico (ex: "Baru Pool #2")')
    mode_group.add_argument('--historical', action='store_true', help='Carga histórica completa')
    
    # Argumentos de data (opcionais, dependem do contexto)  
    parser.add_argument('--date', help='Data específica (dd/mm/yyyy)')
    parser.add_argument('--date-range', help='Período (dd/mm/yyyy:dd/mm/yyyy)')
    parser.add_argument('--start-date', help='Data inicial para --historical')
    parser.add_argument('--end-date', help='Data final para --historical')
    
    # Argumentos de comportamento (mutuamente exclusivos)
    behavior_group = parser.add_mutually_exclusive_group(required=True)
    behavior_group.add_argument('--preview', action='store_true',
                               help='Gerar JSON temporário para análise (não modifica arquivos)')
    behavior_group.add_argument('--commit', action='store_true', 
                               help='Aplicar mudanças ao JSON diário definitivo')
    
    # Argumentos opcionais
    parser.add_argument('--no-backup', action='store_true',
                       help='Desabilitar backup automático')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simular execução sem modificar arquivos')
    parser.add_argument('--preview-dir', default='temp/previews',
                       help='Diretório para arquivos de preview')
    
    args = parser.parse_args()
    
    # Validações
    if args.date_range and (args.date or args.start_date or args.end_date):
        parser.error("--date-range não pode ser usado com --date, --start-date ou --end-date")
    
    if args.historical and args.date:
        parser.error("--historical não pode ser usado com --date")
    
    if args.pool and args.date_range:
        parser.error("--date-range com --pool não é suportado. Use --start-date e --end-date")
    
    # Determinar modo
    mode = 'preview' if args.preview else 'commit'
    
    # Criar monitor
    monitor = AmFiMonitor(
        backup_enabled=not args.no_backup,
        preview_dir=args.preview_dir,
        dry_run=args.dry_run
    )
    
    try:
        # Executar baseado nos argumentos
        if args.routine:
            resultado = monitor.run_daily_routine(mode=mode)
            
        elif args.pool:
            if args.date_range:
                # Converter range para start/end dates
                start_date, end_date = args.date_range.split(':')
                resultado = monitor.run_date_range(
                    pool_name=args.pool,
                    start_date=start_date,
                    end_date=end_date,
                    mode=mode
                )
            else:
                resultado = monitor.run_single_pool(
                    pool_name=args.pool,
                    date=args.date,
                    mode=mode
                )
                
        elif args.historical:
            resultado = monitor.run_historical_load(
                start_date=args.start_date,
                end_date=args.end_date,
                mode=mode
            )
        
        # Exibir resultado
        if resultado.get('success'):
            print(f"\n🎉 EXECUÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"   Modo: {resultado['mode'].upper()}")
            
            if 'pools_processados' in resultado:
                print(f"   Pools processados: {len(resultado['pools_processados'])}")
            
            if 'files_generated' in resultado:
                print(f"   Arquivos gerados: {len(resultado['files_generated'])}")
                for file_path in resultado['files_generated']:
                    print(f"     • {file_path}")
            
            if resultado['mode'] == 'preview':
                print(f"\n⚠️  ARQUIVO TEMPORÁRIO GERADO")
                print(f"⚠️  Para aplicar as mudanças, execute novamente com --commit")
        else:
            print(f"\n❌ EXECUÇÃO FALHOU")
            print(f"   Erro: {resultado.get('error', 'Erro desconhecido')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()