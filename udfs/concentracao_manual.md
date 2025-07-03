# 📊 Manual Completo - AmfiConcentracao

## 🎯 Visão Geral

A função `AmfiConcentracao` é uma ferramenta avançada para análise de concentração de risco em carteiras de fundos de investimento. Permite monitoramento de limites individuais e agregados com alta performance para carteiras com milhares de ativos.

---

## 📋 Sintaxe Completa

```excel
=AmfiConcentracao(arquivo_xlsx, pool, pl_total, [tipo], [top], [limite], [ignore_list])
```

### **Parâmetros Obrigatórios**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `arquivo_xlsx` | String | Caminho do arquivo XLSX da carteira |
| `pool` | String | Nome do pool para filtrar |
| `pl_total` | Número | Valor total do PL para cálculo de percentuais |

### **Parâmetros Opcionais**
| Parâmetro | Tipo | Descrição | Padrão |
|-----------|------|-----------|---------|
| `tipo` | String | `"sacado"`, `"cedente"` ou vazio | Combinado (cedente/sacado) |
| `top` | String | `"top=X"` para os X maiores | Todos os registros |
| `limite` | String | Configuração de limites | Sem monitoramento |
| `ignore_list` | Variável | Entidades para ignorar | Nenhuma |

---

## 🔧 Tipos de Análise

### **1. Concentração por Cedente**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente")
```
**Resultado:** Lista todos os cedentes ordenados por valor decrescente
- Agrupa por `Nome do Cedente`
- Calcula valor, percentual e quantidade de operações
- Ordena do maior para o menor valor

### **2. Concentração por Sacado**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "sacado")
```
**Resultado:** Lista todos os sacados ordenados por valor decrescente
- Agrupa por `Nome do Sacado`
- Calcula valor, percentual e quantidade de operações
- Ordena do maior para o menor valor

### **3. Concentração Combinada (Padrão)**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000)
```
**Resultado:** Lista combinações cedente/sacado
- Agrupa por `"Cedente / Sacado"`
- Útil para análise de concentração cruzada
- Formato: "EMPRESA_A / CLIENTE_X"

---

## 🎚️ Parâmetro TOP - Limitando Resultados

### **Sintaxe**
- `"top=X"` onde X é o número de registros desejados
- Aceita também apenas o número: `"5"` ou `5`

### **Exemplos**

#### **Top 5 Cedentes**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=5")
```
**Resultado:** Apenas os 5 maiores cedentes + linha de total

#### **Top 10 Sacados**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "sacado", "top=10")
```
**Resultado:** Apenas os 10 maiores sacados + linha de total

#### **Todos os Registros (Sem Top)**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente")
```
**Resultado:** Lista completa, sem linha de total

---

## ⚖️ Sistema de Limites

### **Tipos de Limite**

| Tipo | Formato | Descrição | Exemplo |
|------|---------|-----------|---------|
| **Individual** | `individual=X` | Limite por entidade (%) | `individual=15` |
| **Top Agregado** | `topN=X` | Limite para soma do topN (%) | `top5=60` |
| **Múltiplos** | `param1=X,param2=Y` | Combinação de limites | `individual=10,top3=30` |

### **Exemplos de Configuração**

#### **Limite Individual Apenas**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", , "individual=15")
```
**Monitoramento:**
- Nenhum cedente pode ter mais de 15% da carteira
- Status: "ok" ou "violado" por entidade
- Espaço/Excesso: quanto falta/sobra para o limite

#### **Limite Agregado Apenas**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=5", "top5=60")
```
**Monitoramento:**
- Top 5 cedentes não podem somar mais de 60%
- Linha "Total" mostra status agregado
- Espaço/Excesso total na linha de resumo

#### **Ambos os Limites**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=3", "individual=12,top3=40")
```
**Monitoramento Duplo:**
- Individual: cada cedente máximo 12%
- Agregado: top 3 cedentes máximo 40% somados
- Status combinado na linha total

---

## 🚫 Sistema Ignore List

### **Comportamento por Tipo**
- **`tipo="cedente"`**: Ignora os cedentes da lista
- **`tipo="sacado"`**: Ignora os sacados da lista  
- **`tipo=vazio`**: Ignora apenas cedentes (padrão)

### **Formatos Suportados**

#### **String Simples**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", , , "EMPRESA_X")
```
**Resultado:** Remove EMPRESA_X da análise

#### **Múltiplas Entidades (Separadas por |)**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", , , "EMPRESA_X|EMPRESA_Y|EMPRESA_Z")
```
**Resultado:** Remove todas as 3 empresas da análise

#### **Range do Excel**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", , , A1:A5)
```
**Resultado:** Remove todas as empresas listadas em A1:A5

