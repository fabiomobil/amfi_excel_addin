# BaseMonitor API Documentation

## Visão Geral

O BaseMonitor é a classe base do sistema AmFi que padroniza a criação de monitores de compliance para fundos de investimento. Ele fornece uma interface consistente e funcionalidades comuns para todos os monitores.

## Localização

- **Arquivo principal**: `/monitor/core/base_monitor.py`
- **Sistema de imports**: `/monitor/core/imports.py`
- **Monitores implementados**: `/monitor/core/subordinacao_monitor.py`

## Arquitetura

### Padrão de Design

O BaseMonitor implementa o **Template Method Pattern**, onde a classe base define o algoritmo geral de execução de monitoramento, e as subclasses implementam etapas específicas.

```
run() [Template Method - BaseMonitor]
 ├── validate_inputs() [Concreto - BaseMonitor]
 ├── is_active() [Concreto - BaseMonitor]
 ├── calculate() [Abstrato - Subclasse]
 ├── format_result() [Concreto - BaseMonitor]
 └── log_execution() [Concreto - BaseMonitor]
```

## Interface Principal

### Classe BaseMonitor

```python
from monitor.core.base_monitor import BaseMonitor

class BaseMonitor:
    def __init__(self, pool_id: str, config: Dict, csv_data: pd.DataFrame, xlsx_data: pd.DataFrame = None):
        """
        Inicializa um monitor base.
        
        Args:
            pool_id: Identificador do pool (ex: "AFA Pool #1")
            config: Configuração JSON do pool
            csv_data: DataFrame com dados resumidos do pool
            xlsx_data: DataFrame com carteira detalhada (opcional)
        """
    
    def run(self) -> MonitorResult:
        """
        Executa o monitoramento completo.
        
        Returns:
            MonitorResult com status, dados e metadados
        """
    
    # Métodos abstratos (devem ser implementados nas subclasses)
    def get_monitor_type(self) -> str:
        """Retorna o tipo do monitor (ex: 'subordinacao')"""
        raise NotImplementedError
    
    def calculate(self) -> Dict:
        """Implementa a lógica específica de cálculo do monitor"""
        raise NotImplementedError
```

### Classe MonitorResult

```python
class MonitorResult:
    def __init__(self, status: str, data: Dict = None, metadata: Dict = None):
        """
        Resultado padronizado de um monitor.
        
        Args:
            status: 'success', 'error', 'warning'
            data: Dados específicos do resultado
            metadata: Metadados de execução
        """
    
    def to_dict(self) -> Dict:
        """Converte o resultado para dicionário"""
    
    def is_success(self) -> bool:
        """Verifica se a execução foi bem-sucedida"""
    
    def get_violations(self) -> List[Dict]:
        """Retorna lista de violações detectadas"""
```

## Métodos Disponíveis

### Métodos Públicos

#### `run() -> MonitorResult`
Método principal que executa todo o fluxo de monitoramento.

**Fluxo interno:**
1. Validação de entradas
2. Verificação se monitor está ativo
3. Execução do cálculo específico
4. Formatação do resultado
5. Log da execução

**Retorno:**
```python
MonitorResult(
    status='success|error|warning',
    data={
        'monitor_type': 'subordinacao',
        'pool_id': 'AFA Pool #1',
        'resultado_calculado': {...},
        'violacoes': [...]
    },
    metadata={
        'execution_time': 1.234,
        'timestamp': '2025-07-17T09:00:00Z',
        'version': '2.0'
    }
)
```

#### `is_active() -> bool`
Verifica se o monitor está configurado como ativo no JSON do pool.

```python
monitor = SubordinacaoMonitor(pool_id, config, csv_data)
if monitor.is_active():
    result = monitor.run()
```

#### `validate_inputs() -> bool`
Valida se os dados de entrada estão corretos.

**Validações aplicadas:**
- `pool_id` não pode ser vazio
- `config` deve ser um dicionário válido
- `csv_data` deve ter colunas obrigatórias: ['sr', 'jr', 'pl']
- Dados monetários devem ser numéricos

### Métodos Auxiliares Protegidos

#### `_get_pool_data() -> pd.Series`
Retorna os dados específicos do pool do DataFrame CSV.

```python
def calculate(self):
    pool_data = self._get_pool_data()
    sr = pool_data['sr']
    jr = pool_data['jr']
    pl = pool_data['pl']
    # ... lógica de cálculo
```

#### `_get_config_value(key: str, default=None) -> Any`
Busca um valor na configuração do monitor.

```python
def calculate(self):
    limite_minimo = self._get_config_value('limite_minimo', 0.25)
    limite_critico = self._get_config_value('limite_critico', 0.20)
    # ... usar limites
```

#### `_find_monitor_config() -> Dict`
Busca a configuração específica do monitor no JSON do pool.

