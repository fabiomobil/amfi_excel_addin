"""
Base Cash Flow Engine - Análise de Fluxo de Caixa
================================================

Classe base abstrata para análise de fluxo de caixa do sistema AmFi.
Define interface comum para as duas modalidades de análise.

Modalidades:
1. PU_Analysis_Engine: Segregar juros vs amortização
2. PL_Percentage_Engine: Pagamento total proporcional

Autor: AmFi Development Team
Data: 2025-07-18
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta


class BaseCashFlowEngine(ABC):
    """
    Classe base abstrata para análise de fluxo de caixa.
    
    Define interface comum para as duas modalidades:
    - Modalidade 1: Análise por PU (segregar juros vs amortização)
    - Modalidade 2: Análise por % PL (pagamento total proporcional)
    """
    
    def __init__(self, config: Dict[str, Any], csv_data: pd.DataFrame, xlsx_data: pd.DataFrame):
        """
        Inicializa engine de análise de fluxo de caixa.
        
        Args:
            config: Configuração JSON completa do pool
            csv_data: DataFrame com dados do dashboard (PL, caixa, etc.)
            xlsx_data: DataFrame com portfolio detalhado (enriquecido)
        """
        self.config = config
        self.csv_data = csv_data
        self.xlsx_data = xlsx_data
        
        # Validar dados na inicialização
        if not self.validate_data_sources():
            raise ValueError("Fontes de dados inválidas")
    
    @abstractmethod
    def calculate_new_pu(self, current_pu: float) -> Dict[str, Any]:
        """
        Calcula o novo PU após o próximo pagamento.
        
        Args:
            current_pu: PU atual do pool
            
        Returns:
            Dict com novo PU e detalhes do cálculo
        """
        pass
    
    @abstractmethod
    def calculate_payment_need(self) -> Dict[str, Any]:
        """
        Calcula a necessidade de pagamento do próximo vencimento.
        
        Returns:
            Dict com valor do pagamento e detalhes
        """
        pass
    
    def validate_data_sources(self) -> bool:
        """
        Validação comum das fontes de dados.
        
        Returns:
            True se dados são válidos
        """
        try:
            # Validar CSV
            if self.csv_data.empty:
                return False
                
            # Validar XLSX
            if self.xlsx_data.empty:
                return False
                
            # Validar config
            if not self.config or 'cronograma_amortizacao' not in self.config:
                return False
                
            return True
            
        except Exception:
            return False
    
    def get_next_payment_info(self) -> Tuple[str, float]:
        """
        Identifica próximo pagamento do cronograma.
        
        Returns:
            Tuple com (data_pagamento, percentual)
        """
        try:
            cronograma = self.config.get('cronograma_amortizacao', {})
            schedule = cronograma.get('cronograma_amortizacao', [])
            
            if not schedule:
                raise ValueError("Cronograma de amortização não encontrado")
            
            # Encontrar próxima data > hoje
            today = datetime.now().date()
            
            for payment in schedule:
                payment_date = datetime.strptime(payment['data'], '%Y-%m-%d').date()
                if payment_date > today:
                    return payment['data'], payment['percentual']
            
            # Se não encontrou, usar primeiro do cronograma
            return schedule[0]['data'], schedule[0]['percentual']
            
        except Exception as e:
            raise ValueError(f"Erro ao obter próximo pagamento: {str(e)}")
    
    def get_current_pl(self) -> float:
        """
        Obtém PL atual do CSV.
        
        Returns:
            Valor do PL atual
        """
        try:
            return float(self.csv_data['pl'].iloc[0])
        except Exception as e:
            raise ValueError(f"Erro ao obter PL atual: {str(e)}")
    
    def get_available_cash(self) -> float:
        """
        Calcula caixa disponível (caixa + saldo em aplicações).
        
        Returns:
            Valor do caixa disponível
        """
        try:
            caixa = float(self.csv_data['caixa'].iloc[0])
            saldo_aplicacoes = float(self.csv_data['saldo em aplicações'].iloc[0])
            return caixa + saldo_aplicacoes
        except Exception as e:
            raise ValueError(f"Erro ao calcular caixa disponível: {str(e)}")
    
    def run_analysis(self, current_pu: float) -> Dict[str, Any]:
        """
        Executa análise completa de fluxo de caixa.
        
        Args:
            current_pu: PU atual do pool
            
        Returns:
            Dict com análise completa
        """
        try:
            # Calcular necessidade de pagamento
            payment_analysis = self.calculate_payment_need()
            
            # Calcular novo PU
            new_pu_analysis = self.calculate_new_pu(current_pu)
            
            # Compilar resultado
            return {
                'pool': self.config.get('pool_name', 'Unknown'),
                'modality': self.__class__.__name__,
                'current_pu': current_pu,
                'payment_analysis': payment_analysis,
                'new_pu_analysis': new_pu_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'pool': self.config.get('pool_name', 'Unknown'),
                'modality': self.__class__.__name__,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }