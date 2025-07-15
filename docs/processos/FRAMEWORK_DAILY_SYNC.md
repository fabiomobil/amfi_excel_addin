# Framework de Ritual Diário - AmFi Daily Sync Protocol

## 🎯 Objetivo
Garantir inicialização consistente e completa do contexto de desenvolvimento para qualquer sessão de trabalho no projeto AmFi.

## 📋 Processo de 7 Etapas (15-20 minutos)

### **ETAPA 1: CONTEXTUALIZAÇÃO PRINCIPAL (5 min)**
```bash
# Sequência obrigatória de leitura
1. CLAUDE.md → Contexto técnico completo
2. PRD.md → Objetivos e roadmap  
3. SYSTEM_STATE.md → Estado atual
4. USAGE_EXAMPLES.md → Padrões de uso
```

**Checklist de Validação:**
- [ ] Compreendi a arquitetura atual
- [ ] Conheço os objetivos de negócio
- [ ] Sei o estado dos dados (métricas)
- [ ] Entendo as interfaces disponíveis

### **ETAPA 2: DOCUMENTAÇÃO ESPECIALIZADA (3 min)**
```bash
# Leitura seletiva baseada no foco da sessão
docs/processos/ → Para trabalho operacional
docs/technical/ → Para implementação técnica
```

**Checklist de Validação:**
- [ ] Li documentação relevante ao foco da sessão
- [ ] Identifiquei processos aplicáveis

### **ETAPA 3: SINCRONIZAÇÃO DE DOCUMENTOS (2 min)**
```bash
# Verificar consistência entre documentos principais
1. Métricas CLAUDE.md == SYSTEM_STATE.md
2. Objetivos CLAUDE.md == PRD.md  
3. Exemplos USAGE_EXAMPLES.md funcionais
```

**Checklist de Validação:**
- [ ] Documentos estão sincronizados
- [ ] Métricas são consistentes
- [ ] Exemplos estão funcionais

### **ETAPA 4: ORGANIZAÇÃO TEMPORAL (3 min)**
```bash
# Gestão de sessões anteriores
1. Listar arquivos docs/sessions/
2. Renomear expirados: to_do_YYYYMMDD.md → exp_to_do_YYYYMMDD.md
3. Verificar se há arquivos sem prefixo exp_ de dias anteriores
```

**Checklist de Validação:**
- [ ] Arquivos expirados renomeados
- [ ] Apenas sessão atual sem prefixo exp_

### **ETAPA 5: CONSOLIDAÇÃO DE TAREFAS (5 min)**
```bash
# Extração de tarefas pendentes
1. Ler APENAS arquivos docs/sessions/ que NÃO possuem 'exp_'
2. Extrair tarefas não concluídas dos arquivos ativos
3. Consolidar por prioridade (Alto/Médio/Baixo)
4. Adicionar novas tarefas identificadas
```

**Checklist de Validação:**
- [ ] Tarefas pendentes identificadas
- [ ] Prioridades definidas
- [ ] Novas demandas incluídas

### **ETAPA 6: CRIAÇÃO DO TO-DO ATUAL (2 min)**
```bash
# Arquivo: docs/sessions/to_do_YYYYMMDD.md
1. Usar template padrão
2. Incluir métricas de progresso
3. Definir foco da sessão
4. Estabelecer próxima ação prioritária
```

**Checklist de Validação:**
- [ ] Arquivo criado com data atual
- [ ] Template seguido corretamente
- [ ] Foco da sessão definido
- [ ] Próxima ação clara

### **ETAPA 7: DEFINIÇÃO DE FOCO (2 min)**
```bash
# Escolher foco da sessão
1. Revisar prioridades Alto no to-do
2. Verificar dependências técnicas
3. Estimar complexidade vs tempo disponível
4. Definir critério de sucesso da sessão
```

**Checklist de Validação:**
- [ ] Foco definido e realista
- [ ] Dependências verificadas
- [ ] Critério de sucesso claro

## 🔄 Template de To-Do Diário

```markdown
# To-Do - [DATA] - AmFi

## 📊 Métricas de Progresso (Herdadas)
- **Monitores base**: X/5 (Subordinação ✅, Inadimplência ✅, PDD ✅)
- **Monitores customizados**: X/20+
- **Pools auditados**: X/7
- **Documentação**: Sincronizada ✅

## 🎯 Foco da Sessão
**Prioridade**: [DEFINIR]
**Critério de Sucesso**: [DEFINIR]

## 📋 Tarefas por Prioridade

### 🔥 ALTA PRIORIDADE
- [ ] [TAREFA PRINCIPAL DO DIA]

### ⚡ MÉDIA PRIORIDADE
- [ ] [TAREFAS IMPORTANTES]

### 💡 BAIXA PRIORIDADE
- [ ] [TAREFAS OPCIONAIS]

## 🚀 Próxima Ação Recomendada
[DEFINIR PRIMEIRA AÇÃO ESPECÍFICA]
```

## 🎨 Automação Futura

### **Nível 1: Semi-automatizado**
- Script para renomear arquivos expirados
- Template automático de to-do
- Checklist interativo

### **Nível 2: Inteligente**
- Análise automática de sincronização
- Extração automática de tarefas pendentes
- Sugestão de foco baseado em prioridades

### **Nível 3: Adaptativo**
- Aprendizado de padrões de produtividade
- Recomendações baseadas em histórico
- Otimização dinâmica do processo

## 📈 Métricas de Sucesso do Framework

### **Eficiência:**
- Tempo de inicialização: < 20 minutos
- Tarefas perdidas entre sessões: 0%
- Documentação desatualizada: < 5%

### **Qualidade:**
- Contexto completo carregado: 100%
- Próxima ação sempre clara: 100%
- Continuidade entre sessões: 100%

### **Escalabilidade:**
- Funciona para múltiplos desenvolvedores
- Adapta-se a diferentes tipos de sessão
- Mantém consistência em projetos longos

## 🔍 Princípios Fundamentais

### **1. Contextualização Total**
Nunca começar trabalho sem contexto completo

### **2. Continuidade Garantida**
Zero perda de progresso entre sessões

### **3. Priorização Baseada em Dados**
Decisões baseadas em métricas e progresso real

### **4. Documentação Como Fonte de Verdade**
Documentos sempre refletem a realidade atual

### **5. Escalabilidade Humana**
Qualquer pessoa pode executar o protocolo

## 💡 Adaptações por Contexto

### **Sessão de Desenvolvimento Técnico:**
- Foco em CLAUDE.md + SYSTEM_STATE.md
- Leitura detalhada de docs/technical/
- Priorização de implementação

### **Sessão de Planejamento:**
- Foco em PRD.md + métricas
- Leitura de docs/processos/
- Priorização de roadmap

### **Sessão de Debugging:**
- Foco em USAGE_EXAMPLES.md
- Análise de logs e erros
- Priorização de correções

### **Sessão de Documentação:**
- Verificação de sincronização
- Atualização de métricas
- Priorização de gaps

## 🎯 Implementação Imediata

### **Hoje (Sessão Atual):**
- [x] Framework documentado
- [ ] Primeira execução completa
- [ ] Refinamentos baseados na experiência

### **Próxima Sessão:**
- [ ] Validar eficácia do processo
- [ ] Identificar otimizações
- [ ] Considerar automação nível 1

### **Médio Prazo:**
- [ ] Criar script de automação
- [ ] Treinar outros desenvolvedores
- [ ] Estabelecer métricas de sucesso

---

**Última Atualização**: 2025-07-15  
**Versão**: 1.0  
**Status**: Implementação inicial