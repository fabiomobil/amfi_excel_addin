# AmFi Dashboard PDD - Sistema Interativo de Drilldown

## 📋 Visão Geral

Sistema JavaScript avançado para análise interativa hierárquica de PDD/Inadimplência no dashboard AmFi. Oferece funcionalidades completas de drilldown, lazy loading, auto-expand inteligente, tooltips contextuais e quick actions.

**Versão:** 2.0  
**Data:** 2025-07-22  
**Arquivos:**
- `pdd-dashboard-interactive.js` - JavaScript principal
- `pdd-dashboard-interactive.css` - Estilos complementares
- `README_PDD_INTERACTIVE.md` - Documentação

## 🚀 Funcionalidades Principais

### 1. Drilldown Interativo
- **toggleGroup(poolId, groupId, element)** - Expand/collapse grupos de risco
- **toggleCedente(poolId, cedenteId, element)** - Expand/collapse cedentes individuais  
- **showAtivoDetails(poolId, ativoId, ativoData)** - Modal com detalhes completos do ativo

### 2. Lazy Loading Hierárquico
- **loadHierarchicalData(poolId, options)** - Carregamento assíncrono com cache inteligente
- Sistema de cache com timeout configurável (5 minutos por padrão)
- Validação automática da estrutura de dados recebidos
- Retry automático com backoff exponencial

### 3. Smart Auto-Expand
- **smartDefaults(poolId, options)** - Expansão automática baseada em níveis de risco
- Auto-expand para grupos com PDD > 5% (configurável)
- Priorização de violações ativas
- Limite máximo de expansões simultâneas

### 4. Trending Indicators
- **updateTrends(poolId)** - Atualização de indicadores de tendência com animações
- Auto-refresh a cada minuto
- Animações diferenciadas por tipo de mudança (up, down, stable)
- Cache local para otimização de performance

### 5. Sistema de Tooltips
- Tooltips contextuais com informações detalhadas
- Cache de 30 segundos para otimização
- Suporte a múltiplos tipos: PDD, cedente, ativo, trend
- Posicionamento automático inteligente

### 6. Quick Actions
- **showQuickActions(entityType, entityId, triggerElement)** - Menu contextual
- **configureAlert(entityType, entityId, poolId)** - Configuração de alertas
- **generateReport(entityType, entityId, poolId, reportType)** - Geração de relatórios
- **showContactInfo(entityType, entityId, poolId)** - Informações de contato

### 7. Função PDD Tabs (Correção)
- **showPDDTab(tabName, containerId)** - Navegação entre abas (grupos, cedentes, metodologia)
- Carregamento lazy do conteúdo das abas
- Animações suaves de transição

## 🔧 Instalação e Configuração

### 1. Inclusão dos Arquivos

```html
<!-- CSS (incluir no <head>) -->
<link rel="stylesheet" href="pdd-dashboard-interactive.css">

<!-- JavaScript (incluir antes do </body>) -->
<script src="pdd-dashboard-interactive.js"></script>
```

### 2. Configuração da API

O sistema espera que as seguintes APIs estejam disponíveis:

```
GET  /api/pdd/{pool_id}/hierarchy?level=full&include_history=true&include_trends=true
GET  /api/pdd/{pool_id}/trends
GET  /api/pdd/cedente/{cedente_id}/worst_assets
POST /api/pdd_history
POST /api/pdd_cedente_breakdown  
POST /api/pdd_methodology
POST /api/alerts
POST /api/reports
POST /api/contacts
```

### 3. Estrutura HTML Esperada

```html
<!-- Elementos devem ter data attributes apropriados -->
<tr class="pool-row" data-pool-id="pool123">
    <td class="clickable-element" onclick="toggleGroup('pool123', 'group456', this)">
        <span class="toggle-icon">▼</span>
        Grupo de Risco Alto
    </td>
    <!-- ... outras células ... -->
</tr>

<!-- Elementos com tooltips -->
<span data-tooltip="pdd_detail" data-entity-id="cedente123" data-pool-id="pool123">
    15.5% PDD
</span>

<!-- Botões de quick actions -->
<button onclick="showQuickActions('cedente', 'cedente123', this)">
    ⚡ Actions
</button>
```

## 📊 Estrutura de Dados Esperada

### Hierarquia do Pool
```json
{
  "pool_id": "string",
  "grupos_risco": [
    {
      "id": "string",
      "nome": "string", 
      "pdd_percentual": 15.5,
      "status": "violado|ok|warning",
      "cedentes": [
        {
          "id": "string",
          "nome": "string",
          "pdd_percentual": 8.2,
          "ativos_vencidos": 5,
          "status": "critical|warning|ok"
        }
      ],
      "auto_expand_cedentes": true,
      "trending": {
        "direction": "up|down|stable",
        "change_percentage": 2.1
      }
    }
  ],
  "metadata": {
    "total_pools": 46,
    "last_updated": "2025-07-22T10:30:00Z"
  }
}
```

### Dados de Trending
```json
[
  {
    "entity_id": "string",
    "entity_type": "group|cedente|ativo", 
    "direction": "up|down|stable|new",
    "change_percentage": 2.1,
    "period": "7d|30d|90d",
    "significant_change": true
  }
]
```

## 🎛️ Configuração Avançada

### Personalização do PDDDashboard

```javascript
// Alterar threshold para auto-expand
PDDDashboard.state.autoExpandThreshold = 8.0; // Default: 5.0

// Configurar timeouts de API
PDDDashboard.config.timeouts.hierarchy = 90000; // 90 segundos

// Alterar URLs base
PDDDashboard.config.baseUrl = '/api/custom/pdd';

// Configurar cache timeout
PDDDashboard.config.cacheTimeout = 600000; // 10 minutos
```

