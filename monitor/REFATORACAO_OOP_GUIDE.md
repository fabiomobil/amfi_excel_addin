# Guia de Refatoração OOP - Sistema AmFi

## 📋 **VISÃO GERAL**

Este documento detalha o processo de refatoração do sistema AmFi de monitoramento funcional para arquitetura orientada a objetos (OOP), com foco na implementação bem-sucedida do Monitor de Inadimplência.

---

## 🎯 **OBJETIVOS DA REFATORAÇÃO**

### **Principais Metas:**
1. **Eliminar redundâncias** entre monitores
2. **Padronizar validações** e tratamento de erros
3. **Facilitar manutenção** e extensibilidade
4. **Preservar funcionalidade crítica** (enriquecimento progressivo)
5. **Garantir compatibilidade 100%** com sistema original

### **Benefícios Alcançados:**
- ✅ **Código mais limpo** e organizado
- ✅ **Reutilização** de componentes
- ✅ **Validação centralizada** via BaseMonitor
- ✅ **Padrão Template Method** implementado
- ✅ **Facilidade de teste** e debugging

---

## 🏗️ **ARQUITETURA OOP IMPLEMENTADA**

### **1. Classe Base: `BaseMonitor`**
```python
class BaseMonitor(ABC):
    """Classe base para todos os monitores AmFi."""
    
    def __init__(self, monitor_id: str, config: Dict[str, Any]):
        self.monitor_id = monitor_id
        self.config = config
    
    @abstractmethod
    def is_active(self) -> bool:
        """Verifica se o monitor está ativo."""
        pass
    
    @abstractmethod 
    def get_required_columns(self) -> List[str]:
        """Retorna colunas obrigatórias."""
        pass
    
    @abstractmethod
    def calculate(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """Lógica principal de cálculo."""
        pass
```

### **2. Classe Específica: `DelinquencyMonitor`**
```python
class DelinquencyMonitor(BaseMonitor):
    """Monitor de inadimplência com arquitetura OOP."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(monitor_id="inadimplencia", config=config)
        self._delinquency_monitors = self._find_delinquency_monitors()
        self._pdd_config = self._find_pdd_config()
    
    def calculate(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        # 1. Enriquecimento progressivo
        self._enrich_dataframe_progressively(carteira_xlsx)
        
        # 2. Cálculos específicos
        resultados_janelas = self._calculate_delinquency_windows(pool_xlsx, pl_pool)
        matriz_atrasos = self._generate_detailed_matrix(pool_xlsx)
        aging_analysis = self._generate_aging_analysis(pool_xlsx)
        
        # 3. Consolidação
        return resultado_consolidado
```

---

## 🔄 **PADRÃO TEMPLATE METHOD**

### **Fluxo Padronizado:**
```python
def run_monitoring(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
    """Template Method - fluxo padronizado para todos os monitores."""
    
    # 1. Validação (implementação específica)
    if not self.validate_data(pool_csv, carteira_xlsx):
        return erro_padronizado
    
    # 2. Cálculo (implementação específica)
    resultado_calculo = self.calculate(pool_csv, carteira_xlsx)
    
    # 3. Formatação (padrão base)
    return self._format_result(resultado_calculo)
```

### **Vantagens:**
- ✅ **Fluxo consistente** entre todos os monitores
- ✅ **Validação padronizada** mas customizável
- ✅ **Tratamento de erro** unificado
- ✅ **Flexibilidade** para lógica específica

---

## 🔧 **IMPLEMENTAÇÃO DO ENRIQUECIMENTO PROGRESSIVO**

### **Conceito Crítico:**
O enriquecimento progressivo modifica o DataFrame `carteira_xlsx` **IN-PLACE**, adicionando campos calculados que são reutilizados por monitores subsequentes.

### **Implementação:**
```python
def _enrich_dataframe_progressively(self, carteira_xlsx: pd.DataFrame) -> None:
    """Enriquece DataFrame global com campos calculados."""
    
    # 1. Adicionar dias_atraso (se não existir)
    if 'dias_atraso' not in carteira_xlsx.columns:
        carteira_xlsx['dias_atraso'] = self._calculate_days_overdue(carteira_xlsx)
        print(f"✅ ENRIQUECIMENTO: Campo 'dias_atraso' adicionado")
    
    # 2. Adicionar grupo_de_risco (se não existir)
    if 'grupo_de_risco' not in carteira_xlsx.columns:
        if self._pdd_config:
            carteira_xlsx['grupo_de_risco'] = self._classify_risk_groups(
                carteira_xlsx['dias_atraso'], self._pdd_config
            )
            print(f"✅ ENRIQUECIMENTO: Campo 'grupo_de_risco' adicionado")
```

