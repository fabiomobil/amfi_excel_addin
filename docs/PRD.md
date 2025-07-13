# PRD - Sistema de Monitoramento de Portfólio AmFi

## Resumo Executivo
Sistema automatizado de monitoramento de compliance e liquidez para fundos de investimento estruturados, processando dados diários de múltiplas fontes para gerar dashboards de exceção e análises preditivas de fluxo de caixa.

## Visão do Produto
Transformar o processo manual de verificação de compliance (atualmente 4-6 horas/dia) em monitoramento automatizado em tempo real, permitindo gestão por exceção e antecipação de problemas de liquidez.

## Objetivos de Negócio
1. **Reduzir tempo de análise**: De 4-6 horas para <30 minutos/dia
2. **Eliminar erros manuais**: Zero falhas de cálculo em produção
3. **Antecipar problemas**: Alertas com 6+ meses de antecedência
4. **Garantir compliance**: 100% de cobertura dos requisitos das escrituras
5. **Facilitar auditoria**: Histórico completo e rastreável

## Componentes do Sistema

### 1. Monitoramento Individual por Pool
**Objetivo**: Verificar compliance de cada fundo contra suas regras específicas.

**Funcionalidades**:
- Cálculo de índice de subordinação (IS)
- Análise de concentração (sacado/cedente)
- Monitoramento de inadimplência (30/60/90 dias)
- Verificação de prazo médio da carteira
- Controle de limites customizados por pool

**Saída**: JSON detalhado com status de cada indicador

### 2. Dashboard Consolidado de Exceções
**Objetivo**: Visão executiva focada apenas em violações e alertas.

**Funcionalidades**:
- Filtrar apenas pools com problemas
- Priorizar por severidade (crítico/alto/médio)
- Indicar ações corretivas necessárias
- Mostrar prazos de cura disponíveis

**Saída**: JSON consolidado + visualização Excel

### 3. Análise Comparativa Temporal
**Objetivo**: Identificar tendências e deterioração de indicadores.

**Funcionalidades**:
- Comparar indicadores dia-a-dia
- Detectar novos desenquadramentos
- Identificar melhorias/pioras
- Projetar tendências futuras

**Saída**: Relatório de evolução com alertas preditivos

### 4. Análise de Fluxo de Caixa
**Objetivo**: Projetar recebimentos futuros considerando qualidade da carteira.

**Funcionalidades**:
- Segregar fluxo de adimplentes vs inadimplentes
- Aplicar probabilidades de recuperação por aging
- Considerar sazonalidade histórica
- Gerar cenários (base/otimista/pessimista)

**Saída**: Projeção mensal de recebimentos por 12 meses

### 5. Verificação de Liquidez para Amortizações
**Objetivo**: Garantir capacidade de pagamento das obrigações.

**Funcionalidades**:
- Cruzar fluxo projetado vs cronograma de amortizações
- Identificar gaps de liquidez futuros
- Sugerir ações preventivas
- Simular impacto de stress scenarios

**Saída**: Análise de cobertura com recomendações

## Requisitos Funcionais

### RF1: Processamento de Dados
- Ler arquivos CSV diários (dados dos pools)
- Processar XLSX com carteiras (até 100MB)
- Interpretar JSONs de configuração (escrituras)
- Suportar processamento incremental

### RF2: Cálculos de Monitoramento
- Precisão financeira (6 casas decimais)
- Fórmulas auditáveis e rastreáveis
- Suporte a regras customizadas por pool
- Performance <5s por pool

### RF3: Geração de Relatórios
- Formato JSON estruturado
- Exportação para Excel formatado
- Histórico consultável
- Visualizações gráficas básicas

### RF4: Sistema de Alertas
- Notificações por severidade
- Prazos de cura automáticos
- Escalação por tempo
- Log de ações tomadas

## Desafios de Negócio a Resolver

### 1. Heterogeneidade das Escrituras
**Problema**: Cada fundo tem regras únicas além do padrão.
**Impacto**: Dificulta automação e padronização.
**Solução**: Sistema modular com core (80%) + plugins (20%).

### 2. Qualidade dos Dados de Entrada
**Problema**: CSVs/XLSXs com formatos variáveis.
**Impacto**: Erros de parsing e cálculos incorretos.
**Solução**: Validação rigorosa + normalização automática.

### 3. Complexidade dos Cálculos de Recuperação
**Problema**: Estimar recuperação de inadimplentes.
**Impacto**: Projeções de fluxo irrealistas.
**Solução**: Machine learning com dados históricos.

### 4. Mudanças Regulatórias
**Problema**: Regras de compliance mudam com frequência.
**Impacto**: Sistema fica desatualizado rapidamente.
**Solução**: Configurações externalizadas + versionamento.

### 5. Integração com Processos Existentes
**Problema**: Usuários acostumados com Excel manual.
**Impacto**: Resistência à adoção.
**Solução**: Interface Excel familiar + migração gradual.

## Métricas de Sucesso

