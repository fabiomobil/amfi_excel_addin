"""
Classe para gerenciamento centralizado de dados - AmFi Sistema de Monitoramento

Esta classe centraliza o gerenciamento de dados, enriquecimento progressivo e filtros
por pool, eliminando redundâncias identificadas nos monitores existentes.

Responsabilidades:
- Gerenciamento centralizado de DataFrames CSV e XLSX
- Enriquecimento progressivo de dados (dias_atraso, grupo_de_risco)
- Filtros por pool padronizados
- Controle de estado de enriquecimento
- Otimização de performance (cálculos únicos)

Padrões Centralizados:
- Filtro por pool: get_pool_data()
- Enriquecimento condicional: ensure_enriched()
- Controle de estado: _enriched_fields
- Reutilização de dados: evita recálculos

Autor: AmFi Development Team
Data: 2025-07-17
"""

import pandas as pd
from typing import Dict, Any, List, Tuple, Set, Optional
from datetime import datetime
import numpy as np


class DataHandler:
    """
    Gerenciador centralizado de dados para o sistema de monitoramento.
    
    Centraliza padrões identificados pelos agentes:
    - Enriquecimento progressivo do DataFrame XLSX
    - Filtros por pool padronizados
    - Controle de estado de enriquecimento
    """
    
    def __init__(self, csv_data: pd.DataFrame, xlsx_data: pd.DataFrame, 
                 pools_configs: Dict[str, Dict[str, Any]]):
        """
        Inicializa o gerenciador de dados.
        
        Args:
            csv_data: DataFrame com dados agregados dos pools
            xlsx_data: DataFrame com carteira detalhada (será enriquecido)
            pools_configs: Configurações JSON de todos os pools
        """
        self.csv_data = csv_data
        self.xlsx_data = xlsx_data  # Referência, não cópia
        self.pools_configs = pools_configs
        self._enriched_fields: Set[str] = set()
        self._original_columns = set(xlsx_data.columns)
        
    def get_pool_data(self, pool_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filtra dados CSV e XLSX para pool específico.
        
        Centraliza lógica de filtro identificada no orquestrador:
        - Tratamento de diferentes nomes de colunas (nome/Nome)
        - Filtros consistentes por pool
        - Validação de dados encontrados
        
        Args:
            pool_name: Nome do pool para filtrar
            
        Returns:
            Tuple com (csv_filtrado, xlsx_filtrado)
        """
        # Filtro CSV - tratamento de diferentes nomes de coluna
        nome_col = 'nome' if 'nome' in self.csv_data.columns else 'Nome'
        pool_csv = self.csv_data[self.csv_data[nome_col] == pool_name]
        
        # Filtro XLSX - usar coluna 'pool' padronizada
        pool_xlsx = self.xlsx_data[self.xlsx_data['pool'] == pool_name]
        
        # Validação
        if pool_csv.empty:
            raise ValueError(f"Pool '{pool_name}' não encontrado nos dados CSV")
        if pool_xlsx.empty:
            raise ValueError(f"Pool '{pool_name}' não encontrado nos dados XLSX")
            
        return pool_csv, pool_xlsx
    
    def ensure_enriched(self, fields: List[str]) -> None:
        """
        Garante que campos específicos estejam enriquecidos no DataFrame XLSX.
        
        Implementa enriquecimento progressivo identificado no monitor de inadimplência:
        - Cálculo único, reutilização múltipla
        - Modificação in-place do DataFrame
        - Controle de estado para evitar recálculos
        
        Args:
            fields: Lista de campos a serem enriquecidos
                   Suportados: ['dias_atraso', 'grupo_de_risco']
        """
        for field in fields:
            if field not in self._enriched_fields:
                if field == 'dias_atraso':
                    self._calculate_days_overdue()
                elif field == 'grupo_de_risco':
                    self._calculate_risk_groups()
                else:
                    raise ValueError(f"Campo de enriquecimento não suportado: {field}")
                
                self._enriched_fields.add(field)
    
    def _calculate_days_overdue(self) -> None:
        """
        Calcula dias de atraso para toda a carteira.
        
        Baseado na implementação do monitor de inadimplência:
        - Cálculo: (data_atual - vencimento_original).days
        - Apenas valores positivos (negativo = não vencido)
        - Aplicado a todos os 79k+ registros
        """
        if 'vencimento_original' not in self.xlsx_data.columns:
            raise ValueError("Coluna 'vencimento_original' não encontrada")
        
        # Converter para datetime se necessário
        if not pd.api.types.is_datetime64_any_dtype(self.xlsx_data['vencimento_original']):
            self.xlsx_data['vencimento_original'] = pd.to_datetime(
                self.xlsx_data['vencimento_original'], errors='coerce'
            )
        
        # Calcular dias de atraso
        data_atual = datetime.now()
        self.xlsx_data['dias_atraso'] = (
            data_atual - self.xlsx_data['vencimento_original']
        ).dt.days
        
        # Apenas valores positivos (negativo = não vencido)
        self.xlsx_data['dias_atraso'] = self.xlsx_data['dias_atraso'].clip(lower=0)
        
        # Preencher NaN com 0
        self.xlsx_data['dias_atraso'] = self.xlsx_data['dias_atraso'].fillna(0).astype(int)
    
    def _calculate_risk_groups(self) -> None:
        """
        Calcula grupos de risco para toda a carteira.
        
        Baseado na implementação do monitor de inadimplência:
        - Usa configuração PDD do primeiro pool processado
        - Mapeamento de dias_atraso para grupos AA-H
        - Fallback para grupo 'H' se não encontrar configuração
        """
        # Garantir que dias_atraso existe
        if 'dias_atraso' not in self._enriched_fields:
            self.ensure_enriched(['dias_atraso'])
        
        # Obter configuração PDD do primeiro pool (estratégia atual)
        pdd_config = self._get_pdd_config()
        if not pdd_config:
            # Fallback: classificar tudo como grupo 'H'
            self.xlsx_data['grupo_de_risco'] = 'H'
            return
        
        # Mapeamento de dias de atraso para grupos de risco
        def classify_risk_group(dias_atraso: int) -> str:
            for grupo, config in pdd_config.items():
                if dias_atraso <= config.get('atraso_max_dias', 0):
                    return grupo
            return 'H'  # Fallback para pior grupo
        
        self.xlsx_data['grupo_de_risco'] = self.xlsx_data['dias_atraso'].apply(
            classify_risk_group
        )
    
    def _get_pdd_config(self) -> Optional[Dict[str, Any]]:
        """
        Obtém configuração PDD do primeiro pool que possui.
        
        Estratégia atual do sistema: usar configuração do primeiro pool
        para classificar toda a carteira globalmente.
        """
        for pool_name, config in self.pools_configs.items():
            pdd_config = config.get('provisoes_pdd', {}).get('grupos_risco', {})
            if pdd_config:
                return pdd_config
        
        return None
    
    def get_enriched_fields(self) -> Set[str]:
        """
        Retorna conjunto de campos já enriquecidos.
        
        Returns:
            Set com nomes dos campos enriquecidos
        """
        return self._enriched_fields.copy()
    
    def get_original_columns(self) -> Set[str]:
        """
        Retorna conjunto de colunas originais do DataFrame.
        
        Returns:
            Set com nomes das colunas originais
        """
        return self._original_columns.copy()
    
    def is_enriched(self, field: str) -> bool:
        """
        Verifica se campo específico está enriquecido.
        
        Args:
            field: Nome do campo a verificar
            
        Returns:
            True se campo está enriquecido
        """
        return field in self._enriched_fields
    
    def get_pool_config(self, pool_name: str) -> Dict[str, Any]:
        """
        Obtém configuração específica de um pool.
        
        Args:
            pool_name: Nome do pool
            
        Returns:
            Dict com configuração do pool
        """
        if pool_name not in self.pools_configs:
            raise ValueError(f"Configuração do pool '{pool_name}' não encontrada")
        
        return self.pools_configs[pool_name]
    
    def get_available_pools(self) -> List[str]:
        """
        Retorna lista de pools disponíveis nos dados.
        
        Returns:
            Lista com nomes dos pools
        """
        return list(self.pools_configs.keys())
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo dos dados carregados.
        
        Returns:
            Dict com estatísticas dos dados
        """
        return {
            "csv_records": len(self.csv_data),
            "xlsx_records": len(self.xlsx_data),
            "pools_available": len(self.pools_configs),
            "enriched_fields": list(self._enriched_fields),
            "original_columns": len(self._original_columns),
            "current_columns": len(self.xlsx_data.columns)
        }
    
    def __str__(self) -> str:
        """Representação em string do DataHandler."""
        return f"DataHandler(CSV: {len(self.csv_data)}, XLSX: {len(self.xlsx_data)}, Pools: {len(self.pools_configs)})"
    
    def __repr__(self) -> str:
        """Representação detalhada do DataHandler."""
        return (f"DataHandler(csv_records={len(self.csv_data)}, "
                f"xlsx_records={len(self.xlsx_data)}, "
                f"pools={len(self.pools_configs)}, "
                f"enriched_fields={list(self._enriched_fields)})")