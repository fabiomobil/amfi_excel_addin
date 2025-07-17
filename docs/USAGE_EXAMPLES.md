# Exemplos Práticos de Uso - run_monitoring()

## Interface Única do Sistema AmFi

A função `run_monitoring()` é a **ÚNICA interface oficial** do sistema de monitoramento AmFi. Todas as funções legacy foram removidas em 2025-07-14.

### Monitores Disponíveis (2025-07-17)
- ✅ **Subordinação**: Índice de subordinação com limites (BaseMonitor implementado)
- ✅ **Inadimplência**: Janelas customizáveis (30d, 90d, etc.) com drill-down completo
- ✅ **PDD**: Provisão para Devedores Duvidosos (grupos AA-H) ⚠️ CCB não implementada
- ✅ **Concentração**: Sacados/cedentes individual e top-N + análise sequencial + matriz de sobra + filtro de entidades
- ✅ **Elegibilidade**: Critérios de ativos (implementação planejada - usar BaseMonitor)

## 1. Uso Básico

### **🆕 Sistema Otimizado (2025-07-16)**

#### **Usando Sistema de Imports Centralizado**
```python
# NOVO: Sistema centralizado (3 linhas vs. 87 linhas)
from monitor.core.imports import import_function
run_monitoring = import_function('orchestrator', 'run_monitoring', 'util')

# Ou importação direta simplificada
from monitor.orchestrator import run_monitoring
```

#### **Usando Classe Base para Monitores Customizados**
```python
# NOVO: Criando monitor customizado com BaseMonitor
from monitor.core.base_monitor import BaseMonitor

class MeuMonitorCustomizado(BaseMonitor):
    def get_monitor_type(self):
        return 'meu_monitor'
    
    def calculate(self):
        # Apenas lógica específica - validação e erro handling automáticos
        pool_data = self._get_pool_data()
        limite = self._get_config_value('limite', 0.05)
        
        return {
            'resultado': 'calculado',
            'limite_usado': limite
        }

# Uso
monitor = MeuMonitorCustomizado('AFA Pool #1', config, csv_data)
resultado = monitor.run()  # Automático: validação + cálculo + logging
```

### Processar Todos os Pools (Modo Debug)
```python
from monitor.orchestrator import run_monitoring

# Executa todos os pools configurados em test_pools.json
resultado = run_monitoring()

# Verificar sucesso geral
if resultado['sucesso']:
    print(f"✅ {resultado['estatisticas']['total']} pools processados")
    print(f"📊 Taxa de sucesso: {resultado['estatisticas']['taxa_sucesso']}%")
else:
    print(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")
```

### Processar Pool Específico
```python
# Executa apenas um pool específico
resultado = run_monitoring("LeCapital Pool #1")

if resultado['sucesso']:
    pool_result = resultado['resultados']['LeCapital Pool #1']
    print(f"✅ Pool processado com sucesso")
    print(f"📋 Monitores executados: {pool_result['monitores_executados']}")
```

## 2. Analisando Resultados de Subordinação

```python
resultado = run_monitoring("AFA Pool #1")

if resultado['sucesso']:
    # Navegar até resultados de subordinação
    pool_result = resultado['resultados']['AFA Pool #1']
    sub_result = pool_result['resultados']['subordinacao']
    
    # Verificar status
    sr_percent = sub_result['subordination_ratio_percent']
    status = sub_result['status_limite_minimo']
    limite_min = sub_result['limite_minimo'] * 100
    
    print(f"🎯 Subordinação: {sr_percent}%")
    print(f"📊 Limite mínimo: {limite_min}%")
    print(f"📋 Status: {status}")
    
    # Se violado, mostrar aporte necessário
    if status == 'violado':
        aporte = sub_result['aporte_necessario']['para_limite_minimo']
        print(f"💰 Aporte necessário: R$ {aporte:,.2f}")
        print("🚨 AÇÃO NECESSÁRIA: Pool em violação!")
```

## 3. Analisando Resultados de Inadimplência