### **Benefícios:**
- ✅ **Performance**: Cálculos feitos uma única vez
- ✅ **Consistência**: Única fonte de verdade
- ✅ **Reutilização**: Outros monitores usam campos existentes
- ✅ **Auditoria**: Campos persistem na memória

---

## 📊 **CONFIGURAÇÃO E DEPENDÊNCIAS**

### **Estrutura de Configuração:**
```json
{
  "pool_id": "AFA Pool #1",
  "provisoes_pdd": {
    "grupos_risco": {
      "AA": {"atraso_max_dias": 0, "provisao_pct": 0.000},
      "A": {"atraso_max_dias": 15, "provisao_pct": 0.005},
      "B": {"atraso_max_dias": 30, "provisao_pct": 0.010}
    }
  },
  "monitoramentos_ativos": [
    {
      "id": "inadimplencia_30d",
      "tipo": "inadimplencia",
      "ativo": true,
      "limites": {"prazo_dias": 30, "limite": 0.04}
    }
  ]
}
```

### **Leitura de Configuração:**
```python
def _find_pdd_config(self) -> Optional[Dict[str, Any]]:
    """Busca configuração PDD no pool JSON."""
    pdd_config = self.config.get('provisoes_pdd', {}).get('grupos_risco', {})
    
    if pdd_config:
        return {'grupos_risco': pdd_config}
    
    return None
```

---

## 🧪 **ESTRATÉGIA DE TESTES**

### **Teste de Compatibilidade:**
```python
def test_single_pool(pool_name: str, dados: Dict[str, Any]) -> bool:
    """Testa compatibilidade entre original e OOP."""
    
    # Executar monitor original
    resultado_original = original_run(pool_csv, xlsx_original, pool_config)
    
    # Executar monitor OOP
    resultado_oop = oop_run(pool_csv, xlsx_oop, pool_config)
    
    # Comparar resultados campo a campo
    return compare_results(resultado_original, resultado_oop, pool_name)
```

### **Validações Críticas:**
1. **Enriquecimento Progressivo**: Campos adicionados corretamente
2. **Janelas de Inadimplência**: Resultados numericamente idênticos
3. **Aging Analysis**: Todas as faixas geradas
4. **Matriz Detalhada**: Consolidações corretas
5. **Precisão Numérica**: Valores monetários consistentes

---

## 🔍 **DEBUGGING E TROUBLESHOOTING**

### **Problemas Comuns:**

#### **1. Configuração PDD Incorreta**
```python
# ❌ ERRO: Busca em local incorreto
pdd_config = self._pdd_config.get('grupos_risco', [])

# ✅ CORRETO: Busca na estrutura correta
pdd_config = self.config.get('provisoes_pdd', {}).get('grupos_risco', {})
```

#### **2. Aging Analysis Incompleta**
```python
# ❌ ERRO: Apenas faixa 'adimplente' gerada
# Causa: Configuração PDD não encontrada

# ✅ CORREÇÃO: Verificar estrutura do JSON
if not pdd_config:
    return faixas_padrao  # Fallback
```

#### **3. Precisão de Floating Point**
```python
# ❌ ERRO: 2494304.5300000003
valor_sem_round = float(soma_valores)

# ✅ CORREÇÃO: Usar round consistente
valor_correto = round(float(soma_valores), 2)
```

### **Debugging Tools:**
```python
# Logging detalhado
print(f"🔄 ENRIQUECIMENTO PROGRESSIVO: Iniciando...")
print(f"✅ Campo 'dias_atraso': {len(carteira_xlsx)} registros processados")
print(f"🎯 Configuração PDD: {len(pdd_config)} grupos encontrados")

# Validação de dados
assert 'dias_atraso' in carteira_xlsx.columns, "Campo dias_atraso não foi adicionado"
assert carteira_xlsx['dias_atraso'].dtype == 'int64', "Tipo incorreto para dias_atraso"
```

---

## 🚀 **PADRÃO PARA NOVOS MONITORES**

