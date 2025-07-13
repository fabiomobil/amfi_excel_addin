# Checklist Abrangente de Extração de Features para Conversão de Documentos Legais para JSON

> **Documentos Relacionados:**
> - [Processo de Extração Sistemática](./PROCESSO_EXTRACAO_SISTEMATICA.md) - Metodologia completa

## Visão Geral
Este checklist garante que NENHUMA feature de monitoramento seja perdida ao converter documentos legais (escrituras) para arquivos JSON compatíveis com monitoramento. Cada seção deve ser sistematicamente revisada para CADA pool.

## 🔍 **TERMOS DE BUSCA OBRIGATÓRIOS** (Buscar TODOS no documento)

### Termos de Recuperação e Regresso
- [ ] "direito de regresso" / "right of recourse"
- [ ] "recovery" / "recuperação" / "recuperar"
- [ ] "recompra" / "repurchase" / "buyback"
- [ ] "substituição" / "substitution"
- [ ] "fraud" / "fraude"
- [ ] "má formalização" / "poor formalization"
- [ ] "recovery rate" / "taxa de recuperação"
- [ ] "cobrança" / "collection"

### Monitoramento Baseado em Tempo
- [ ] Todos os números seguidos de "dias"
- [ ] Todos os números seguidos de "meses"
- [ ] "prazo" / "deadline" / "período"
- [ ] "vencimento" / "maturity"
- [ ] "antecipado" / "early" / "anticipated"
- [ ] "cura" / "cure" / "remedy"

### Limites Financeiros e Índices
- [ ] Todos os símbolos de porcentagem (%)
- [ ] "limite" / "limit" / "máximo" / "mínimo"
- [ ] "concentração" / "concentration"
- [ ] "subordinação" / "subordination"
- [ ] "índice" / "index" / "ratio"
- [ ] "inadimplência" / "default" / "delinquency"
- [ ] Números com símbolos monetários (R$, $)

### Conformidade e Monitoramento
- [ ] "monitoramento" / "monitoring"
- [ ] "evento" / "event" / "trigger"
- [ ] "avaliação" / "evaluation" / "assessment"
- [ ] "violação" / "violation" / "breach"
- [ ] "critério" / "criteria" / "requirement"
- [ ] "elegibilidade" / "eligibility"

### Provisões e Risco
- [ ] "provisão" / "provision" / "PDD"
- [ ] "risco" / "risk" / "grupo de risco"
- [ ] "atraso" / "delay" / "late" / "overdue"
- [ ] "classificação" / "classification"

## 📋 **PROCESSO DE EXTRAÇÃO SISTEMÁTICA**

### Fase 1: Análise da Estrutura do Documento
1. **Identificação do Tipo de Documento**
   - [ ] Escritura de emissão principal
   - [ ] Aditamento
   - [ ] Termo aditivo
   - [ ] Número/data da versão

2. **Revisão do Índice**
   - [ ] Extrair todos os números e títulos de cláusulas
   - [ ] Identificar seções relacionadas a monitoramento
   - [ ] Sinalizar cláusulas complexas/aninhadas para revisão aprofundada

3. **Identificação de Anexos**
   - [ ] Listar todos os anexos (Anexo I, II, III, etc.)
   - [ ] Identificar anexos relevantes para monitoramento
   - [ ] Extrair títulos e propósitos dos anexos

### Fase 2: Extração de Informações Principais

#### A. Informações Básicas do Pool
- [ ] **Nome do Pool**: Nome oficial e nome administrativo
- [ ] **Número da Emissão**: Número sequencial na série de emissões
- [ ] **Data de Emissão**: Data de início do pool
- [ ] **Data de Vencimento**: Data de vencimento final
- [ ] **Valor Total**: Valor total da emissão
- [ ] **Emissora**: Empresa emitente
- [ ] **Lei Aplicável**: Marco legal (Lei 14.430/22, etc.)

#### B. Estrutura Financeira
- [ ] **Série Sênior**: Número, valor, hierarquia de subordinação
- [ ] **Série Subordinada**: Número, valor, hierarquia de subordinação
- [ ] **Índice Mínimo de Subordinação**: Percentuais limites
- [ ] **Índice Crítico de Subordinação**: Limites de emergência
- [ ] **Cronograma de Pagamento**: Calendário e percentuais de amortização

#### C. Critérios de Elegibilidade de Ativos
- [ ] **Tipos de Ativos Permitidos**: CCBs, duplicatas, etc. com limites percentuais
- [ ] **Limites Individuais**: Valor mínimo, faixa de vencimento, taxas de juros
- [ ] **Limites de Portfólio**: Vencimento médio, limites de concentração
- [ ] **Lista de Devedores Elegíveis**: Contrapartes pré-aprovadas
- [ ] **Período de Aquisição**: Prazos para aquisição de novos ativos

### Fase 3: Extração de Eventos de Monitoramento