```python
resultado = run_monitoring("LeCapital Pool #1")

if resultado['sucesso']:
    # Navegar até resultados de inadimplência
    pool_result = resultado['resultados']['LeCapital Pool #1']
    inad_result = pool_result['resultados']['inadimplencia']
    
    print("🔍 INADIMPLÊNCIA POR JANELA:")
    print("-" * 40)
    
    # Iterar por todas as janelas configuradas
    for janela_id, dados in inad_result['resultados'].items():
        percentual = dados['inadimplencia_percent']
        limite = dados['limite_configurado'] * 100
        status = dados['status']
        
        # Extrair número de dias da janela
        dias = janela_id.replace('inadimplencia_', '').replace('d', '')
        
        print(f"📅 {dias} dias: {percentual}% (limite: {limite}%) - {status}")
        
        if status == 'violado':
            print(f"   🚨 VIOLAÇÃO: Acima do limite permitido!")
```

## 4. Processamento em Lote com Tratamento de Erros

```python
def monitorar_todos_pools():
    """Executa monitoramento para todos os pools com tratamento robusto."""
    
    resultado = run_monitoring()
    
    if not resultado['sucesso']:
        print(f"❌ Falha crítica: {resultado.get('erro')}")
        return False
    
    stats = resultado['estatisticas']
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total: {stats['total']}")
    print(f"   Sucesso: {stats['sucesso']}")
    print(f"   Erro: {stats['erro']}")
    print(f"   Taxa: {stats['taxa_sucesso']}%")
    
    # Analisar pools com erro
    if stats['erro'] > 0:
        print(f"\n❌ POOLS COM ERRO:")
        for pool_name, pool_result in resultado['resultados'].items():
            if not pool_result.get('sucesso', True):
                erro = pool_result.get('erro', 'Desconhecido')
                print(f"   - {pool_name}: {erro}")
    
    # Analisar violações
    pools_violados = []
    for pool_name, pool_result in resultado['resultados'].items():
        if pool_result.get('sucesso'):
            # Verificar subordinação
            sub_result = pool_result['resultados'].get('subordinacao', {})
            if sub_result.get('status_limite_minimo') == 'violado':
                pools_violados.append((pool_name, 'subordinacao'))
            
            # Verificar inadimplência
            inad_result = pool_result['resultados'].get('inadimplencia', {})
            if 'resultados' in inad_result:
                for janela, dados in inad_result['resultados'].items():
                    if dados.get('status') == 'violado':
                        pools_violados.append((pool_name, f'inadimplencia_{janela}'))
            
            # Verificar PDD (se configurado)
            pdd_result = pool_result['resultados'].get('pdd', {})
            if pdd_result.get('sucesso') and 'pdd_analysis' in pdd_result:
                # PDD não tem "violação" - apenas análise de provisões
    
    if pools_violados:
        print(f"\n🚨 VIOLAÇÕES DETECTADAS:")
        for pool, tipo_violacao in pools_violados:
            print(f"   - {pool}: {tipo_violacao}")
    
    return True

# Executar
if __name__ == "__main__":
    monitorar_todos_pools()
```

## 5. Acessando DataFrame Enriquecido

```python
resultado = run_monitoring()

if resultado['sucesso']:
    # Acessar DataFrame XLSX globalmente enriquecido
    xlsx_enriched = resultado['xlsx_enriched']
    
    print(f"📊 DADOS ENRIQUECIDOS:")
    print(f"   Total de registros: {len(xlsx_enriched):,}")
    print(f"   Colunas originais: 16")
    print(f"   Colunas totais: {len(xlsx_enriched.columns)}")
    
    # Verificar campos adicionados
    campos_novos = []
    if 'dias_atraso' in xlsx_enriched.columns:
        campos_novos.append('dias_atraso')
    if 'grupo_de_risco' in xlsx_enriched.columns:
        campos_novos.append('grupo_de_risco')
    
    print(f"   Campos adicionados: {campos_novos}")
    
    # Análise rápida de dias de atraso
    if 'dias_atraso' in xlsx_enriched.columns:
        max_atraso = xlsx_enriched['dias_atraso'].max()
        atrasados = len(xlsx_enriched[xlsx_enriched['dias_atraso'] > 0])
        print(f"   📈 Máximo atraso: {max_atraso} dias")
        print(f"   📉 Títulos atrasados: {atrasados:,}")
    
    # Análise de grupos de risco
    if 'grupo_de_risco' in xlsx_enriched.columns:
        grupos = xlsx_enriched['grupo_de_risco'].value_counts()
        print(f"   🎯 Distribuição por grupo de risco:")
        for grupo, count in grupos.head().items():
            print(f"      {grupo}: {count:,} títulos")
```

