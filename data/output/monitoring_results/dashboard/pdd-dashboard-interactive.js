/**
 * AmFi Dashboard PDD - Sistema Interativo de Drilldown
 * Funcionalidades avançadas para análise hierárquica de PDD/Inadimplência
 * 
 * @author AmFi Development Team
 * @version 2.0
 * @date 2025-07-22
 */

// ============================================================================
// CONFIGURAÇÕES GLOBAIS E ESTADO
// ============================================================================

const PDDDashboard = {
    // Estado global da aplicação
    state: {
        expandedGroups: new Set(),
        expandedCedentes: new Set(),
        loadedData: new Map(),
        autoExpandThreshold: 5.0, // % PDD para auto-expand
        trendingData: new Map(),
        tooltipCache: new Map(),
        lastUpdateTime: null,
        activeModals: new Set()
    },

    // Configurações de API
    config: {
        baseUrl: '/api/pdd',
        endpoints: {
            hierarchy: '/hierarchy',
            trends: '/trends',
            worstAssets: '/cedente/{cedente_id}/worst_assets',
            methodology: '/methodology',
            history: '/history',
            cedenteBreakdown: '/cedente_breakdown',
            alerts: '/alerts',
            reports: '/reports',
            contacts: '/contacts'
        },
        timeouts: {
            default: 30000,
            hierarchy: 60000,
            trends: 15000
        },
        retryAttempts: 3,
        cacheTimeout: 300000 // 5 minutos
    },

    // Configurações visuais
    ui: {
        animations: {
            expand: 300,
            fadeIn: 200,
            slideDown: 250,
            bounce: 400
        },
        thresholds: {
            critical: 10.0,
            warning: 5.0,
            good: 2.0
        },
        colors: {
            critical: '#e53e3e',
            warning: '#ffa500',
            good: '#38a169',
            neutral: '#666'
        }
    }
};

// ============================================================================
// FUNÇÕES PRINCIPAIS DE DRILLDOWN
// ============================================================================

/**
 * Toggle grupo de risco - expand/collapse com lazy loading
 * @param {string} poolId - ID do pool
 * @param {string} groupId - ID do grupo de risco
 * @param {Element} element - Elemento DOM clicado
 */
async function toggleGroup(poolId, groupId, element = null) {
    try {
        const groupKey = `${poolId}_${groupId}`;
        const isExpanded = PDDDashboard.state.expandedGroups.has(groupKey);

        // Feedback visual imediato
        if (element) {
            element.classList.add('loading');
            updateToggleIcon(element, 'loading');
        }

        if (!isExpanded) {
            // Expandir grupo
            await expandGroup(poolId, groupId, element);
            PDDDashboard.state.expandedGroups.add(groupKey);
            logInteraction('expand_group', { poolId, groupId });
        } else {
            // Contrair grupo
            collapseGroup(poolId, groupId, element);
            PDDDashboard.state.expandedGroups.delete(groupKey);
            logInteraction('collapse_group', { poolId, groupId });
        }

        // Atualizar ícone de toggle
        if (element) {
            element.classList.remove('loading');
            updateToggleIcon(element, isExpanded ? 'collapsed' : 'expanded');
        }

    } catch (error) {
        console.error('Erro ao toggle grupo:', error);
        showErrorNotification(`Erro ao ${isExpanded ? 'contrair' : 'expandir'} grupo: ${error.message}`);
        
        if (element) {
            element.classList.remove('loading');
            updateToggleIcon(element, 'error');
        }
    }
}

/**
 * Toggle cedente individual - expand/collapse com carregamento de ativos
 * @param {string} poolId - ID do pool
 * @param {string} cedenteId - ID do cedente
 * @param {Element} element - Elemento DOM clicado
 */
