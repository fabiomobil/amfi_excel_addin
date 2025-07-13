# Escritura JSON Template - Padrão Ideal para Monitoramento

## Resumo
O arquivo `lecapital_pool_1_monitoring.json` foi selecionado como padrão ideal para configuração de monitoramento de pools. Este documento explica por que sua estrutura é superior e como deve ser replicada.

## Características Diferenciais

### 1. Integração de Limites nos Monitores
**Vantagem**: Limites integrados diretamente em cada monitor ativo
```json
"monitoramentos_ativos": [
  {
    "id": "mon_subordinacao",
    "tipo": "subordinacao",
    "limites": { "minimo": 0.25, "critico": 0.20 },
    "ativo": true
  }
]
```

**Benefício**: Elimina redundância e centraliza configuração de monitoramento em uma estrutura única.

### 2. Formato Decimal Consistente
**Vantagem**: Todos os percentuais em formato decimal (0.25 = 25%)
```json
"subordinacao": { "minimo": 0.25, "critico": 0.20 },
"concentracao": { "limite": 0.35 }
```

**Benefício**: Elimina ambiguidade entre formatos (25% vs 0.25) e facilita cálculos Python diretos.

### 3. Array de Concentração Flexível
**Vantagem**: Estrutura genérica para qualquer tipo de limite
```json
"concentracao": {
  "limites": [
    {"tipo": "individual", "entidade": "sacado", "limite": 0.35},
    {"tipo": "top_n", "entidade": "sacado", "n": 10, "limite": 1.00}
  ]
}
```

**Benefício**: Suporta tanto limites individuais quanto top_N sem duplicação de código.

### 4. Configuração Temporal Estruturada
**Vantagem**: Períodos especiais claramente definidos
```json
"periodos_especiais": {
  "formacao_carteira": {
    "dias": 60,
    "inicio": "2025-03-18",
    "fim": "2025-05-17",
    "regras_especiais": ["limites_concentracao_flexibilizados"]
  }
}
```

**Benefício**: Permite aplicar regras diferentes por período automaticamente.

### 5. Triggers de Aceleração Padronizados
**Vantagem**: Estrutura uniforme para todos os eventos
```json
"triggers_aceleracao": {
  "falencia_recuperacao": {
    "prazo_cura_dias": 0,
    "automatico": true,
    "notificacao_requerida": false
  }
}
```

**Benefício**: Sistematiza tratamento de eventos críticos com lógica clara.

### 6. Configuração Completa por Monitor
**Vantagem**: Cada monitor contém toda sua configuração
```json
"monitoramentos_ativos": [
  {
    "id": "mon_subordinacao",
    "tipo": "subordinacao",
    "ativo": true,
    "prioridade": "critica",
    "limites": { "minimo": 0.25, "critico": 0.20 },
    "campos_necessarios": ["pl_senior", "pl_subordinada"],
    "funcao_calculo": "calc_subordinacao"
  }
]
```

**Benefício**: Descoberta automática simplificada e configuração centralizada por monitor.

## Comparação com Estruturas Antigas

### Problema: Redundância e Limites Dispersos
**Estrutura antiga**:
```json
"subordinacao_minima": 0.25,
"concentracao_sacado": 0.35,
"monitoramentos_ativos": [
  {"id": "mon_subordinacao", "limite_ref": "subordinacao_minima"}
]
```

**Escritura JSON Template (Refatorada)**:
```json
"monitoramentos_ativos": [
  {
    "id": "mon_subordinacao",
    "tipo": "subordinacao", 
    "limites": {"minimo": 0.25, "critico": 0.20},
    "ativo": true
  }
]
```

**Melhoria**: Elimina redundância e centraliza configuração em uma estrutura única.

### Problema: Formatos Inconsistentes
**Estrutura antiga**:
```json
"limite_sacado": "35%",
"limite_cedente": 0.50,
"inadimplencia": "4%"
```

**Escritura JSON Template**:
```json
"concentracao": {"limite": 0.35},
"inadimplencia": {"limite": 0.04}
```

**Melhoria**: Formato decimal único elimina parsing complexo.

## Regra 80/20 Implementada

### 80% Comum (Estrutura Padrão)
- `limites_monitoramento`: Seção padrão para todos os pools
- `monitoramentos_ativos`: Array fixo de monitores base
- `triggers_aceleracao`: Eventos padrão do mercado
- `provisoes_pdd`: Grupos de risco padrão (AA-H)

### 20% Customizado (Seção Específica)
- `monitores_customizados`: Referências para arquivos Python específicos
- `sacados_elegiveis`: Lista específica por pool
- `periodos_especiais`: Datas e regras únicas

## Benefícios Técnicos

### 1. Validação Automatizada
Estrutura única simplifica validação:
```python
def validar_json(config):
    for monitor in config['monitoramentos_ativos']:
        if 'limites' not in monitor and monitor['tipo'] != 'provisao':
            raise ValueError(f"Monitor {monitor['id']} sem limites definidos")
```

### 2. Descoberta Automática Simplificada
Monitores e limites em uma estrutura:
```python
def descobrir_monitores(config):
    return [(m['tipo'], m['limites']) for m in config['monitoramentos_ativos'] if m['ativo']]
```

### 3. Acesso Direto aos Limites
Limites diretamente acessíveis no monitor:
```python
def obter_limite(monitor):
    return monitor['limites']  # Acesso direto, sem navegação
```

## Aplicação do Padrão

### Template Criado
Baseado na escritura JSON template, foi criado `pool_monitoring_template.json` em `/data/templates/` com:
- Comentários explicativos para IA
- Instruções de preenchimento
- Seção `monitores_customizados` para arquivos específicos
- Exemplos de nomenclatura: `{pool_id}_{funcionalidade}.py`

### Migração de Pools Existentes
Pools existentes devem ser migrados para seguir o padrão da escritura JSON template:
1. ~~Consolidar limites em `limites_monitoramento`~~ → **Integrar limites em `monitoramentos_ativos`**
2. Converter percentuais para decimal
3. Estruturar concentração como array
4. Adicionar seção `monitores_customizados`
5. **Eliminar redundância** entre seções de limites e monitores

## Conclusão

A escritura JSON template representa a evolução ideal para configuração de monitoramento porque:
- **Elimina redundância** entre limites e monitores
- **Centraliza configuração** em estrutura única por monitor
- **Padroniza** formatos de dados e descoberta automática
- **Facilita** manutenção sem duplicação de informações
- **Suporta** customizações específicas e flexibilidade
- **Permite** automação completa com acesso direto

Esta estrutura refatorada deve ser o padrão para todos os novos pools e meta de migração para pools existentes.