#### `_log(level: str, message: str, extra: Dict = None)`
Sistema de logging padronizado.

```python
self._log('info', 'Iniciando cálculo de subordinação')
self._log('warning', 'Valor encontrado próximo ao limite', {'valor': 0.251})
self._log('error', 'Falha na validação de dados', {'erro': str(e)})
```

## Implementando Novos Monitores

### Template Básico

```python
from monitor.core.base_monitor import BaseMonitor, MonitorResult

class MeuNovoMonitor(BaseMonitor):
    def get_monitor_type(self) -> str:
        return 'meu_monitor'
    
    def calculate(self) -> Dict:
        # 1. Obter dados do pool
        pool_data = self._get_pool_data()
        
        # 2. Obter configurações
        limite = self._get_config_value('limite', 0.10)
        
        # 3. Executar cálculo específico
        valor_calculado = self._meu_calculo_especifico(pool_data)
        
        # 4. Verificar violações
        status = 'enquadrado' if valor_calculado <= limite else 'violado'
        
        # 5. Retornar resultado
        return {
            'valor_calculado': valor_calculado,
            'limite_configurado': limite,
            'status': status,
            'dados_auxiliares': {
                'pl_pool': pool_data['pl'],
                'percentual': (valor_calculado / pool_data['pl']) * 100
            }
        }
    
    def _meu_calculo_especifico(self, pool_data: pd.Series) -> float:
        """Implementa a lógica específica do monitor."""
        # Sua lógica aqui
        return resultado
```

### Configuração no JSON do Pool

```json
{
  "monitoramentos_ativos": [
    {
      "id": "meu_monitor",
      "tipo": "meu_monitor",
      "ativo": true,
      "limite": 0.10,
      "configuracoes_especificas": {
        "parametro1": "valor1",
        "parametro2": 123
      }
    }
  ]
}
```

### Uso do Novo Monitor

```python
# Importação
from monitor.custom.meu_novo_monitor import MeuNovoMonitor

# Instanciação
monitor = MeuNovoMonitor(
    pool_id="AFA Pool #1",
    config=pool_config,
    csv_data=csv_data
)

# Execução
if monitor.is_active():
    result = monitor.run()
    
    if result.is_success():
        print(f"Resultado: {result.data}")
    else:
        print(f"Erro: {result.metadata['error']}")
```

## Integração com Orchestrator

### Registro Automático

O orchestrator automaticamente detecta e executa monitores baseados na configuração JSON:

```python
# Em orchestrator.py
def _execute_monitor_if_configured(monitor_type: str):
    """Executa monitor se configurado no pool."""
    
    if monitor_type == 'meu_monitor':
        from monitor.custom.meu_novo_monitor import MeuNovoMonitor
        monitor = MeuNovoMonitor(pool_id, config, csv_data)
        if monitor.is_active():
            return monitor.run()
    
    return None
```

### Detecção Automática

```python
# O orchestrator verifica automaticamente todos os monitores configurados
resultado = run_monitoring("AFA Pool #1")

# Acessar resultado do seu monitor
meu_resultado = resultado['resultados']['AFA Pool #1']['resultados']['meu_monitor']
```

## Tratamento de Erros

### Hierarquia de Exceções

```python
class MonitorError(Exception):
    """Erro base para monitores"""
    pass

class ValidationError(MonitorError):
    """Erro de validação de dados"""
    pass

class ConfigurationError(MonitorError):
    """Erro de configuração"""
    pass

class CalculationError(MonitorError):
    """Erro durante cálculo"""
    pass
```

### Tratamento Robusto

```python
def calculate(self) -> Dict:
    try:
        # Sua lógica aqui
        return resultado
    
    except ValidationError as e:
        self._log('error', f'Validação falhou: {e}')
        raise
    
    except Exception as e:
        self._log('error', f'Erro inesperado: {e}')
        raise CalculationError(f"Falha no cálculo: {e}") from e
```

## Testes Padronizados

### Framework de Testes

```python
import pytest
from monitor.core.base_monitor import BaseMonitor

class TestMeuNovoMonitor:
    def test_initialization(self, sample_csv_data, sample_pool_config):
        """Teste de inicialização básica."""
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        assert monitor.pool_id == 'AFA Pool #1'
        assert monitor.get_monitor_type() == 'meu_monitor'
    
    def test_active_detection(self, sample_csv_data, sample_pool_config):
        """Teste de detecção de monitor ativo."""
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        # Monitor deve estar ativo se configurado no JSON
        assert monitor.is_active() == True
    
    def test_calculation_logic(self, sample_csv_data, sample_pool_config):
        """Teste da lógica de cálculo."""
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        
        result = monitor.run()
        
        assert result.is_success()
        assert 'valor_calculado' in result.data
        assert 'status' in result.data
    
    def test_error_handling(self, sample_pool_config):
        """Teste de tratamento de erro."""
        # DataFrame vazio para forçar erro
        empty_csv = pd.DataFrame()
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, empty_csv)
        
        result = monitor.run()
        
        assert not result.is_success()
        assert result.status == 'error'
```

