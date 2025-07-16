"""
Concentration Calculation Strategies
===================================

Estratégias de cálculo para diferentes tipos de concentração:
- IndividualConcentration: Por entidade específica (sacado/cedente)
- TopNConcentration: Top-N entidades
- EconomicGroupConcentration: Grupos econômicos agregados

Based on Building Block 2 analysis:
- Padrão Strategy Pattern para flexibilidade
- Implementação modular para cada tipo de concentração
- Suporte a diferentes métodos de cálculo

Author: Claude (Building Block 3)
Date: 2025-07-15
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import numpy as np

# Tentar import relativo, fallback para import direto
try:
    from .concentration_config import ConcentrationConfig, ConcentrationLimit, ConcentrationType, ConcentrationEntity, CalculationMethod
except (ImportError, ValueError):
    import sys
    import os
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from concentration_config import ConcentrationConfig, ConcentrationLimit, ConcentrationType, ConcentrationEntity, CalculationMethod


class ConcentrationStrategy(ABC):
    """Interface base para estratégias de cálculo de concentração."""
    
    @abstractmethod
    def calculate(self, 
                  carteira_df: pd.DataFrame, 
                  limite: ConcentrationLimit, 
                  pl_pool: float) -> Dict[str, Any]:
        """
        Calcula concentração para um limite específico.
        
        Args:
            carteira_df: DataFrame com carteira do pool
            limite: Configuração do limite
            pl_pool: Patrimônio líquido do pool (denominador)
            
        Returns:
            Dict com resultado do cálculo
        """
        pass


class IndividualConcentration(ConcentrationStrategy):
    """Estratégia para concentração individual por entidade."""
    
    def calculate(self, 
                  carteira_df: pd.DataFrame, 
                  limite: ConcentrationLimit, 
                  pl_pool: float) -> Dict[str, Any]:
        """
        Calcula concentração individual por entidade.
        
        Args:
            carteira_df: DataFrame com carteira do pool
            limite: Configuração do limite individual
            pl_pool: Patrimônio líquido do pool
            
        Returns:
            Dict com resultado da concentração individual
        """
        # Validar entrada
        if carteira_df.empty:
            return self._empty_result(limite)
        
        # Determinar coluna da entidade
        if limite.entidade == ConcentrationEntity.SACADO:
            entidade_col = 'nome_do_sacado'
        elif limite.entidade == ConcentrationEntity.CEDENTE:
            entidade_col = 'nome_do_cedente'
        else:
            raise ValueError(f"Entidade não suportada: {limite.entidade}")
        
        # Verificar se coluna existe
        if entidade_col not in carteira_df.columns:
            raise ValueError(f"Coluna '{entidade_col}' não encontrada na carteira")
        
        # Aplicar método de cálculo
        if limite.metodo_calculo == CalculationMethod.SIMPLES:
            concentracao_df = self._calculate_simple(carteira_df, entidade_col)
        elif limite.metodo_calculo == CalculationMethod.CNPJ_8_DIGITOS:
            concentracao_df = self._calculate_cnpj_8_digits(carteira_df, entidade_col)
        else:
            # Default para métodos não implementados
            concentracao_df = self._calculate_simple(carteira_df, entidade_col)
        
        # Calcular percentuais vs PL
        concentracao_df['percentual_pl'] = (concentracao_df['valor_total'] / pl_pool) * 100
        
        # Identificar maior concentração
        maior_concentracao = concentracao_df.loc[concentracao_df['percentual_pl'].idxmax()]
        
        # Verificar violação
        limite_percent = limite.limite * 100
        violacao = maior_concentracao['percentual_pl'] > limite_percent
        
        # Calcular entidades em violação
        entidades_violacao = concentracao_df[concentracao_df['percentual_pl'] > limite_percent]
        
        # Gerar resultado
        resultado = {
            "tipo": "individual",
            "entidade": limite.entidade.value,
            "limite_configurado": limite_percent,
            "metodo_calculo": limite.metodo_calculo.value,
            "pl_pool": pl_pool,
            "maior_concentracao": {
                "entidade": maior_concentracao['entidade'],
                "valor_absoluto": float(maior_concentracao['valor_total']),
                "percentual_pl": float(maior_concentracao['percentual_pl']),
                "quantidade_titulos": int(maior_concentracao['quantidade_titulos'])
            },
            "status": "violado" if violacao else "enquadrado",
            "margem_limite": limite_percent - maior_concentracao['percentual_pl'],
            "entidades_em_violacao": len(entidades_violacao),
            "total_entidades_analisadas": len(concentracao_df),
            "top_10_concentracoes": self._get_top_concentrations(concentracao_df, 10),
            "detalhes_violacoes": self._get_violation_details(entidades_violacao, limite_percent) if violacao else []
        }
        
        return resultado
    
    def _calculate_simple(self, carteira_df: pd.DataFrame, entidade_col: str) -> pd.DataFrame:
        """Cálculo simples: valor presente por entidade."""
        return carteira_df.groupby(entidade_col).agg({
            'valor_presente': ['sum', 'count']
        }).reset_index().pipe(self._flatten_columns, entidade_col)
    
    def _calculate_cnpj_8_digits(self, carteira_df: pd.DataFrame, entidade_col: str) -> pd.DataFrame:
        """Cálculo por CNPJ 8 dígitos (raiz)."""
        # Implementar lógica de extração de CNPJ raiz
        # Por enquanto, fallback para cálculo simples
        # TODO: Implementar extração de CNPJ raiz quando coluna CNPJ estiver disponível
        return self._calculate_simple(carteira_df, entidade_col)
    
    def _flatten_columns(self, df: pd.DataFrame, entidade_col: str) -> pd.DataFrame:
        """Achatar colunas MultiIndex para formato padrão."""
        df.columns = [entidade_col, 'valor_total', 'quantidade_titulos']
        df = df.rename(columns={entidade_col: 'entidade'})
        return df.sort_values('valor_total', ascending=False)
    
    def _get_top_concentrations(self, concentracao_df: pd.DataFrame, n: int) -> List[Dict[str, Any]]:
        """Retorna top N concentrações."""
        top_n = concentracao_df.head(n)
        return [
            {
                "entidade": row['entidade'],
                "valor_absoluto": float(row['valor_total']),
                "percentual_pl": float(row['percentual_pl']),
                "quantidade_titulos": int(row['quantidade_titulos'])
            }
            for _, row in top_n.iterrows()
        ]
    
    def _get_violation_details(self, violacoes_df: pd.DataFrame, limite: float) -> List[Dict[str, Any]]:
        """Retorna detalhes das violações."""
        return [
            {
                "entidade": row['entidade'],
                "valor_absoluto": float(row['valor_total']),
                "percentual_pl": float(row['percentual_pl']),
                "excesso_percentual": float(row['percentual_pl'] - limite),
                "quantidade_titulos": int(row['quantidade_titulos'])
            }
            for _, row in violacoes_df.iterrows()
        ]
    
    def _empty_result(self, limite: ConcentrationLimit) -> Dict[str, Any]:
        """Resultado para carteira vazia."""
        return {
            "tipo": "individual",
            "entidade": limite.entidade.value,
            "limite_configurado": limite.limite * 100,
            "metodo_calculo": limite.metodo_calculo.value,
            "pl_pool": 0.0,
            "maior_concentracao": {
                "entidade": "N/A",
                "valor_absoluto": 0.0,
                "percentual_pl": 0.0,
                "quantidade_titulos": 0
            },
            "status": "enquadrado",
            "margem_limite": limite.limite * 100,
            "entidades_em_violacao": 0,
            "total_entidades_analisadas": 0,
            "top_10_concentracoes": [],
            "detalhes_violacoes": []
        }


class TopNConcentration(ConcentrationStrategy):
    """Estratégia para concentração Top-N."""
    
    def calculate(self, 
                  carteira_df: pd.DataFrame, 
                  limite: ConcentrationLimit, 
                  pl_pool: float) -> Dict[str, Any]:
        """
        Calcula concentração Top-N.
        
        Args:
            carteira_df: DataFrame com carteira do pool
            limite: Configuração do limite Top-N
            pl_pool: Patrimônio líquido do pool
            
        Returns:
            Dict com resultado da concentração Top-N
        """
        # Validar entrada
        if carteira_df.empty:
            return self._empty_result(limite)
        
        if limite.n is None:
            raise ValueError("Limite Top-N requer parâmetro 'n'")
        
        # Usar IndividualConcentration para obter concentrações individuais
        individual_strategy = IndividualConcentration()
        resultado_individual = individual_strategy.calculate(carteira_df, limite, pl_pool)
        
        # Extrair top N concentrações
        top_n_concentracoes = resultado_individual['top_10_concentracoes'][:limite.n]
        
        # Calcular total do top N
        total_top_n = sum(item['valor_absoluto'] for item in top_n_concentracoes)
        percentual_top_n = (total_top_n / pl_pool) * 100
        
        # Verificar violação
        limite_percent = limite.limite * 100
        violacao = percentual_top_n > limite_percent
        
        # Gerar resultado
        resultado = {
            "tipo": "top_n",
            "entidade": limite.entidade.value,
            "n": limite.n,
            "limite_configurado": limite_percent,
            "metodo_calculo": limite.metodo_calculo.value,
            "pl_pool": pl_pool,
            "concentracao_top_n": {
                "valor_absoluto": total_top_n,
                "percentual_pl": percentual_top_n,
                "quantidade_entidades": len(top_n_concentracoes)
            },
            "status": "violado" if violacao else "enquadrado",
            "margem_limite": limite_percent - percentual_top_n,
            "detalhes_top_n": top_n_concentracoes,
            "total_entidades_analisadas": resultado_individual['total_entidades_analisadas']
        }
        
        return resultado
    
    def _empty_result(self, limite: ConcentrationLimit) -> Dict[str, Any]:
        """Resultado para carteira vazia."""
        return {
            "tipo": "top_n",
            "entidade": limite.entidade.value,
            "n": limite.n,
            "limite_configurado": limite.limite * 100,
            "metodo_calculo": limite.metodo_calculo.value,
            "pl_pool": 0.0,
            "concentracao_top_n": {
                "valor_absoluto": 0.0,
                "percentual_pl": 0.0,
                "quantidade_entidades": 0
            },
            "status": "enquadrado",
            "margem_limite": limite.limite * 100,
            "detalhes_top_n": [],
            "total_entidades_analisadas": 0
        }


class ConcentrationStrategyFactory:
    """Factory para criar estratégias de concentração."""
    
    @staticmethod
    def create_strategy(tipo: ConcentrationType) -> ConcentrationStrategy:
        """
        Cria estratégia apropriada para o tipo de concentração.
        
        Args:
            tipo: Tipo de concentração
            
        Returns:
            ConcentrationStrategy: Estratégia apropriada
            
        Raises:
            ValueError: Se tipo não suportado
        """
        if tipo == ConcentrationType.INDIVIDUAL:
            return IndividualConcentration()
        elif tipo == ConcentrationType.TOP_N:
            return TopNConcentration()
        else:
            raise ValueError(f"Tipo de concentração não suportado: {tipo}")


def calculate_concentration_for_limit(
    carteira_df: pd.DataFrame, 
    limite: ConcentrationLimit, 
    pl_pool: float
) -> Dict[str, Any]:
    """
    Função de conveniência para calcular concentração.
    
    Args:
        carteira_df: DataFrame com carteira do pool
        limite: Configuração do limite
        pl_pool: Patrimônio líquido do pool
        
    Returns:
        Dict com resultado do cálculo
    """
    strategy = ConcentrationStrategyFactory.create_strategy(limite.tipo)
    return strategy.calculate(carteira_df, limite, pl_pool)


if __name__ == "__main__":
    # Exemplo de uso
    print("ConcentrationStrategies carregado com sucesso")
    print("Use calculate_concentration_for_limit() para calcular concentração")