## 🆕 6. Análise Sequencial de Capacidade (2025-07-15)

### Monitor de Concentração v2.1
```python
from monitor.orchestrator import run_monitoring

# Executar monitoramento com análise sequencial automática
resultado = run_monitoring(pool_name="UnionNational Pool #5")

if resultado['sucesso']:
    # Acessar resultados do monitor de concentração
    for pool_resultado in resultado['resultados']:
        if pool_resultado['pool_id'] == "UnionNational Pool #5":
            monitor_concentracao = None
            
            # Encontrar monitor de concentração
            for monitor in pool_resultado['monitores']:
                if monitor['tipo'] == 'concentracao':
                    monitor_concentracao = monitor
                    break
            
            if monitor_concentracao and 'analises_capacidade' in monitor_concentracao:
                print(f"\n🎯 ANÁLISE SEQUENCIAL DE CAPACIDADE")
                
                # Análise para sacados
                if 'sacado' in monitor_concentracao['analises_capacidade']:
                    analise_sacado = monitor_concentracao['analises_capacidade']['sacado']
                    resumo = analise_sacado['resumo']
                    
                    print(f"\n📊 RESUMO SACADOS:")
                    print(f"   PL Pool: R$ {resumo['pl_pool']:,.0f}")
                    print(f"   Limite Individual: {resumo['limite_individual_pct']:.1f}%")
                    print(f"   Limite Top-{resumo['top_n_size']}: {resumo['limite_top_n_pct']:.1f}%")
                    print(f"   Exposição Atual: {resumo['percentual_top_n_atual']:.1f}%")
                    print(f"   Espaço Disponível: {resumo['espaco_total_disponivel']:,.0f}")
                    
                    print(f"\n🔄 ANÁLISE SEQUENCIAL:")
                    for item in analise_sacado['analise_sequencial']:
                        print(f"   Posição {item['posicao']}: {item['entidade']}")
                        print(f"      Atual: R$ {item['exposicao_atual']:,.0f} ({item['percentual_atual']:.1f}%)")
                        print(f"      Pode crescer: R$ {item['capacidade_efetiva']:,.0f}")
                        print(f"      Saldo após: R$ {item['saldo_apos']:,.0f}")
                        print(f"      Limitado por: {item['limitada_por']}")
                        print(f"      📝 {item['explicacao']}")
                        print()
                
                # Análise para cedentes
                if 'cedente' in monitor_concentracao['analises_capacidade']:
                    analise_cedente = monitor_concentracao['analises_capacidade']['cedente']
                    print(f"\n💼 ANÁLISE CEDENTES DISPONÍVEL")
```

### 🆕 Matriz de Sobra Tabular (2025-07-16)
```python
def visualizar_matriz_sobra(pool_name):
    """Visualização da matriz de sobra com tabela ASCII formatada."""
    resultado = run_monitoring(pool_name=pool_name)
    
    if not resultado['sucesso']:
        print(f"❌ Erro ao processar {pool_name}")
        return
    
    # Buscar análise de capacidade com matriz de sobra
    for pool_resultado in resultado['resultados']:
        if pool_resultado['pool_id'] == pool_name:
            for monitor in pool_resultado['monitores']:
                if monitor['tipo'] == 'concentracao' and 'analises_capacidade' in monitor:
                    analise = monitor['analises_capacidade'].get('sacado')
                    if analise and 'matriz_sobra' in analise:
                        matriz = analise['matriz_sobra']
                        
                        print(f"\n🎯 MATRIZ DE SOBRA - {pool_name}")
                        print("=" * 60)
                        
                        # Cabeçalho da matriz
                        print(f"📊 {matriz['cabecalho']['titulo']}")
                        print(f"   PL: {matriz['cabecalho']['pl_pool']:,.0f}")
                        print(f"   Limite Individual: {matriz['cabecalho']['limite_individual']}")
                        print(f"   Limite Top-N: {matriz['cabecalho']['limite_top_n']}")
                        print(f"   Espaço Disponível: {matriz['cabecalho']['espaco_disponivel']:,.0f}")
                        print()
                        
                        # Tabela ASCII formatada
                        print(matriz['tabela_ascii'])
                        
                        return matriz
    
    print(f"⚠️ Matriz de sobra não disponível para {pool_name}")
    return None

# Exemplo de uso
if __name__ == "__main__":
    visualizar_matriz_sobra("UnionNational Pool #5")
```