async function toggleCedente(poolId, cedenteId, element = null) {
    try {
        const cedenteKey = `${poolId}_${cedenteId}`;
        const isExpanded = PDDDashboard.state.expandedCedentes.has(cedenteKey);

        // Feedback visual imediato
        if (element) {
            element.classList.add('loading');
            updateToggleIcon(element, 'loading');
        }

        if (!isExpanded) {
            // Expandir cedente
            await expandCedente(poolId, cedenteId, element);
            PDDDashboard.state.expandedCedentes.add(cedenteKey);
            logInteraction('expand_cedente', { poolId, cedenteId });
        } else {
            // Contrair cedente
            collapseCedente(poolId, cedenteId, element);
            PDDDashboard.state.expandedCedentes.delete(cedenteKey);
            logInteraction('collapse_cedente', { poolId, cedenteId });
        }

        // Atualizar ícone de toggle
        if (element) {
            element.classList.remove('loading');
            updateToggleIcon(element, isExpanded ? 'collapsed' : 'expanded');
        }

    } catch (error) {
        console.error('Erro ao toggle cedente:', error);
        showErrorNotification(`Erro ao ${isExpanded ? 'contrair' : 'expandir'} cedente: ${error.message}`);
        
        if (element) {
            element.classList.remove('loading');
            updateToggleIcon(element, 'error');
        }
    }
}

/**
 * Mostrar detalhes do ativo em modal interativo
 * @param {string} poolId - ID do pool
 * @param {string} ativoId - ID do ativo
 * @param {Object} ativoData - Dados do ativo (opcional)
 */
async function showAtivoDetails(poolId, ativoId, ativoData = null) {
    try {
        // Mostrar modal de loading
        showLoadingModal('Carregando detalhes do ativo...');

        let ativoDetails = ativoData;
        
        // Carregar dados se não fornecidos
        if (!ativoDetails) {
            ativoDetails = await loadAtivoDetails(poolId, ativoId);
        }

        // Fechar modal de loading
        hideLoadingModal();

        // Criar e mostrar modal de detalhes
        const modalId = `ativo_details_${ativoId}_${Date.now()}`;
        createAtivoDetailsModal(modalId, ativoDetails);
        showModal(modalId);

        // Registrar interação
        logInteraction('view_ativo_details', { poolId, ativoId });

    } catch (error) {
        hideLoadingModal();
        console.error('Erro ao mostrar detalhes do ativo:', error);
        showErrorNotification(`Erro ao carregar detalhes do ativo: ${error.message}`);
    }
}

// ============================================================================
// SISTEMA DE LAZY LOADING HIERÁRQUICO
// ============================================================================

/**
 * Carregar dados hierárquicos do pool via API com cache inteligente
 * @param {string} poolId - ID do pool
 * @param {Object} options - Opções de carregamento
 */
