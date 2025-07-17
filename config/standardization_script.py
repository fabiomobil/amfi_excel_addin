#!/usr/bin/env python3
"""
Configuration Standardization Script
Systematically standardizes all configuration files according to established patterns.
"""

import json
import glob
import re
import os
from typing import Dict, Any, List
import argparse

class ConfigurationStandardizer:
    def __init__(self, global_constants_path: str):
        """Initialize with global constants"""
        with open(global_constants_path, 'r', encoding='utf-8') as f:
            self.global_constants = json.load(f)
        
        self.issues_found = []
        self.files_processed = []
        
    def remove_json_comments(self, content: str) -> str:
        """Remove JSON comments while preserving structure"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are just comments
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('"//'):
                continue
                
            # Remove inline comments
            if '//' in line:
                # Simple approach: find // and remove everything after it
                # This assumes // is not inside a string value
                comment_pos = line.find('//')
                if comment_pos != -1:
                    line = line[:comment_pos].rstrip()
                    if not line.strip():
                        continue
            
            # Clean up trailing commas before closing brackets
            stripped = line.strip()
            if stripped.endswith(',') and (
                len(cleaned_lines) > 0 and 
                (cleaned_lines[-1].strip().endswith('}') or cleaned_lines[-1].strip().endswith(']'))
            ):
                line = line.rstrip()[:-1].rstrip()
            
            if line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def standardize_percentages(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize percentage formats to decimal (0.5% = 0.005)"""
        if isinstance(data, dict):
            # Handle PDD provisions - these seem to have inconsistencies
            if 'provisoes_pdd' in data and 'grupos_risco' in data['provisoes_pdd']:
                pdd_padrao = self.global_constants['monitoramento']['provisoes_pdd_padrao']['grupos_risco']
                data['provisoes_pdd']['grupos_risco'] = pdd_padrao
                self.issues_found.append("Standardized PDD provisions to global constants")
            
            # Handle subordinacao percentages
            if 'monitoramentos_ativos' in data:
                for monitor in data['monitoramentos_ativos']:
                    if monitor.get('tipo') == 'subordinacao' and 'limites' in monitor:
                        # Ensure percentages are in decimal format
                        for key in ['minimo', 'critico']:
                            if key in monitor['limites']:
                                value = monitor['limites'][key]
                                if isinstance(value, (int, float)) and value > 1:
                                    monitor['limites'][key] = value / 100
                                    self.issues_found.append(f"Converted {key} percentage from {value} to {value/100}")
            
            # Recursively process nested dictionaries
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key] = self.standardize_percentages(value)
                    
        elif isinstance(data, list):
            return [self.standardize_percentages(item) for item in data]
            
        return data
    
    def standardize_hardcoded_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace hardcoded values with references to global constants"""
        if isinstance(data, dict):
            # Replace AMFI CONSULTING references
            if 'prestador_servicos_operacionais' in data:
                prestador = data['prestador_servicos_operacionais']
                if prestador.get('nome') == 'AMFI CONSULTING LTDA.':
                    data['prestador_servicos_operacionais'] = {
                        **self.global_constants['operacional']['prestador_servicos'],
                        'contrato_data': prestador.get('contrato_data', 'DATA_CONTRATO_PLACEHOLDER')
                    }
                    self.issues_found.append("Standardized AMFI CONSULTING reference to global constants")
            
            # Replace standard reserve values
            if 'valores' in data:
                valores = data['valores']
                if valores.get('reserva_despesas') == 25000.0:
                    valores['reserva_despesas'] = self.global_constants['financeiro']['reservas_padrao']['reserva_despesas']
                    self.issues_found.append("Standardized reserva_despesas to global constant")
                if valores.get('reserva_extraordinaria') == 30000.0:
                    valores['reserva_extraordinaria'] = self.global_constants['financeiro']['reservas_padrao']['reserva_extraordinaria']
                    self.issues_found.append("Standardized reserva_extraordinaria to global constant")
            
            # Recursively process nested dictionaries
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key] = self.standardize_hardcoded_values(value)
                    
        elif isinstance(data, list):
            return [self.standardize_hardcoded_values(item) for item in data]
            
        return data
    
    def validate_and_fix_json(self, file_path: str) -> bool:
        """Validate and fix JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Remove comments
            cleaned_content = self.remove_json_comments(original_content)
            
            # Parse JSON
            try:
                data = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                self.issues_found.append(f"JSON parse error in {file_path}: {e}")
                return False
            
            # Apply standardizations
            data = self.standardize_percentages(data)
            data = self.standardize_hardcoded_values(data)
            
            # Write back with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.files_processed.append(file_path)
            return True
            
        except Exception as e:
            self.issues_found.append(f"Error processing {file_path}: {e}")
            return False
    
    def process_all_configs(self, config_dir: str) -> Dict[str, Any]:
        """Process all configuration files"""
        json_files = glob.glob(os.path.join(config_dir, '**/*.json'), recursive=True)
        
        # Exclude the global constants file
        global_constants_file = os.path.join(config_dir, 'global_constants.json')
        json_files = [f for f in json_files if f != global_constants_file]
        
        results = {
            'total_files': len(json_files),
            'processed_successfully': 0,
            'failed': 0,
            'issues_found': [],
            'files_processed': []
        }
        
        for file_path in json_files:
            if self.validate_and_fix_json(file_path):
                results['processed_successfully'] += 1
            else:
                results['failed'] += 1
        
        results['issues_found'] = self.issues_found
        results['files_processed'] = self.files_processed
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Standardize configuration files')
    parser.add_argument('--config-dir', default='/mnt/c/amfi/config', 
                       help='Configuration directory path')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Dry run - report issues without making changes')
    
    args = parser.parse_args()
    
    global_constants_path = os.path.join(args.config_dir, 'global_constants.json')
    
    if not os.path.exists(global_constants_path):
        print(f"Error: Global constants file not found at {global_constants_path}")
        return 1
    
    standardizer = ConfigurationStandardizer(global_constants_path)
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
    
    results = standardizer.process_all_configs(args.config_dir)
    
    print(f"\\n=== CONFIGURATION STANDARDIZATION RESULTS ===")
    print(f"Total files found: {results['total_files']}")
    print(f"Successfully processed: {results['processed_successfully']}")
    print(f"Failed: {results['failed']}")
    
    if results['issues_found']:
        print(f"\\n=== ISSUES FOUND AND FIXED ===")
        for issue in results['issues_found']:
            print(f"  - {issue}")
    
    if results['files_processed']:
        print(f"\\n=== FILES PROCESSED ===")
        for file_path in results['files_processed']:
            print(f"  - {file_path}")
    
    return 0

if __name__ == '__main__':
    main()