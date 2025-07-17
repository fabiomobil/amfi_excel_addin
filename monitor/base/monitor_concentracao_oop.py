"""
Monitor de Concentração - Versão Orientada a Objetos
===================================================

Refatoração do monitor de concentração usando arquitetura OOP baseada em BaseMonitor.
Mantém 100% compatibilidade com a interface original run_concentration_monitoring().

Responsabilidades:
- Monitorar concentração individual por sacado/cedente
- Monitorar concentração top-N (ex: top 10 maiores)
- Análise sequencial de capacidade
- Matriz tabular de sobra de capacidade

Melhorias implementadas:
- Herança de BaseMonitor (elimina redundâncias)
- Validação centralizada
- Resultado padronizado via ResultBuilder
- Código mais limpo e reutilizável

Funcionalidades preservadas:
- Concentração individual e top-N
- Análise sequencial completa
- Matriz tabular de sobra
- Filtros de entidades ignoradas
- Todas as validações originais

Autor: AmFi Development Team
Data: 2025-07-17
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import os
import json

# Imports das classes base
try:
    from .base_monitor import BaseMonitor
    from .result_builder import ResultBuilder
    from .data_handler import DataHandler
except ImportError:
    from base_monitor import BaseMonitor
    from result_builder import ResultBuilder
    from data_handler import DataHandler


class ConcentrationType(Enum):
    """Tipos de concentração suportados pelo monitor base."""
    INDIVIDUAL = "individual"
    TOP_N = "top_n"


class ConcentrationEntity(Enum):
    """Entidades monitoradas para concentração."""
    SACADO = "sacado"
    CEDENTE = "cedente"


@dataclass
class ConcentrationLimit:
    """Estrutura para um limite de concentração."""
    tipo: ConcentrationType
    entidade: ConcentrationEntity
    limite: float
    n: Optional[int] = None  # Para top_n
    
    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.tipo == ConcentrationType.TOP_N and self.n is None:
            raise ValueError("Top-N concentration requires 'n' parameter")
        
        if self.limite < 0 or self.limite > 1:
            raise ValueError(f"Limite deve estar entre 0 e 1, recebido: {self.limite}")


class ConcentrationMonitor(BaseMonitor):
    """
    Monitor de concentração usando arquitetura orientada a objetos.
    
    Herda de BaseMonitor e implementa lógica específica de concentração:
    - Validação de dados de concentração
    - Cálculo de concentração individual e top-N
    - Análise sequencial de capacidade
    - Matriz tabular de sobra
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa monitor de concentração.
        
        Args:
            config: Configuração JSON completa do pool
        """
        super().__init__(monitor_id="concentracao", config=config)
        self._filters_config = self._load_concentration_filters()
    
    def get_required_columns(self) -> List[str]:
        """
        Retorna colunas obrigatórias para monitoramento de concentração.
        
        Obtém campos necessários da configuração JSON ou usa padrão.
        Mapeia campos da configuração para colunas reais dos dados.
        
        Returns:
            Lista de colunas obrigatórias
        """
        # Mapeamento de campos da configuração para colunas reais
        campo_mapping = {
            'sacado': 'nome_do_sacado',
            'cedente': 'nome_do_cedente',
            'valor_presente': 'valor_presente',
            'grupo_economico': 'grupo_economico'  # Opcional
        }
        
        if self.monitor_config:
            campos_config = self.monitor_config.get('campos_necessarios', ['sacado', 'cedente', 'valor_presente'])
            # Mapear campos da configuração para colunas reais
            campos_reais = []
            for campo in campos_config:
                if campo in campo_mapping:
                    campos_reais.append(campo_mapping[campo])
                else:
                    campos_reais.append(campo)
            return campos_reais
        return ['nome_do_sacado', 'nome_do_cedente', 'valor_presente']
    
    def _load_concentration_filters(self) -> Dict[str, Any]:
        """
        Carrega configuração de filtros para concentração.
        
        Returns:
            Dict com configuração de entidades ignoradas
        """
        try:
            # Caminho para configuração de filtros
            filters_path = Path(__file__).parent.parent.parent / "config" / "monitoring" / "concentration_filters.json"
            
            if filters_path.exists():
                with open(filters_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Configuração padrão se arquivo não existir
            return {
                "entidades_ignoradas": {
                    "sacado": [],
                    "cedente": []
                },
                "configuracoes_adicionais": {
                    "case_sensitive": False,
                    "normalize_names": True,
                    "partial_match": False
                }
            }
        except Exception as e:
            print(f"⚠️ Erro ao carregar filtros de concentração: {e}")
            return {
                "entidades_ignoradas": {"sacado": [], "cedente": []},
                "configuracoes_adicionais": {"case_sensitive": False, "normalize_names": True, "partial_match": False}
            }
    
    def _should_ignore_entity(self, entity_name: str, entity_type: str) -> bool:
        """
        Verifica se uma entidade deve ser ignorada na análise de concentração.
        
        Args:
            entity_name: Nome da entidade
            entity_type: Tipo da entidade ('cedente' ou 'sacado')
            
        Returns:
            True se deve ignorar, False caso contrário
        """
        try:
            entidades_ignoradas = self._filters_config.get("entidades_ignoradas", {})
            # CORREÇÃO: Original usa plural (cedentes/sacados), não singular
            lista_ignoradas = entidades_ignoradas.get(f"{entity_type}s", [])
            
            if not lista_ignoradas:
                return False
            
            # Configurações de comparação
            config_adicional = self._filters_config.get("configuracoes_adicionais", {})
            case_sensitive = config_adicional.get("case_sensitive", False)
            normalize_names = config_adicional.get("normalize_names", True)
            partial_match = config_adicional.get("partial_match", False)
            
            # Normalizar nome se configurado
            entity_check = entity_name
            if normalize_names:
                entity_check = entity_name.strip()
            
            # Verificar cada entidade na lista
            for ignored_entity in lista_ignoradas:
                ignored_check = ignored_entity
                if normalize_names:
                    ignored_check = ignored_entity.strip()
                
                # Comparação case sensitive/insensitive
                if case_sensitive:
                    if partial_match:
                        if ignored_check in entity_check:
                            return True
                    else:
                        if ignored_check == entity_check:
                            return True
                else:
                    entity_lower = entity_check.lower()
                    ignored_lower = ignored_check.lower()
                    
                    if partial_match:
                        if ignored_lower in entity_lower:
                            return True
                    else:
                        if ignored_lower == entity_lower:
                            return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar entidade ignorada: {e}")
            # Em caso de erro, não ignora para segurança
            return False
    
    def _filter_concentration_data(self, df: pd.DataFrame, entity_type: str) -> pd.DataFrame:
        """
        Filtra DataFrame removendo entidades que devem ser ignoradas.
        
        Args:
            df: DataFrame com dados de concentração
            entity_type: Tipo da entidade ('cedente' ou 'sacado')
            
        Returns:
            DataFrame filtrado
        """
        try:
            # Determinar coluna baseada no tipo de entidade
            if entity_type == "cedente":
                entity_column = "nome_do_cedente"
            elif entity_type == "sacado":
                entity_column = "nome_do_sacado"
            else:
                return df
            
            # Verificar se coluna existe
            if entity_column not in df.columns:
                return df
            
            # Filtrar dados
            mask = df[entity_column].apply(
                lambda x: not self._should_ignore_entity(str(x), entity_type)
            )
            
            filtered_df = df[mask].copy()
            
            # Log se alguma entidade foi filtrada
            original_count = len(df)
            filtered_count = len(filtered_df)
            
            if original_count != filtered_count:
                removed_count = original_count - filtered_count
                print(f"🔽 Concentração {entity_type}: {removed_count} registros filtrados (entidades ignoradas)")
            
            return filtered_df
            
        except Exception as e:
            print(f"⚠️ Erro ao filtrar dados de concentração: {e}")
            # Em caso de erro, retorna dados originais
            return df
    
    def _parse_concentration_config(self) -> List[ConcentrationLimit]:
        """
        Extrai configurações de limites de concentração do JSON.
        
        Returns:
            Lista de limites de concentração configurados
        """
        try:
            if not self.monitor_config:
                return []
            
            limites_config = self.monitor_config.get('limites', [])
            limites = []
            
            for limite_config in limites_config:
                try:
                    # Parsear tipo
                    tipo_str = limite_config.get('tipo', '').lower()
                    if tipo_str == 'individual':
                        tipo = ConcentrationType.INDIVIDUAL
                    elif tipo_str == 'top_n':
                        tipo = ConcentrationType.TOP_N
                    else:
                        print(f"⚠️ Tipo de concentração inválido: {tipo_str}")
                        continue
                    
                    # Parsear entidade
                    entidade_str = limite_config.get('entidade', '').lower()
                    if entidade_str == 'sacado':
                        entidade = ConcentrationEntity.SACADO
                    elif entidade_str == 'cedente':
                        entidade = ConcentrationEntity.CEDENTE
                    else:
                        print(f"⚠️ Entidade de concentração inválida: {entidade_str}")
                        continue
                    
                    # Parsear limite
                    limite = float(limite_config.get('limite', 0))
                    
                    # Parsear N (para top_n)
                    n = None
                    if tipo == ConcentrationType.TOP_N:
                        n = int(limite_config.get('n', 10))
                    
                    # Criar limite
                    limite_obj = ConcentrationLimit(
                        tipo=tipo,
                        entidade=entidade,
                        limite=limite,
                        n=n
                    )
                    
                    limites.append(limite_obj)
                    
                except Exception as e:
                    print(f"⚠️ Erro ao parsear limite de concentração: {e}")
                    continue
            
            return limites
            
        except Exception as e:
            print(f"⚠️ Erro ao parsear configuração de concentração: {e}")
            return []
    
    def validate_data(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> bool:
        """
        Validação específica para monitoramento de concentração.
        
        Extends BaseMonitor.validate_basic_data() com validações específicas:
        - Dados do pool válidos (PL)
        - Carteira não vazia
        - Colunas obrigatórias presentes
        - Configuração de limites válida
        
        Args:
            pool_csv: DataFrame com dados do pool (PL, etc.)
            carteira_xlsx: DataFrame com carteira detalhada
            
        Returns:
            True se dados são válidos
        """
        try:
            # 1. Validações básicas via BaseMonitor
            if not self.validate_basic_data(pool_csv, ['pl']):
                return False
            
            # 2. Validar PL do pool
            pl_pool = pool_csv['pl'].iloc[0]
            if pd.isna(pl_pool) or pl_pool <= 0:
                raise ValueError(f"PL do pool inválido: {pl_pool}")
            
            # 3. Validar carteira não vazia
            if carteira_xlsx.empty:
                raise ValueError("Carteira XLSX está vazia")
            
            # 4. Validar colunas obrigatórias na carteira
            required_columns = self.get_required_columns()
            # Filtrar apenas colunas realmente obrigatórias (excluir opcionais)
            essential_columns = ['nome_do_sacado', 'nome_do_cedente', 'valor_presente']
            missing_columns = [col for col in essential_columns if col not in carteira_xlsx.columns]
            if missing_columns:
                raise ValueError(f"Colunas obrigatórias ausentes na carteira: {missing_columns}")
            
            # Verificar se campos opcionais existem
            optional_columns = [col for col in required_columns if col not in essential_columns]
            for col in optional_columns:
                if col not in carteira_xlsx.columns:
                    print(f"⚠️  Coluna opcional '{col}' não encontrada - usando funcionalidade básica")
            
            # 5. Validar configuração de limites
            limites = self._parse_concentration_config()
            if not limites:
                # Sem limites configurados é válido (retorna "sem_limites")
                return True
            
            # 6. Validar valores numéricos na carteira
            if not pd.api.types.is_numeric_dtype(carteira_xlsx['valor_presente']):
                raise ValueError("Coluna 'valor_presente' não é numérica")
            
            # Verificar se valores são positivos
            valores_negativos = carteira_xlsx['valor_presente'] < 0
            if valores_negativos.any():
                raise ValueError("Coluna 'valor_presente' contém valores negativos")
            
            return True
            
        except Exception as e:
            print(f"Erro na validação de concentração: {e}")
            return False
    
    def _calculate_individual_concentration(self, carteira_df: pd.DataFrame, 
                                            limite: ConcentrationLimit, 
                                            pl_pool: float) -> Dict[str, Any]:
        """
        Calcula concentração individual para uma entidade específica.
        
        Args:
            carteira_df: DataFrame com carteira do pool
            limite: Configuração do limite
            pl_pool: Patrimônio líquido do pool
            
        Returns:
            Dict com resultados da concentração individual
        """
        try:
            # Determinar coluna da entidade
            entity_column = "nome_do_sacado" if limite.entidade == ConcentrationEntity.SACADO else "nome_do_cedente"
            
            # Filtrar dados (remover entidades ignoradas)
            filtered_df = self._filter_concentration_data(carteira_df, limite.entidade.value)
            
            # Agrupar por entidade e somar valores
            concentracao_por_entidade = filtered_df.groupby(entity_column)['valor_presente'].agg(['sum', 'count']).reset_index()
            concentracao_por_entidade.columns = [entity_column, 'valor_absoluto', 'quantidade_titulos']
            
            # Calcular percentual em relação ao PL
            concentracao_por_entidade['percentual_pl'] = (concentracao_por_entidade['valor_absoluto'] / pl_pool) * 100
            
            # Encontrar maior concentração
            if concentracao_por_entidade.empty:
                return {
                    "limite_id": f"individual_{limite.entidade.value}",
                    "tipo": limite.tipo.value,
                    "entidade": limite.entidade.value,
                    "limite_configurado": limite.limite * 100,
                    "status": "sem_dados",
                    "maior_concentracao": None,
                    "margem_limite": 0,
                    "total_entidades": 0
                }
            
            maior_concentracao = concentracao_por_entidade.loc[concentracao_por_entidade['percentual_pl'].idxmax()]
            
            # Determinar status
            percentual_maior = maior_concentracao['percentual_pl']
            limite_pct = limite.limite * 100
            status = "enquadrado" if percentual_maior <= limite_pct else "violado"
            
            # Calcular margem
            margem = limite_pct - percentual_maior
            
            return {
                "limite_id": f"individual_{limite.entidade.value}",
                "tipo": limite.tipo.value,
                "entidade": limite.entidade.value,
                "limite_configurado": limite_pct,
                "status": status,
                "maior_concentracao": {
                    "entidade": maior_concentracao[entity_column],
                    "valor_absoluto": float(maior_concentracao['valor_absoluto']),
                    "percentual_pl": percentual_maior,  # Manter sem arredondamento
                    "quantidade_titulos": int(maior_concentracao['quantidade_titulos'])
                },
                "margem_limite": margem,  # Não arredondar aqui para manter compatibilidade
                "total_entidades": len(concentracao_por_entidade)
            }
            
        except Exception as e:
            return {
                "limite_id": f"individual_{limite.entidade.value}",
                "tipo": limite.tipo.value,
                "entidade": limite.entidade.value,
                "status": "erro",
                "erro": str(e)
            }
    
    def _calculate_top_n_concentration(self, carteira_df: pd.DataFrame,
                                       limite: ConcentrationLimit,
                                       pl_pool: float) -> Dict[str, Any]:
        """
        Calcula concentração top-N para maiores entidades.
        
        Args:
            carteira_df: DataFrame com carteira do pool
            limite: Configuração do limite
            pl_pool: Patrimônio líquido do pool
            
        Returns:
            Dict com resultados da concentração top-N
        """
        try:
            # Determinar coluna da entidade
            entity_column = "nome_do_sacado" if limite.entidade == ConcentrationEntity.SACADO else "nome_do_cedente"
            
            # Filtrar dados (remover entidades ignoradas)
            filtered_df = self._filter_concentration_data(carteira_df, limite.entidade.value)
            
            # Agrupar por entidade e somar valores
            concentracao_por_entidade = filtered_df.groupby(entity_column)['valor_presente'].agg(['sum', 'count']).reset_index()
            concentracao_por_entidade.columns = [entity_column, 'valor_absoluto', 'quantidade_titulos']
            
            # Calcular percentual em relação ao PL
            concentracao_por_entidade['percentual_pl'] = (concentracao_por_entidade['valor_absoluto'] / pl_pool) * 100
            
            # Ordenar por valor decrescente e pegar top N
            concentracao_ordenada = concentracao_por_entidade.sort_values('valor_absoluto', ascending=False)
            top_n = concentracao_ordenada.head(limite.n)
            
            if top_n.empty:
                return {
                    "limite_id": f"top_{limite.n}_{limite.entidade.value}",
                    "tipo": limite.tipo.value,
                    "entidade": limite.entidade.value,
                    "n": limite.n,
                    "limite_configurado": limite.limite * 100,
                    "status": "sem_dados",
                    "concentracao_agregada": None,
                    "margem_limite": 0,
                    "total_entidades": 0
                    # REMOVED: "detalhes_top_n": [] - não existe na versão original
                }
            
            # Calcular agregação
            valor_total_top_n = top_n['valor_absoluto'].sum()
            percentual_agregado = (valor_total_top_n / pl_pool) * 100
            
            # Determinar status
            limite_pct = limite.limite * 100
            status = "enquadrado" if percentual_agregado <= limite_pct else "violado"
            
            # Calcular margem
            margem = limite_pct - percentual_agregado
            
            # Detalhes do top N removidos para manter compatibilidade com versão original
            # detalhes_top_n = []
            # for _, row in top_n.iterrows():
            #     detalhes_top_n.append({
            #         "entidade": row[entity_column],
            #         "valor_absoluto": float(row['valor_absoluto']),
            #         "percentual_pl": float(row['percentual_pl']),  # Manter sem arredondamento
            #         "quantidade_titulos": int(row['quantidade_titulos'])
            #     })
            
            return {
                "limite_id": f"top_{limite.n}_{limite.entidade.value}",
                "tipo": limite.tipo.value,
                "entidade": limite.entidade.value,
                "n": limite.n,
                "limite_configurado": limite_pct,
                "status": status,
                "concentracao_top_n": {
                    "valor_absoluto": float(valor_total_top_n),
                    "percentual_pl": percentual_agregado,  # Manter sem arredondamento
                    "quantidade_entidades": len(top_n)
                },
                "margem_limite": margem,  # Não arredondar aqui para manter compatibilidade
                "total_entidades": len(concentracao_por_entidade)
                # REMOVED: "detalhes_top_n": detalhes_top_n - não existe na versão original
            }
            
        except Exception as e:
            return {
                "limite_id": f"top_{limite.n}_{limite.entidade.value}",
                "tipo": limite.tipo.value,
                "entidade": limite.entidade.value,
                "n": limite.n,
                "status": "erro",
                "erro": str(e)
            }
    
    def _gerar_explicacao_sequencial(self, capacidade_efetiva: float, limitada_por: str, 
                                      capacidade_individual: float, saldo_disponivel: float) -> str:
        """Gera explicação clara da limitação sequencial."""
        
        if limitada_por == "esgotado":
            return "Espaço Top-N já esgotado por posições anteriores"
        elif limitada_por == "individual":
            return f"Limitado por teto individual. Restaria {saldo_disponivel - capacidade_efetiva:.1f} no Top-N"
        elif limitada_por == "top_n":
            return f"Usa todo saldo Top-N restante. Individual permitiria {capacidade_individual:.1f}"
        else:
            return "Análise não disponível"
    
    def _formatar_tabela_ascii(self, linhas: List[Dict], cabecalho: Dict) -> str:
        """
        Formata matriz de sobra em tabela ASCII legível.
        
        Args:
            linhas: Lista com dados das linhas
            cabecalho: Dict com informações do cabeçalho
            
        Returns:
            String com tabela ASCII formatada
        """
        
        # Cabeçalho informativo
        header_info = f"""