async function loadHierarchicalData(poolId, options = {}) {
    const {
        level = 'full', // 'summary', 'groups', 'cedentes', 'full'
        forceRefresh = false,
        includeHistory = false,
        includeTrends = true
    } = options;

    const cacheKey = `hierarchy_${poolId}_${level}`;
    
    // Verificar cache se não for refresh forçado
    if (!forceRefresh && PDDDashboard.state.loadedData.has(cacheKey)) {
        const cachedData = PDDDashboard.state.loadedData.get(cacheKey);
        const cacheAge = Date.now() - cachedData.timestamp;
        
        if (cacheAge < PDDDashboard.config.cacheTimeout) {
            console.log(`Dados hierárquicos carregados do cache: ${poolId}`);
            return cachedData.data;
        }
    }

    try {
        // Construir URL da API
        const url = `${PDDDashboard.config.baseUrl}/${poolId}${PDDDashboard.config.endpoints.hierarchy}`;
        const params = new URLSearchParams({
            level,
            include_history: includeHistory,
            include_trends: includeTrends
        });

        // Fazer requisição com timeout configurado
        const response = await fetchWithTimeout(`${url}?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        }, PDDDashboard.config.timeouts.hierarchy);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Validar estrutura dos dados
        validateHierarchicalData(data);

        // Armazenar no cache
        PDDDashboard.state.loadedData.set(cacheKey, {
            data,
            timestamp: Date.now()
        });

        console.log(`Dados hierárquicos carregados da API: ${poolId}`);
        return data;

    } catch (error) {
        console.error('Erro ao carregar dados hierárquicos:', error);
        throw new Error(`Falha ao carregar dados: ${error.message}`);
    }
}

/**
 * Expandir grupo de risco com carregamento assíncrono
 */
async function expandGroup(poolId, groupId, element) {
    const containerId = `group_${poolId}_${groupId}_content`;
    let container = document.getElementById(containerId);

    // Criar container se não existir
    if (!container) {
        container = createGroupContainer(poolId, groupId);
        const parentRow = element?.closest('tr');
        if (parentRow) {
            insertAfterRow(parentRow, container);
        }
    }

    // Mostrar indicador de loading
    container.innerHTML = createLoadingIndicator('Carregando cedentes do grupo...');
    container.style.display = 'table-row';

    try {
        // Carregar dados do grupo
        const groupData = await loadGroupData(poolId, groupId);
        
        // Renderizar conteúdo do grupo
        const groupContent = generateGroupContent(groupData, poolId, groupId);
        
        // Animação de entrada
        await animateElementIn(container, () => {
            container.innerHTML = groupContent;
        });

        // Auto-expand cedentes com PDD alto se habilitado
        if (groupData.auto_expand_cedentes) {
            await autoExpandHighRiskCedentes(poolId, groupId, groupData.cedentes);
        }

    } catch (error) {
        container.innerHTML = createErrorIndicator(`Erro ao carregar grupo: ${error.message}`);
        throw error;
    }
}

/**
 * Expandir cedente com carregamento de ativos
 */
async function expandCedente(poolId, cedenteId, element) {
    const containerId = `cedente_${poolId}_${cedenteId}_content`;
    let container = document.getElementById(containerId);

    // Criar container se não existir
    if (!container) {
        container = createCedenteContainer(poolId, cedenteId);
        const parentRow = element?.closest('tr');
        if (parentRow) {
            insertAfterRow(parentRow, container);
        }
    }

    // Mostrar indicador de loading
    container.innerHTML = createLoadingIndicator('Carregando ativos do cedente...');
    container.style.display = 'table-row';

    try {
        // Carregar dados do cedente
        const cedenteData = await loadCedenteData(poolId, cedenteId);
        
        // Renderizar conteúdo do cedente
        const cedenteContent = generateCedenteContent(cedenteData, poolId, cedenteId);
        
        // Animação de entrada
        await animateElementIn(container, () => {
            container.innerHTML = cedenteContent;
        });

        // Inicializar tooltips nos novos elementos
        initializeTooltips(container);

    } catch (error) {
        container.innerHTML = createErrorIndicator(`Erro ao carregar cedente: ${error.message}`);
        throw error;
    }
}

// ============================================================================
// SMART AUTO-EXPAND BASEADO EM NÍVEIS DE RISCO
// ============================================================================

/**
 * Aplicar defaults inteligentes baseados em risk level
 * @param {string} poolId - ID do pool
 * @param {Object} options - Opções de configuração
 */
async function smartDefaults(poolId, options = {}) {
    const {
        autoExpandThreshold = PDDDashboard.state.autoExpandThreshold,
        maxAutoExpanded = 5,
        prioritizeViolations = true,
        includeTrends = true
    } = options;

    try {
        console.log(`Aplicando smart defaults para pool: ${poolId}`);
        
        // Carregar dados resumidos do pool
        const poolData = await loadHierarchicalData(poolId, { 
            level: 'summary',
            includeTrends 
        });

        let expandedCount = 0;
        const expandPromises = [];

        // Ordenar grupos por criticidade se priorizar violações
        const groups = prioritizeViolations 
            ? sortGroupsByCriticality(poolData.grupos_risco)
            : poolData.grupos_risco;

        for (const group of groups) {
            if (expandedCount >= maxAutoExpanded) break;

            // Verificar se grupo deve ser auto-expandido
            const shouldAutoExpand = group.pdd_percentual >= autoExpandThreshold ||
                                   group.status === 'violado' ||
                                   (group.trending && group.trending.direction === 'up');

            if (shouldAutoExpand) {
                console.log(`Auto-expandindo grupo: ${group.id} (PDD: ${group.pdd_percentual}%)`);
                
                // Encontrar elemento do grupo no DOM
                const groupElement = document.querySelector(`[data-group-id="${group.id}"]`);
                if (groupElement) {
                    expandPromises.push(toggleGroup(poolId, group.id, groupElement));
                    expandedCount++;
                }
            }
        }

        // Executar expansões em paralelo
        await Promise.allSettled(expandPromises);
        
        console.log(`Smart defaults aplicado: ${expandedCount} grupos expandidos`);
        
        // Aplicar auto-expand para cedentes dentro dos grupos expandidos
        await autoExpandHighRiskCedentes(poolId);

    } catch (error) {
        console.error('Erro ao aplicar smart defaults:', error);
        showWarningNotification('Não foi possível aplicar expansão automática');
    }
}

/**
 * Auto-expandir cedentes com alto risco
 */
async function autoExpandHighRiskCedentes(poolId, groupId = null, cedentesList = null) {
    try {
        let cedentes = cedentesList;
        
        // Se não fornecido, buscar cedentes dos grupos expandidos
        if (!cedentes) {
            cedentes = await getHighRiskCedentesFromExpandedGroups(poolId, groupId);
        }

        const expandPromises = [];
        let expandedCount = 0;
        const maxCedentesAutoExpand = 3;

        for (const cedente of cedentes) {
            if (expandedCount >= maxCedentesAutoExpand) break;

            const shouldAutoExpand = cedente.pdd_percentual >= PDDDashboard.state.autoExpandThreshold ||
                                   cedente.status === 'critical' ||
                                   cedente.ativos_vencidos > 0;

            if (shouldAutoExpand) {
                const cedenteElement = document.querySelector(`[data-cedente-id="${cedente.id}"]`);
                if (cedenteElement) {
                    expandPromises.push(toggleCedente(poolId, cedente.id, cedenteElement));
                    expandedCount++;
                }
            }
        }

        await Promise.allSettled(expandPromises);
        console.log(`Auto-expandidos ${expandedCount} cedentes de alto risco`);

    } catch (error) {
        console.error('Erro ao auto-expandir cedentes:', error);
    }
}

// ============================================================================
// SISTEMA DE TRENDING INDICATORS COM ANIMAÇÕES
// ============================================================================

/**
 * Atualizar indicadores de tendência com animações
 * @param {string} poolId - ID do pool (opcional, se null atualiza todos)
 */
async function updateTrends(poolId = null) {
    try {
        console.log('Atualizando trending indicators...');
        
        const pools = poolId ? [poolId] : getAllPoolIds();
        const updatePromises = [];

        for (const pool of pools) {
            updatePromises.push(updatePoolTrends(pool));
        }

        const results = await Promise.allSettled(updatePromises);
        
        // Processar resultados
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const failed = results.filter(r => r.status === 'rejected').length;

        console.log(`Trending indicators atualizados: ${successful} sucessos, ${failed} falhas`);
        
        // Atualizar timestamp da última atualização
        PDDDashboard.state.lastUpdateTime = Date.now();
        
        // Atualizar indicador visual
        updateLastUpdateIndicator();

    } catch (error) {
        console.error('Erro ao atualizar trends:', error);
        showErrorNotification('Erro ao atualizar indicadores de tendência');
    }
}

/**
 * Atualizar trends de um pool específico
 */
async function updatePoolTrends(poolId) {
    try {
        // Carregar dados de trending
        const trendData = await fetchTrendData(poolId);
        
        // Armazenar no estado
        PDDDashboard.state.trendingData.set(poolId, {
            data: trendData,
            timestamp: Date.now()
        });

        // Atualizar elementos visuais
        updateTrendingElements(poolId, trendData);
        
        return trendData;

    } catch (error) {
        console.error(`Erro ao atualizar trends do pool ${poolId}:`, error);
        throw error;
    }
}

/**
 * Atualizar elementos visuais de trending
 */
function updateTrendingElements(poolId, trendData) {
    const trendElements = document.querySelectorAll(`[data-pool-id="${poolId}"] .trend-indicator`);
    
    trendElements.forEach(element => {
        const entityId = element.dataset.entityId;
        const entityType = element.dataset.entityType;
        
        const trend = trendData.find(t => t.entity_id === entityId && t.entity_type === entityType);
        
        if (trend) {
            updateTrendIndicator(element, trend);
        }
    });
}

/**
 * Atualizar indicador de trend individual com animação
 */
function updateTrendIndicator(element, trendInfo) {
    // Remover classes antigas
    element.classList.remove('trend-up', 'trend-down', 'trend-stable', 'trend-new');
    
    // Aplicar nova classe baseada na direção
    const direction = trendInfo.direction;
    element.classList.add(`trend-${direction}`);
    
    // Atualizar conteúdo
    const arrow = getTrendArrow(direction);
    const percentage = Math.abs(trendInfo.change_percentage).toFixed(1);
    
    element.innerHTML = `
        <span class="trend-arrow">${arrow}</span>
        <span class="trend-value">${percentage}%</span>
        <span class="trend-period">${trendInfo.period}</span>
    `;
    
    // Animação de destaque
    if (trendInfo.significant_change) {
        element.classList.add('trend-highlight');
        setTimeout(() => {
            element.classList.remove('trend-highlight');
        }, PDDDashboard.ui.animations.bounce);
    }
    
    // Tooltip dinâmico
    updateTrendTooltip(element, trendInfo);
}

// ============================================================================
// SISTEMA DE HOVER TOOLTIPS
// ============================================================================

/**
 * Inicializar tooltips em elementos
 * @param {Element} container - Container para buscar elementos com tooltip
 */
function initializeTooltips(container = document) {
    const tooltipElements = container.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        // Remover listeners antigos se existirem
        element.removeEventListener('mouseenter', handleTooltipShow);
        element.removeEventListener('mouseleave', handleTooltipHide);
        element.removeEventListener('mousemove', handleTooltipMove);
        
        // Adicionar novos listeners
        element.addEventListener('mouseenter', handleTooltipShow);
        element.addEventListener('mouseleave', handleTooltipHide);
        element.addEventListener('mousemove', handleTooltipMove);
    });
}

/**
 * Mostrar tooltip com informações contextuais
 */
async function handleTooltipShow(event) {
    const element = event.target;
    const tooltipType = element.dataset.tooltip;
    const entityId = element.dataset.entityId;
    const poolId = element.dataset.poolId;

    try {
        // Buscar conteúdo do tooltip (com cache)
        const tooltipContent = await getTooltipContent(tooltipType, entityId, poolId);
        
        // Criar e mostrar tooltip
        showTooltip(event, tooltipContent);
        
    } catch (error) {
        console.error('Erro ao carregar tooltip:', error);
        showTooltip(event, 'Erro ao carregar informações');
    }
}

/**
 * Ocultar tooltip
 */
function handleTooltipHide(event) {
    hideTooltip();
}

/**
 * Mover tooltip junto com o cursor
 */
function handleTooltipMove(event) {
    moveTooltip(event);
}

/**
 * Obter conteúdo do tooltip com cache inteligente
 */
async function getTooltipContent(type, entityId, poolId) {
    const cacheKey = `tooltip_${type}_${entityId}_${poolId}`;
    
    // Verificar cache
    if (PDDDashboard.state.tooltipCache.has(cacheKey)) {
        const cached = PDDDashboard.state.tooltipCache.get(cacheKey);
        const cacheAge = Date.now() - cached.timestamp;
        
        if (cacheAge < 30000) { // Cache de 30 segundos para tooltips
            return cached.content;
        }
    }

    let content = '';

    switch (type) {
        case 'pdd_detail':
            content = await generatePDDTooltip(entityId, poolId);
            break;
        case 'cedente_info':
            content = await generateCedenteTooltip(entityId, poolId);
            break;
        case 'ativo_status':
            content = await generateAtivoTooltip(entityId, poolId);
            break;
        case 'trend_info':
            content = await generateTrendTooltip(entityId, poolId);
            break;
        default:
            content = 'Informação não disponível';
    }

    // Armazenar no cache
    PDDDashboard.state.tooltipCache.set(cacheKey, {
        content,
        timestamp: Date.now()
    });

    return content;
}

// ============================================================================
// QUICK ACTIONS (ALERTS, REPORTS, CONTATOS)
// ============================================================================

/**
 * Mostrar menu de quick actions
 * @param {string} entityType - Tipo da entidade (pool, cedente, ativo)
 * @param {string} entityId - ID da entidade
 * @param {Element} triggerElement - Elemento que disparou a ação
 */
function showQuickActions(entityType, entityId, triggerElement) {
    // Criar menu contextual
    const menuId = `quick_actions_${entityType}_${entityId}_${Date.now()}`;
    const menu = createQuickActionsMenu(menuId, entityType, entityId);
    
    // Posicionar menu
    positionContextMenu(menu, triggerElement);
    
    // Adicionar ao DOM e mostrar
    document.body.appendChild(menu);
    showContextMenu(menu);
    
    // Auto-fechar após 10 segundos
    setTimeout(() => {
        if (document.body.contains(menu)) {
            hideContextMenu(menu);
        }
    }, 10000);
}

/**
 * Configurar alert para entidade
 */
async function configureAlert(entityType, entityId, poolId) {
    try {
        showLoadingModal('Configurando alerta...');
        
        // Carregar configurações atuais de alerta
        const currentConfig = await fetchAlertConfig(entityType, entityId, poolId);
        
        hideLoadingModal();
        
        // Mostrar modal de configuração
        const modalId = `alert_config_${entityType}_${entityId}`;
        createAlertConfigModal(modalId, entityType, entityId, poolId, currentConfig);
        showModal(modalId);
        
    } catch (error) {
        hideLoadingModal();
        console.error('Erro ao configurar alerta:', error);
        showErrorNotification('Erro ao carregar configurações de alerta');
    }
}

/**
 * Gerar relatório da entidade
 */
async function generateReport(entityType, entityId, poolId, reportType = 'detailed') {
    try {
        showLoadingModal('Gerando relatório...');
        
        // Fazer requisição para gerar relatório
        const response = await fetchWithTimeout(`${PDDDashboard.config.baseUrl}${PDDDashboard.config.endpoints.reports}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entity_type: entityType,
                entity_id: entityId,
                pool_id: poolId,
                report_type: reportType,
                include_charts: true,
                include_history: true
            })
        }, PDDDashboard.config.timeouts.default);

        if (!response.ok) {
            throw new Error(`Erro na geração do relatório: ${response.statusText}`);
        }

        const reportData = await response.json();
        
        hideLoadingModal();
        
        // Se relatório é um arquivo, fazer download
        if (reportData.download_url) {
            downloadFile(reportData.download_url, reportData.filename);
            showSuccessNotification('Relatório gerado com sucesso');
        } else {
            // Se relatório é HTML, mostrar em nova janela
            showReportWindow(reportData.html_content);
        }
        
        logInteraction('generate_report', { entityType, entityId, poolId, reportType });
        
    } catch (error) {
        hideLoadingModal();
        console.error('Erro ao gerar relatório:', error);
        showErrorNotification('Erro ao gerar relatório');
    }
}

