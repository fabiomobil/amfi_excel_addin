"""
Validador de Consistência de Datas
=================================

Responsável por:
- Extrair datas dos nomes de arquivos CSV e XLSX
- Validar se as datas são consistentes entre si
- Garantir que a data de execução seja compatível
- Gerar alertas para inconsistências temporais

Validações críticas:
- CSV e XLSX devem ter a mesma data
- Data dos arquivos deve ser utilizada no JSON histórico
- Detectar arquivos desatualizados ou inconsistentes
"""

import re
import os
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Compatibilidade Spyder vs módulo
try:
    from .alerts import log_alerta
except (ImportError, ValueError):
    import sys
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from alerts import log_alerta


class DateConsistencyValidator:
    """
    Validador de consistência temporal para arquivos de dados.
    
    Funcionalidades:
    - Extração de datas de nomes de arquivos
    - Validação de consistência CSV ↔ XLSX
    - Verificação de compatibilidade temporal
    - Geração de alertas e recomendações
    """
    
    def __init__(self):
        """Inicializa o validador de datas."""
        self.patterns = {
            'csv': [
                r'(\d{2}-\d{2}-\d{4})',  # 10-07-2025 (DD-MM-YYYY)
                r'(\d{4}-\d{2}-\d{2})',  # 2025-07-18
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}_\d{2}_\d{2})',  # 2025-07-15 09_33_29
                r'(\d{2}/\d{2}/\d{4})',  # 18/07/2025
            ],
            'xlsx': [
                r'(\d{4}-\d{2}-\d{2})',  # 2025-07-18
                r'(\d{4}-\d{2}-\d{2}\s+\d{6})',  # 2025-07-15 070048
                r'(\d{2}/\d{2}/\d{4})',  # 18/07/2025
            ]
        }
    
    def validate_date_consistency(self, csv_file_path: str, 
                                xlsx_file_path: str) -> Dict[str, Any]:
        """
        Valida consistência de datas entre arquivos CSV e XLSX.
        
        Args:
            csv_file_path: Caminho para arquivo CSV
            xlsx_file_path: Caminho para arquivo XLSX
            
        Returns:
            Dict com resultado da validação e recomendações
        """
        result = {
            "consistent": False,
            "csv_date": None,
            "xlsx_date": None,
            "recommended_execution_date": None,
            "warnings": [],
            "errors": [],
            "metadata": {
                "csv_filename": Path(csv_file_path).name,
                "xlsx_filename": Path(xlsx_file_path).name,
                "validation_timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            # Extrair datas dos nomes dos arquivos
            csv_date = self._extract_date_from_filename(csv_file_path, 'csv')
            xlsx_date = self._extract_date_from_filename(xlsx_file_path, 'xlsx')
            
            result["csv_date"] = csv_date.isoformat() if csv_date else None
            result["xlsx_date"] = xlsx_date.isoformat() if xlsx_date else None
            
            # Validar consistência
            if csv_date and xlsx_date:
                if csv_date == xlsx_date:
                    result["consistent"] = True
                    result["recommended_execution_date"] = csv_date.isoformat()
                    
                    log_alerta({
                        "tipo": "info",
                        "titulo": "Consistência de Datas",
                        "mensagem": f"✅ Datas consistentes: {csv_date.isoformat()}",
                        "detalhes": {
                            "csv_file": result["metadata"]["csv_filename"],
                            "xlsx_file": result["metadata"]["xlsx_filename"]
                        }
                    })
                else:
                    result["errors"].append(f"Inconsistência de datas: CSV={csv_date.isoformat()}, XLSX={xlsx_date.isoformat()}")
                    result["recommended_execution_date"] = max(csv_date, xlsx_date).isoformat()
                    
                    log_alerta({
                        "tipo": "erro",
                        "titulo": "Inconsistência de Datas",
                        "mensagem": f"❌ Datas diferentes: CSV={csv_date.isoformat()}, XLSX={xlsx_date.isoformat()}",
                        "detalhes": {
                            "csv_file": result["metadata"]["csv_filename"],
                            "xlsx_file": result["metadata"]["xlsx_filename"],
                            "recomendacao": f"Usar data mais recente: {result['recommended_execution_date']}"
                        }
                    })
            else:
                # Problemas na extração de datas
                if not csv_date:
                    result["errors"].append(f"Não foi possível extrair data do CSV: {result['metadata']['csv_filename']}")
                
                if not xlsx_date:
                    result["errors"].append(f"Não foi possível extrair data do XLSX: {result['metadata']['xlsx_filename']}")
                
                # Usar data atual como fallback
                result["recommended_execution_date"] = date.today().isoformat()
                result["warnings"].append(f"Usando data atual como fallback: {result['recommended_execution_date']}")
                
                log_alerta({
                    "tipo": "warning",
                    "titulo": "Extração de Datas",
                    "mensagem": "⚠️ Problemas na extração de datas dos arquivos",
                    "detalhes": {
                        "csv_extraida": csv_date is not None,
                        "xlsx_extraida": xlsx_date is not None,
                        "fallback_date": result["recommended_execution_date"]
                    }
                })
            
            # Validações adicionais
            self._validate_temporal_relevance(result)
            
            return result
            
        except Exception as e:
            result["errors"].append(f"Erro na validação de datas: {str(e)}")
            result["recommended_execution_date"] = date.today().isoformat()
            
            log_alerta({
                "tipo": "erro",
                "titulo": "Erro na Validação",
                "mensagem": f"❌ Falha na validação de consistência de datas: {str(e)}"
            })
            
            return result
    
    def _extract_date_from_filename(self, file_path: str, file_type: str) -> Optional[date]:
        """
        Extrai data do nome do arquivo usando padrões específicos.
        
        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo ('csv' ou 'xlsx')
            
        Returns:
            Date object ou None se não conseguir extrair
        """
        filename = Path(file_path).name
        patterns = self.patterns.get(file_type, self.patterns['csv'])
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                
                try:
                    # Tentar diferentes formatos de data
                    date_formats = [
                        '%d-%m-%Y',  # 10-07-2025
                        '%Y-%m-%d',
                        '%Y-%m-%d %H_%M_%S',
                        '%Y-%m-%d %H%M%S',
                        '%d/%m/%Y'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            # Para formatos com hora, extrair apenas a data
                            if ' ' in date_str:
                                date_part = date_str.split(' ')[0]
                            else:
                                date_part = date_str
                            
                            if fmt in ['%d/%m/%Y', '%d-%m-%Y']:
                                parsed_date = datetime.strptime(date_part, fmt).date()
                            else:
                                parsed_date = datetime.strptime(date_part, '%Y-%m-%d').date()
                            
                            return parsed_date
                            
                        except ValueError:
                            continue
                            
                except Exception:
                    continue
        
        return None
    
    def _validate_temporal_relevance(self, result: Dict[str, Any]) -> None:
        """Valida relevância temporal dos dados."""
        
        if not result["recommended_execution_date"]:
            return
        
        try:
            execution_date = datetime.fromisoformat(result["recommended_execution_date"]).date()
            today = date.today()
            days_diff = (today - execution_date).days
            
            if days_diff < 0:
                result["warnings"].append(f"Data dos arquivos é futura: {execution_date.isoformat()}")
            elif days_diff == 0:
                result["warnings"].append("Dados são de hoje - ideal para monitoramento")
            elif days_diff == 1:
                result["warnings"].append("Dados são de ontem - aceitável")
            elif days_diff <= 3:
                result["warnings"].append(f"Dados têm {days_diff} dias - podem estar defasados")
            else:
                result["warnings"].append(f"Dados têm {days_diff} dias - possivelmente desatualizados")
                
        except Exception as e:
            result["warnings"].append(f"Erro na validação temporal: {str(e)}")
    
    def get_execution_date_from_files(self, csv_file_path: str, 
                                    xlsx_file_path: str) -> str:
        """
        Obtém data de execução recomendada baseada nos arquivos.
        
        Returns:
            String da data no formato ISO (YYYY-MM-DD)
        """
        validation_result = self.validate_date_consistency(csv_file_path, xlsx_file_path)
        return validation_result["recommended_execution_date"] or date.today().isoformat()


def validate_file_dates(csv_file_path: str, xlsx_file_path: str) -> Dict[str, Any]:
    """
    Função de conveniência para validação de datas.
    
    Args:
        csv_file_path: Caminho para arquivo CSV
        xlsx_file_path: Caminho para arquivo XLSX
        
    Returns:
        Dict com resultado da validação
    """
    validator = DateConsistencyValidator()
    return validator.validate_date_consistency(csv_file_path, xlsx_file_path)


def get_recommended_execution_date(csv_file_path: str, xlsx_file_path: str) -> str:
    """
    Obtém data de execução recomendada.
    
    Returns:
        String da data no formato ISO (YYYY-MM-DD)
    """
    validator = DateConsistencyValidator()
    return validator.get_execution_date_from_files(csv_file_path, xlsx_file_path)


if __name__ == "__main__":
    # Teste básico do validador
    print("📅 TESTE - Validador de Consistência de Datas")
    print("=" * 60)
    
    # Testar com arquivos exemplo
    csv_test = "/mnt/c/amfi/data/input/csv/AcompanhamentoDeOportunidades-2025-07-15 09_33_29 -0300.csv"
    xlsx_test = "/mnt/c/amfi/data/input/xlsx/Carteira Global 2025-07-15 070048.xlsx"
    
    validator = DateConsistencyValidator()
    
    # Teste de extração individual
    csv_date = validator._extract_date_from_filename(csv_test, 'csv')
    xlsx_date = validator._extract_date_from_filename(xlsx_test, 'xlsx')
    
    print(f"📄 CSV: {Path(csv_test).name}")
    print(f"   Data extraída: {csv_date}")
    print(f"📊 XLSX: {Path(xlsx_test).name}")
    print(f"   Data extraída: {xlsx_date}")
    
    # Teste de validação completa
    result = validate_file_dates(csv_test, xlsx_test)
    
    print(f"\n✅ Validação:")
    print(f"   Consistente: {result['consistent']}")
    print(f"   Data recomendada: {result['recommended_execution_date']}")
    print(f"   Avisos: {len(result['warnings'])}")
    print(f"   Erros: {len(result['errors'])}")
    
    if result['warnings']:
        print(f"   Detalhes: {result['warnings']}")