#### A. Limites de Concentração
- [ ] **Devedor Individual**: Percentual máximo por entidade
- [ ] **Cedente Individual**: Percentual máximo por originador
- [ ] **Análise Top N**: Limites agregados para maiores entidades
- [ ] **Específico por Instituição**: Limites especiais para instituições parceiras
- [ ] **Geográfico**: Limites de concentração regional (se houver)

#### B. Métricas de Performance Financeira
- [ ] **Índice de Subordinação**: Limites mínimos e frequência de monitoramento
- [ ] **Taxas de Inadimplência**: Percentuais máximos para diferentes faixas de atraso
- [ ] **Taxas de Recuperação**: Percentuais mínimos de recuperação e métodos de cálculo
- [ ] **Qualidade do Portfólio**: Métricas e limites de qualidade de ativos

#### C. Eventos Baseados em Tempo
- [ ] **Prazos de Aquisição**: Datas limites para aquisição de novos ativos
- [ ] **Formação do Portfólio**: Período inicial com critérios relaxados
- [ ] **Janelas de Vencimento**: Requisitos de vencimento de ativos individuais
- [ ] **Períodos de Cura**: Tempo permitido para remediar violações

### Fase 4: Análise de Mecanismos de Recuperação

#### A. Direito de Regresso
- [ ] **Condições de Elegibilidade**: Quando o regresso pode ser exercido
- [ ] **Gatilhos Temporais**: Dias de atraso antes da ativação do regresso
- [ ] **Categorias de Causa**: Fraude, má formalização, outras razões
- [ ] **Alvos de Recuperação**: Contra quem o regresso pode ser exercido
- [ ] **Taxas de Recuperação**: Percentuais esperados de recuperação

#### B. Recompra Obrigatória
- [ ] **Eventos Gatilho**: Condições que exigem recompra
- [ ] **Prazos**: Deadlines para recompra/substituição
- [ ] **Critérios de Substituição**: Requisitos para ativos substitutos
- [ ] **Parte Responsável**: Quem deve executar a recompra
- [ ] **Método de Avaliação**: Como o preço de recompra é determinado

#### C. Mecanismos de Cobrança
- [ ] **Agente de Cobrança**: Quem gerencia as cobranças
- [ ] **Contas de Cobrança**: Contas dedicadas para recuperações
- [ ] **Performance de Cobrança**: Taxas mínimas de cobrança
- [ ] **Relatórios de Cobrança**: Frequência e formato dos requisitos

### Fase 5: Provisionamento de Risco

#### A. Classificação de Risco
- [ ] **Grupos de Risco**: Sistema de classificação (AA, A, B, C, etc.)
- [ ] **Faixas de Atraso**: Dias de atraso para cada categoria de risco
- [ ] **Percentuais de Provisão**: Taxas de provisão para cada grupo de risco
- [ ] **Regras de Reclassificação**: Quando ativos mudam entre grupos de risco

#### B. Cálculo de Provisão
- [ ] **Metodologia de Cálculo**: Como as provisões são computadas
- [ ] **Frequência**: Com que frequência as provisões são recalculadas
- [ ] **Requisitos de Relatório**: Obrigações de relatório de provisões
- [ ] **Requisitos de Reserva**: Níveis mínimos de reserva

### Fase 6: Eventos de Vencimento Antecipado

#### A. Eventos Automáticos (Sem Período de Cura)
- [ ] **Falência/Recuperação Judicial**: Gatilhos de aceleração imediata
- [ ] **Mudanças Societárias**: Fusões, cisões sem aprovação
- [ ] **Litígios Materiais**: Decisões judiciais acima do limite
- [ ] **Questões Regulatórias**: Revogação de licença, sanções

#### B. Eventos Curáveis (Com Período de Cura)
- [ ] **Inadimplência de Pagamento**: Violações de obrigações monetárias
- [ ] **Violações de Covenants**: Violações de obrigações não monetárias
- [ ] **Violações de Limites**: Violações de limites de concentração ou performance
- [ ] **Questões de Documentação**: Documentação faltante ou incorreta

### Fase 7: Estrutura Operacional

#### A. Contas e Banking
- [ ] **Conta Centralizadora**: Detalhes e propósitos da conta principal
- [ ] **Contas Vinculadas**: Contas escrow e dedicadas
- [ ] **Restrições de Conta**: Limitações e controles de movimentação
- [ ] **Requisitos Bancários**: Instituições autorizadas

#### B. Regras de Investimento
- [ ] **Investimentos Permitidos**: Tipos de investimento permitidos
- [ ] **Restrições de Investimento**: Investimentos proibidos
- [ ] **Requisitos de Liquidez**: Necessidades de liquidez diária
- [ ] **Limitações de Instituição**: Contrapartes aprovadas

#### C. Prestadores de Serviço
- [ ] **Serviços Operacionais**: Detalhes dos prestadores de serviço
- [ ] **Originador**: Responsabilidades e obrigações do originador
- [ ] **Debenturistas**: Direitos e obrigações
- [ ] **Outras Partes**: Prestadores de serviço adicionais

