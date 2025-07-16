"""
Concentration Configuration Parser
=================================

Parser universal para configurações de concentração de diferentes pools.
Normaliza formatos heterogêneos em estruturas padronizadas.

Based on Building Block 1 analysis:
- 4 tipos: individual, top_n, lista_especifica, ausente
- 2 entidades: sacado, cedente  
- 3 métodos: simples, 8_digitos_cnpj_raiz, grupo_economico
- Complexidade: 0-4 limites por pool

Author: Claude (Building Block 2)
Date: 2025-07-15
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ConcentrationType(Enum):
    """Tipos de concentração identificados nos pools."""
    INDIVIDUAL = "individual"
    TOP_N = "top_n"
    LISTA_ESPECIFICA = "lista_especifica"
    AUSENTE = "ausente"


class ConcentrationEntity(Enum):
    """Entidades monitoradas para concentração."""
    SACADO = "sacado"
    CEDENTE = "cedente"


class CalculationMethod(Enum):
    """Métodos de cálculo de concentração."""
    SIMPLES = "simples"
    CNPJ_8_DIGITOS = "8_digitos_cnpj_raiz"


@dataclass
class ConcentrationLimit:
    """Estrutura normalizada para um limite de concentração."""
    tipo: ConcentrationType
    entidade: ConcentrationEntity
    limite: float
    n: Optional[int] = None  # Para top_n
    metodo_calculo: CalculationMethod = CalculationMethod.SIMPLES
    
    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.tipo == ConcentrationType.TOP_N and self.n is None:
            raise ValueError("Top-N concentration requires 'n' parameter")
        
        if self.limite < 0 or self.limite > 1:
            raise ValueError(f"Limite deve estar entre 0 e 1, encontrado: {self.limite}")


@dataclass
class ConcentrationConfig:
    """Configuração completa de concentração de um pool."""
    pool_id: str
    ativo: bool
    limites: List[ConcentrationLimit]
    sacados_elegiveis: List[str] = None
    campos_necessarios: List[str] = None
    
    def __post_init__(self):
        """Configurações padrão pós-inicialização."""
        if self.campos_necessarios is None:
            self.campos_necessarios = ["sacado", "cedente", "valor_presente"]
    
    @property
    def tem_limites(self) -> bool:
        """Verifica se há limites configurados."""
        return len(self.limites) > 0
    
    @property
    def complexidade(self) -> str:
        """Classifica complexidade baseado no número de limites."""
        num_limites = len(self.limites)
        if num_limites == 0:
            return "sem_limites"
        elif num_limites == 1:
            return "simples"
        elif num_limites == 2:
            return "media"
        else:
            return "alta"
    
    def get_limits_by_type(self, tipo: ConcentrationType) -> List[ConcentrationLimit]:
        """Filtra limites por tipo."""
        return [limit for limit in self.limites if limit.tipo == tipo]
    
    def get_limits_by_entity(self, entidade: ConcentrationEntity) -> List[ConcentrationLimit]:
        """Filtra limites por entidade."""
        return [limit for limit in self.limites if limit.entidade == entidade]


class ConcentrationConfigParser:
    """Parser para diferentes formatos de configuração de concentração."""
    
    @staticmethod
    def parse_from_json(config: Dict[str, Any]) -> ConcentrationConfig:
        """
        Parseia configuração de concentração do JSON de um pool.
        
        Args:
            config: Configuração completa do pool (JSON)
            
        Returns:
            ConcentrationConfig: Configuração normalizada
            
        Raises:
            ValueError: Se configuração inválida
        """
        pool_id = config.get('pool_id', 'desconhecido')
        
        # Buscar monitor de concentração
        monitor = ConcentrationConfigParser._find_concentration_monitor(config)
        
        if monitor is None:
            # Pool sem concentração (Up Vendas, a55)
            return ConcentrationConfig(
                pool_id=pool_id,
                ativo=False,
                limites=[]
            )
        
        # Verificar se monitor está ativo
        if not monitor.get('ativo', False):
            return ConcentrationConfig(
                pool_id=pool_id,
                ativo=False,
                limites=[]
            )
        
        # Parsear limites
        limites = []
        limites_config = monitor.get('limites', [])
        
        for limite_config in limites_config:
            limite = ConcentrationConfigParser._parse_limite(limite_config)
            limites.append(limite)
        
        # Extrair sacados elegíveis se houver
        sacados_elegiveis = config.get('sacados_elegiveis', [])
        
        # Extrair campos necessários do monitor
        campos_necessarios = monitor.get('campos_necessarios', [])
        
        return ConcentrationConfig(
            pool_id=pool_id,
            ativo=True,
            limites=limites,
            sacados_elegiveis=sacados_elegiveis if sacados_elegiveis else None,
            campos_necessarios=campos_necessarios if campos_necessarios else None
        )
    
    @staticmethod
    def _find_concentration_monitor(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Busca monitor de concentração na configuração."""
        monitores = config.get('monitoramentos_ativos', [])
        
        for monitor in monitores:
            if monitor.get('tipo') == 'concentracao':
                return monitor
        
        return None
    
    @staticmethod
    def _parse_limite(limite_config: Dict[str, Any]) -> ConcentrationLimit:
        """Parseia um limite individual."""
        # Determinar tipo
        tipo_str = limite_config.get('tipo', 'individual')
        tipo = ConcentrationType(tipo_str)
        
        # Determinar entidade
        entidade_str = limite_config.get('entidade', 'sacado')
        entidade = ConcentrationEntity(entidade_str)
        
        # Valor do limite
        limite_valor = limite_config.get('limite', 0.0)
        
        # Parâmetros opcionais
        n = limite_config.get('n')
        
        # Método de cálculo
        metodo_str = limite_config.get('metodo_calculo', 'simples')
        if metodo_str == 'simples':
            metodo = CalculationMethod.SIMPLES
        elif metodo_str == '8_digitos_cnpj_raiz':
            metodo = CalculationMethod.CNPJ_8_DIGITOS
        else:
            # Outros métodos customizados
            metodo = CalculationMethod.SIMPLES  # Default para métodos não implementados
        
        return ConcentrationLimit(
            tipo=tipo,
            entidade=entidade,
            limite=limite_valor,
            n=n,
            metodo_calculo=metodo
        )
    
    @staticmethod
    def validate_config(config: ConcentrationConfig) -> List[str]:
        """
        Valida configuração de concentração.
        
        Args:
            config: Configuração a validar
            
        Returns:
            Lista de erros encontrados (vazia se válida)
        """
        errors = []
        
        # Validar pool_id
        if not config.pool_id or config.pool_id == 'desconhecido':
            errors.append("pool_id é obrigatório")
        
        # Validar limites se ativo
        if config.ativo:
            if not config.limites:
                errors.append("Monitor ativo deve ter pelo menos 1 limite")
            
            # Validar cada limite
            for i, limite in enumerate(config.limites):
                try:
                    # Validações já são feitas no __post_init__
                    pass
                except ValueError as e:
                    errors.append(f"Limite {i+1}: {str(e)}")
        
        # Validar campos necessários
        if config.ativo and not config.campos_necessarios:
            errors.append("Campos necessários não definidos")
        
        return errors


def create_concentration_config(pool_config: Dict[str, Any]) -> ConcentrationConfig:
    """
    Função de conveniência para criar configuração de concentração.
    
    Args:
        pool_config: Configuração completa do pool
        
    Returns:
        ConcentrationConfig: Configuração normalizada
        
    Raises:
        ValueError: Se configuração inválida
    """
    config = ConcentrationConfigParser.parse_from_json(pool_config)
    
    # Validar configuração
    errors = ConcentrationConfigParser.validate_config(config)
    if errors:
        raise ValueError(f"Configuração inválida: {', '.join(errors)}")
    
    return config


if __name__ == "__main__":
    # Exemplo de uso
    print("ConcentrationConfig carregado com sucesso")
    print("Use create_concentration_config(pool_config) para criar configurações")