/**
 * Mostrar informações de contato
 */
async function showContactInfo(entityType, entityId, poolId) {
    try {
        showLoadingModal('Carregando contatos...');
        
        // Buscar informações de contato
        const contactData = await fetchWithTimeout(`${PDDDashboard.config.baseUrl}${PDDDashboard.config.endpoints.contacts}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entity_type: entityType,
                entity_id: entityId,
                pool_id: poolId
            })
        }, PDDDashboard.config.timeouts.default);

        if (!contactData.ok) {
            throw new Error(`Erro ao buscar contatos: ${contactData.statusText}`);
        }

        const contacts = await contactData.json();
        
        hideLoadingModal();
        
        // Mostrar modal com informações de contato
        const modalId = `contact_info_${entityType}_${entityId}`;
        createContactInfoModal(modalId, entityType, entityId, contacts);
        showModal(modalId);
        
    } catch (error) {
        hideLoadingModal();
        console.error('Erro ao carregar contatos:', error);
        showErrorNotification('Erro ao carregar informações de contato');
    }
}

// ============================================================================
// FUNÇÃO SHOWPDDTAB (FALTANTE DO SISTEMA EXISTENTE)
// ============================================================================

/**
 * Mostrar aba específica do PDD (grupos, cedentes, metodologia)
 * @param {string} tabName - Nome da aba (grupos, cedentes, metodologia)
 * @param {string} containerId - ID do container principal
 */
async function showPDDTab(tabName, containerId) {
    try {
        // Extrair poolId do containerId
        const poolId = extractPoolIdFromContainerId(containerId);
        
        // Atualizar botões de aba
        const tabButtons = document.querySelectorAll(`#${containerId} .pdd-tab-button`);
        tabButtons.forEach(button => {
            button.classList.remove('active');
            if (button.textContent.toLowerCase().includes(tabName)) {
                button.classList.add('active');
            }
        });

        // Ocultar todas as abas
        const tabContents = document.querySelectorAll(`#${containerId} .pdd-tab-content`);
        tabContents.forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });

        // Mostrar aba selecionada
        const targetTab = document.getElementById(`${containerId}_${tabName}`);
        if (targetTab) {
            targetTab.style.display = 'block';
            
            // Carregar conteúdo se necessário
            if (targetTab.innerHTML.trim() === '' || targetTab.innerHTML.includes('Carregando...')) {
                await loadPDDTabContent(tabName, containerId, poolId);
            }
            
            // Animação de entrada
            setTimeout(() => {
                targetTab.classList.add('active');
            }, 50);
        }

        logInteraction('show_pdd_tab', { tabName, containerId, poolId });

    } catch (error) {
        console.error('Erro ao mostrar aba PDD:', error);
        showErrorNotification(`Erro ao carregar aba ${tabName}`);
    }
}