**Exemplo de Saída:**
```
🎯 MATRIZ DE SOBRA - UnionNational Pool #5
============================================================
📊 MATRIZ DE SOBRA - ANÁLISE SEQUENCIAL
   PL: 8,500,000
   Limite Individual: 27.0%
   Limite Top-N: 100.0%
   Espaço Disponível: 1,275,000

┌──────────────┬────────┬──────────┬─────────────┬─────────────┬───────────────┐
│Entidade      │Atual   │Cap.Indiv │Cap.Efetiva  │Saldo Antes  │Limitado Por   │
├──────────────┼────────┼──────────┼─────────────┼─────────────┼───────────────┤
│Empresa ABC   │1200000 │+1095000  │+1095000     │1275000      │individual     │
│Empresa XYZ   │800000  │+1495000  │+180000      │180000       │top_n          │
│Empresa DEF   │600000  │+1695000  │+0           │0            │esgotado       │
└──────────────┴────────┴──────────┴─────────────┴─────────────┴───────────────┘
```

### Casos de Uso Práticos
```python
def analisar_capacidade_originacao(pool_name):
    """Exemplo de uso para gestão de originação."""
    resultado = run_monitoring(pool_name=pool_name)
    
    if not resultado['sucesso']:
        print(f"❌ Erro ao processar {pool_name}")
        return
    
    # Buscar análise de capacidade
    for pool_resultado in resultado['resultados']:
        if pool_resultado['pool_id'] == pool_name:
            for monitor in pool_resultado['monitores']:
                if monitor['tipo'] == 'concentracao' and 'analises_capacidade' in monitor:
                    analise = monitor['analises_capacidade'].get('sacado')
                    if analise:
                        print(f"\n🎯 CAPACIDADE DE ORIGINAÇÃO - {pool_name}")
                        
                        # Prioridades de originação
                        for item in analise['analise_sequencial']:
                            if item['capacidade_efetiva'] > 0:
                                print(f"✅ {item['entidade']}: "
                                      f"Pode originar até R$ {item['capacidade_efetiva']:,.0f}")
                            else:
                                print(f"❌ {item['entidade']}: Sem capacidade restante")
                        
                        # Mostrar matriz de sobra se disponível
                        if 'matriz_sobra' in analise:
                            print(f"\n📊 MATRIZ DE SOBRA DISPONÍVEL")
                            print(f"   Use visualizar_matriz_sobra('{pool_name}') para ver tabela formatada")
                        
                        return analise
    
    print(f"⚠️ Análise de capacidade não disponível para {pool_name}")
    return None

# Exemplo de uso
if __name__ == "__main__":
    analisar_capacidade_originacao("UnionNational Pool #5")
```

### 🔽 Filtro de Entidades Ignoradas (2025-07-16)
```python
def monitorar_com_filtro_entidades(pool_name):
    """Exemplo de monitoramento com filtro automático de entidades."""
    resultado = run_monitoring(pool_name=pool_name)
    
    if not resultado['sucesso']:
        print(f"❌ Erro ao processar {pool_name}")
        return
    
    # Buscar resultados de concentração
    for pool_resultado in resultado['resultados']:
        if pool_resultado['pool_id'] == pool_name:
            for monitor in pool_resultado['monitores']:
                if monitor['tipo'] == 'concentracao':
                    print(f"\n🔽 FILTRO AUTOMÁTICO APLICADO - {pool_name}")
                    print("   Entidades ignoradas: Amfi Digital Assets LTDA")
                    print("   Configuração: /config/monitoring/concentration_filters.json")
                    
                    # Mostrar resultados de concentração
                    for resultado_limite in monitor['resultados_por_limite']:
                        tipo = resultado_limite['tipo']
                        entidade = resultado_limite['entidade']
                        
                        if tipo == 'individual':
                            maior = resultado_limite['maior_concentracao']
                            print(f"   📊 Individual {entidade}: {maior['entidade']} ({maior['percentual_pl']:.1f}%)")
                        elif tipo == 'top_n':
                            n = resultado_limite['n']
                            concentracao = resultado_limite['concentracao_top_n']
                            print(f"   📊 Top-{n} {entidade}: {concentracao['percentual_pl']:.1f}%")
                    
                    # Verificar se houve filtros aplicados no log
                    print(f"   💬 Verifique logs para detalhes sobre registros filtrados")
                    
                    return monitor
    
    print(f"⚠️ Monitor de concentração não encontrado para {pool_name}")
    return None

# Exemplo de uso
if __name__ == "__main__":
    monitorar_com_filtro_entidades("UnionNational Pool #5")
```