### Métricas de Adoção
- 100% dos gestores usando em 3 meses
- >50 consultas/dia ao sistema
- <2h treinamento necessário

### Métricas de Performance
- Redução de 80% no tempo de análise
- Zero erros de cálculo em produção
- <5 minutos para processar todos os pools

### Métricas de Negócio
- Redução de 90% em multas por desenquadramento
- Antecipação de 100% dos problemas de liquidez
- ROI positivo em 6 meses

## Critérios de Aceitação

### Para Monitoramento Individual
- [x] ✅ Sistema de carregamento robusto implementado
- [x] ✅ Validação e consistência de dados
- [x] ✅ Configurações por pool (ignore list, debug mode)
- [x] ✅ Auditoria sistemática de 100% dos pools
- [x] ✅ Integridade de dados verificada contra escrituras originais
- [x] ✅ Template padronizado v2.2 com 5 seções lógicas
- [x] ✅ Nomenclatura padronizada CSV ↔ JSON
- [x] ✅ Descoberta automática de pools funcional
- [ ] Processa 100% das regras da escritura
- [ ] Identifica todas as violações corretamente
- [ ] Gera relatório em <5 segundos
- [ ] Mantém histórico auditável

### Para Dashboard de Exceções
- [ ] Mostra apenas violações ativas
- [ ] Ordena por prioridade/severidade
- [ ] Indica ações corretivas claras
- [ ] Atualiza em tempo real

### Para Análise de Fluxo
- [ ] Projeta 12 meses futuros
- [ ] Aplica taxas de recuperação realistas
- [ ] Gera 3 cenários (base/otimista/pessimista)
- [ ] Considera sazonalidade

## Roadmap de Implementação

### Fase 1 (Atual): Fundação
- ✅ Sistema de monitoramento básico
- ✅ Processamento de dados core
- ✅ JSON otimizado para monitoramento
- ✅ Sistema de carregamento completo (data_loader.py)
- ✅ Fluxo de 9 etapas com debug/normal mode
- ✅ Sistema de ignore list e configurações
- 🔄 5 arquivos de monitoramento por natureza
- 🔄 Primeiros 2 monitores (subordinação, concentração)

### Fase 2: Expansão
- Todos os 24 monitores implementados
- Dashboard de exceções
- Análise temporal

### Fase 3: Inteligência
- Fluxo de caixa preditivo
- Análise de liquidez
- Machine learning para recuperação

### Fase 4: Integração
- APIs para sistemas externos
- Notificações automáticas
- Mobile dashboard

## Arquitetura de Monitoramento

### Nova Arquitetura Integrada com Enriquecimento Progressivo:

#### **Fluxo de Execução Centralizado:**
```
orchestrator.run_monitoring(pool_name=None)
    ↓
data_loader.load_pool_data() [CENTRALIZADOR]
    ├── Descoberta automática de pools
    ├── Carregamento de JSONs de configuração
    ├── Modo DEBUG (test_pools.json) vs NORMAL
    └── Filtros (ignore_pools.json)
    ↓
Execução sequencial por pool:
    ├── monitor_subordinacao [não modifica dados]
    ├── monitor_inadimplencia [ENRIQUECE DataFrame XLSX]
    └── futuros monitores [usam dados enriquecidos]
```

#### **Monitores Base (80% comum a todos os pools)**
Localizados em `/monitor/base/`:

1. **monitor_subordinacao.py** (2 eventos base) ✅ **IMPLEMENTADO**
   - `subordinacao` - Índice mínimo de subordinação
   - `subordinacao_critica` - Limite crítico de subordinação

2. **monitor_inadimplencia.py** (2 eventos base) ✅ **PRONTO**
   - `inadimplencia_30_dias` - Atraso 30+ dias
   - `inadimplencia_90_dias` - Atraso 90+ dias
   - **ENRIQUECE DADOS**: adiciona `dias_atraso`, `grupo_de_risco`

3. **monitor_concentracao.py** (2 eventos base)
   - `concentracao_sacados` - Limite individual por sacado
   - `concentracao_cedentes` - Limite individual por cedente

4. **monitor_elegibilidade.py** (1 evento base)
   - `elegibilidade_geral` - Critérios gerais de elegibilidade

**EVENTOS CUSTOMIZADOS IDENTIFICADOS (20+):**

**🔧 Específicos por Pool:**
- **SuperSim**: `recovery_rate_mensal`, `concentracao_socinal`, `concentracao_bmp`
- **UpVendas**: `substituicao_pix_parcelado`, `despesas_adicionais_maximas`
- **AFA**: `sacados_especificos_bmp`, `sacados_especificos_socinal`