### Fase 8: Identificação de Features Especiais

#### A. Regras Específicas do Pool
- [ ] **Limites Únicos de Concentração**: Regras de concentração específicas do pool
- [ ] **Relacionamentos Especiais**: Arranjos com instituições parceiras
- [ ] **Tipos Únicos de Ativos**: Ativos elegíveis específicos do pool
- [ ] **Métodos Especiais de Cálculo**: Fórmulas específicas do pool

#### B. Monitoramento Aprimorado
- [ ] **Métricas Adicionais**: Indicadores de performance específicos do pool
- [ ] **Eventos Especiais**: Eventos de monitoramento únicos
- [ ] **Relatórios Aprimorados**: Requisitos adicionais de relatório
- [ ] **Testes de Estresse**: Requisitos especiais de teste de estresse

## ✅ **CHECKLIST DE VALIDAÇÃO**

### Verificação de Completude
- [ ] Todos os termos de busca foram sistematicamente revisados
- [ ] Todos os anexos foram analisados quanto a conteúdo de monitoramento
- [ ] Todas as tabelas e fórmulas foram extraídas
- [ ] Todos os períodos e prazos foram capturados
- [ ] Todos os limites percentuais foram identificados

### Verificação de Precisão
- [ ] Todas as porcentagens convertidas para formato decimal (5% = 0.05)
- [ ] Todos os valores monetários em formato float
- [ ] Todos os valores nulos adequadamente definidos (não "NaN" ou "N/A")
- [ ] Todas as datas no formato AAAA-MM-DD
- [ ] Todas as flags booleanas adequadamente definidas

### Verificação de Compatibilidade de Monitoramento
- [ ] Todos os eventos de monitoramento têm flags "ativo"
- [ ] Todos os limites têm especificações adequadas de "unidade"
- [ ] Todos os eventos baseados em tempo têm prazos claros
- [ ] Todas as fórmulas estão em formato amigável ao monitoramento
- [ ] Todas as regras específicas do pool usam estrutura padronizada

### Verificação de Referência Cruzada
- [ ] Comparar com outros pools para identificar features ausentes
- [ ] Verificar se todos os eventos têm referências de cláusulas correspondentes
- [ ] Verificar consistência na nomenclatura de campos
- [ ] Validar contra requisitos do schema

## 🚨 **RED FLAGS** (Indicadores de Features Ausentes)

### Sinais de Alerta
- [ ] Pool tem significativamente menos eventos de monitoramento que outros
- [ ] Nenhum mecanismo de recuperação identificado
- [ ] Faltam prazos baseados em tempo
- [ ] Sem regras específicas por instituição
- [ ] Estrutura incomumente simples comparada a pools similares

### Omissões Comuns
- [ ] Cálculos de taxa de recuperação enterrados em descrições de eventos
- [ ] Múltiplos tipos de prazo (dias úteis vs. corridos)
- [ ] Limites de concentração implícitos não explicitamente declarados
- [ ] Mecanismos de cobrança mencionados sem detalhes
- [ ] Regras de provisionamento de risco espalhadas por múltiplas cláusulas

## 📊 **PONTUAÇÃO DE QUALIDADE**

### Critérios de Pontuação (Total: 100 pontos)
- **Informações Básicas**: 20 pontos (identificação completa do pool)
- **Estrutura Financeira**: 15 pontos (séries, subordinação, cronogramas)
- **Eventos de Monitoramento**: 25 pontos (cobertura abrangente de eventos)
- **Mecanismos de Recuperação**: 20 pontos (todas as features de recuperação capturadas)
- **Provisionamento de Risco**: 10 pontos (estrutura PDD completa)
- **Validação**: 10 pontos (conformidade de formato e verificações cruzadas)

### Limites de Qualidade
- **95-100 pontos**: Excelente - Pronto para produção
- **85-94 pontos**: Bom - Pequenos ajustes necessários
- **75-84 pontos**: Aceitável - Algumas features podem estar faltando
- **Abaixo de 75 pontos**: Incompleto - Requer revisão abrangente

## 🔄 **MELHORIA CONTÍNUA**

### Aprendendo com Features Perdidas
- [ ] Documentar quaisquer features perdidas durante a extração inicial
- [ ] Atualizar termos de busca baseados em novas descobertas
- [ ] Aprimorar checklist com padrões específicos do pool
- [ ] Melhorar critérios de validação baseados em erros encontrados

### Refinamento do Processo
- [ ] Rastrear tempo gasto em cada fase de extração
- [ ] Identificar tipos de features mais comumente perdidas
- [ ] Desenvolver scripts de validação automatizados
- [ ] Criar ferramentas de comparação de pools para verificação de consistência

---

**Nota**: Este checklist deve ser usado para CADA conversão de pool. Cada checkbox deve ser explicitamente verificado. Features ausentes em sistemas de monitoramento podem levar a riscos significativos de conformidade e financeiros.