/**
 * Carregar conteúdo específico da aba PDD
 */
async function loadPDDTabContent(tabName, containerId, poolId) {
    const targetTab = document.getElementById(`${containerId}_${tabName}`);
    if (!targetTab) return;

    // Mostrar indicador de loading
    targetTab.innerHTML = createLoadingIndicator(`Carregando ${tabName}...`);

    try {
        let content = '';

        switch (tabName) {
            case 'grupos':
                content = await loadPDDGruposContent(poolId);
                break;
            case 'cedentes':
                content = await loadPDDCedentesContent(poolId);
                break;
            case 'metodologia':
                content = await loadPDDMetodologiaContent(poolId);
                break;
            default:
                throw new Error(`Aba desconhecida: ${tabName}`);
        }

        // Animar entrada do conteúdo
        await animateElementIn(targetTab, () => {
            targetTab.innerHTML = content;
        });

        // Inicializar tooltips no novo conteúdo
        initializeTooltips(targetTab);

    } catch (error) {
        targetTab.innerHTML = createErrorIndicator(`Erro ao carregar ${tabName}: ${error.message}`);
        throw error;
    }
}

// ============================================================================
// FUNÇÕES AUXILIARES E UTILITÁRIOS
// ============================================================================

/**
 * Fazer requisição HTTP com timeout personalizado
 */