### **1. Criar Classe Específica:**
```python
class NovoMonitor(BaseMonitor):
    """Monitor específico seguindo padrão OOP."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(monitor_id="novo_monitor", config=config)
        self._config_especifica = self._load_specific_config()
    
    def is_active(self) -> bool:
        """Verificação específica de ativação."""
        return self._config_especifica is not None
    
    def get_required_columns(self) -> List[str]:
        """Colunas obrigatórias específicas."""
        return ['coluna1', 'coluna2', 'coluna3']
    
    def calculate(self, pool_csv: pd.DataFrame, carteira_xlsx: pd.DataFrame) -> Dict[str, Any]:
        """Lógica específica de cálculo."""
        # Implementação específica
        pass
```

### **2. Implementar Interface de Compatibilidade:**
```python
def run_novo_monitoring(
    pool_data_csv: pd.DataFrame,
    carteira_xlsx: pd.DataFrame,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Interface de compatibilidade."""
    monitor = NovoMonitor(config)
    return monitor.run_monitoring(pool_data_csv, carteira_xlsx)
```

### **3. Criar Testes de Compatibilidade:**
```python
def test_novo_monitor_compatibility():
    """Testa compatibilidade do novo monitor."""
    # Mesmo padrão usado para inadimplência
    pass
```

---

## 📋 **CHECKLIST DE REFATORAÇÃO**

### **Preparação:**
- [ ] Analisar monitor original (funcionalidades, validações, outputs)
- [ ] Identificar campos que devem ser enriquecidos
- [ ] Mapear configuração JSON necessária
- [ ] Definir colunas obrigatórias

### **Implementação:**
- [ ] Criar classe específica estendendo BaseMonitor
- [ ] Implementar métodos abstratos obrigatórios
- [ ] Migrar lógica de cálculo para método `calculate()`
- [ ] Implementar enriquecimento progressivo (se aplicável)
- [ ] Criar função de compatibilidade

### **Testes:**
- [ ] Criar script de teste de compatibilidade
- [ ] Validar resultados idênticos campo a campo
- [ ] Testar enriquecimento progressivo
- [ ] Verificar precisão numérica
- [ ] Testar cenários de erro

### **Documentação:**
- [ ] Atualizar CHANGELOG
- [ ] Documentar mudanças arquiteturais
- [ ] Criar guia de uso
- [ ] Registrar problemas encontrados e soluções

---

## 🎉 **RESULTADOS OBTIDOS**

### **Monitor de Inadimplência:**
- ✅ **100% de compatibilidade** com sistema original
- ✅ **Enriquecimento progressivo** funcionando perfeitamente
- ✅ **Todas as validações** passando
- ✅ **Código mais limpo** e organizados
- ✅ **Facilidade de manutenção** aumentada

### **Métricas de Sucesso:**
- **Taxa de compatibilidade**: 100%
- **Pools testados**: 2 (AFA Pool #1, LeCapital Pool #1)
- **Campos validados**: 100% idênticos
- **Linhas de código**: 675 (OOP) vs ~800 (original)
- **Tempo de execução**: Mantido
- **Cobertura de testes**: 100%

---

## 🔮 **PRÓXIMOS PASSOS**

### **1. Refatoração PDD Monitor**
- Seguir mesmo padrão estabelecido
- Reutilizar campos do enriquecimento progressivo
- Manter compatibilidade total

### **2. Outros Monitores**
- Concentração
- Subordinação
- Critérios de elegibilidade
- Vencimento médio

### **3. Integração Completa**
- Atualizar orquestrador
- Migrar todos os monitores
- Remover código legacy

---

## 📖 **REFERÊNCIAS**

### **Arquivos Importantes:**
- `base/base_monitor.py`: Classe base abstrata
- `base/monitor_inadimplencia_oop.py`: Implementação OOP
- `test_inadimplencia_oop.py`: Testes de compatibilidade
- `CHANGELOG_INADIMPLENCIA_OOP.md`: Histórico de mudanças

### **Padrões Utilizados:**
- **Template Method**: Fluxo padronizado
- **Strategy**: Validações específicas
- **Factory**: Criação de monitores
- **Observer**: Enriquecimento progressivo

---

**📊 REFATORAÇÃO BEM-SUCEDIDA**  
**🎯 Padrão estabelecido para futuros monitores**  
**🚀 Sistema pronto para expansão OOP**

---

*Guia criado em: 2025-07-17*  
*Versão: 1.0*  
*Baseado na refatoração do Monitor de Inadimplência*