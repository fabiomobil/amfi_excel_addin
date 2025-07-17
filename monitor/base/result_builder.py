"""
Classe para padronização de resultados - AmFi Sistema de Monitoramento

Esta classe centraliza a construção de resultados padronizados para todos os monitores,
eliminando redundâncias na estrutura de retorno identificadas pelos agentes.

Responsabilidades:
- Construção padronizada de resultados de sucesso
- Construção padronizada de resultados de erro
- Validação de estrutura de dados
- Formatação consistente de timestamps
- Metadados padronizados

Padrões Centralizados:
- Campos obrigatórios: sucesso, monitor, timestamp
- Estrutura de erro: erro, timestamp, monitor
- Metadados: pool_id, data_analise
- Formatação: ISO timestamps, estrutura Dict[str, Any]

Autor: AmFi Development Team
Data: 2025-07-17
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class ResultBuilder:
    """
    Construtor padronizado de resultados para monitores.
    
    Centraliza padrões de resultado identificados pelos agentes:
    - Estrutura comum: sucesso, monitor, timestamp
    - Formatação padronizada de erros
    - Metadados consistentes
    """
    
    @staticmethod
    def build_success_result(
        monitor_name: str,
        data: Dict[str, Any],
        pool_id: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Constrói resultado de sucesso padronizado.
        
        Centraliza estrutura de sucesso identificada em todos os monitores:
        - Campos obrigatórios: sucesso=True, monitor, timestamp
        - Dados específicos do monitor
        - Metadados opcionais
        
        Args:
            monitor_name: Nome do monitor (ex: 'subordinacao', 'inadimplencia')
            data: Dados específicos do monitor
            pool_id: ID do pool processado (opcional)
            additional_metadata: Metadados adicionais (opcional)
            
        Returns:
            Dict com resultado padronizado de sucesso
        """
        result = {
            "sucesso": True,
            "monitor": monitor_name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adicionar pool_id se fornecido
        if pool_id:
            result["pool_id"] = pool_id
            
        # Adicionar data de análise
        result["data_analise"] = datetime.now().strftime("%Y-%m-%d")
        
        # Adicionar dados específicos do monitor
        if data:
            result.update(data)
            
        # Adicionar metadados adicionais
        if additional_metadata:
            result.update(additional_metadata)
            
        return result
    
    @staticmethod
    def build_error_result(
        monitor_name: str,
        error_message: str,
        pool_id: Optional[str] = None,
        error_code: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Constrói resultado de erro padronizado.
        
        Centraliza estrutura de erro identificada em todos os monitores:
        - Campos obrigatórios: sucesso=False, monitor, timestamp, erro
        - Informações de diagnóstico
        - Contexto adicional
        
        Args:
            monitor_name: Nome do monitor
            error_message: Mensagem de erro
            pool_id: ID do pool processado (opcional)
            error_code: Código de erro (opcional)
            additional_info: Informações adicionais (opcional)
            
        Returns:
            Dict com resultado padronizado de erro
        """
        result = {
            "sucesso": False,
            "monitor": monitor_name,
            "timestamp": datetime.now().isoformat(),
            "erro": error_message
        }
        
        # Adicionar pool_id se fornecido
        if pool_id:
            result["pool_id"] = pool_id
            
        # Adicionar código de erro se fornecido
        if error_code:
            result["error_code"] = error_code
            
        # Adicionar informações adicionais
        if additional_info:
            result.update(additional_info)
            
        return result
    
    @staticmethod
    def build_monitoring_result(
        monitor_results: List[Dict[str, Any]],
        pool_name: str,
        executed_monitors: List[str],
        overall_success: bool = True
    ) -> Dict[str, Any]:
        """
        Constrói resultado consolidado de monitoramento de pool.
        
        Usado pelo orquestrador para consolidar resultados de múltiplos monitores.
        
        Args:
            monitor_results: Lista de resultados de monitores individuais
            pool_name: Nome do pool processado
            executed_monitors: Lista de monitores executados
            overall_success: Se o processamento geral foi bem-sucedido
            
        Returns:
            Dict com resultado consolidado
        """
        result = {
            "sucesso": overall_success,
            "pool_name": pool_name,
            "timestamp": datetime.now().isoformat(),
            "monitores_executados": executed_monitors,
            "resultados": {}
        }
        
        # Organizar resultados por monitor
        for monitor_result in monitor_results:
            monitor_name = monitor_result.get("monitor")
            if monitor_name:
                result["resultados"][monitor_name] = monitor_result
        
        return result
    
    @staticmethod
    def build_orchestrator_result(
        pools_processados: List[str],
        resultados_pools: Dict[str, Dict[str, Any]],
        xlsx_enriched: Any,  # pd.DataFrame
        total_pools: int,
        successful_pools: int,
        failed_pools: int
    ) -> Dict[str, Any]:
        """
        Constrói resultado final do orquestrador.
        
        Mantém compatibilidade com interface atual do run_monitoring().
        
        Args:
            pools_processados: Lista de pools processados
            resultados_pools: Resultados por pool
            xlsx_enriched: DataFrame enriquecido
            total_pools: Total de pools processados
            successful_pools: Pools processados com sucesso
            failed_pools: Pools que falharam
            
        Returns:
            Dict com resultado final do orquestrador
        """
        taxa_sucesso = (successful_pools / total_pools * 100) if total_pools > 0 else 0
        
        return {
            "sucesso": failed_pools == 0,
            "timestamp": datetime.now().isoformat(),
            "pools_processados": pools_processados,
            "estatisticas": {
                "total": total_pools,
                "sucesso": successful_pools,
                "erro": failed_pools,
                "taxa_sucesso": round(taxa_sucesso, 2)
            },
            "resultados": resultados_pools,
            "xlsx_enriched": xlsx_enriched,
            "metadados": {
                "sistema": "AmFi",
                "versao": "2.0",
                "arquitetura": "orientada_a_objetos"
            }
        }
    
    @staticmethod
    def validate_monitor_result(result: Dict[str, Any]) -> bool:
        """
        Valida estrutura de resultado de monitor.
        
        Verifica se resultado segue padrão esperado:
        - Campos obrigatórios presentes
        - Tipos corretos
        - Estrutura válida
        
        Args:
            result: Resultado a ser validado
            
        Returns:
            True se estrutura é válida
        """
        required_fields = ["sucesso", "monitor", "timestamp"]
        
        try:
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in result:
                    return False
            
            # Verificar tipos
            if not isinstance(result["sucesso"], bool):
                return False
            
            if not isinstance(result["monitor"], str):
                return False
            
            if not isinstance(result["timestamp"], str):
                return False
            
            # Verificar se timestamp é válido
            datetime.fromisoformat(result["timestamp"])
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def extract_monitor_name(result: Dict[str, Any]) -> Optional[str]:
        """
        Extrai nome do monitor de um resultado.
        
        Args:
            result: Resultado do monitor
            
        Returns:
            Nome do monitor ou None se não encontrado
        """
        return result.get("monitor")
    
    @staticmethod
    def is_success(result: Dict[str, Any]) -> bool:
        """
        Verifica se resultado indica sucesso.
        
        Args:
            result: Resultado do monitor
            
        Returns:
            True se resultado é de sucesso
        """
        return result.get("sucesso", False)
    
    @staticmethod
    def get_error_message(result: Dict[str, Any]) -> Optional[str]:
        """
        Extrai mensagem de erro de um resultado.
        
        Args:
            result: Resultado do monitor
            
        Returns:
            Mensagem de erro ou None se não há erro
        """
        return result.get("erro")
    
    @staticmethod
    def format_for_json(result: Dict[str, Any]) -> str:
        """
        Formata resultado para JSON.
        
        Args:
            result: Resultado a ser formatado
            
        Returns:
            String JSON formatada
        """
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def merge_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge múltiplos resultados em um resultado consolidado.
        
        Args:
            results: Lista de resultados para mergear
            
        Returns:
            Resultado consolidado
        """
        if not results:
            return ResultBuilder.build_error_result(
                "consolidation", 
                "Nenhum resultado para consolidar"
            )
        
        merged = {
            "sucesso": all(r.get("sucesso", False) for r in results),
            "timestamp": datetime.now().isoformat(),
            "monitores": [r.get("monitor") for r in results if r.get("monitor")],
            "resultados_individuais": results
        }
        
        return merged
    
    @staticmethod
    def add_metadata(result: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona metadados a um resultado existente.
        
        Args:
            result: Resultado original
            metadata: Metadados a adicionar
            
        Returns:
            Resultado com metadados adicionados
        """
        updated_result = result.copy()
        updated_result.update(metadata)
        return updated_result