async function fetchWithTimeout(url, options = {}, timeout = 30000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout');
        }
        throw error;
    }
}

/**
 * Validar estrutura dos dados hierárquicos
 */
function validateHierarchicalData(data) {
    if (!data || typeof data !== 'object') {
        throw new Error('Dados inválidos: estrutura não é um objeto');
    }

    const required = ['pool_id', 'grupos_risco'];
    for (const field of required) {
        if (!(field in data)) {
            throw new Error(`Dados inválidos: campo obrigatório '${field}' não encontrado`);
        }
    }

    if (!Array.isArray(data.grupos_risco)) {
        throw new Error('Dados inválidos: grupos_risco deve ser um array');
    }
}

/**
 * Animar entrada de elemento
 */
async function animateElementIn(element, updateCallback) {
    return new Promise((resolve) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';
        
        if (updateCallback) {
            updateCallback();
        }
        
        requestAnimationFrame(() => {
            element.style.transition = `opacity ${PDDDashboard.ui.animations.fadeIn}ms ease, transform ${PDDDashboard.ui.animations.fadeIn}ms ease`;
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
            
            setTimeout(() => {
                element.style.transition = '';
                resolve();
            }, PDDDashboard.ui.animations.fadeIn);
        });
    });
}

/**
 * Criar indicador de loading
 */
