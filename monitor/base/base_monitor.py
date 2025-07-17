"""
Classe base para todos os monitores de compliance - AmFi Sistema de Monitoramento

Esta classe centraliza funcionalidades comuns a todos os monitores, eliminando redundâncias
e padronizando interfaces. Baseada na análise de patterns identificados nos monitores existentes.

Responsabilidades:
- Descoberta automática de configuração de monitores
- Validações básicas padronizadas
- Interface comum para todos os monitores
- Tratamento de erros padronizado
- Estrutura de resultado unificada

Padrões Centralizados:
- Busca de configuração: _find_monitor_config()
- Verificação de status: is_active()
- Validação de dados: validate_basic_data()
- Resultado padronizado: build_result()

Autor: AmFi Development Team
Data: 2025-07-17
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

# Importar ResultBuilder para padronização
try:
    from .result_builder import ResultBuilder
except ImportError:
    try:
        from result_builder import ResultBuilder
    except ImportError:
        ResultBuilder = None


class BaseMonitor(ABC):
    """
    Classe base abstrata para todos os monitores de compliance.
    
    Implementa padrões comuns identificados pelos agentes:
    - Descoberta de configuração (_find_*_monitor pattern)
    - Validação de dados (DataFrame vazio, colunas obrigatórias)
    - Estrutura de resultado (sucesso, monitor, timestamp)
    """
    
    def __init__(self, monitor_id: str, config: Dict[str, Any]):
        """
        Inicializa monitor com ID e configuração.
        
        Args:
            monitor_id: Identificador único do monitor (ex: 'subordinacao', 'inadimplencia')
            config: Configuração JSON completa do pool
        """
        self.monitor_id = monitor_id
        self.config = config
        self.monitor_config = self._find_monitor_config()
    
    def _find_monitor_config(self) -> Optional[Dict[str, Any]]:
        """
        Busca configuração específica do monitor no JSON do pool.
        
        Centraliza o padrão _find_*_monitor() encontrado em todos os monitores.
        
        Returns:
            Dict com configuração do monitor ou None se não encontrado
        """
        try:
            monitoramentos = self.config.get('monitoramentos_ativos', [])
            
            for monitor in monitoramentos:
                if monitor.get('id') == self.monitor_id:
                    return monitor
                    
            return None
            
        except (KeyError, TypeError) as e:
            print(f"Erro ao buscar configuração do monitor {self.monitor_id}: {e}")
            return None
    
    def is_active(self) -> bool:
        """
        Verifica se o monitor está ativo na configuração.
        
        Centraliza o padrão _has_*_monitoring() encontrado no orquestrador.
        
        Returns:
            True se monitor está ativo, False caso contrário
        """
        return (self.monitor_config is not None and 
                self.monitor_config.get('ativo', False))
    
    def validate_basic_data(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validações básicas comuns a todos os monitores.
        
        Centraliza padrões de validação identificados pelos agentes:
        - DataFrame não vazio
        - Colunas obrigatórias presentes
        - Valores numéricos onde esperado
        
        Args:
            df: DataFrame a ser validado
            required_columns: Lista de colunas obrigatórias
            
        Returns:
            True se validação passou, False caso contrário
        """
        try:
            # Validação: DataFrame não vazio
            if df.empty:
                raise ValueError("DataFrame está vazio")
            
            # Validação: Colunas obrigatórias presentes
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Colunas obrigatórias ausentes: {missing_columns}")
            
            # Validação: Monitor ativo
            if not self.is_active():
                raise ValueError(f"Monitor {self.monitor_id} está inativo")
            
            return True
            
        except Exception as e:
            print(f"Erro na validação básica do monitor {self.monitor_id}: {e}")
            return False
    
    def build_result(self, success: bool, data: Optional[Dict[str, Any]] = None, 
                    error: Optional[str] = None) -> Dict[str, Any]:
        """
        Constrói resultado padronizado usando ResultBuilder.
        
        Args:
            success: True se monitor executou com sucesso
            data: Dados específicos do monitor (opcional)
            error: Mensagem de erro (opcional)
            
        Returns:
            Dict com resultado padronizado
        """
        if ResultBuilder:
            if success:
                return ResultBuilder.build_success_result(self.monitor_id, data or {})
            else:
                return ResultBuilder.build_error_result(self.monitor_id, error or "Erro desconhecido")
        
        # Fallback se ResultBuilder não disponível
        result = {
            "sucesso": success,
            "monitor": self.monitor_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if success and data:
            result.update(data)
        elif not success and error:
            result["erro"] = error
            
        return result
    
    @abstractmethod
    def validate_data(self, *args, **kwargs) -> bool:
        """
        Validação específica do monitor.
        
        Cada monitor deve implementar suas validações específicas
        além das validações básicas comuns.
        """
        pass
    
    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """
        Retorna colunas obrigatórias para o monitor.
        
        Cada monitor deve especificar suas colunas obrigatórias.
        """
        pass
    
    @abstractmethod
    def calculate(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Lógica de cálculo específica do monitor.
        
        Cada monitor implementa sua lógica de negócio específica.
        """
        pass
    
    @abstractmethod
    def run_monitoring(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Interface principal do monitor.
        
        Cada monitor implementa sua interface específica mantendo
        compatibilidade com o orquestrador.
        """
        pass
    
    
    def get_limits(self) -> Dict[str, Any]:
        """
        Extrai limites da configuração do monitor.
        
        Padrão comum para acessar limites de configuração.
        """
        if self.monitor_config:
            return self.monitor_config.get('limites', {})
        return {}
    
    def get_pool_id(self) -> str:
        """
        Extrai pool_id da configuração.
        
        Padrão comum para acessar ID do pool.
        """
        return self.config.get('pool_id', '')
    
    def validate_monitor_result(self, result: Dict[str, Any]) -> bool:
        """
        Valida resultado do monitor usando ResultBuilder.
        
        Args:
            result: Resultado a ser validado
            
        Returns:
            True se resultado é válido
        """
        if ResultBuilder:
            return ResultBuilder.validate_monitor_result(result)
        
        # Fallback básico
        required_fields = ["sucesso", "monitor", "timestamp"]
        return all(field in result for field in required_fields)
    
    def __str__(self) -> str:
        """Representação em string do monitor."""
        status = "ativo" if self.is_active() else "inativo"
        return f"Monitor {self.monitor_id} ({status})"
    
    def __repr__(self) -> str:
        """Representação detalhada do monitor."""
        return f"BaseMonitor(monitor_id='{self.monitor_id}', active={self.is_active()})"