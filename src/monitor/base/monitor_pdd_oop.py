"""
Monitor de PDD (Provisão para Devedores Duvidosos) - Versão Orientada a Objetos
==============================================================================

Refatoração completa do monitor PDD usando arquitetura OOP baseada em BaseMonitor.
Implementa lógica crítica por cedente SEM dependências do sistema funcional antigo.

Responsabilidades:
- Lógica por cedente (CRÍTICA): Pior ativo determina provisão de todos os títulos
- Cálculos de provisão por grupo de risco (AA-H)
- Análise detalhada por cedente
- Comparação metodológica (cedente vs individual)
- Relatórios de compliance

Funcionalidade CRÍTICA - Lógica por Cedente:
- Identifica ativo mais atrasado por cedente
- Aplica grupo de risco do pior ativo a TODAS as operações do cedente
- Títulos em dia recebem provisão do grupo mais alto do cedente

Dependências:
- Requer enriquecimento progressivo do Monitor de Inadimplência
- Campos obrigatórios: 'dias_atraso', 'grupo_de_risco', 'valor_presente', 'nome_do_cedente'

Melhorias da Arquitetura OOP:
- Herança de BaseMonitor (elimina redundâncias)
- Validação centralizada
- Tratamento de erro padronizado
- Código mais limpo e reutilizável
- Sem dependências do sistema funcional (será removido)

Autor: AmFi Development Team
Data: 2025-07-17
"""

import sys
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Adicionar path para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

try:
    from .base_monitor import BaseMonitor
except ImportError:
    # Fallback para execução direta
    from base_monitor import BaseMonitor


