# Análise Comparativa dos JSONs de Pools

## Resumo da Análise
Comparação detalhada entre as estruturas JSON existentes para identificar inconsistências, problemas e oportunidades de padronização baseadas na escritura JSON template.

## Pools Analisados

### 1. LeCapital Pool 1 ⭐ (Padrão Ideal)
- **Arquivo**: `lecapital_pool_1_monitoring.json`
- **Status**: Estrutura otimizada para monitoramento
- **Características**: Consolidação de limites, formato decimal, arrays flexíveis

### 2. AFA Pool 1 ⚠️ (Estrutura Legada)
- **Arquivo**: `afa_pool_1.json`
- **Status**: Estrutura antiga com problemas significativos
- **Características**: Limites dispersos, formatos inconsistentes, seções duplicadas

### 3. SuperSim Pool 1 ⚠️ (Estrutura Específica)
- **Arquivo**: `supersim_pool_1.json`
- **Status**: Estrutura customizada com regras específicas
- **Características**: Monitores únicos (recovery rate), limites por instituição

## Problemas Identificados

### 1. **Inconsistências de Formato**

#### Percentuais
- **AFA**: Mistura `25.0` (decimal) com `"4%"` (string)
- **SuperSim**: Usa `0.35` (decimal) consistentemente
- **LeCapital**: Usa `0.25` (decimal) em todos os casos

**Recomendação**: Padronizar formato decimal (0.25 = 25%)

#### Valores Nulos
- **AFA**: Usa `"NaN"` (string) para valores ausentes
- **SuperSim**: Usa `null` (JSON null) corretamente
- **LeCapital**: Usa `null` consistentemente

**Recomendação**: Sempre usar `null` para valores ausentes

### 2. **Dispersão de Limites**

#### AFA Pool 1 (Problemático)
```json
"indices_minimos": {
  "subordinacao_minima": 25.0,
  "subordinacao_critica": 20.0
},
"limites_carteira": {
  "concentracao_maxima_sacado": 27,
  "concentracao_maxima_cedente": 30,
  "inadimplencia_maxima_percentual": 4
}
```

#### Escritura JSON Template (Ideal)
```json
"limites_monitoramento": {
  "subordinacao": {"minimo": 0.25, "critico": 0.20},
  "concentracao": {"limites": [...]},
  "inadimplencia": {"30_dias": {"limite": 0.04}}
}
```

**Problema**: Limites espalhados dificultam manutenção e validação
**Solução**: Consolidar em seção única `limites_monitoramento`

### 3. **Estrutura de Concentração**

#### AFA Pool 1 (Rígida)
```json
"concentracao_maxima_sacado": 27,
"concentracao_maxima_cedente": 30,
"concentracao_maxima_top_10_sacados": 100,
"concentracao_maxima_top_10_cedentes": 70
```

#### Escritura JSON Template (Flexível)
```json
"concentracao": {
  "limites": [
    {"tipo": "individual", "entidade": "sacado", "limite": 0.35},
    {"tipo": "top_n", "entidade": "sacado", "n": 10, "limite": 1.00}
  ]
}
```

**Problema**: Estrutura rígida não suporta limites dinâmicos
**Solução**: Array flexível suporta qualquer combinação de limites

### 4. **Monitores Customizados**

#### SuperSim (Específico)
```json
"recovery_rate_mensal": {
  "limite": 0.95,
  "janela_monitoramento": 3,
  "formula": "∑(Valor Pago) / ∑(Valor Aquisição)"
}
```

#### Escritura JSON Template (Padronizado)
```json
"monitores_customizados": {
  "arquivos_necessarios": ["supersim_pool_1_recovery_rate.py"],
  "descricoes": ["Taxa de recuperação mínima 95% em janela de 3 meses"]
}
```

**Problema**: Regras específicas misturadas com configuração padrão
**Solução**: Seção dedicada para monitores customizados

## Oportunidades de Melhoria

### 1. **Migração AFA Pool 1**
**Problemas a corrigir**:
- Converter percentuais para decimal
- Consolidar limites em `limites_monitoramento`
- Substituir `"NaN"` por `null`
- Estruturar concentração como array
- Adicionar seção `monitores_customizados`

**Benefícios**:
- Compatibilidade com sistema de monitoramento
- Facilidade de manutenção
- Validação automática

### 2. **Padronização SuperSim Pool 1**
**Problemas a corrigir**:
- Extrair regras específicas (recovery rate, limites BMP/SOCINAL)
- Criar monitores customizados separados
- Padronizar seção `limites_monitoramento`

**Benefícios**:
- Separação clara entre comum (80%) e específico (20%)
- Monitores reutilizáveis
- Manutenção simplificada

### 3. **Template para Novos Pools**
**Recursos implementados**:
- Baseado na estrutura LeCapital
- Comentários explicativos para IA
- Seção `monitores_customizados` preparada
- Validação de schema facilita

## Análise por Categoria

### Subordinação
- **LeCapital**: ✅ Estrutura ideal com mínimo/crítico
- **AFA**: ⚠️ Separado em `indices_minimos`
- **SuperSim**: ⚠️ Separado em `indices_minimos`

### Concentração
- **LeCapital**: ✅ Array flexível suporta qualquer limite
- **AFA**: ❌ Campos fixos, não extensível
- **SuperSim**: ❌ Estrutura específica para BMP/SOCINAL

### Inadimplência
- **LeCapital**: ✅ Estrutura por prazo (30_dias, 90_dias)
- **AFA**: ❌ Campos fixos dispersos
- **SuperSim**: ❌ Não implementado

### Provisões PDD
- **LeCapital**: ✅ Estrutura padronizada AA-H
- **AFA**: ❌ Percentuais como decimal puro
- **SuperSim**: ❌ Percentuais como decimal puro

### Monitores Customizados
- **LeCapital**: ✅ Seção dedicada (vazia - não necessária)
- **AFA**: ❌ Ausente (necessária para sacados específicos)
- **SuperSim**: ❌ Ausente (necessária para recovery rate)

## Recomendações de Migração

### Prioridade Alta
1. **Migrar AFA Pool 1** para escritura JSON template
2. **Extrair monitores customizados** do SuperSim
3. **Padronizar formatos** em todos os pools

### Prioridade Média
1. Criar monitores customizados:
   - `afa_pool_1_sacados_especificos.py`
   - `supersim_pool_1_recovery_rate.py`
2. Validar consistência entre pools
3. Documentar diferenças específicas

### Prioridade Baixa
1. Migrar pools restantes (credmei, formento, etc.)
2. Implementar validação automática
3. Criar ferramentas de migração

## Conclusão

A escritura JSON template representa o estado ideal para configuração de pools porque:
- **Consolida** limites relacionados
- **Padroniza** formatos de dados
- **Flexibiliza** estruturas de concentração
- **Separa** regras comuns (80%) de específicas (20%)
- **Facilita** manutenção e validação

A migração dos pools existentes deve seguir este padrão para garantir compatibilidade com o sistema de monitoramento automatizado.