function createLoadingIndicator(message = 'Carregando...') {
    return `
        <div class="loading-indicator">
            <div class="loading-spinner"></div>
            <span class="loading-text">${message}</span>
        </div>
    `;
}

/**
 * Criar indicador de erro
 */
function createErrorIndicator(message) {
    return `
        <div class="error-indicator">
            <span class="error-icon">⚠️</span>
            <span class="error-text">${message}</span>
            <button onclick="location.reload()" class="error-retry-btn">Tentar Novamente</button>
        </div>
    `;
}

/**
 * Mostrar notificação de sucesso
 */
function showSuccessNotification(message) {
    showNotification(message, 'success');
}

/**
 * Mostrar notificação de erro
 */
function showErrorNotification(message) {
    showNotification(message, 'error');
}

/**
 * Mostrar notificação de aviso
 */
function showWarningNotification(message) {
    showNotification(message, 'warning');
}

/**
 * Mostrar notificação genérica
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    // Adicionar ao DOM
    document.body.appendChild(notification);

    // Auto-remover após duração especificada
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

/**
 * Registrar interação do usuário para analytics
 */
function logInteraction(action, data = {}) {
    try {
        const logEntry = {
            timestamp: new Date().toISOString(),
            action,
            data,
            user_agent: navigator.userAgent,
            url: window.location.href
        };

        // Enviar para endpoint de analytics (se configurado)
        if (PDDDashboard.config.analyticsEndpoint) {
            fetch(PDDDashboard.config.analyticsEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logEntry)
            }).catch(error => {
                console.warn('Erro ao enviar analytics:', error);
            });
        }

        // Log local para debug
        console.log('Interação registrada:', logEntry);

    } catch (error) {
        console.warn('Erro ao registrar interação:', error);
    }
}