MATRIZ DE SOBRA - ANÁLISE SEQUENCIAL
PL: {cabecalho['pl_pool']:,.0f} | Individual: {cabecalho.get('limite_individual', 'N/A')}% | Top-{cabecalho['top_n_size']}: {cabecalho['limite_top_n']}%
Espaço disponível: {cabecalho['espaco_disponivel']:,.0f}
"""
        
        # Larguras das colunas
        col_entidade = max(len(linha["entidade"]) for linha in linhas) + 2
        col_entidade = max(col_entidade, 12)  # Mínimo 12 chars
        
        # Cabeçalho da tabela
        separador = "┌" + "─" * col_entidade + "┬" + "─" * 8 + "┬" + "─" * 10 + "┬" + "─" * 13 + "┬" + "─" * 13 + "┬" + "─" * 15 + "┐"
        cabecalho_tabela = f"│{'Entidade':<{col_entidade}}│{'Atual':<8}│{'Cap.Indiv':<10}│{'Cap.Efetiva':<13}│{'Saldo Antes':<13}│{'Limitado Por':<15}│"
        separador_meio = "├" + "─" * col_entidade + "┼" + "─" * 8 + "┼" + "─" * 10 + "┼" + "─" * 13 + "┼" + "─" * 13 + "┼" + "─" * 15 + "┤"
        
        # Linhas de dados
        linhas_dados = []
        for linha in linhas:
            entidade = linha["entidade"][:col_entidade-2]  # Truncar se muito longo
            atual = f"{linha['exposicao_atual']:.0f}"
            cap_indiv = f"+{linha['capacidade_individual']:.0f}" if linha['capacidade_individual'] and linha['capacidade_individual'] > 0 else "0"
            cap_efetiva = f"+{linha['capacidade_efetiva']:.0f}"
            saldo_antes = f"{linha['saldo_antes']:.0f}"
            limitada_por = linha["limitada_por"][:13]  # Truncar se muito longo
            
            linha_formatada = f"│{entidade:<{col_entidade}}│{atual:<8}│{cap_indiv:<10}│{cap_efetiva:<13}│{saldo_antes:<13}│{limitada_por:<15}│"
            linhas_dados.append(linha_formatada)
        
        # Rodapé da tabela
        separador_fim = "└" + "─" * col_entidade + "┴" + "─" * 8 + "┴" + "─" * 10 + "┴" + "─" * 13 + "┴" + "─" * 13 + "┴" + "─" * 15 + "┘"
        
        # Montar tabela completa
        tabela_completa = "\n".join([
            header_info,
            separador,
            cabecalho_tabela,
            separador_meio,
            *linhas_dados,
            separador_fim
        ])
        
        return tabela_completa
    
    def _gerar_matriz_sobra_tabular(self, analise_sequencial: List[Dict], resumo_analise: Dict) -> Dict[str, Any]:
        """
        Gera matriz de sobra tabular para visualização clara da capacidade incremental.
        
        Args:
            analise_sequencial: Lista com análise sequencial por posição
            resumo_analise: Dict com resumo da análise (PL, limites, etc.)
            
        Returns:
            Dict com matriz tabular formatada e dados estruturados
        """
        
        # Cabeçalho da matriz
        cabecalho_info = {
            "pl_pool": resumo_analise["pl_pool"],
            "limite_individual": resumo_analise.get("limite_individual_pct"),
            "limite_top_n": resumo_analise["limite_top_n_pct"],
            "top_n_size": resumo_analise["top_n_size"],
            "espaco_disponivel": resumo_analise["espaco_total_disponivel"]
        }
        
        # Gerar linhas da tabela
        linhas_tabela = []
        for item in analise_sequencial:
            linha = {
                "posicao": item["posicao"],
                "entidade": item["entidade"],
                "exposicao_atual": item["exposicao_atual"],
                "percentual_atual": item["percentual_atual"],
                "capacidade_individual": item.get("capacidade_individual", 0) or 0,
                "capacidade_efetiva": item["capacidade_efetiva"],
                "saldo_antes": item["saldo_antes"],
                "saldo_apos": item["saldo_apos"],
                "limitada_por": item["limitada_por"],
                "pode_crescer": f"+{item['capacidade_efetiva']:.0f}",
                "sobra_proximo": f"{item['saldo_apos']:.0f}"
            }
            linhas_tabela.append(linha)
        
        # Gerar tabela ASCII formatada
        tabela_ascii = self._formatar_tabela_ascii(linhas_tabela, cabecalho_info)
        
        # Gerar resumo da matriz
        total_crescimento_possivel = sum(item["capacidade_efetiva"] for item in analise_sequencial)
        entidades_com_capacidade = len([item for item in analise_sequencial if item["capacidade_efetiva"] > 0])
        
        resumo_matriz = {
            "total_crescimento_possivel": total_crescimento_possivel,
            "entidades_com_capacidade": entidades_com_capacidade,
            "total_entidades_analisadas": len(analise_sequencial),
            "utilizacao_espaco_disponivel": (total_crescimento_possivel / resumo_analise["espaco_total_disponivel"]) * 100 if resumo_analise["espaco_total_disponivel"] > 0 else 0
        }
        
        return {
            "cabecalho": cabecalho_info,
            "linhas": linhas_tabela,
            "tabela_ascii": tabela_ascii,
            "resumo": resumo_matriz
        }
    
    def _calculate_sequential_capacity(self, concentracao_df: pd.DataFrame,
                                       limites: List[ConcentrationLimit], 
                                       pl_pool: float,
                                       entidade_tipo: str = "sacado") -> Dict[str, Any]:
        """
        Calcula capacidade sequencial/cascata considerando ordem de prioridade.
        
        Simula como o espaço disponível vai sendo consumido sequencialmente,
        mostrando saldo restante após cada alocação.
        
        Args:
            concentracao_df: DataFrame com concentração por entidade (já ordenado)
            limites: Lista de limites de concentração
            pl_pool: Patrimônio líquido do pool
            entidade_tipo: "sacado" ou "cedente"
            
        Returns:
            Dict com análise sequencial de capacidade
        """
        
        # Identificar limites relevantes para esta entidade
        limite_individual = None
        limite_top_n = None
        
        for limite in limites:
            if limite.entidade.value == entidade_tipo:
                if limite.tipo == ConcentrationType.INDIVIDUAL:
                    limite_individual = limite
                elif limite.tipo == ConcentrationType.TOP_N:
                    limite_top_n = limite
        
        if not limite_top_n:
            # Se não tem top-N, não faz sentido análise sequencial
            return {
                "tipo_analise": "sem_top_n",
                "mensagem": f"Análise sequencial não aplicável - sem limite Top-N para {entidade_tipo}"
            }
        
        # Calcular espaço disponível no top-N
        top_n_df = concentracao_df.head(limite_top_n.n)
        top_n_atual = top_n_df['valor_total'].sum()
        limite_top_n_valor = limite_top_n.limite * pl_pool
        espaco_total_disponivel = limite_top_n_valor - top_n_atual
        
        # Debug para identificar problemas
        print(f"🔍 DEBUG {entidade_tipo}: DataFrame total={len(concentracao_df)}, top_n={limite_top_n.n}")
        print(f"   top_n_atual={top_n_atual:,.2f}, limite_valor={limite_top_n_valor:,.2f}, espaço={espaco_total_disponivel:,.2f}")
        
        # Verificação de segurança - problema identificado!
        if espaco_total_disponivel < 0:
            print(f"⚠️ Espaço negativo detectado para {entidade_tipo}: {espaco_total_disponivel:,.2f}")
            print(f"   Limite: {limite_top_n.limite} * {pl_pool:,.2f} = {limite_top_n_valor:,.2f}")
            print(f"   Top-N atual: {top_n_atual:,.2f}")
            print(f"   DataFrame shape: {top_n_df.shape}")
            print(f"   Valores top-N:\n{top_n_df[['entidade', 'valor_total']]}")
            
            # CORREÇÃO: Se espaço é negativo, significa que já ultrapassou o limite
            # Neste caso, o espaço disponível deve ser 0
            espaco_total_disponivel = 0.0
            print(f"   🔧 CORREÇÃO: Espaço ajustado para 0.0")
        
        # Análise sequencial
        analise_sequencial = []
        saldo_restante = espaco_total_disponivel
        
        for i, (_, row) in enumerate(top_n_df.iterrows()):
            entidade = row['entidade']
            exposicao_atual = row['valor_total']
            percentual_atual = (exposicao_atual / pl_pool) * 100
            
            # Capacidade individual disponível
            if limite_individual:
                limite_individual_valor = limite_individual.limite * pl_pool
                capacidade_individual = limite_individual_valor - exposicao_atual
            else:
                capacidade_individual = float('inf')
            
            # Capacidade efetiva = min(individual, saldo_restante)
            capacidade_efetiva = min(
                max(0, capacidade_individual) if capacidade_individual != float('inf') else saldo_restante,
                max(0, saldo_restante)
            )
            
            # Determinar limitação
            if saldo_restante <= 0:
                limitada_por = "esgotado"
            elif capacidade_individual != float('inf') and capacidade_individual <= saldo_restante:
                limitada_por = "individual"
            else:
                limitada_por = "top_n"
            
            # Atualizar saldo restante
            saldo_apos_uso = saldo_restante - capacidade_efetiva
            
            analise_sequencial.append({
                "posicao": i + 1,
                "entidade": entidade,
                "exposicao_atual": float(exposicao_atual),
                "percentual_atual": float(percentual_atual),
                "capacidade_individual": float(max(0, capacidade_individual)) if capacidade_individual != float('inf') else None,
                "capacidade_efetiva": float(capacidade_efetiva),
                "saldo_antes": float(saldo_restante),
                "saldo_apos": float(max(0, saldo_apos_uso)),
                "limitada_por": limitada_por,
                "explicacao": self._gerar_explicacao_sequencial(
                    capacidade_efetiva, 
                    limitada_por, 
                    capacidade_individual if capacidade_individual != float('inf') else 0, 
                    saldo_restante
                )
            })
            
            # Atualizar saldo para próxima iteração
            saldo_restante = max(0, saldo_apos_uso)
        
        # Gerar matriz de sobra tabular
        resumo_analise = {
            "pl_pool": float(pl_pool),
            "limite_individual_pct": limite_individual.limite * 100 if limite_individual else None,
            "limite_top_n_pct": limite_top_n.limite * 100,
            "top_n_size": limite_top_n.n,
            "espaco_total_disponivel": float(espaco_total_disponivel),
            "espaco_utilizado_na_analise": float(espaco_total_disponivel - saldo_restante)
        }
        
        matriz_sobra = self._gerar_matriz_sobra_tabular(analise_sequencial, resumo_analise)
        
        return {
            "tipo_analise": "sequencial",
            "entidade_tipo": entidade_tipo,
            "resumo": resumo_analise,
            "analise_sequencial": analise_sequencial,
            "matriz_sobra_tabular": matriz_sobra
        }
    
    def calculate(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula concentração completa para todos os limites configurados.
        
        Args:
            pool_csv: DataFrame com dados do pool (PL, etc.)
            carteira_xlsx: DataFrame com carteira detalhada
            
        Returns:
            Dict com resultados de concentração
        """
        try:
            # Obter informações básicas
            pool_id = self.config.get('pool_id', 'desconhecido')
            pl_pool = pool_csv['pl'].iloc[0]
            
            # Filtrar carteira para o pool
            nome_pool = pool_csv['pool'].iloc[0] if 'pool' in pool_csv.columns else pool_id
            carteira_pool = carteira_xlsx[carteira_xlsx['pool'] == nome_pool]
            
            if carteira_pool.empty:
                raise ValueError(f"Carteira do pool '{nome_pool}' não encontrada")
            
            # Parsear configuração
            limites = self._parse_concentration_config()
            
            if not limites:
                return {
                    "pool_id": pool_id,
                    "pl_pool": pl_pool,
                    "status_geral": "sem_limites",
                    "configuracao": {
                        "ativo": True,
                        "numero_limites": 0,
                        "complexidade": "sem_limites"
                    },
                    "resumo": {
                        "total_limites_analisados": 0,
                        "limites_enquadrados": 0,
                        "limites_violados": 0
                    },
                    "resultados_por_limite": [],
                    "analises_capacidade": {}
                }
            
            # Calcular concentração para cada limite
            resultados_limites = []
            limites_enquadrados = 0
            limites_violados = 0
            
            for i, limite in enumerate(limites):
                try:
                    if limite.tipo == ConcentrationType.INDIVIDUAL:
                        resultado = self._calculate_individual_concentration(carteira_pool, limite, pl_pool)
                    elif limite.tipo == ConcentrationType.TOP_N:
                        resultado = self._calculate_top_n_concentration(carteira_pool, limite, pl_pool)
                    else:
                        resultado = {
                            "tipo": limite.tipo.value,
                            "entidade": limite.entidade.value,
                            "status": "erro",
                            "erro": f"Tipo de limite não suportado: {limite.tipo}"
                        }
                    
                    resultados_limites.append(resultado)
                    
                    # Contar status
                    if resultado.get("status") == "enquadrado":
                        limites_enquadrados += 1
                    elif resultado.get("status") == "violado":
                        limites_violados += 1
                    
                except Exception as e:
                    print(f"⚠️ Erro ao calcular limite {i+1}: {e}")
                    resultados_limites.append({
                        "limite_id": f"limite_{i+1}",
                        "status": "erro",
                        "erro": str(e)
                    })
            
            # Calcular análises de capacidade para sacado e cedente
            analises_capacidade = {}
            
            for entidade_tipo in ["sacado", "cedente"]:
                try:
                    # Determinar coluna da entidade
                    entity_column = "nome_do_sacado" if entidade_tipo == "sacado" else "nome_do_cedente"
                    
                    # Verificar se há dados para esta entidade
                    if entity_column not in carteira_pool.columns:
                        continue
                    
                    # CORREÇÃO: Filtrar dados igual ao monitor original
                    filtered_df = self._filter_concentration_data(carteira_pool, entidade_tipo)
                    
                    # Debug para verificar filtro
                    print(f"🔍 FILTRO {entidade_tipo}: {len(carteira_pool)} → {len(filtered_df)} registros")
                    
                    # Agrupar por entidade e somar valores
                    concentracao_por_entidade = filtered_df.groupby(entity_column)['valor_presente'].agg(['sum', 'count']).reset_index()
                    concentracao_por_entidade.columns = ['entidade', 'valor_total', 'quantidade_titulos']
                    
                    # Ordenar por valor decrescente
                    concentracao_por_entidade = concentracao_por_entidade.sort_values('valor_total', ascending=False)
                    
                    # Debug para verificar concentração
                    print(f"🔍 CONCENTRAÇÃO {entidade_tipo}: {len(concentracao_por_entidade)} entidades")
                    print(f"   Total valor: {concentracao_por_entidade['valor_total'].sum():,.2f}")
                    
                    # Calcular análise sequencial
                    analise_capacidade = self._calculate_sequential_capacity(
                        concentracao_por_entidade, limites, pl_pool, entidade_tipo
                    )
                    
                    if analise_capacidade.get("tipo_analise") == "sequencial":
                        analises_capacidade[entidade_tipo] = analise_capacidade
                    
                except Exception as e:
                    print(f"⚠️ Erro ao calcular análise de capacidade para {entidade_tipo}: {e}")
                    continue
            
            # Determinar status geral
            if limites_violados > 0:
                status_geral = "violado"
            elif limites_enquadrados > 0:
                status_geral = "enquadrado"
            else:
                status_geral = "sem_dados"
            
            # Determinar complexidade
            if len(limites) >= 4:
                complexidade = "alta"
            elif len(limites) >= 2:
                complexidade = "media"
            else:
                complexidade = "baixa"
            
            return {
                "pool_id": pool_id,
                "pl_pool": pl_pool,
                "status_geral": status_geral,
                "configuracao": {
                    "ativo": True,
                    "numero_limites": len(limites),
                    "complexidade": complexidade
                },
                "resumo": {
                    "total_limites_analisados": len(limites),
                    "limites_enquadrados": limites_enquadrados,
                    "limites_violados": limites_violados
                },
                "resultados_por_limite": resultados_limites,
                "analises_capacidade": analises_capacidade
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao calcular concentração: {str(e)}")
    
    def run_monitoring(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Executa monitoramento completo de concentração.
        
        Interface principal compatível com orquestrador.
        Usa ResultBuilder para padronizar resultado.
        
        Args:
            pool_csv: DataFrame com dados do pool (PL, etc.)
            carteira_xlsx: DataFrame com carteira detalhada
            
        Returns:
            Dict com resultado completo padronizado
        """
        try:
            # Verificar se monitoramento está ativo
            if not self.is_active():
                return {
                    "sucesso": True,
                    "pool_id": self.config.get('pool_id', 'desconhecido'),
                    "status_geral": "sem_limites",
                    "configuracao": {
                        "ativo": False,
                        "numero_limites": 0,
                        "complexidade": "sem_limites"
                    },
                    "resumo": {
                        "total_limites_analisados": 0,
                        "limites_enquadrados": 0,
                        "limites_violados": 0
                    },
                    "resultados_por_limite": [],
                    "timestamp": datetime.now().isoformat()
                }
            
            # 1. Validar dados de entrada
            if not self.validate_data(pool_csv, carteira_xlsx):
                return ResultBuilder.build_error_result(
                    monitor_name="concentracao",
                    error_message="Falha na validação de dados"
                )
            
            # 2. Calcular concentração
            resultado = self.calculate(pool_csv, carteira_xlsx)
            
            # 3. Construir resultado de sucesso
            resultado_final = ResultBuilder.build_success_result(
                monitor_name="concentracao",
                data=resultado
            )
            
            # Adicionar timestamp
            resultado_final["timestamp"] = datetime.now().isoformat()
            
            return resultado_final
            
        except Exception as e:
            return ResultBuilder.build_error_result(
                monitor_name="concentracao",
                error_message=f"Erro inesperado no monitoramento: {str(e)}"
            )


# Função de compatibilidade com interface original
def run_concentration_monitoring(pool_data_csv: pd.DataFrame,
                                 carteira_xlsx: pd.DataFrame,
                                 config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função de compatibilidade com interface original.
    
    Mantém 100% compatibilidade com código existente.
    Internamente usa ConcentrationMonitor.
    
    Args:
        pool_data_csv: DataFrame com dados do pool (PL, etc.)
        carteira_xlsx: DataFrame com carteira detalhada
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com resultado completo (formato original)
    """
    monitor = ConcentrationMonitor(config)
    return monitor.run_monitoring(pool_data_csv, carteira_xlsx)


# Função auxiliar para uso direto da classe
def create_concentration_monitor(config: Dict[str, Any]) -> ConcentrationMonitor:
    """
    Factory function para criar monitor de concentração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Instância de ConcentrationMonitor
    """
    return ConcentrationMonitor(config)