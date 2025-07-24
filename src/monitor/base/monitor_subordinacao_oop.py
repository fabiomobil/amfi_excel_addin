"""
Monitor de Subordinação - Versão Orientada a Objetos
=====================================================

Refatoração do monitor de subordinação usando arquitetura OOP baseada em BaseMonitor.
Mantém 100% compatibilidade com a interface original run_subordination_monitoring().

Responsabilidades:
- Monitorar Subordination Ratio (SR) mínimo e crítico
- Cálculos de adequação patrimonial
- Aportes necessários para regularização

Melhorias implementadas:
- Herança de BaseMonitor (elimina redundâncias)
- Validação centralizada
- Resultado padronizado via ResultBuilder
- Código mais limpo e reutilizável

Autor: AmFi Development Team
Data: 2025-07-17
"""

import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

# Imports das classes base
try:
    from .base_monitor import BaseMonitor
    from .result_builder import ResultBuilder
except ImportError:
    from base_monitor import BaseMonitor
    from result_builder import ResultBuilder


class SubordinationMonitor(BaseMonitor):
    """
    Monitor de subordinação usando arquitetura orientada a objetos.
    
    Herda de BaseMonitor e implementa lógica específica de subordinação:
    - Validação de dados financeiros
    - Cálculo de subordination ratio
    - Análise de compliance com limites
    - Cálculo de aportes necessários
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa monitor de subordinação.
        
        Args:
            config: Configuração JSON completa do pool
        """
        super().__init__(monitor_id="subordinacao", config=config)
    
    def get_required_columns(self) -> List[str]:
        """
        Retorna colunas obrigatórias para monitoramento de subordinação.
        
        Obtém campos necessários da configuração JSON ou usa padrão.
        
        Returns:
            Lista de colunas obrigatórias
        """
        if self.monitor_config:
            return self.monitor_config.get('campos_necessarios', ['pl', 'sr', 'jr'])
        return ['pl', 'sr', 'jr']
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validação específica para monitoramento de subordinação.
        
        Extends BaseMonitor.validate_basic_data() com validações específicas:
        - Valores numéricos positivos
        - Configuração de limites válida
        - Consistência entre limites crítico e mínimo
        
        Args:
            df: DataFrame com dados da carteira (CSV)
            
        Returns:
            True se dados são válidos
        """
        try:
            # 1. Validações básicas via BaseMonitor
            required_columns = self.get_required_columns()
            if not self.validate_basic_data(df, required_columns):
                return False
            
            # 2. Validações específicas de subordinação
            
            # Verificar se valores são numéricos (dados já convertidos pelo data_loader)
            for col in required_columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise ValueError(f"Coluna '{col}' não é numérica")
                
                # Verificar se valores são positivos
                valores_negativos = df[col] < 0
                if valores_negativos.any():
                    raise ValueError(f"Coluna '{col}' contém valores negativos")
            
            # Verificar configuração de limites
            limites = self.get_limits()
            if not limites:
                raise ValueError("Monitor de subordinação não possui 'limites' definidos")
            
            # Verificar limites obrigatórios
            limites_obrigatorios = ['minimo', 'critico']
            limites_faltantes = [limite for limite in limites_obrigatorios if limite not in limites]
            if limites_faltantes:
                raise ValueError(f"Limites obrigatórios ausentes: {limites_faltantes}")
            
            # Validar se limites fazem sentido (crítico <= mínimo)
            limite_minimo = limites.get('minimo')
            limite_critico = limites.get('critico')
            if limite_critico > limite_minimo:
                raise ValueError(f"Limite crítico ({limite_critico}) não pode ser maior que mínimo ({limite_minimo})")
            
            return True
            
        except Exception as e:
            print(f"Erro na validação de subordinação: {e}")
            return False
    
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula o subordination ratio atual da carteira.
        
        Fórmula: SR = JR / (SR + JR) ou SR = Subordinada / (Senior + Subordinada)
        
        Args:
            df: DataFrame com dados da carteira (CSV)
            
        Returns:
            Dict com valor atual, limites, status e aportes necessários
        """
        try:
            # Obter valores financeiros do CSV (assumindo primeira linha para o pool)
            linha_pool = df.iloc[0]
            
            # Obter valores financeiros já convertidos pelo data_loader (colunas minúsculas)
            pl_atual = linha_pool['pl'] if not pd.isna(linha_pool['pl']) else 0.0
            sr_atual = linha_pool['sr'] if not pd.isna(linha_pool['sr']) else 0.0
            jr_atual = linha_pool['jr'] if not pd.isna(linha_pool['jr']) else 0.0
            
            # Validar se valores fazem sentido
            if pl_atual <= 0:
                raise ValueError(f"PL inválido: {pl_atual}")
            if sr_atual < 0 or jr_atual < 0:
                raise ValueError(f"Valores negativos: SR={sr_atual}, JR={jr_atual}")
            
            # Calcular subordination ratio atual (fórmula correta: JR / (SR + JR))
            denominador = sr_atual + jr_atual
            if denominador > 0:
                subordination_ratio = jr_atual / denominador  # Resultado em decimal (0.25 = 25%)
            else:
                raise ValueError("Denominador zero: SR + JR = 0")
            
            # Obter limites da configuração (em decimal: 0.25 = 25%)
            limites = self.get_limits()
            limite_minimo = limites['minimo']  # ex: 0.25
            limite_critico = limites['critico']  # ex: 0.20
            
            # Determinar status para cada limite (comparação em decimal)
            status_minimo = "enquadrado" if subordination_ratio >= limite_minimo else "violado"
            status_critico = "enquadrado" if subordination_ratio >= limite_critico else "violado"
            
            # Calcular aportes necessários (apenas se violado)
            # Fórmula: SR_min = (JR + x) / (PL + x)
            # Resolvendo: x = (SR_min * PL - JR) / (1 - SR_min)
            aporte_minimo = 0.0
            aporte_critico = 0.0
            
            if status_minimo == "violado":
                aporte_minimo = (limite_minimo * pl_atual - jr_atual) / (1 - limite_minimo)
                aporte_minimo = max(0.0, aporte_minimo)  # Garantir que não seja negativo
            
            if status_critico == "violado":
                aporte_critico = (limite_critico * pl_atual - jr_atual) / (1 - limite_critico)
                aporte_critico = max(0.0, aporte_critico)  # Garantir que não seja negativo
            
            resultado = {
                "subordination_ratio": round(subordination_ratio, 4),  # Decimal: 0.2517 = 25.17%
                "subordination_ratio_percent": round(subordination_ratio * 100, 2),  # Para exibição: 25.17%
                "limite_minimo": limite_minimo,
                "limite_critico": limite_critico,
                "status_limite_minimo": status_minimo,
                "status_limite_critico": status_critico,
                "aporte_necessario": {
                    "para_limite_minimo": round(aporte_minimo, 2),
                    "para_limite_critico": round(aporte_critico, 2)
                },
                "dados_financeiros": {
                    "pl_atual": pl_atual,
                    "sr_atual": sr_atual,
                    "jr_atual": jr_atual,
                    "denominador_calculo": denominador
                }
            }
            
            return resultado
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular subordination ratio: {str(e)}")
    
    def run_monitoring(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executa monitoramento completo de subordinação.
        
        Interface principal compatível com orquestrador.
        Usa ResultBuilder para padronizar resultado.
        
        Args:
            df: DataFrame com dados da carteira (CSV)
            
        Returns:
            Dict com resultado completo padronizado
        """
        try:
            # 1. Validar dados de entrada
            if not self.validate_data(df):
                return ResultBuilder.build_error_result(
                    monitor_name="subordination_ratio",
                    error_message="Falha na validação de dados"
                )
            
            # 2. Calcular subordination ratio
            resultado = self.calculate(df)
            
            # 3. Construir resultado de sucesso
            return ResultBuilder.build_success_result(
                monitor_name="subordination_ratio",
                data=resultado
            )
            
        except Exception as e:
            return ResultBuilder.build_error_result(
                monitor_name="subordination_ratio",
                error_message=f"Erro inesperado no monitoramento: {str(e)}"
            )


# Função de compatibilidade com interface original
def run_subordination_monitoring(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função de compatibilidade com interface original.
    
    Mantém 100% compatibilidade com código existente.
    Internamente usa SubordinationMonitor.
    
    Args:
        df: DataFrame com dados da carteira (CSV)
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com resultado completo (formato original)
    """
    monitor = SubordinationMonitor(config)
    return monitor.run_monitoring(df)


# Função auxiliar para uso direto da classe
def create_subordination_monitor(config: Dict[str, Any]) -> SubordinationMonitor:
    """
    Factory function para criar monitor de subordinação.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Instância de SubordinationMonitor
    """
    return SubordinationMonitor(config)