/**
 * Inicializar sistema quando DOM estiver pronto
 */
function initializePDDDashboard() {
    console.log('Inicializando AmFi PDD Dashboard Interactive System v2.0');

    // Inicializar tooltips existentes
    initializeTooltips();

    // Aplicar smart defaults para pools visíveis
    const poolElements = document.querySelectorAll('[data-pool-id]');
    poolElements.forEach(element => {
        const poolId = element.dataset.poolId;
        if (poolId && !PDDDashboard.state.expandedGroups.size) {
            // Aplicar smart defaults apenas se nenhum grupo estiver expandido
            smartDefaults(poolId).catch(error => {
                console.warn(`Erro ao aplicar smart defaults para ${poolId}:`, error);
            });
        }
    });

    // Configurar auto-refresh de trends
    setInterval(() => {
        updateTrends().catch(error => {
            console.warn('Erro no auto-refresh de trends:', error);
        });
    }, 60000); // A cada minuto

    // Fechar modais ao clicar fora
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            hideModal(event.target.id);
        }
    });

    // Fechar menus contextuais ao clicar fora
    document.addEventListener('click', (event) => {
        const contextMenus = document.querySelectorAll('.context-menu');
        contextMenus.forEach(menu => {
            if (!menu.contains(event.target)) {
                hideContextMenu(menu);
            }
        });
    });

    console.log('AmFi PDD Dashboard Interactive System inicializado com sucesso');
}

// ============================================================================
// AUTO-INICIALIZAÇÃO
// ============================================================================

// Inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePDDDashboard);
} else {
    initializePDDDashboard();
}

// Exportar funções principais para uso global
window.PDDDashboard = PDDDashboard;
window.toggleGroup = toggleGroup;
window.toggleCedente = toggleCedente;
window.showAtivoDetails = showAtivoDetails;
window.loadHierarchicalData = loadHierarchicalData;
window.smartDefaults = smartDefaults;
window.updateTrends = updateTrends;
window.showPDDTab = showPDDTab;
window.showQuickActions = showQuickActions;
window.configureAlert = configureAlert;
window.generateReport = generateReport;
window.showContactInfo = showContactInfo;

console.log('AmFi PDD Dashboard Interactive System v2.0 carregado');