### Fixtures Disponíveis

```python
@pytest.fixture
def sample_csv_data():
    """DataFrame de teste com dados válidos."""
    return pd.DataFrame({
        'nome': ['AFA Pool #1', 'LeCapital Pool #1'],
        'sr': [6555273.93, 5200000.00],
        'jr': [2205966.66, 1800000.00],
        'pl': [8761240.59, 7000000.00]
    })

@pytest.fixture  
def sample_pool_config():
    """Configuração JSON de teste."""
    return {
        'pool_id': 'AFA Pool #1',
        'monitoramentos_ativos': [
            {
                'id': 'meu_monitor',
                'tipo': 'meu_monitor',
                'ativo': True,
                'limite': 0.10
            }
        ]
    }
```

## Performance e Otimização

### Boas Práticas

1. **Cache de Configuração**
   ```python
   @property
   def monitor_config(self):
       if not hasattr(self, '_monitor_config'):
           self._monitor_config = self._find_monitor_config()
       return self._monitor_config
   ```

2. **Validação Lazy**
   ```python
   def _validate_on_demand(self):
       if not hasattr(self, '_validation_done'):
           self.validate_inputs()
           self._validation_done = True
   ```

3. **Reuso de Dados**
   ```python
   def calculate(self):
       # Reutilizar dados já enriquecidos se disponíveis
       if 'dias_atraso' in self.xlsx_data.columns:
           # Usar dados já calculados
           pass
       else:
           # Calcular se necessário
           pass
   ```

### Métricas de Performance

- **Inicialização**: < 0.1s
- **Validação**: < 0.1s  
- **Cálculo típico**: < 1.0s
- **Formatação**: < 0.1s
- **Total por monitor**: < 2.0s

## Migração de Monitores Existentes

### Strategy de Migração

1. **Identificar monitor existente**
2. **Criar subclasse do BaseMonitor**
3. **Migrar lógica para calculate()**
4. **Adaptar testes existentes**
5. **Manter backward compatibility**

### Exemplo de Migração

```python
# ANTES (monitor antigo)
def run_subordination_monitoring(pool_id, config, csv_data):
    # 200+ linhas de validação, cálculo, formatação
    pass

# DEPOIS (BaseMonitor)
class SubordinacaoMonitor(BaseMonitor):
    def get_monitor_type(self):
        return 'subordinacao'
    
    def calculate(self):
        # Apenas 20-30 linhas de lógica pura
        pass

# Wrapper para compatibilidade
def run_subordination_monitoring(pool_id, config, csv_data):
    monitor = SubordinacaoMonitor(pool_id, config, csv_data)
    result = monitor.run()
    return result.to_dict()  # Formato legacy
```

## Troubleshooting

### Problemas Comuns

1. **Monitor não executa**
   - Verificar se `ativo: true` no JSON
   - Verificar se `id` e `tipo` estão corretos
   - Verificar imports no orchestrator

2. **Erro de validação**
   - Verificar colunas obrigatórias no CSV
   - Verificar tipos de dados (numéricas)
   - Verificar se pool_id existe no CSV

3. **Resultado inesperado**
   - Verificar logs com `self._log()`
   - Usar debug no método `calculate()`
   - Verificar configurações no JSON

### Debug Avançado

```python
# Habilitar logs detalhados
import logging
logging.getLogger('monitor').setLevel(logging.DEBUG)

# Executar monitor individual
monitor = MeuNovoMonitor(pool_id, config, csv_data)
result = monitor.run()

# Acessar metadados de execução
print(result.metadata['execution_time'])
print(result.metadata['logs'])
```

## Versionamento e Compatibilidade

- **Versão atual**: 2.0
- **Backward compatibility**: 100% mantida via wrappers
- **API estável**: Métodos públicos não mudam
- **Extensibilidade**: Novos métodos protegidos podem ser adicionados

## Conclusão

O BaseMonitor oferece:

✅ **Padronização**: Interface consistente para todos os monitores  
✅ **Reutilização**: Funcionalidades comuns implementadas uma vez  
✅ **Testabilidade**: Framework de testes integrado  
✅ **Performance**: Otimizações automáticas aplicadas  
✅ **Manutenibilidade**: Separação clara de responsabilidades  
✅ **Extensibilidade**: Fácil criação de novos monitores  

Para implementar um novo monitor, simplesmente:
1. Herde de `BaseMonitor`
2. Implemente `get_monitor_type()` e `calculate()`
3. Configure no JSON do pool
4. Execute via `run_monitoring()`