class PDDMonitor(BaseMonitor):
    """
    Monitor de PDD usando arquitetura orientada a objetos.
    
    Herda de BaseMonitor e implementa lógica específica de PDD:
    - Lógica crítica por cedente (pior ativo)
    - Cálculos de provisão por grupo de risco
    - Análise detalhada por cedente
    - Comparação metodológica
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa monitor PDD.
        
        Args:
            config: Configuração JSON completa do pool
        """
        super().__init__(monitor_id="pdd", config=config)
        self._pdd_config = self._find_pdd_config()
        self._grupos_risco = self._extract_risk_groups()
        
        # Debug removido - versão final
    
    def is_active(self) -> bool:
        """
        Verifica se o monitor PDD está ativo.
        
        Para PDD, considera ativo se houver configuração de grupos de risco.
        
        Returns:
            True se monitor está ativo
        """
        return self._pdd_config is not None and bool(self._grupos_risco)
    
    def get_required_columns(self) -> List[str]:
        """
        Retorna colunas obrigatórias para PDD.
        
        Todas essas colunas devem estar presentes no DataFrame enriquecido.
        
        Returns:
            Lista de colunas obrigatórias
        """
        return [
            'dias_atraso',       # Do enriquecimento progressivo
            'grupo_de_risco',    # Do enriquecimento progressivo
            'valor_presente',    # Valor do título
            'nome_do_cedente'    # Para lógica por cedente
        ]
    
    def validate_data(self, carteira_xlsx: pd.DataFrame) -> bool:
        """
        Validação específica para PDD.
        
        Args:
            carteira_xlsx: DataFrame com carteira enriquecida
            
        Returns:
            True se validação passou
        """
        try:
            # Validações básicas da classe base
            required_columns = self.get_required_columns()
            if not self.validate_basic_data(carteira_xlsx, required_columns):
                return False
            
            # Validação específica: dados enriquecidos presentes
            if 'dias_atraso' not in carteira_xlsx.columns:
                raise ValueError("Campo 'dias_atraso' não encontrado. Execute monitor de inadimplência primeiro.")
            
            if 'grupo_de_risco' not in carteira_xlsx.columns:
                raise ValueError("Campo 'grupo_de_risco' não encontrado. Execute monitor de inadimplência primeiro.")
            
            # Validação: configuração PDD existe
            if not self._pdd_config:
                raise ValueError("Configuração PDD não encontrada em 'provisoes_pdd.grupos_risco'")
            
            # Validação: grupos de risco válidos
            grupos_validos = set(self._grupos_risco.keys())
            grupos_nos_dados = set(carteira_xlsx['grupo_de_risco'].dropna().unique())
            grupos_invalidos = grupos_nos_dados - grupos_validos
            
            if grupos_invalidos:
                raise ValueError(f"Grupos de risco inválidos: {grupos_invalidos}. Válidos: {grupos_validos}")
            
            # Validação: valores presente numéricos
            if not pd.api.types.is_numeric_dtype(carteira_xlsx['valor_presente']):
                raise ValueError("Coluna 'valor_presente' deve ser numérica")
            
            return True
            
        except Exception as e:
            print(f"Erro na validação de PDD: {e}")
            return False
    
    def calculate(self, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Lógica principal de cálculo de PDD.
        
        Args:
            carteira_xlsx: DataFrame com carteira enriquecida
            
        Returns:
            Dict com resultados completos
        """
        try:
            # 1. Aplicar lógica crítica por cedente
            df_with_cedente_logic = self._apply_cedente_logic(carteira_xlsx)
            
            # 2. Calcular provisões por grupo de risco
            pdd_analysis = self._calculate_provisions_by_group(df_with_cedente_logic)
            
            # 3. Gerar análise detalhada por cedente
            cedente_analysis = self._generate_cedente_analysis(df_with_cedente_logic)
            
            # 4. Comparação metodológica
            metodologia_comparison = self._compare_methodologies(df_with_cedente_logic)
            
            # 5. Consolidar resultados
            resultado = {
                "pdd_analysis": pdd_analysis,
                "cedente_analysis": cedente_analysis,
                "comparacao_metodologica": metodologia_comparison,
                "metodologia": {
                    "calculo": "por_cedente",
                    "regra": "Provisão baseada no ativo mais atrasado de cada cedente",
                    "explicacao": "Todas as operações do cedente recebem a provisão do grupo mais alto (pior ativo)"
                },
                "compliance": {
                    "grupos_configurados": len(self._grupos_risco),
                    "grupos_com_exposicao": len([g for g in pdd_analysis["grupos"].values() if g["quantidade"] > 0]),
                    "provisao_total_percentual": pdd_analysis["totais"]["provisao_percentual"]
                }
            }
            
            return resultado
            
        except Exception as e:
            print(f"Erro no cálculo de PDD: {e}")
            raise
    
    def _apply_cedente_logic(self, carteira_xlsx: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica lógica crítica por cedente.
        
        REGRA FUNDAMENTAL: PDD é calculado por cedente, não por título individual.
        - Para cada cedente: identifica o ativo mais atrasado (maior dias_atraso)
        - Classifica esse atraso em grupo de risco
        - Aplica esse grupo de risco a TODAS as operações do mesmo cedente
        - Inclusive operações em dia recebem provisão do grupo mais alto do cedente
        
        Args:
            carteira_xlsx: DataFrame com carteira enriquecida
            
        Returns:
            DataFrame com lógica por cedente aplicada
        """
        df = carteira_xlsx.copy()
        
        # Para cada cedente, encontrar o MAIOR ATRASO (não o grupo máximo)
        cedente_max_atraso = df.groupby('nome_do_cedente')['dias_atraso'].max().reset_index()
        cedente_max_atraso.columns = ['nome_do_cedente', 'max_dias_atraso']
        
        # Classificar o maior atraso em grupo de risco
        cedente_max_atraso['grupo_pdd_cedente'] = cedente_max_atraso['max_dias_atraso'].apply(
            self._classify_risk_group_from_days
        )
        
        # Mapear de volta para o DataFrame principal
        df = df.merge(
            cedente_max_atraso[['nome_do_cedente', 'grupo_pdd_cedente', 'max_dias_atraso']], 
            on='nome_do_cedente', 
            how='left'
        )
        
        # Aplicar provisão baseada no grupo PDD do cedente
        df['provisao_pct'] = df['grupo_pdd_cedente'].map(
            {g: v['provisao_pct'] for g, v in self._grupos_risco.items()}
        )
        df['provisao_valor'] = df['valor_presente'] * df['provisao_pct']
        
        # Log para debug
        cedentes_com_provisao = df[df['provisao_valor'] > 0]['nome_do_cedente'].nunique()
        total_cedentes = df['nome_do_cedente'].nunique()
        
        print(f"✅ PDD: {cedentes_com_provisao} cedentes com provisão (de {total_cedentes} total)")
        
        return df
    
    def _classify_risk_group_from_days(self, dias_atraso: int) -> str:
        """
        Classifica grupo de risco baseado em dias de atraso.
        
        Args:
            dias_atraso: Número de dias de atraso
            
        Returns:
            Grupo de risco (AA, A, B, C, D, E, F, G, H)
        """
        for grupo, params in sorted(self._grupos_risco.items(), key=lambda x: x[1]['atraso_max_dias']):
            if dias_atraso <= params['atraso_max_dias']:
                return grupo
        return 'H'  # Grupo mais alto por default
    
    def _calculate_provisions_by_group(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula provisões por grupo de risco.
        
        Args:
            df: DataFrame com lógica por cedente aplicada
            
        Returns:
            Dict com análise por grupo
        """
        # Análise por grupo PDD (baseado no grupo aplicado por cedente)
        analise_grupos = {}
        
        for grupo in sorted(self._grupos_risco.keys()):
            # Usar grupo_pdd_cedente (não grupo_de_risco individual)
            titulos_grupo = df[df['grupo_pdd_cedente'] == grupo]
            
            if len(titulos_grupo) > 0:
                analise_grupos[grupo] = {
                    "quantidade": len(titulos_grupo),
                    "valor_total": round(float(titulos_grupo['valor_presente'].sum()), 2),
                    "provisao_pct": self._grupos_risco[grupo]['provisao_pct'] * 100,
                    "provisao_valor": round(float(titulos_grupo['provisao_valor'].sum()), 2),
                    "atraso_max_dias": self._grupos_risco[grupo]['atraso_max_dias'],
                    "cedentes_afetados": len(titulos_grupo['nome_do_cedente'].unique())
                }
            else:
                # Grupo sem títulos
                analise_grupos[grupo] = {
                    "quantidade": 0,
                    "valor_total": 0.0,
                    "provisao_pct": self._grupos_risco[grupo]['provisao_pct'] * 100,
                    "provisao_valor": 0.0,
                    "atraso_max_dias": self._grupos_risco[grupo]['atraso_max_dias'],
                    "cedentes_afetados": 0
                }
        
        # Totais consolidados
        total_carteira = df['valor_presente'].sum()
        total_provisao = df['provisao_valor'].sum()
        
        return {
            "grupos": analise_grupos,
            "totais": {
                "carteira_valor": round(float(total_carteira), 2),
                "provisao_valor": round(float(total_provisao), 2),
                "provisao_percentual": round((total_provisao / total_carteira * 100) if total_carteira > 0 else 0, 2)
            }
        }
    
    def _generate_cedente_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera análise detalhada por cedente.
        
        Mostra como a lógica PDD funciona para cada cedente:
        - Identifica título mais atrasado
        - Mostra grupo aplicado a todas as operações
        - Calcula impacto financeiro
        
        Args:
            df: DataFrame com lógica por cedente aplicada
            
        Returns:
            Dict com análise por cedente
        """
        analise_cedentes = {}
        
        for cedente in df['nome_do_cedente'].unique():
            if pd.isna(cedente) or cedente == '':
                continue
                
            titulos_cedente = df[df['nome_do_cedente'] == cedente].copy()
            
            # Identificar título mais atrasado
            idx_mais_atrasado = titulos_cedente['dias_atraso'].idxmax()
            titulo_mais_atrasado = titulos_cedente.loc[idx_mais_atrasado]
            
            # Grupo PDD aplicado
            grupo_pdd = titulos_cedente['grupo_pdd_cedente'].iloc[0]
            
            # Estatísticas do cedente
            total_valor = titulos_cedente['valor_presente'].sum()
            provisao_valor = titulos_cedente['provisao_valor'].sum()
            provisao_pct = self._grupos_risco[grupo_pdd]['provisao_pct']
            
            # Distribuição por grupo original (antes da aplicação PDD)
            distribuicao_original = titulos_cedente['grupo_de_risco'].value_counts().to_dict()
            
            analise_cedentes[cedente] = {
                "total_titulos": len(titulos_cedente),
                "valor_total": round(float(total_valor), 2),
                "grupo_pdd_aplicado": grupo_pdd,
                "provisao_pct": round(provisao_pct * 100, 2),
                "provisao_valor": round(float(provisao_valor), 2),
                "titulo_mais_atrasado": {
                    "dias_atraso": int(titulo_mais_atrasado['dias_atraso']),
                    "grupo_original": titulo_mais_atrasado['grupo_de_risco'],
                    "valor": round(float(titulo_mais_atrasado['valor_presente']), 2),
                    "data_vencimento": titulo_mais_atrasado.get('vencimento_original', 'N/A')
                },
                "distribuicao_grupos_originais": distribuicao_original
            }
        
        return {
            "total_cedentes": len(analise_cedentes),
            "cedentes": analise_cedentes
        }
    
    def _compare_methodologies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compara metodologia por cedente vs individual.
        
        Args:
            df: DataFrame com lógica por cedente aplicada
            
        Returns:
            Dict com comparação metodológica
        """
        # Cálculo individual (se fosse aplicado por título)
        df_individual = df.copy()
        df_individual['provisao_individual'] = df_individual['grupo_de_risco'].map(
            {g: v['provisao_pct'] for g, v in self._grupos_risco.items()}
        ) * df_individual['valor_presente']
        
        # Totais por metodologia
        total_provisao_cedente = df['provisao_valor'].sum()
        total_provisao_individual = df_individual['provisao_individual'].sum()
        
        # Diferença
        diferenca_valor = total_provisao_cedente - total_provisao_individual
        diferenca_percentual = (diferenca_valor / total_provisao_individual * 100) if total_provisao_individual > 0 else 0
        
        return {
            "provisao_por_cedente": round(float(total_provisao_cedente), 2),
            "provisao_individual": round(float(total_provisao_individual), 2),
            "diferenca_valor": round(float(diferenca_valor), 2),
            "diferenca_percentual": round(diferenca_percentual, 2),
            "metodologia_utilizada": "por_cedente",
            "explicacao": "Metodologia por cedente aplica provisão do pior ativo a todas as operações do cedente"
        }
    
    def _find_pdd_config(self) -> Optional[Dict[str, Any]]:
        """
        Busca configuração PDD no pool JSON.
        
        Returns:
            Configuração PDD ou None
        """
        return self.config.get('provisoes_pdd', {}).get('grupos_risco', {})
    
    def _extract_risk_groups(self) -> Dict[str, Any]:
        """
        Extrai grupos de risco da configuração.
        
        Returns:
            Dict com grupos de risco
        """
        if self._pdd_config:
            return self._pdd_config
        return {}
    
    def run_monitoring(self, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Interface principal do monitor PDD.
        
        Args:
            carteira_xlsx: DataFrame com carteira enriquecida
            
        Returns:
            Dict com resultado completo
        """
        try:
            # Validar dados
            if not self.validate_data(carteira_xlsx):
                return {
                    "sucesso": False,
                    "monitor": "pdd",
                    "erro": "Falha na validação de dados",
                    "tipo_erro": "ValidacaoError"
                }
            
            # Calcular PDD
            resultado_calculo = self.calculate(carteira_xlsx)
            
            # Construir resultado final
            resultado_final = {
                "sucesso": True,
                "monitor": "pdd",
                "pool_id": self.config.get('pool_id', 'desconhecido'),
                "data_analise": datetime.now().isoformat(),
                "dependencias": {
                    "monitor_inadimplencia": "OK - Dados enriquecidos presentes",
                    "campos_utilizados": self.get_required_columns()
                }
            }
            
            # Adicionar resultados do cálculo
            resultado_final.update(resultado_calculo)
            
            return resultado_final
            
        except Exception as e:
            return {
                "sucesso": False,
                "monitor": "pdd",
                "erro": str(e),
                "tipo_erro": type(e).__name__
            }


# Função de compatibilidade temporária (será removida quando sistema funcional for apagado)
def run_pdd_monitoring(carteira_xlsx: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interface de compatibilidade temporária.
    
    NOTA: Esta função será removida quando o sistema funcional for apagado.
    Use PDDMonitor diretamente.
    
    Args:
        carteira_xlsx: DataFrame com carteira enriquecida
        config: Configuração JSON do pool
        
    Returns:
        Dict com resultado completo
    """
    monitor = PDDMonitor(config)
    return monitor.run_monitoring(carteira_xlsx)


if __name__ == "__main__":
    print("Monitor PDD OOP carregado com sucesso")
    print("Use PDDMonitor(config).run_monitoring(carteira_xlsx) para uso direto")
    print("Ou run_pdd_monitoring(carteira_xlsx, config) para compatibilidade temporária")