**Saída Esperada:**
```
🔽 Concentração cedente: 5 registros filtrados (entidades ignoradas)
🔽 Concentração sacado: 3 registros filtrados (entidades ignoradas)

🔽 FILTRO AUTOMÁTICO APLICADO - UnionNational Pool #5
   Entidades ignoradas: Amfi Digital Assets LTDA
   Configuração: /config/monitoring/concentration_filters.json
   📊 Individual sacado: Empresa ABC (14.1%)
   📊 Top-10 cedente: 67.5%
   💬 Verifique logs para detalhes sobre registros filtrados
```

## 🏗️ **NOVO: Usando BaseMonitor para Monitores Customizados (2025-07-17)**

### **Criando Monitor Customizado com BaseMonitor**

```python
from monitor.core.base_monitor import BaseMonitor

class MonitorVencimentoMedio(BaseMonitor):
    def get_monitor_type(self):
        return 'vencimento_medio'
    
    def calculate(self):
        # Acessar dados do pool automaticamente
        pool_data = self._get_pool_data()
        
        # Buscar configurações específicas
        limite_maximo = self._get_config_value('limite_maximo_dias', 90)
        
        # Usar dados XLSX se disponível
        if self.xlsx_data is not None:
            # Calcular vencimento médio ponderado
            carteira = self.xlsx_data[self.xlsx_data['pool'] == self.pool_id]
            
            # Calcular dias até vencimento
            carteira['dias_vencimento'] = (
                pd.to_datetime(carteira['vencimento_original']) - pd.Timestamp.now()
            ).dt.days
            
            # Vencimento médio ponderado por valor
            vencimento_medio = (
                carteira['dias_vencimento'] * carteira['valor_presente']
            ).sum() / carteira['valor_presente'].sum()
            
            # Verificar conformidade
            status = 'enquadrado' if vencimento_medio <= limite_maximo else 'violado'
            
            return {
                'vencimento_medio_dias': round(vencimento_medio, 1),
                'limite_maximo_dias': limite_maximo,
                'status': status,
                'quantidade_titulos': len(carteira),
                'valor_total_carteira': carteira['valor_presente'].sum()
            }
        else:
            # Fallback se não houver dados XLSX
            self._log('warning', 'Dados XLSX não disponíveis para cálculo detalhado')
            return {
                'erro': 'Dados XLSX necessários para cálculo de vencimento médio'
            }

# Configuração no JSON do pool
json_config = {
    "monitoramentos_ativos": [
        {
            "id": "vencimento_medio",
            "tipo": "vencimento_medio", 
            "ativo": True,
            "limite_maximo_dias": 85,
            "descricao": "Prazo médio ponderado da carteira"
        }
    ]
}

# Uso do monitor
monitor = MonitorVencimentoMedio(
    pool_id="AFA Pool #1",
    config=json_config,
    csv_data=csv_data,
    xlsx_data=xlsx_data
)

# Execução automática com validação e logging
result = monitor.run()

if result.is_success():
    print(f"✅ Vencimento médio: {result.data['vencimento_medio_dias']} dias")
    print(f"📊 Status: {result.data['status']}")
else:
    print(f"❌ Erro: {result.metadata['error']}")
```

### **Integração Automática com Orchestrator**

```python
# 1. Registrar o monitor no orchestrator
# Em orchestrator.py, adicionar:
def _execute_vencimento_medio_monitoring():
    """Executa monitor de vencimento médio se configurado."""
    from monitor.custom.monitor_vencimento_medio import MonitorVencimentoMedio
    
    monitor = MonitorVencimentoMedio(pool_id, config, csv_data, xlsx_data)
    if monitor.is_active():
        return monitor.run().to_dict()
    return None

# 2. Usar via run_monitoring() automaticamente
resultado = run_monitoring("AFA Pool #1")

# 3. Acessar resultado do novo monitor
if resultado['sucesso']:
    vencimento_result = resultado['resultados']['AFA Pool #1']['resultados']['vencimento_medio']
    print(f"Vencimento médio: {vencimento_result['vencimento_medio_dias']} dias")
```