#### **Células com Múltiplos Valores**
Se a célula A1 contém: `"EMPRESA_X|EMPRESA_Y"`
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", , , A1)
```
**Resultado:** Remove ambas as empresas

---

## 📊 Interpretação dos Resultados

### **Colunas do Resultado**
| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| **Empresa** | Nome do cedente/sacado | "EMPRESA_A" |
| **Valor** | Valor em reais | 5000000.50 |
| **Percentual** | Percentual sobre PL total | 0.15 (=15%) |
| **Espaço/Excesso** | Valor absoluto até/acima do limite | 2000000 ou -500000 |
| **Status** | Conformidade com limite individual | "ok" ou "violado" |

### **Linha Total (apenas com TOP)**
Aparece quando parâmetro `top` é usado:
```
["Total", 15000000, 0.45, 1000000, "top enquadrado, individual violado"]
```

### **Status Possíveis da Linha Total**
- `"ambos ok"` - Individual e agregado dentro dos limites
- `"top violado, individual ok"` - Limite agregado estourou
- `"top enquadrado, individual violado"` - Limite individual estourou
- `"ambos violados"` - Ambos os limites estouraram

---

## 🎯 Casos de Uso Práticos

### **Caso 1: Monitoramento Básico de Cedentes**
**Objetivo:** Ver top 10 cedentes com limite individual de 15%

```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 50000000, "cedente", "top=10", "individual=15")
```

**Resultado Esperado:**
- Lista dos 10 maiores cedentes
- Status individual para cada um
- Linha total com resumo agregado
- Identificação clara de violações

### **Caso 2: Análise de Compliance Completa**
**Objetivo:** Política rigorosa de concentração

```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=5", "individual=10,top3=25,top5=45")
```

**Política Aplicada:**
- Nenhum cedente > 10% individual
- Top 3 cedentes < 25% somados  
- Top 5 cedentes < 45% somados
- Monitoramento em múltiplas camadas

### **Caso 3: Análise Excluindo Grupos Econômicos**
**Objetivo:** Concentração real excluindo empresas relacionadas

```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 75000000, "cedente", "top=8", "individual=12", "GRUPO_A|GRUPO_B|EMPRESA_RELACIONADA")
```

**Benefícios:**
- Visão limpa da concentração
- Exclusão de entidades relacionadas
- Foco nos verdadeiros riscos de concentração

### **Caso 4: Monitoramento de Sacados por Região**
**Objetivo:** Análise de concentração por devedor

```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 200000000, "sacado", "top=15", "individual=8,top10=50")
```

**Aplicação:**
- Controle de concentração por devedor
- Limite conservador individual (8%)
- Monitoramento agregado dos maiores

### **Caso 5: Análise Combinada Cedente/Sacado**
**Objetivo:** Concentração cruzada para identificar dependências

```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 150000000, , "top=20", "individual=5")
```

**Insights:**
- Identifica combinações cedente+sacado concentradas
- Revela dependências operacionais
- Limite rigoroso para combinações (5%)

---

## ⚡ Otimizações e Performance

### **Para Carteiras Grandes (1000+ ativos)**
1. **Use TOP sempre que possível** - Reduz processamento
2. **Cache automático** - Arquivo é cacheado após primeira leitura
3. **Filtros eficientes** - ignore_list usa operações otimizadas

### **Dicas de Performance**
```excel
// ✅ Recomendado - Top limitado
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=20")

// ⚠️ Cuidado - Lista completa em carteira muito grande
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente")
```

---

## 🔍 Troubleshooting

### **Erros Comuns**

#### **"Pool não encontrado"**
```excel
// ❌ Problema: Nome do pool incorreto
=AmfiConcentracao("carteira.xlsx", "POOL_ERRADO", 100000000)

// ✅ Solução: Verificar nome exato do pool
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000)
```

#### **"Colunas ausentes"**
**Colunas obrigatórias no XLSX:**
- `Pool`
- `Valor presente (R$)`
- `Nome do Sacado`
- `Nome do Cedente`

#### **"PL deve ser maior que zero"**
```excel
// ❌ Problema: PL inválido
=AmfiConcentracao("carteira.xlsx", "POOL_001", 0)

// ✅ Solução: Usar valor real do PL
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000)
```

### **Validação de Parâmetros**
- `tipo`: Apenas "sacado", "cedente" ou vazio
- `top`: Formato "top=X" ou número positivo
- `limite`: Formato "chave=valor,chave=valor"
- `pl_total`: Número positivo obrigatório

---

## 📈 Exemplos Avançados

### **Estratégia de Monitoramento Escalonada**

#### **Nível 1: Visão Geral**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=10")
```

#### **Nível 2: Compliance Individual**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=15", "individual=12")
```

#### **Nível 3: Compliance Completa**
```excel
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=10", "individual=10,top3=25,top5=40,top10=60")
```

### **Análise Comparativa**

#### **Cedentes vs Sacados**
```excel
// Planilha A: Cedentes
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "cedente", "top=10", "individual=15")

// Planilha B: Sacados  
=AmfiConcentracao("carteira.xlsx", "POOL_001", 100000000, "sacado", "top=10", "individual=15")
```

---

## 🎛️ Configurações de Política Típicas

### **Conservadora (Baixo Risco)**
```excel
"individual=8,top3=20,top5=35,top10=55"
```

### **Moderada (Risco Médio)**
```excel
"individual=12,top3=30,top5=50,top10=70"
```

### **Agressiva (Alto Risco)**
```excel
"individual=20,top5=60,top10=80"
```

### **Regulatória (Compliance)**
```excel
"individual=15,top3=35,top5=55"
```

---

## 📋 Checklist de Implementação

### **Antes de Usar**
- [ ] Arquivo XLSX com colunas obrigatórias
- [ ] Nome exato do pool
- [ ] Valor correto do PL total
- [ ] Definição clara dos limites de política

### **Durante o Uso**
- [ ] Verificar se resultados fazem sentido
- [ ] Validar percentuais (soma deve ser lógica)
- [ ] Conferir status de compliance
- [ ] Analisar linha de total quando usar TOP

### **Monitoramento Contínuo**
- [ ] Configurar alertas para violações
- [ ] Revisar limites periodicamente  
- [ ] Documentar exceções aprovadas
- [ ] Manter histórico de análises

---

## 🚀 Conclusão

A função `AmfiConcentracao` oferece análise completa e flexível para gestão de risco de concentração, combinando:

- **Performance otimizada** para carteiras grandes
- **Flexibilidade total** de configuração  
- **Monitoramento automático** de compliance
- **Integração nativa** com Excel
- **Documentação detalhada** para todos os cenários

Use este manual como referência completa para implementar análises robustas de concentração em seus fundos!