**🔧 Legacy (Comum a múltiplos pools):**
- `vencimento_medio_carteira` - Prazo médio ponderado
- `valor_minimo_direito_creditorio` - Valor mínimo por ativo
- `valor_individual_maximo` - Valor máximo por ativo
- `taxa_minima_financiamento` - 150% CDI mínimo
- `periodo_formacao_carteira` - Período inicial
- `prazo_limite_aquisicoes` - Limite temporal para aquisições
- `provisoes_pdd` - Cálculo por grupos de risco
- `fundos_reserva` - Reservas obrigatórias
- `concentracao_top_10_sacados` - Top 10 sacados
- `concentracao_top_10_cedentes` - Top 10 cedentes
- `vencimento_individual_minimo` - Vencimento mínimo
- `vencimento_individual_maximo` - Vencimento máximo

#### **Monitores Customizados (20% específicos por pool)**
Localizados em `/monitor/custom/{pool_id}/`:

- **SuperSim Pool 1**: `supersim_pool_1_recovery_rate.py` - Taxa de recuperação de inadimplentes
- **AFA Pool 1**: `afa_pool_1_sacados_especificos.py` - Limites especiais para sacados (BMP, SOCINAL)
- **Outros pools**: Monitores específicos conforme necessário

### Sistema de Descoberta Automática Integrado
- **data_loader como Centralizador**: Unifica descoberta, configuração e carregamento
- **Modo DEBUG vs NORMAL**: Flexibilidade para desenvolvimento e produção
- **Execução Condicional**: Monitores executam apenas se configurados nos JSONs
- **Enriquecimento Progressivo**: Dados calculados ficam disponíveis para monitores seguintes

#### **Benefícios da Nova Arquitetura:**
- ✅ **Performance**: Cálculos feitos uma vez, reutilizados sempre
- ✅ **Flexibilidade**: Pool específico ou todos os pools
- ✅ **Escalabilidade**: Novos monitores integram automaticamente
- ✅ **Auditoria**: Dados enriquecidos persistem na memória

## Métricas de Progresso do Projeto

### Status de Implementação por Pool:
| Pool | JSON Config | Auditoria | Nomenclatura | Descoberta Auto | Status |
|------|-------------|-----------|--------------|----------------|---------|
| LeCapital Pool #1 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 50% |
| AFA Pool #1 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 45% |
| SuperSim Pool #1 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 45% |
| Credmei Pool #1 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 40% |
| Formento Pool #3 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 40% |
| Up Vendas Pool #2 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 40% |
| a55 Pool #2 | ✅ v2.2 | ✅ 100% | ✅ Padronizada | ✅ Funcional | 40% |

### Status Geral do Sistema:
- **Pools mapeados**: 7/7 (100%)
- **JSONs de configuração**: 7/7 (100% - template v2.2)
- **Auditoria de dados**: 7/7 (100% - verificados contra escrituras originais)
- **Integridade**: 100% - Zero dados inventados ou incorretos
- **Nomenclatura padronizada**: 7/7 (100% - matching CSV ↔ JSON)
- **Descoberta automática**: ✅ Funcional (44 pools processados)
- **Template padronizado**: v2.2 com 5 seções lógicas
- **Estrutura organizada**: ✅ `/base/`, `/custom/`, `/utils/`
- **Arquitetura integrada**: ✅ data_loader + orchestrator definida
- **Monitores base prontos**: 2/5 (subordinação ✅, inadimplência ✅)
- **Estratégia de enriquecimento**: ✅ Definida (dias_atraso, grupo_de_risco)
- **Monitores customizados identificados**: 20+ arquivos mapeados
- **Utilitários**: 5/5 (100% funcionais)
- **Sistema de orquestração**: ✅ Arquitetura centralizada
- **Cobertura de monitoramento**: 65% (infraestrutura + 2 monitores prontos)

### Próximas Entregas:

#### **Fase 2a: Integração Imediata (Julho 2025)**
- Implementação de `orchestrator.run_monitoring()` master
- Integração de `monitor_inadimplencia.py` com enriquecimento
- Testes da arquitetura integrada completa

#### **Fase 2b: Expansão (Q3 2025)**  
- Implementação de `monitor_concentracao.py` e `monitor_elegibilidade.py`
- Dashboard consolidado de exceções
- Análise temporal automatizada

#### **Fase 3: Inteligência (Q4 2025)**  
- Análise preditiva de fluxo de caixa
- Sistema de alertas antecipados
- Projeções de liquidez com cenários

#### **Fase 4: Integração (Q1 2026)**
- APIs para sistemas externos
- Notificações automáticas por email/SMS  
- Dashboard mobile para gestores

## Stakeholders
- **Usuários Primários**: Gestores de portfólio, analistas de risco
- **Usuários Secundários**: Compliance, auditoria, investidores
- **Patrocinador**: Diretor de Operações
- **Time Técnico**: 2 desenvolvedores, 1 analista de negócios

## Status do Projeto
- **Última atualização**: 2025-07-11
- **Sessão atual**: Padronização de nomenclatura e descoberta automática
- **Próxima revisão**: Implementação dos 24 monitores de compliance
- **Status atual**: 7/7 pools com nomenclatura padronizada e descoberta automática funcional
- **Conquistas**: Template v2.2, auditoria completa, matching CSV ↔ JSON 100%
- **Capacidade atual**: Sistema processa 44 pools automaticamente