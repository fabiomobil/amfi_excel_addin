# Lógica CCB vs PDD - Documentação Técnica

## Resumo Executivo

**Status**: Lógica CCB **NÃO IMPLEMENTADA** no sistema atual
**Impacto**: CCB recebe provisão incorreta (lógica por cedente aplicada)
**Localização**: `/mnt/c/amfi/monitor/base/monitor_pdd.py`

## Diferenças Fundamentais

### Lógica Atual (Por Cedente)
```python
# Sistema atual implementado
def calculate_pdd_by_cedente(cedente_grupo):
    # 1. Encontrar pior ativo do cedente
    pior_grupo = cedente_grupo['grupo_de_risco'].max()
    
    # 2. Aplicar a TODOS os ativos do cedente
    provisao_cedente = pior_grupo.provisao_pct
    
    # 3. Resultado: todos recebem mesma provisão
    return provisao_cedente
```

### Lógica CCB (Por Ativo) - NÃO IMPLEMENTADA
```python
# Lógica que deveria ser implementada para CCB
def calculate_pdd_by_ativo(ativo):
    if ativo.tipo == 'CCB':
        # CCB: provisão individual por ativo
        return ativo.grupo_de_risco.provisao_pct
    else:
        # Outros: lógica por cedente (atual)
        return calculate_pdd_by_cedente(ativo.cedente)
```

## Exemplo Prático

### Cenário: Cedente XYZ com CCBs

**Ativos**:
- CCB A: 0 dias atraso → Grupo AA (0% provisão)
- CCB B: 10 dias atraso → Grupo A (0.5% provisão)
- CCB C: 95 dias atraso → Grupo G (70% provisão)

**Resultado Esperado (CCB)**:
- CCB A: 0% provisão (individual)
- CCB B: 0.5% provisão (individual)
- CCB C: 70% provisão (individual)

**Resultado Atual (Sistema)**:
- CCB A: 70% provisão (pior do cedente)
- CCB B: 70% provisão (pior do cedente)
- CCB C: 70% provisão (correto, mas por acaso)

## Impacto Financeiro

### Superprovisão em CCB Adimplentes
- **CCB A**: R$ 100.000 com 0% → deveria ter R$ 0 provisão
- **Sistema atual**: R$ 100.000 × 70% = R$ 70.000 provisão
- **Erro**: R$ 70.000 superprovisão

### Distorção na Análise de Risco
- Pools com CCB aparecem mais arriscados
- Análise de concentração por cedente distorcida
- Decisões de investimento baseadas em dados incorretos

## Solução Técnica Proposta

### 1. Detecção de Tipo de Ativo
```python
def detect_asset_type(ativo):
    # Implementar lógica de detecção
    if 'CCB' in ativo.tipo_documento:
        return 'CCB'
    return 'OUTROS'
```

### 2. Cálculo Híbrido
```python
def calculate_pdd_hybrid(xlsx_df, config):
    for ativo in xlsx_df.iterrows():
        if detect_asset_type(ativo) == 'CCB':
            # Lógica por ativo
            provisao = ativo.grupo_de_risco.provisao_pct
        else:
            # Lógica por cedente (atual)
            provisao = get_cedente_worst_risk(ativo.cedente)
        
        ativo.provisao_pdd = provisao
```

### 3. Campos Necessários
- `tipo_documento` ou `tipo_ativo` no XLSX
- Identificação clara de CCB vs outros tipos
- Manter compatibilidade com sistema atual

## Workaround Atual

### Para Gestores
1. **Identificar pools com CCB**: Verificar tipo de ativo na carteira
2. **Análise manual**: Calcular provisão CCB separadamente
3. **Ajuste gerencial**: Considerar diferença na análise de risco

### Para Desenvolvedores
1. **Documentação clara**: Limitação documentada em código e docs
2. **Alertas no sistema**: Indicar quando CCB está presente
3. **Preparação para futuro**: Estrutura pronta para implementação

## Critérios de Aceitação (Futura Implementação)

### Detecção Automática
- [ ] Sistema identifica CCB automaticamente
- [ ] Distingue CCB de outros tipos de ativo
- [ ] Mantém compatibilidade com tipos existentes

### Cálculo Correto
- [ ] CCB usa provisão individual por ativo
- [ ] Outros tipos mantêm lógica por cedente
- [ ] Resultados auditáveis e rastreáveis

### Validação
- [ ] Testes unitários para ambas as lógicas
- [ ] Validação contra escrituras CCB
- [ ] Comparação com cálculos manuais

## Arquivos Relacionados

### Código
- `/mnt/c/amfi/monitor/base/monitor_pdd.py` - Lógica PDD atual
- `/mnt/c/amfi/monitor/base/monitor_inadimplencia.py` - Enriquecimento de dados

### Documentação
- `/mnt/c/amfi/docs/CLAUDE.md` - Documentação principal
- `/mnt/c/amfi/docs/PRD.md` - Especificação do produto
- `/mnt/c/amfi/docs/technical/LOGICA_CCB_PDD.md` - Este arquivo

### Configuração
- `/mnt/c/amfi/config/pools/*.json` - Configurações por pool
- Verificar pools com CCB: buscar por `tipo_documento` ou `tipo_ativo`

## Histórico de Mudanças

- **2025-07-15**: Documentação inicial da limitação CCB
- **2025-07-15**: Atualização de CLAUDE.md e PRD.md com limitação
- **2025-07-15**: Adição de comentários no código monitor_pdd.py

## Próximos Passos

1. **Identificar pools com CCB**: Auditoria completa dos 7 pools
2. **Quantificar impacto**: Cálculo da superprovisão atual
3. **Priorizar implementação**: Definir urgência baseada no impacto
4. **Implementar solução**: Desenvolver lógica híbrida quando necessário