### Callbacks Personalizados

```javascript
// Hook para ações pós-expansão
PDDDashboard.hooks = {
    afterGroupExpand: (poolId, groupId, data) => {
        console.log('Grupo expandido:', groupId);
        // Lógica customizada
    },
    beforeDataLoad: (poolId, options) => {
        console.log('Carregando dados para:', poolId);
        // Mostrar indicador customizado
    }
};
```

## 🎨 Personalização Visual

### Classes CSS Disponíveis

```css
/* Estados de loading */
.loading-indicator { /* Indicador de carregamento */ }
.loading { /* Estado de loading para elementos */ }

/* Trending indicators */  
.trend-up { /* Tendência de alta */ }
.trend-down { /* Tendência de baixa */ }
.trend-stable { /* Tendência estável */ }
.trend-highlight { /* Destaque para mudanças significativas */ }

/* Tooltips */
.tooltip { /* Container do tooltip */ }
.tooltip-title { /* Título do tooltip */ }
.tooltip-value { /* Valores no tooltip */ }

/* Modals */
.modal { /* Container do modal */ }
.modal-content { /* Conteúdo do modal */ }
.modal-header { /* Cabeçalho do modal */ }

/* Quick actions */
.context-menu { /* Menu contextual */ }
.context-menu-item { /* Item do menu */ }

/* Notificações */
.notification { /* Container da notificação */ }
.notification-success { /* Notificação de sucesso */ }
.notification-error { /* Notificação de erro */ }
```

### Cores e Temas

```css
/* Variáveis CSS (adicionar ao início do seu CSS) */
:root {
    --pdd-primary: #667eea;
    --pdd-danger: #e53e3e;
    --pdd-warning: #d69e2e;
    --pdd-success: #38a169;
    --pdd-neutral: #666;
}
```

## 🔍 Debugging e Troubleshooting

### Console Logs
O sistema fornece logs detalhados no console:
```javascript
// Ativar logs verbosos
PDDDashboard.config.debug = true;

// Verificar estado atual
console.log('Estado expandido:', PDDDashboard.state.expandedGroups);
console.log('Cache de dados:', PDDDashboard.state.loadedData);
```

### Problemas Comuns

1. **Funções não encontradas**
   - Verificar se o script foi carregado corretamente
   - Confirmar que `window.PDDDashboard` está disponível

2. **APIs retornando erro**
   - Verificar URLs das APIs no network tab
   - Confirmar estrutura de dados retornados

3. **Elementos não respondem ao clique**
   - Verificar se elementos têm `data-*` attributes corretos
   - Confirmar que event handlers estão sendo anexados

4. **Tooltips não aparecem**
   - Verificar se `initializeTooltips()` foi chamado
   - Confirmar estrutura HTML dos elementos

## 📈 Performance e Otimização

### Melhores Práticas

1. **Cache Inteligente**
   ```javascript
   // Forçar refresh apenas quando necessário
   await loadHierarchicalData(poolId, { forceRefresh: true });
   ```

2. **Lazy Loading**
   ```javascript
   // Carregar apenas o nível necessário
   await loadHierarchicalData(poolId, { level: 'summary' });
   ```

3. **Debounce para Updates Frequentes**
   ```javascript
   // Evitar múltiplas chamadas simultâneas
   const debouncedUpdate = debounce(updateTrends, 1000);
   ```

### Métricas de Performance

- **Cache Hit Rate**: Monitorar via `PDDDashboard.state.loadedData.size`
- **API Response Time**: Logs automáticos no console
- **Memory Usage**: Limpeza automática de cache expirado

## 🔐 Segurança

### Validações Implementadas

1. **Sanitização de Input**: Todos os parâmetros são sanitizados
2. **Validação de Estrutura**: Dados da API são validados antes do uso
3. **CSRF Protection**: Headers `X-Requested-With` incluídos
4. **Timeout Protection**: Timeouts configuráveis para todas as requisições

### Headers de Segurança Recomendados
```
Content-Security-Policy: script-src 'self' 'unsafe-inline'
X-Frame-Options: DENY  
X-Content-Type-Options: nosniff
```

## 📱 Responsividade

O sistema é totalmente responsivo com:
- Breakpoints para mobile (< 768px)
- Tooltips redimensionados para telas pequenas
- Modais adaptáveis
- Menus contextuais otimizados para touch

## 🧪 Testes

### Testes Manuais Recomendados

1. **Funcionalidade Básica**
   - [ ] Toggle de grupos funciona
   - [ ] Toggle de cedentes funciona  
   - [ ] Modals de detalhes abrem
   - [ ] Tooltips aparecem no hover

2. **Performance**
   - [ ] Lazy loading funciona corretamente
   - [ ] Cache está operacional
   - [ ] Sem memory leaks após uso prolongado

3. **Responsividade**
   - [ ] Funciona em mobile
   - [ ] Tooltips se ajustam à tela
   - [ ] Modais são scrolláveis

## 🤝 Contribuição

Para contribuir com melhorias:

1. Documentar novas funcionalidades
2. Manter compatibilidade com versões anteriores
3. Adicionar testes apropriados
4. Seguir padrões de código estabelecidos

## 📞 Suporte

Para suporte técnico:
- Verificar logs no console do navegador
- Confirmar estrutura de dados da API
- Testar em ambiente isolado
- Consultar esta documentação

---

**AmFi Development Team - 2025**