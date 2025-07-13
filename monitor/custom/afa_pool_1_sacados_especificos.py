"""
Monitor Customizado: AFA Pool 1 - Sacados Específicos
=====================================================

Monitor específico para validar a lista de sacados elegíveis do AFA Pool 1.
Este pool tem uma lista pré-aprovada de 25 sacados específicos que devem ser
validados antes de qualquer aquisição de direitos creditórios.

Autor: Sistema AmFi
Data: 2025-07-11
Pool: afa_pool_1
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

class AFAPool1SacadosEspecificos:
    """
    Monitor customizado para validação dos sacados específicos do AFA Pool 1.
    
    Este monitor verifica se todos os sacados presentes na carteira estão 
    na lista de sacados elegíveis pré-aprovados para este pool.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o monitor com a configuração do pool.
        
        Args:
            config_path: Caminho para o arquivo de configuração JSON do pool
        """
        self.pool_id = "afa_pool_1"
        self.config_path = config_path
        self.sacados_elegiveis = []
        self.load_config()
    
    def load_config(self):
        """Carrega a configuração do pool e a lista de sacados elegíveis."""
        if self.config_path:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.sacados_elegiveis = config.get('sacados_elegiveis', [])
            except FileNotFoundError:
                print(f"Arquivo de configuração não encontrado: {self.config_path}")
                self.sacados_elegiveis = self._get_default_sacados()
        else:
            self.sacados_elegiveis = self._get_default_sacados()
    
    def _get_default_sacados(self) -> List[str]:
        """
        Retorna a lista padrão de sacados elegíveis para o AFA Pool 1.
        
        Returns:
            Lista com os 25 sacados elegíveis pré-aprovados
        """
        return [
            "BANCO BV S.A.",
            "BANCO VOTORANTIM S.A.",
            "BOTICÁRIO PRODUTOS DE BELEZA LTDA.",
            "CARGILL AGRÍCOLA S.A.",
            "CUTRALE TRADING BRASIL LTDA.",
            "REDE D'OR SÃO LUIZ S.A.",
            "QUÍMICA AMPARO LTDA.",
            "STELLANTIS AUTOMOVEIS DO BRASIL S.A.",
            "DHL GLOBAL FORWARDING (BRAZIL) LOGISTICS LTDA",
            "SUZANO PAPEL E CELULOSE S.A.",
            "AMAZON SERVIÇOS DE VAREJO DO BRASIL LTDA",
            "SANOFI MEDLEY FARMACÊUTICA LTDA",
            "ATACADÃO S/A",
            "CARREFOUR COMÉRCIO E INDÚSTRIA LTDA",
            "RAIA DROGASIL S/A",
            "COMPANHIA BRASILEIRA DE DISTRIBUIÇÃO S/A",
            "SEARA ALIMENTOS LTDA.",
            "MAERSK LOGISTICS SERVICES BRASIL LTDA.",
            "WEG EQUIPAMENTOS ELÉTRICOS S.A.",
            "ARCELORMITTAL BRASIL S.A.",
            "EBAZAR.COM.BR LTDA.",
            "SIEMENS HEALTHCARE DIAGNÓSTICOS S.A.",
            "ELECTROLUX DO BRASIL S.A.",
            "BMW DO BRASIL LTDA",
            "GENERAL MOTORS DO BRASIL"
        ]
    
    def validar_dados(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Valida se o DataFrame contém os campos necessários.
        
        Args:
            df: DataFrame com os dados da carteira
            
        Returns:
            Tuple (is_valid, error_message)
        """
        required_fields = ['sacado', 'valor_presente']
        
        for field in required_fields:
            if field not in df.columns:
                return False, f"Campo obrigatório '{field}' não encontrado no DataFrame"
        
        if df.empty:
            return False, "DataFrame está vazio"
        
        return True, ""
    
    def normalizar_nome_sacado(self, nome: str) -> str:
        """
        Normaliza o nome do sacado para facilitar comparação.
        
        Args:
            nome: Nome do sacado a ser normalizado
            
        Returns:
            Nome normalizado (maiúsculo, sem espaços extras)
        """
        if pd.isna(nome):
            return ""
        
        return str(nome).upper().strip()
    
    def verificar_sacado_elegivel(self, sacado: str) -> bool:
        """
        Verifica se um sacado está na lista de elegíveis.
        
        Args:
            sacado: Nome do sacado a ser verificado
            
        Returns:
            True se o sacado é elegível, False caso contrário
        """
        sacado_normalizado = self.normalizar_nome_sacado(sacado)
        
        for sacado_elegivel in self.sacados_elegiveis:
            if self.normalizar_nome_sacado(sacado_elegivel) == sacado_normalizado:
                return True
        
        return False
    
    def calcular_indicador(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula o indicador de conformidade dos sacados.
        
        Args:
            df: DataFrame com dados da carteira
            
        Returns:
            Dicionário com resultado do cálculo
        """
        # Normalizar nomes dos sacados
        df['sacado_normalizado'] = df['sacado'].apply(self.normalizar_nome_sacado)
        
        # Identificar sacados únicos
        sacados_unicos = df['sacado_normalizado'].unique()
        
        # Verificar elegibilidade de cada sacado
        sacados_elegiveis_carteira = []
        sacados_nao_elegiveis = []
        
        for sacado in sacados_unicos:
            if self.verificar_sacado_elegivel(sacado):
                sacados_elegiveis_carteira.append(sacado)
            else:
                sacados_nao_elegiveis.append(sacado)
        
        # Calcular valores dos sacados não elegíveis
        df_nao_elegiveis = df[df['sacado_normalizado'].isin(sacados_nao_elegiveis)]
        valor_nao_elegivel = df_nao_elegiveis['valor_presente'].sum()
        valor_total = df['valor_presente'].sum()
        
        percentual_nao_elegivel = (valor_nao_elegivel / valor_total) * 100 if valor_total > 0 else 0
        
        return {
            'total_sacados_carteira': len(sacados_unicos),
            'sacados_elegiveis_encontrados': len(sacados_elegiveis_carteira),
            'sacados_nao_elegiveis': len(sacados_nao_elegiveis),
            'lista_sacados_nao_elegiveis': sacados_nao_elegiveis,
            'valor_nao_elegivel': valor_nao_elegivel,
            'valor_total': valor_total,
            'percentual_nao_elegivel': percentual_nao_elegivel,
            'conformidade': len(sacados_nao_elegiveis) == 0
        }
    
    def gerar_resultado(self, indicador: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera o resultado final do monitoramento.
        
        Args:
            indicador: Resultado do cálculo do indicador
            
        Returns:
            Dicionário com o resultado padronizado
        """
        is_compliant = indicador['conformidade']
        
        if is_compliant:
            status = "CONFORME"
            severidade = "info"
            message = f"Todos os {indicador['total_sacados_carteira']} sacados estão na lista de elegíveis"
        else:
            status = "VIOLAÇÃO"
            severidade = "critica"
            message = f"{indicador['sacados_nao_elegiveis']} sacados não estão na lista de elegíveis"
            if indicador['valor_nao_elegivel'] > 0:
                message += f" (R$ {indicador['valor_nao_elegivel']:,.2f} - {indicador['percentual_nao_elegivel']:.2f}%)"
        
        return {
            'pool_id': self.pool_id,
            'monitor_id': 'afa_pool_1_sacados_especificos',
            'tipo': 'elegibilidade_sacados',
            'status': status,
            'severidade': severidade,
            'valor_calculado': indicador['sacados_nao_elegiveis'],
            'limite_permitido': 0,
            'unidade': 'sacados_nao_elegiveis',
            'percentual_nao_elegivel': indicador['percentual_nao_elegivel'],
            'message': message,
            'detalhes': {
                'total_sacados': indicador['total_sacados_carteira'],
                'sacados_elegiveis': indicador['sacados_elegiveis_encontrados'],
                'sacados_nao_elegiveis': indicador['sacados_nao_elegiveis'],
                'lista_nao_elegiveis': indicador['lista_sacados_nao_elegiveis'],
                'valor_nao_elegivel': indicador['valor_nao_elegivel'],
                'valor_total': indicador['valor_total']
            },
            'timestamp': datetime.now().isoformat(),
            'requer_acao': not is_compliant
        }
    
    def executar_monitoramento(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executa o monitoramento completo dos sacados específicos.
        
        Args:
            df: DataFrame com dados da carteira
            
        Returns:
            Resultado do monitoramento
        """
        # Validar dados de entrada
        is_valid, error_msg = self.validar_dados(df)
        if not is_valid:
            return {
                'pool_id': self.pool_id,
                'monitor_id': 'afa_pool_1_sacados_especificos',
                'status': 'ERRO',
                'severidade': 'critica',
                'message': f"Erro na validação dos dados: {error_msg}",
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Calcular indicador
            indicador = self.calcular_indicador(df)
            
            # Gerar resultado
            resultado = self.gerar_resultado(indicador)
            
            return resultado
            
        except Exception as e:
            return {
                'pool_id': self.pool_id,
                'monitor_id': 'afa_pool_1_sacados_especificos',
                'status': 'ERRO',
                'severidade': 'critica',
                'message': f"Erro durante execução: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }


# Função de conveniência para uso direto
def executar_monitor_afa_sacados(df: pd.DataFrame, config_path: str = None) -> Dict[str, Any]:
    """
    Função de conveniência para executar o monitor de sacados específicos do AFA Pool 1.
    
    Args:
        df: DataFrame com dados da carteira
        config_path: Caminho opcional para arquivo de configuração
        
    Returns:
        Resultado do monitoramento
    """
    monitor = AFAPool1SacadosEspecificos(config_path)
    return monitor.executar_monitoramento(df)


if __name__ == "__main__":
    # Exemplo de uso para teste
    import pandas as pd
    
    # Dados de exemplo
    dados_teste = {
        'sacado': ['BANCO BV S.A.', 'EMPRESA NÃO ELEGÍVEL', 'SUZANO PAPEL E CELULOSE S.A.'],
        'valor_presente': [100000.0, 50000.0, 200000.0]
    }
    
    df_teste = pd.DataFrame(dados_teste)
    
    # Executar monitor
    resultado = executar_monitor_afa_sacados(df_teste)
    
    print("=== RESULTADO DO MONITORAMENTO ===")
    print(f"Status: {resultado['status']}")
    print(f"Severidade: {resultado['severidade']}")
    print(f"Mensagem: {resultado['message']}")
    
    if 'detalhes' in resultado:
        print(f"Sacados não elegíveis: {resultado['detalhes']['lista_nao_elegiveis']}")