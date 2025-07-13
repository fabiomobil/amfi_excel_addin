"""
Monitor Customizado: SuperSim Pool 1 - Recovery Rate

ESPECIFICAÇÃO DETALHADA:
Este monitor implementa a validação específica da taxa de recuperação mensal para o pool SuperSim,
conforme definido na escritura. A regra estabelece que recovery rates inferiores a 95% por 3 meses
consecutivos acionam evento de vencimento antecipado.

FUNCIONALIDADES REQUERIDAS:
1. Cálculo de recovery rate mensal
2. Monitoramento de janela deslizante de 3 meses
3. Detecção de violações consecutivas
4. Geração de alertas e eventos de aceleração

FÓRMULA DE CÁLCULO:
Recovery Rate = ∑(Valor Pago dos Direitos Creditórios) / ∑(Valor de Aquisição dos Direitos Creditórios)

REGRAS DE NEGÓCIO:
- Limite mínimo: 95% (0.95)
- Frequência: Mensal
- Janela de avaliação: 3 meses consecutivos
- Gatilho: 3 ocorrências simultâneas abaixo do limite
- Consequência: Evento de avaliação para vencimento antecipado

DADOS DE ENTRADA NECESSÁRIOS:
- DataFrame com colunas: ['data_vencimento', 'valor_aquisicao', 'valor_pago', 'status_pagamento']
- Período de análise: Data de referência e 3 meses anteriores
- Configuração do pool (limites e parâmetros)

FUNÇÕES OBRIGATÓRIAS A IMPLEMENTAR:
"""

def validar_dados(df, config):
    """
    Valida se o DataFrame contém todos os dados necessários para o cálculo.
    
    Parâmetros:
    - df: DataFrame com dados da carteira
    - config: Configuração do pool
    
    Retorna:
    - dict: {'valido': bool, 'erros': list, 'warnings': list}
    
    Validações necessárias:
    - Verificar presença das colunas obrigatórias: ['data_vencimento', 'valor_aquisicao', 'valor_pago']
    - Validar tipos de dados e formatos
    - Verificar se há dados suficientes para 3 meses de análise
    - Validar valores numéricos (não negativos)
    """
    pass

def calcular_recovery_rate_mensal(df, mes_referencia):
    """
    Calcula o recovery rate para um mês específico.
    
    Parâmetros:
    - df: DataFrame com dados da carteira
    - mes_referencia: String no formato 'YYYY-MM'
    
    Retorna:
    - dict: {
        'mes': str,
        'valor_total_aquisicao': float,
        'valor_total_pago': float,
        'recovery_rate': float,
        'quantidade_direitos': int
    }
    
    Lógica:
    - Filtrar direitos creditórios com vencimento no mês de referência
    - Somar valores de aquisição e valores pagos
    - Calcular taxa: valor_pago / valor_aquisicao
    - Retornar 0.0 se não houver direitos no período
    """
    pass

def obter_historico_3_meses(df, data_referencia):
    """
    Obtém histórico de recovery rates dos últimos 3 meses.
    
    Parâmetros:
    - df: DataFrame com dados da carteira
    - data_referencia: Data base para cálculo (formato 'YYYY-MM-DD')
    
    Retorna:
    - list: Lista de dicts com recovery rates dos últimos 3 meses
    [
        {'mes': '2025-01', 'recovery_rate': 0.97, 'valor_aquisicao': 1000000, 'valor_pago': 970000},
        {'mes': '2024-12', 'recovery_rate': 0.94, 'valor_aquisicao': 800000, 'valor_pago': 752000},
        {'mes': '2024-11', 'recovery_rate': 0.93, 'valor_aquisicao': 1200000, 'valor_pago': 1116000}
    ]
    """
    pass

def verificar_violacao_consecutiva(historico_3_meses, limite_minimo=0.95):
    """
    Verifica se houve violação consecutiva do recovery rate.
    
    Parâmetros:
    - historico_3_meses: Lista de recovery rates dos últimos 3 meses
    - limite_minimo: Limite mínimo (default 0.95)
    
    Retorna:
    - dict: {
        'violacao_detectada': bool,
        'meses_consecutivos_abaixo': int,
        'detalhes_violacao': list,
        'gatilho_vencimento_antecipado': bool
    }
    
    Lógica:
    - Verificar se todos os 3 meses estão abaixo do limite
    - Identificar sequência de violações
    - Determinar se atinge critério para vencimento antecipado
    """
    pass

def gerar_alerta_recovery_rate(resultado_verificacao, config):
    """
    Gera alertas baseados no resultado da verificação.
    
    Parâmetros:
    - resultado_verificacao: Output da função verificar_violacao_consecutiva
    - config: Configuração do pool
    
    Retorna:
    - dict: {
        'tipo_alerta': str, # 'warning' | 'critical' | 'info'
        'titulo': str,
        'mensagem': str,
        'acao_requerida': str,
        'dados_suporte': dict
    }
    """
    pass

def executar_monitoramento_recovery_rate(pool_id, data_referencia=None):
    """
    Execução completa do monitoramento de recovery rate.
    
    Parâmetros:
    - pool_id: Identificador do pool
    - data_referencia: Data base (default: hoje)
    
    Retorna:
    - dict: Resultado completo do monitoramento
    {
        'pool_id': str,
        'data_execucao': str,
        'recovery_rate_atual': float,
        'historico_3_meses': list,
        'violacao_detectada': bool,
        'alertas': list,
        'evento_aceleracao': bool,
        'status': 'OK' | 'WARNING' | 'CRITICAL'
    }
    
    Fluxo:
    1. Carregar dados da carteira do pool
    2. Validar dados de entrada
    3. Calcular recovery rates dos últimos 3 meses
    4. Verificar violações consecutivas
    5. Gerar alertas apropriados
    6. Retornar resultado consolidado
    """
    pass

# CONSTANTES DO MONITOR
LIMITE_RECOVERY_RATE_MINIMO = 0.95
JANELA_AVALIACAO_MESES = 3
COLUNAS_OBRIGATORIAS = ['data_vencimento', 'valor_aquisicao', 'valor_pago', 'status_pagamento']

# CONFIGURAÇÃO DE INTEGRAÇÃO
MONITOR_CONFIG = {
    'id': 'supersim_recovery_rate',
    'tipo': 'recovery_rate_customizado',
    'pool_aplicavel': 'supersim_pool_1',
    'frequencia_execucao': 'mensal',
    'prioridade': 'critica',
    'dependencias': ['dados_carteira_mensal', 'historico_pagamentos']
}

"""
INSTRUÇÕES DE IMPLEMENTAÇÃO:
1. Implementar todas as funções listadas acima
2. Adicionar tratamento de erros robusto
3. Incluir logging detalhado das operações
4. Criar testes unitários para cada função
5. Validar com dados reais do pool SuperSim
6. Documentar casos edge (meses sem dados, valores zero, etc.)

CASOS DE TESTE MÍNIMOS:
- Recovery rate exatamente 95%
- 3 meses consecutivos abaixo de 95%
- 2 meses abaixo + 1 mês acima (não deve disparar)
- Mês sem dados de vencimento
- Valores de aquisição zero
- Dados incompletos ou corrompidos

INTEGRAÇÃO COM SISTEMA:
- Este arquivo deve ser importado automaticamente pelo monitoring_engine.py
- A configuração está declarada em supersim_pool_1_monitoring.json
- Alertas devem ser integrados ao alert_manager.py
- Logs devem seguir padrão do sistema (monitor/utils/alerts.py)
"""