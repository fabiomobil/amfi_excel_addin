# Session Documentation

## Propósito

Esta pasta contém **APENAS** listas de tarefas organizadas por data de sessão para tracking de progresso.

## Filosofia do docs/sessions/

**PROPÓSITO EXCLUSIVO**: Lista de tarefas organizadas por data de sessão

### CONTEÚDO PERMITIDO:
- ✅ To-dos priorizados com checkboxes [ ]
- ✅ Status de progresso (x/y tarefas concluídas)
- ✅ Próxima tarefa prioritária a executar
- ✅ Ordem de implementação recomendada

### CONTEÚDO ESTRITAMENTE PROIBIDO:
- ❌ Descobertas técnicas → docs/technical/SYSTEM_STATE.md
- ❌ Definições de arquitetura → docs/COMPREHENSIVE_SYSTEM_GUIDE.md  
- ❌ Checklists e processos → docs/processos/
- ❌ Documentação detalhada → docs/technical/
- ❌ Métricas de performance → docs/technical/SYSTEM_STATE.md
- ❌ Interfaces e código → docs/COMPREHENSIVE_SYSTEM_GUIDE.md
- ❌ Análises e explicações → docs/technical/

## Formato Padrão

Apenas listas estruturadas com prioridades (Alta/Média/Baixa)

## Sistema de To-Do por Sessão

**TODA NOVA SESSÃO** deve seguir este processo:
1. **Criar arquivo**: `docs/sessions/to_do_YYYYMMDD.md`
2. **Listar tarefas**: Incluir tarefas pendentes + novas do dia
3. **Escolher foco**: Selecionar quais tarefas abordar na sessão
4. **Adicionar dinamicamente**: Conforme surgem novas demandas
5. **MANTER FOCO**: Apenas to-dos, sem documentação técnica

## Arquivos Atuais

- `to_do_20250716.md` - Sessão concluída (otimizações arquiteturais)
- `to_do_20250716_continuation.md` - Sessão de continuação (multi-agente)

## Para Documentação Técnica

Consulte:
- `/docs/technical/` - Documentação técnica detalhada
- `/docs/COMPREHENSIVE_SYSTEM_GUIDE.md` - Guia completo do sistema
- `/docs/USAGE_EXAMPLES.md` - Exemplos práticos de uso