### **Vantagens do BaseMonitor**

✅ **Validação Automática**: Dados são validados automaticamente  
✅ **Logging Integrado**: Sistema de logs padronizado  
✅ **Tratamento de Erros**: Handling robusto de exceções  
✅ **Compatibilidade**: Funciona com run_monitoring() automaticamente  
✅ **Testabilidade**: Framework de testes já configurado  
✅ **Performance**: Otimizações automáticas aplicadas  

### **Template para Novos Monitores**

```python
from monitor.core.base_monitor import BaseMonitor

class MeuNovoMonitor(BaseMonitor):
    def get_monitor_type(self):
        return 'meu_monitor'  # ID único do monitor
    
    def calculate(self):
        """Implementa apenas a lógica específica do monitor."""
        
        # 1. Obter dados já validados
        pool_data = self._get_pool_data()
        
        # 2. Buscar configurações específicas  
        limite = self._get_config_value('limite', 0.05)
        
        # 3. Sua lógica de cálculo aqui
        valor_calculado = self._minha_logica(pool_data)
        
        # 4. Retornar resultado estruturado
        return {
            'valor_calculado': valor_calculado,
            'limite_configurado': limite,
            'status': 'enquadrado' if valor_calculado <= limite else 'violado'
        }
    
    def _minha_logica(self, pool_data):
        """Implementa cálculo específico."""
        # Sua implementação aqui
        return resultado
```

## 🧪 **NOVO: Executando Testes (Framework Implementado)**

### **Executar Todos os Testes**
```bash
# No diretório raiz do projeto
pytest

# Com cobertura detalhada
pytest --cov=monitor --cov-report=html

# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration
```

### **Testes Específicos**
```bash
# Testar sistema de imports
pytest tests/test_core_imports.py -v

# Testar classe base de monitores
pytest tests/test_base_monitor.py -v

# Testar orchestrator
pytest tests/test_orchestrator.py -v
```

### **Usando Fixtures de Teste**
```python
# Em novos arquivos de teste, usar fixtures existentes
import pytest

def test_meu_monitor(sample_csv_data, sample_pool_config):
    """Teste usando fixtures padronizadas."""
    # Usar dados de teste consistentes
    assert len(sample_csv_data) == 3
    assert 'AFA Pool #1' in sample_csv_data['nome'].values
    
    # Usar configuração de teste padrão
    assert sample_pool_config['pool_id'] == 'AFA Pool #1'
    assert len(sample_pool_config['monitoramentos_ativos']) == 3

def test_concentracao_scenarios(sample_concentration_data):
    """Teste com dados de concentração específicos."""
    # Dados já preparados para cenários de concentração
    total_value = sample_concentration_data['valor_presente'].sum()
    assert total_value == 4000000  # Cenário controlado
```

### **Criando Novos Testes**
```python
# Template para novos testes
import pytest
from monitor.core.base_monitor import BaseMonitor

class TestMeuNovoMonitor:
    """Testes para MeuNovoMonitor."""
    
    def test_initialization(self, sample_csv_data, sample_pool_config):
        """Teste de inicialização."""
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        assert monitor.pool_id == 'AFA Pool #1'
        assert monitor.is_active() == True  # Se configurado
    
    def test_calculation_logic(self, sample_csv_data, sample_pool_config):
        """Teste da lógica de cálculo."""
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, sample_csv_data)
        result = monitor.calculate()
        
        assert 'resultado' in result
        assert isinstance(result['resultado'], (int, float))
    
    def test_error_handling(self, sample_pool_config):
        """Teste de tratamento de erro."""
        empty_csv = pd.DataFrame()
        monitor = MeuNovoMonitor('AFA Pool #1', sample_pool_config, empty_csv)
        
        result = monitor.run()
        assert result.status == 'error'
        assert 'validation failed' in result.metadata['reason'].lower()
```

**Personalização do Filtro:**
```json
// Editar /config/monitoring/concentration_filters.json
{
  "entidades_ignoradas": {
    "cedentes": ["Amfi Digital Assets LTDA", "Outra Entidade"],
    "sacados": ["Amfi Digital Assets LTDA"]
  },
  "configuracoes_adicionais": {
    "case_sensitive": false,
    "normalize_names": true,
    "partial_match": false
  }
}
```

## 7. Configuração de Modo Debug

