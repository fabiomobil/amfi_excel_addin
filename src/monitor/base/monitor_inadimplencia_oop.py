"""
Monitor de Inadimplência - Versão Orientada a Objetos
====================================================

Refatoração do monitor de inadimplência usando arquitetura OOP baseada em BaseMonitor.
Mantém 100% compatibilidade com a interface original run_delinquency_monitoring().

Responsabilidades:
- Monitorar inadimplência por múltiplas janelas configuráveis
- ENRIQUECIMENTO PROGRESSIVO: Adicionar campos ao DataFrame global
- Gerar matriz detalhada de atrasos
- Análise de aging configurável com drill-down

Funcionalidade CRÍTICA - Enriquecimento Progressivo:
- Adiciona 'dias_atraso' e 'grupo_de_risco' ao DataFrame carteira_xlsx
- Permite reutilização por outros monitores (PDD, Concentração)
- Modifica DataFrame IN-PLACE para performance

Melhorias implementadas:
- Herança de BaseMonitor (elimina redundâncias)
- Validação centralizada
- Resultado padronizado via ResultBuilder
- Código mais limpo e reutilizável

Funcionalidades preservadas:
- Múltiplas janelas de inadimplência
- Enriquecimento progressivo completo
- Matriz detalhada de atrasos
- Aging analysis configurável
- Todas as validações originais

Autor: AmFi Development Team
Data: 2025-07-17
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Adicionar path para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

try:
    from .base_monitor import BaseMonitor
except ImportError:
    # Fallback para execução direta
    from base_monitor import BaseMonitor


class DelinquencyMonitor(BaseMonitor):
    """
    Monitor de inadimplência usando arquitetura orientada a objetos.
    
    Herda de BaseMonitor e implementa lógica específica de inadimplência:
    - Enriquecimento progressivo de dados
    - Múltiplas janelas configuráveis
    - Matriz detalhada de atrasos
    - Análise de aging configurável
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa monitor de inadimplência.
        
        Args:
            config: Configuração JSON completa do pool
        """
        super().__init__(monitor_id="inadimplencia", config=config)
        self._delinquency_monitors = self._find_delinquency_monitors()
        self._pdd_config = self._find_pdd_config()
        
        # Debug removido - versão final
    
    def is_active(self) -> bool:
        """
        Verifica se o monitor está ativo.
        
        Para inadimplência, considera ativo se houver pelo menos um monitor ativo.
        
        Returns:
            True se monitor está ativo
        """
        return len(self._delinquency_monitors) > 0
    
    def get_required_columns(self) -> List[str]:
        """
        Retorna colunas obrigatórias para inadimplência.
        
        Returns:
            Lista de colunas obrigatórias
        """
        return [
            'vencimento_original',
            'valor_presente', 
            'pool',
            'status'
        ]
    
    def validate_data(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> bool:
        """
        Validação específica para inadimplência.
        
        Args:
            pool_csv: DataFrame com dados do pool
            carteira_xlsx: DataFrame com carteira detalhada
            
        Returns:
            True se validação passou
        """
        try:
            # Validações básicas da classe base
            required_columns = self.get_required_columns()
            if not self.validate_basic_data(carteira_xlsx, required_columns):
                return False
            
            # Validação específica: pelo menos um monitor de inadimplência ativo
            if not self._delinquency_monitors:
                raise ValueError("Nenhum monitor de inadimplência ativo encontrado")
            
            # Validação: pool_csv deve ter PL
            if 'pl' not in pool_csv.columns:
                raise ValueError("Coluna 'pl' não encontrada no CSV do pool")
            
            # Validação: vencimento_original deve ser datetime
            if not pd.api.types.is_datetime64_any_dtype(carteira_xlsx['vencimento_original']):
                raise ValueError("Coluna 'vencimento_original' deve ser datetime")
            
            return True
            
        except Exception as e:
            print(f"Erro na validação de inadimplência: {e}")
            return False
    
    def calculate(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Lógica principal de cálculo de inadimplência.
        
        Args:
            pool_csv: DataFrame com dados do pool
            carteira_xlsx: DataFrame com carteira detalhada
            
        Returns:
            Dict com resultados completos
        """
        try:
            # 1. ENRIQUECIMENTO PROGRESSIVO (CRÍTICO)
            self._enrich_dataframe_progressively(carteira_xlsx)
            
            # 2. Filtrar dados do pool
            pool_id = self.config.get('pool_id', '')
            pool_xlsx = carteira_xlsx[carteira_xlsx['pool'] == pool_id].copy()
            
            if pool_xlsx.empty:
                raise ValueError(f"Nenhum dado encontrado para pool '{pool_id}'")
            
            # 3. Obter PL do pool
            pl_pool = float(pool_csv['pl'].iloc[0])
            
            # 4. Calcular inadimplência por janela
            resultados_janelas = self._calculate_delinquency_windows(pool_xlsx, pl_pool)
            
            # 5. Gerar matriz detalhada de atrasos
            matriz_atrasos = self._generate_detailed_matrix(pool_xlsx)
            
            # 6. Gerar análise de aging
            aging_analysis = self._generate_aging_analysis(pool_xlsx)
            
            # 7. Consolidar resultados
            resultado = {
                "pool_id": pool_id,
                "pl_pool": pl_pool,
                "resultados": resultados_janelas,
                "matriz_atrasos": matriz_atrasos,
                "aging_analysis": aging_analysis,
                "metadata": {
                    "dias_atraso_adicionado": 'dias_atraso' in carteira_xlsx.columns,
                    "grupo_de_risco_adicionado": 'grupo_de_risco' in carteira_xlsx.columns,
                    "registros_pool": len(pool_xlsx),
                    "registros_total_xlsx": len(carteira_xlsx)
                }
            }
            
            return resultado
            
        except Exception as e:
            print(f"Erro no cálculo de inadimplência: {e}")
            raise
    
    def _enrich_dataframe_progressively(self, carteira_xlsx: pd.DataFrame) -> None:
        """
        FUNCIONALIDADE CRÍTICA: Enriquecimento progressivo do DataFrame.
        
        Adiciona campos calculados ao DataFrame global para reutilização
        por outros monitores (PDD, Concentração).
        
        Args:
            carteira_xlsx: DataFrame global a ser enriquecido IN-PLACE
        """
        print(f"🔄 ENRIQUECIMENTO PROGRESSIVO: Iniciando...")
        
        # 1. Adicionar dias_atraso
        if 'dias_atraso' not in carteira_xlsx.columns:
            carteira_xlsx['dias_atraso'] = self._calculate_days_overdue(carteira_xlsx)
            print(f"✅ ENRIQUECIMENTO: Campo 'dias_atraso' adicionado ao XLSX global")
        else:
            print(f"ℹ️  Campo 'dias_atraso' já existe - reutilizando")
        
        # 2. Adicionar grupo_de_risco
        if 'grupo_de_risco' not in carteira_xlsx.columns:
            if self._pdd_config:
                carteira_xlsx['grupo_de_risco'] = self._classify_risk_groups(
                    carteira_xlsx['dias_atraso'], 
                    self._pdd_config
                )
                print(f"✅ ENRIQUECIMENTO: Campo 'grupo_de_risco' adicionado ao XLSX global")
            else:
                print(f"⚠️ Configuração PDD não encontrada - grupo_de_risco não adicionado")
        else:
            print(f"ℹ️  Campo 'grupo_de_risco' já existe - reutilizando")
        
        print(f"🎯 ENRIQUECIMENTO PROGRESSIVO: Concluído com sucesso")
    
    def _calculate_days_overdue(self, xlsx_df: pd.DataFrame, reference_date: Optional[datetime] = None) -> pd.Series:
        """
        Calcula dias de atraso para cada título.
        
        Args:
            xlsx_df: DataFrame com carteira
            reference_date: Data de referência (default: hoje)
            
        Returns:
            Series com dias de atraso
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        # Calcular dias de atraso
        dias_atraso = (reference_date - xlsx_df['vencimento_original']).dt.days
        
        # Títulos não vencidos têm 0 dias de atraso
        dias_atraso = dias_atraso.clip(lower=0)
        
        return dias_atraso
    
    def _classify_risk_groups(self, dias_atraso: pd.Series, pdd_config: Dict[str, Any]) -> pd.Series:
        """
        Classifica grupos de risco baseado em dias de atraso.
        
        Args:
            dias_atraso: Series com dias de atraso
            pdd_config: Configuração PDD (monitor completo)
            
        Returns:
            Series com grupos de risco (AA, A, B, C, D, E, F, G, H)
        """
        # Obter configuração PDD diretamente da configuração do pool
        grupos_risco = self.config.get('provisoes_pdd', {}).get('grupos_risco', {})
        
        def classificar_grupo(dias):
            for grupo, config_grupo in sorted(grupos_risco.items()):
                if dias <= config_grupo['atraso_max_dias']:
                    return grupo
            return 'H'  # Fallback para pior grupo
        
        return dias_atraso.apply(classificar_grupo)
    
    def _calculate_delinquency_windows(self, pool_xlsx: pd.DataFrame, pl_pool: float) -> Dict[str, Any]:
        """
        Calcula inadimplência para múltiplas janelas usando estrutura original.
        
        Args:
            pool_xlsx: DataFrame filtrado do pool
            pl_pool: Patrimônio líquido do pool
            
        Returns:
            Dict com resultados por janela (formato original)
        """
        resultados = {}
        
        for monitor in self._delinquency_monitors:
            # Extrair configuração (seguindo estrutura original)
            window_days = monitor['limites'].get('prazo_dias', 1)
            limite = monitor['limites']['limite']
            
            # Gerar key baseada no prazo ou usar ID do monitor se prazo=1
            if window_days == 1:
                key = monitor.get('id', 'inadimplencia_geral')
            else:
                key = f"inadimplencia_{window_days}d"
            
            # Verificar se há títulos atrasados
            titulos_atrasados = pool_xlsx[pool_xlsx['dias_atraso'] > 0]
            
            if titulos_atrasados.empty:
                resultados[key] = {
                    "percentual": 0.0,
                    "valor_absoluto": 0.0,
                    "pl_base": round(float(pl_pool), 2),
                    "limite": round(limite * 100, 2),
                    "status": "enquadrado",
                    "margem": round(limite * 100, 2),
                    "quantidade_titulos": 0
                }
                continue
            
            # Filtrar por janela (>= window_days)
            titulos_janela = titulos_atrasados[titulos_atrasados['dias_atraso'] >= window_days]
            
            # Calcular valores
            valor_total_atraso = titulos_janela['valor_presente'].sum()
            quantidade_titulos = len(titulos_janela)
            
            # Calcular percentual
            percentual_delinquency = (valor_total_atraso / pl_pool) * 100
            
            # Determinar status
            status = "enquadrado" if percentual_delinquency <= (limite * 100) else "violado"
            
            # Calcular margem
            margem = (limite * 100) - percentual_delinquency
            
            # Resultado no formato original
            resultados[key] = {
                "percentual": round(percentual_delinquency, 2),
                "valor_absoluto": round(float(valor_total_atraso), 2),
                "pl_base": round(float(pl_pool), 2),
                "limite": round(limite * 100, 2),
                "status": status,
                "margem": round(margem, 2),
                "quantidade_titulos": quantidade_titulos
            }
        
        return resultados
    
    def _generate_detailed_matrix(self, pool_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera matriz detalhada de atrasos.
        
        Args:
            pool_xlsx: DataFrame filtrado do pool
            
        Returns:
            Dict com matriz completa
        """
        # Filtrar apenas títulos atrasados
        titulos_atrasados = pool_xlsx[pool_xlsx['dias_atraso'] > 0]
        
        if titulos_atrasados.empty:
            return {
                "lista_titulos_atrasados": [],
                "consolidado_por_cedente": {},
                "consolidado_por_sacado": {},
                "estatisticas_gerais": {
                    "total_titulos_atrasados": 0,
                    "valor_total_em_atraso": 0,
                    "atraso_medio_dias": 0,
                    "quantidade_cedentes_afetados": 0,
                    "quantidade_sacados_afetados": 0
                }
            }
        
        # Lista detalhada de títulos
        lista_titulos = []
        for _, row in titulos_atrasados.iterrows():
            lista_titulos.append({
                "cedente": row.get('nome_do_cedente', row.get('cedente', 'N/A')),
                "sacado": row.get('nome_do_sacado', row.get('sacado', 'N/A')),
                "valor_presente": float(row['valor_presente']),
                "dias_atraso": int(row['dias_atraso']),
                "data_vencimento": row['vencimento_original'].strftime('%Y-%m-%d'),
                "grupo_de_risco": row.get('grupo_de_risco', 'N/A'),
                "status": row.get('status', 'atrasada'),
                "numero_documento": row.get('numero_documento', 'N/A'),
                "data_emissao": row['data_emissao'].strftime('%Y-%m-%d') if pd.notna(row.get('data_emissao')) else None
            })
        
        # Consolidação por cedente
        consolidado_cedente = {}
        cedente_col = 'nome_do_cedente' if 'nome_do_cedente' in titulos_atrasados.columns else 'cedente'
        
        for cedente, grupo in titulos_atrasados.groupby(cedente_col):
            consolidado_cedente[cedente] = {
                "quantidade_titulos": len(grupo),
                "valor_total_atraso": float(grupo['valor_presente'].sum()),
                "maior_atraso_dias": int(grupo['dias_atraso'].max()),
                "distribuicao_faixas": self._calculate_distribution_ranges(grupo['dias_atraso'])
            }
        
        # Consolidação por sacado
        consolidado_sacado = {}
        sacado_col = 'nome_do_sacado' if 'nome_do_sacado' in titulos_atrasados.columns else 'sacado'
        
        for sacado, grupo in titulos_atrasados.groupby(sacado_col):
            cedentes_afetados = grupo[cedente_col].unique().tolist()
            consolidado_sacado[sacado] = {
                "quantidade_titulos": len(grupo),
                "valor_total_atraso": float(grupo['valor_presente'].sum()),
                "quantidade_cedentes": len(cedentes_afetados),
                "lista_cedentes": cedentes_afetados
            }
        
        # Estatísticas gerais
        estatisticas = {
            "total_titulos_atrasados": len(titulos_atrasados),
            "valor_total_em_atraso": round(float(titulos_atrasados['valor_presente'].sum()), 2),
            "atraso_medio_dias": round(float(titulos_atrasados['dias_atraso'].mean()), 1),
            "quantidade_cedentes_afetados": len(consolidado_cedente),
            "quantidade_sacados_afetados": len(consolidado_sacado)
        }
        
        return {
            "lista_titulos_atrasados": lista_titulos,
            "consolidado_por_cedente": consolidado_cedente,
            "consolidado_por_sacado": consolidado_sacado,
            "estatisticas_gerais": estatisticas
        }
    
    def _calculate_distribution_ranges(self, dias_atraso: pd.Series) -> Dict[str, int]:
        """
        Calcula distribuição por faixas de atraso.
        
        Args:
            dias_atraso: Series com dias de atraso
            
        Returns:
            Dict com contagem por faixa
        """
        faixas = {
            "1-30": 0,
            "31-60": 0,
            "61-90": 0,
            "90+": 0
        }
        
        for dias in dias_atraso:
            if dias <= 30:
                faixas["1-30"] += 1
            elif dias <= 60:
                faixas["31-60"] += 1
            elif dias <= 90:
                faixas["61-90"] += 1
            else:
                faixas["90+"] += 1
        
        return faixas
    
    def _generate_aging_analysis(self, pool_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera análise de aging configurável.
        
        Args:
            pool_xlsx: DataFrame filtrado do pool
            
        Returns:
            Dict com análise de aging
        """
        # Extrair faixas de aging da configuração PDD
        aging_ranges = self._extract_aging_ranges_from_pdd()
        
        # Agrupar por faixas
        faixas = {}
        pl_pool = float(pool_xlsx['valor_presente'].sum())
        
        for range_name, min_days, max_days in aging_ranges:
            if range_name == "adimplente":
                # Títulos não atrasados (baseado em dias_atraso)
                faixa_data = pool_xlsx[pool_xlsx['dias_atraso'] == 0]
            elif max_days == float('inf'):
                # Faixa final (ex: 181+)
                faixa_data = pool_xlsx[pool_xlsx['dias_atraso'] >= min_days]
            else:
                # Faixa intermediária
                faixa_data = pool_xlsx[
                    (pool_xlsx['dias_atraso'] >= min_days) & 
                    (pool_xlsx['dias_atraso'] <= max_days)
                ]
            
            valor_total = faixa_data['valor_presente'].sum()
            percentual = (valor_total / pl_pool * 100) if pl_pool > 0 else 0
            
            # Detalhes por ativo (drill-down) - obrigatório exceto para adimplente
            detalhes_ativos = []
            detalhes_df = pd.DataFrame()
            if range_name != "adimplente" and not faixa_data.empty:
                for _, row in faixa_data.iterrows():
                    detalhes_ativos.append({
                        "cedente": row.get('nome_do_cedente', row.get('cedente', 'N/A')),
                        "sacado": row.get('nome_do_sacado', row.get('sacado', 'N/A')),
                        "valor_presente": float(row['valor_presente']),
                        "dias_atraso": int(row['dias_atraso']),
                        "vencimento": row['vencimento_original'].strftime('%Y-%m-%d')
                    })
                
                # DataFrame ordenado para análise
                detalhes_df = faixa_data.sort_values([
                    'nome_do_cedente' if 'nome_do_cedente' in faixa_data.columns else 'cedente',
                    'vencimento_original',
                    'valor_presente'
                ], ascending=[True, True, False])
            
            faixas[range_name] = {
                "quantidade": len(faixa_data),
                "valor": round(float(valor_total), 2),
                "percentual": round(percentual, 2),
                "detalhes_ativos": detalhes_ativos,
                "detalhes_ativos_df": detalhes_df
            }
        
        return {
            "faixas": faixas,
            "pl_pool": pl_pool,
            "configuracao_utilizada": "PDD" if self._pdd_config else "Padrão"
        }
    
    def _extract_aging_ranges_from_pdd(self) -> List[Tuple[str, int, int]]:
        """
        Extrai faixas de aging da configuração PDD (compatível com original).
        
        Returns:
            Lista de tuplas (nome_faixa, min_dias, max_dias)
        """
        # Obter configuração PDD diretamente da configuração do pool
        pdd_config = self.config.get('provisoes_pdd', {}).get('grupos_risco', {})
        
        if not pdd_config:
            # Faixas padrão se não houver configuração PDD
            return [
                ("adimplente", 0, 0),
                ("1-30", 1, 30),
                ("31-60", 31, 60),
                ("61-90", 61, 90),
                ("90+", 91, float('inf'))
            ]
        
        # Converter grupos PDD em faixas de aging (usando mesma lógica que o original)
        faixas = []
        grupos_ordenados = sorted(pdd_config.items(), key=lambda x: x[1]['atraso_max_dias'])
        
        # Primeira faixa: adimplente (0 dias)
        faixas.append(("adimplente", 0, 0))
        
        # Faixas baseadas nos grupos de risco
        prev_max = 0
        for grupo, config_grupo in grupos_ordenados:
            max_dias = config_grupo['atraso_max_dias']
            
            if max_dias > prev_max:
                min_dias = prev_max + 1
                
                # Tratamento especial para último grupo (999 dias = infinito)
                if max_dias >= 999:
                    label = f"{min_dias}+"
                    faixas.append((label, min_dias, float('inf')))
                else:
                    if min_dias == max_dias:
                        label = f"{min_dias}d"
                    else:
                        label = f"{min_dias}-{max_dias}"
                    faixas.append((label, min_dias, max_dias))
                
                prev_max = max_dias
        
        return faixas
    
    def _find_delinquency_monitors(self) -> List[Dict[str, Any]]:
        """
        Busca monitores de inadimplência na configuração.
        
        Returns:
            Lista de monitores encontrados
        """
        monitors = []
        
        monitoramentos = self.config.get('monitoramentos_ativos', [])
        for monitor in monitoramentos:
            # Buscar por ID que contém 'inadimplencia' ou tipo 'inadimplencia'
            monitor_id = monitor.get('id', '')
            monitor_tipo = monitor.get('tipo', '')
            
            if 'inadimplencia' in monitor_id or monitor_tipo == 'inadimplencia':
                if monitor.get('ativo', False):  # Apenas ativos
                    monitors.append(monitor)
        
        return monitors
    
    def _find_pdd_config(self) -> Optional[Dict[str, Any]]:
        """
        Busca configuração PDD para classificação de grupos.
        
        Returns:
            Configuração PDD ou None
        """
        # Verificar se há configuração PDD diretamente na configuração do pool
        pdd_config = self.config.get('provisoes_pdd', {}).get('grupos_risco', {})
        
        if pdd_config:
            return {'grupos_risco': pdd_config}
        
        # Fallback: buscar monitor PDD ativo
        monitoramentos = self.config.get('monitoramentos_ativos', [])
        
        for monitor in monitoramentos:
            if monitor.get('id') == 'pdd':
                return monitor
        
        return None
    
    def run_monitoring(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """
        Interface principal do monitor.
        
        Args:
            pool_csv: DataFrame com dados do pool
            carteira_xlsx: DataFrame com carteira detalhada
            
        Returns:
            Dict com resultado completo (formato original)
        """
        try:
            # Validar dados
            if not self.validate_data(pool_csv, carteira_xlsx):
                return {
                    "sucesso": False,
                    "monitor": "inadimplencia",
                    "erro": "Falha na validação de dados"
                }
            
            # Calcular inadimplência
            resultado_calculo = self.calculate(pool_csv, carteira_xlsx)
            
            # Construir resultado no formato original
            resultado_final = {
                "sucesso": True,
                "monitor": "inadimplencia",
                "pool_id": resultado_calculo['pool_id'],
                "data_analise": datetime.now().isoformat(),
                "pl_pool": resultado_calculo['pl_pool'],
                "enriquecimento": {
                    "dias_atraso_adicionado": resultado_calculo['metadata']['dias_atraso_adicionado'],
                    "grupo_de_risco_adicionado": resultado_calculo['metadata']['grupo_de_risco_adicionado'],
                    "registros_pool": resultado_calculo['metadata']['registros_pool'],
                    "registros_total_xlsx": resultado_calculo['metadata']['registros_total_xlsx']
                },
                "aging_analysis": resultado_calculo['aging_analysis'],
                "matriz_atrasos": resultado_calculo['matriz_atrasos']
            }
            
            # Adicionar resultados por janela diretamente no nível raiz
            for janela_key, janela_result in resultado_calculo['resultados'].items():
                resultado_final[janela_key] = janela_result
            
            return resultado_final
            
        except Exception as e:
            return {
                "sucesso": False,
                "monitor": "inadimplencia",
                "erro": str(e),
                "tipo_erro": type(e).__name__
            }


# Função de compatibilidade com interface original
def run_delinquency_monitoring(
    pool_data_csv: pd.DataFrame,
    carteira_xlsx: pd.DataFrame,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Interface de compatibilidade com sistema original.
    
    CRÍTICO: Mantém funcionalidade de enriquecimento progressivo.
    
    Args:
        pool_data_csv: DataFrame com dados do pool
        carteira_xlsx: DataFrame com carteira detalhada (será enriquecido)
        config: Configuração JSON do pool
        
    Returns:
        Dict com resultado completo
    """
    monitor = DelinquencyMonitor(config)
    return monitor.run_monitoring(pool_data_csv, carteira_xlsx)