# Dashboard AmFi - Guia Completo

## 📊 Visão Geral

Dashboard interativo web para monitoramento de pools de recebíveis com análise histórica e drilldown detalhado.

> **⚠️ ATUALIZAÇÃO IMPORTANTE (2025-07-24)**: Os comandos foram atualizados para a nova estrutura. 
> Use `python scripts/[nome_script].py` em vez dos comandos antigos. 
> O dashboard continua funcionando em `http://localhost:8080`.

## 🚀 Como Usar

### Executar Monitoramento
```bash
# Executar análise completa de todos os pools
python scripts/run_monitoring.py

# Forçar nova execução mesmo se já rodou hoje
python scripts/run_monitoring.py --force
```

### Geração do Dashboard
```bash
cd C:\amfi
python scripts/generate_dashboard.py
```

### Acesso
Abra o arquivo gerado: `C:\amfi\data\output\monitoring_results\dashboard\table_dashboard.html`

### Servidor de Dashboard (Opcional)
```bash
# Para acessar via navegador em http://localhost:8080
python scripts/run_dashboard.py
```

## 🎯 Funcionalidades Principais

### 1. Visão Geral (Header)
- **Data de Referência**: Última data processada
- **Pools Monitorados**: Total de pools ativos
- **Pools Violados**: Quantidade em violação
- **Taxa Compliance**: Percentual de conformidade

### 2. Seções do Dashboard (Todas Colapsíveis)

#### Seção Subordinação:
- **Pool**: Nome do pool
- **Status**: 
  - 🔴 **VIOLADO CRÍTICO**: Abaixo do limite crítico
  - 🟡 **VIOLADO MÍNIMO**: Entre crítico e mínimo
  - 🟢 **ENQUADRADO**: Acima do limite mínimo
- **Dias Consecutivos**: Tempo em violação
- **Valor Atual**: Percentual de subordinação atual
- **Limite Mínimo**: Limite regulatório
- **Limite Crítico**: Limite de alerta
- **Aporte/Saque**: Valor financeiro inteligente

#### Seção PDD/Inadimplência (Simplificada):
**Melhorias 2025-07-25:**
- **Colunas removidas**: "Metodologia" e "Ações" (desnecessárias)
- **Drilldown simplificado**: Clique no pool mostra cedentes diretamente
- **Foco essencial**: Pool, Status, Dias, PDD%, Limite, Margem
- **Performance otimizada**: Carregamento mais rápido

#### Seção Concentração (NOVA - Colapsível):
**Nova funcionalidade 2025-07-25:**
- **Agora colapsível**: Mesmo padrão visual das outras seções
- **Contagem de dias**: Dias consecutivos de violação implementada
- **Header padronizado**: Gradiente e ícone de expansão
- **Interface consistente**: Segue mesmo estilo do dashboard

#### Ordenação Padrão:
1. **Violados Críticos** (topo)
2. **Violados Mínimos** 
3. **Enquadrados** (base)

### 3. Análise Drilldown

**Como Acessar**: Clique em qualquer linha da tabela

#### Dados Financeiros Detalhados:
- **PL Atual**: Patrimônio Líquido
- **SR Atual**: Saldo de Recebíveis  
- **JR Atual**: Juros sobre Recebíveis

#### Histórico de Subordinação:
- **Últimos 7 dias**: Evolução temporal
- **Status por Data**: Mudanças de enquadramento
- **Valores IS**: Percentuais históricos
- **Valores Financeiros**: Aporte/saque por período

## 💰 Lógica Financeira

### Pools Violados
**Aporte para Enquadrar** = `max(aporte_mínimo, aporte_crítico)`

```python
# Cálculo do aporte necessário
if violacao_critica:
    aporte = (limite_critico - valor_atual) / 100 * pl_atual
else:  # violacao_minima
    aporte = (limite_minimo - valor_atual) / 100 * pl_atual
```

### Pools Enquadrados
**Saque Disponível** = `(valor_atual - limite_mínimo) / 100 * pl_atual`

```python
# Margem de segurança disponível para saque
margem = (subordinacao_atual - limite_minimo) / 100
saque_disponivel = margem * pl_atual
```

## 🎨 Interface Visual

### Design Atualizado (2025-07-25):
- **Logo SVG**: Exibido no header via caminho `/logo.svg`
- **Header Colapsível**: Todas as seções podem ser recolhidas/expandidas
- **Gradientes Consistentes**: Visual padronizado em todo o dashboard
- **Animações Suaves**: Transições CSS para melhor UX