### Arquivo test_pools.json
```json
{
  "metadata": {
    "description": "Configuração de debug para sistema de monitoramento",
    "version": "2.0"
  },
  "debug_pools": [
    "AFA Pool #1",
    "LeCapital Pool #1"
  ],
  "monitor": [
    "concentracao_sacados",
    "indice_subordinacao",
    "inadimplencia"
  ]
}
```

### Uso do Modo Debug
```python
# Se test_pools.json existir, processa apenas pools listados
resultado = run_monitoring()  # Processa apenas AFA e LeCapital

# Para forçar um pool específico (ignora test_pools.json)
resultado = run_monitoring("Outro Pool #3")
```

## 7. Comparação de Resultados Entre Pools

```python
def comparar_subordinacao_pools():
    """Compara índices de subordinação entre pools."""
    
    resultado = run_monitoring()
    
    if not resultado['sucesso']:
        return
    
    subordinacoes = []
    
    for pool_name, pool_result in resultado['resultados'].items():
        if pool_result.get('sucesso'):
            sub_result = pool_result['resultados'].get('subordinacao', {})
            if 'subordination_ratio_percent' in sub_result:
                sr = sub_result['subordination_ratio_percent']
                limite = sub_result.get('limite_minimo', 0) * 100
                status = sub_result.get('status_limite_minimo', 'N/A')
                
                subordinacoes.append({
                    'pool': pool_name,
                    'sr': sr,
                    'limite': limite,
                    'status': status,
                    'margem': sr - limite
                })
    
    # Ordenar por subordinação (menor para maior - mais crítico primeiro)
    subordinacoes.sort(key=lambda x: x['sr'])
    
    print("📊 RANKING DE SUBORDINAÇÃO (MAIS CRÍTICO PRIMEIRO):")
    print("=" * 80)
    
    for i, dados in enumerate(subordinacoes, 1):
        pool = dados['pool']
        sr = dados['sr']
        limite = dados['limite']
        status = dados['status']
        margem = dados['margem']
        
        status_icon = "🚨" if status == 'violado' else "✅"
        
        print(f"{i:2d}. {status_icon} {pool}")
        print(f"     SR: {sr:5.1f}% | Limite: {limite:5.1f}% | Margem: {margem:+5.1f}%")
        print()

# Executar comparação
comparar_subordinacao_pools()
```

## 8. Analisando Resultados de PDD (Provisão para Devedores Duvidosos)

```python
def analisar_pdd_detalhado(pool_name):
    """Análise detalhada de PDD para um pool específico."""
    
    resultado = run_monitoring(pool_name)
    
    if not resultado['sucesso']:
        print(f"❌ Erro ao processar {pool_name}")
        return
    
    pool_result = resultado['resultados'][pool_name]
    
    if 'pdd' not in pool_result['resultados']:
        print(f"ℹ️ Pool {pool_name} não possui monitor PDD configurado")
        return
    
    pdd_result = pool_result['resultados']['pdd']
    
    if not pdd_result.get('sucesso'):
        print(f"❌ Erro no monitor PDD: {pdd_result.get('erro')}")
        return
    
    pdd_analysis = pdd_result['pdd_analysis']
    
    print(f"💰 PDD - {pool_name}")
    print("=" * 50)
    
    # Totais consolidados
    totais = pdd_analysis['totais']
    print(f"📊 TOTAIS:")
    print(f"   Carteira Total: R$ {totais['carteira_valor']:,.2f}")
    print(f"   Provisão Total: R$ {totais['provisao_valor']:,.2f}")
    print(f"   Provisão %: {totais['provisao_percentual']}%")
    
    # Análise por grupo de risco
    print(f"\n🎯 ANÁLISE POR GRUPO DE RISCO:")
    grupos = pdd_analysis['grupos']
    
    for grupo in sorted(grupos.keys()):
        dados = grupos[grupo]
        if dados['quantidade'] > 0:  # Apenas grupos com exposição
            print(f"   📈 Grupo {grupo}:")
            print(f"      Títulos: {dados['quantidade']:,}")
            print(f"      Valor: R$ {dados['valor_total']:,.2f}")
            print(f"      Provisão %: {dados['provisao_pct']}%")
            print(f"      Provisão R$: R$ {dados['provisao_valor']:,.2f}")
            print(f"      Atraso máx: {dados['atraso_max_dias']} dias")
    
    # Estatísticas complementares
    if 'estatisticas' in pdd_analysis:
        stats = pdd_analysis['estatisticas']
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total de títulos: {stats['titulos_total']:,}")
        print(f"   Títulos c/ provisão: {stats['titulos_com_provisao']:,}")
        print(f"   Grupo modal: {stats['grupo_risco_modal']}")
        print(f"   Provisão média: R$ {stats['provisao_media_por_titulo']:,.2f}/título")

# Executar análise
analisar_pdd_detalhado("LeCapital Pool #1")
```

## 9. Dashboard Executivo - Visão Consolidada

```python
def dashboard_executivo():
    """Dashboard executivo com visão consolidada de todos os monitores."""
    
    resultado = run_monitoring()
    
    if not resultado['sucesso']:
        print(f"❌ Falha crítica: {resultado.get('erro')}")
        return
    
    print("📊 DASHBOARD EXECUTIVO - AmFi Monitoring")
    print("=" * 60)
    
    stats = resultado['estatisticas']
    print(f"🎯 RESUMO GERAL:")
    print(f"   Pools processados: {stats['total']}")
    print(f"   Taxa de sucesso: {stats['taxa_sucesso']}%")
    
    # Análise por pool
    violacoes_totais = 0
    provisoes_totais = 0
    
    for pool_name, pool_result in resultado['resultados'].items():
        if not pool_result.get('sucesso'):
            continue
            
        print(f"\n🏦 {pool_name}:")
        monitores = pool_result.get('monitores_executados', [])
        print(f"   Monitores: {', '.join(monitores)}")
        
        resultados = pool_result.get('resultados', {})
        
        # Subordinação
        if 'subordinacao' in resultados:
            sub = resultados['subordinacao']
            sr = sub.get('subordination_ratio_percent', 0)
            status = sub.get('status_limite_minimo', 'N/A')
            emoji = "🟢" if status == "enquadrado" else "🔴"
            print(f"   {emoji} Subordinação: {sr}% ({status})")
            if status == "violado":
                violacoes_totais += 1
        
        # Inadimplência
        if 'inadimplencia' in resultados:
            inad = resultados['inadimplencia']
            if 'resultados' in inad:
                for janela, dados in inad['resultados'].items():
                    perc = dados.get('inadimplencia_percent', 0)
                    status = dados.get('status', 'N/A')
                    emoji = "🟢" if status == "enquadrado" else "🔴"
                    janela_nome = janela.replace('inadimplencia_', '').replace('d', ' dias')
                    print(f"   {emoji} Inadimpl. {janela_nome}: {perc}% ({status})")
                    if status == "violado":
                        violacoes_totais += 1
        
        # PDD
        if 'pdd' in resultados:
            pdd = resultados['pdd']
            if pdd.get('sucesso') and 'pdd_analysis' in pdd:
                totais = pdd['pdd_analysis']['totais']
                provisao_valor = totais.get('provisao_valor', 0)
                provisao_perc = totais.get('provisao_percentual', 0)
                print(f"   💰 PDD: R$ {provisao_valor:,.2f} ({provisao_perc}%)")
                provisoes_totais += provisao_valor
    
    # Resumo final
    print(f"\n📈 RESUMO FINAL:")
    print(f"   🚨 Total de violações: {violacoes_totais}")
    print(f"   💰 Provisões totais: R$ {provisoes_totais:,.2f}")
    
    # Acesso aos dados enriquecidos
    xlsx_enriched = resultado['xlsx_enriched']
    print(f"   📊 Registros enriquecidos: {len(xlsx_enriched):,}")

# Executar dashboard
dashboard_executivo()
```

## Compatibilidade

A função `run_monitoring()` funciona em todos os ambientes:

- ✅ **Windows**: `C:\amfi\...`
- ✅ **WSL**: `/mnt/c/amfi/...`
- ✅ **Spyder**: Descoberta automática de caminhos
- ✅ **Linha de comando**: Python direto
- ✅ **Jupyter**: Notebooks compatíveis

## Observações Importantes

1. **Interface única**: `run_monitoring()` é a única função oficial
2. **Funções legacy removidas**: Não use funções antigas do orchestrator
3. **Enriquecimento automático**: DataFrame XLSX é automaticamente enriquecido
4. **Modo debug**: Use `test_pools.json` para limitar pools processados
5. **Tratamento robusto**: Falha de um pool não para a execução dos outros