### Códigos de Cor:
- **🔴 Vermelho**: Violações (crítica/mínima)
- **🟢 Verde**: Pools enquadrados
- **🟡 Amarelo**: Alertas e avisos

### Estados Visuais:
- **Hover Effects**: Destaque ao passar mouse
- **Row Highlighting**: Diferenciação de status
- **Responsive Design**: Adapta a diferentes telas
- **Seções Colapsíveis**: Clique no header para expandir/recolher

### Badges de Status:
- **VIOLADO CRÍTICO**: Fundo vermelho
- **VIOLADO MÍNIMO**: Fundo laranja
- **ENQUADRADO**: Fundo verde

## 📱 Recursos Técnicos

### Auto-refresh
- **Intervalo**: 5 minutos
- **Automático**: Recarrega página automaticamente
- **Manual**: F5 para atualização forçada

### Responsividade
- **Desktop**: Layout completo
- **Tablet**: Colunas adaptadas
- **Mobile**: Interface simplificada

### JavaScript
```javascript
// Toggle drilldown
function toggleDrilldown(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = element.style.display === 'none' ? 'table-row' : 'none';
}
```

## 📈 Interpretação de Dados

### Status de Violação

#### VIOLADO CRÍTICO
- **Risco**: Alto
- **Ação**: Aporte imediato necessário
- **Prazo**: Urgente (regulatório)

#### VIOLADO MÍNIMO  
- **Risco**: Médio
- **Ação**: Planejamento de aporte
- **Prazo**: Médio prazo

#### ENQUADRADO
- **Risco**: Baixo
- **Ação**: Manutenção ou possível saque
- **Prazo**: Monitoramento regular

### Dias Consecutivos
- **1-3 dias**: Situação pontual
- **4-7 dias**: Tendência preocupante  
- **8+ dias**: Problema estrutural

### Evolução Histórica
- **Melhoria**: Valores IS crescentes
- **Deterioração**: Valores IS decrescentes
- **Estabilidade**: Variação < 0.5%

## 🔧 Configuração e Customização

### Modificar Períodos Históricos
```python
# Em src/dashboard/generator.py
historico_dias = 7  # Alterar para mais/menos dias
```

### Personalizar Limites
```python
# Alterar thresholds de alerta
limite_dias_critico = 7  # Dias para alerta crítico
auto_refresh_interval = 300000  # 5 minutos em ms
```

### Adicionar Métricas
```python
# Incluir novos indicadores na tabela
indicadores_extras = ['concentracao', 'inadimplencia', 'pdd']
```

## 🛠️ Troubleshooting

### Dashboard Não Carrega
1. **Verificar arquivo**: Confirmar geração bem-sucedida
2. **Navegador**: Limpar cache (Ctrl+F5)
3. **Dados**: Verificar JSONs de origem

### Dados Desatualizados
1. **Regerar**: Execute `python scripts/generate_dashboard.py`
2. **Fonte**: Verificar data de referência no header
3. **Processamento**: Rodar `python scripts/run_monitoring.py` se necessário

### Performance Lenta
1. **Dados**: Reduzir período histórico
2. **Browser**: Usar Chrome/Firefox atualizados
3. **Arquivo**: Verificar tamanho do HTML gerado

### Drilldown Não Funciona
1. **JavaScript**: Verificar se JS está habilitado
2. **Console**: Verificar erros no F12
3. **Estrutura**: Validar IDs únicos dos elementos

## 📊 Métricas de Exemplo

### Dashboard Típico:
- **Pools Monitorados**: 7-77 (dependendo do modo)
- **Taxa Compliance**: 57-70%
- **Pools Violados**: 2-5 pools
- **Tamanho HTML**: 50-200KB
- **Tempo Carregamento**: <2 segundos

### Histórico Comum:
- **Variação IS**: ±0.1-0.5% por dia
- **Mudanças Status**: 1-2 pools por semana
- **Aporte Médio**: R$ 50K - R$ 2M por pool
- **Saque Disponível**: R$ 10K - R$ 1M por pool

## 🚀 Funcionalidades Futuras

### Em Desenvolvimento:
- **Filtros**: Por status, pool, período
- **Exportação**: PDF, Excel, CSV
- **Alertas**: Email automático para violações
- **Gráficos**: Evolução temporal visual
- **Comparação**: Múltiplos pools lado a lado

### Integração:
- **API REST**: Dados via JSON endpoint
- **WebSocket**: Updates em tempo real
- **Mobile App**: Versão nativa iOS/Android
- **Slack/Teams**: Notificações integradas