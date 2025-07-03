# 🚨 MONITORING GAPS DETECTED

Found 124 unimplemented monitors across 7 pools

## Summary by Category
- evento_monitoramento: 58 monitors
- vencimento_antecipado: 54 monitors
- mecanismo_recuperacao: 10 monitors
- obrigacao_cura: 2 monitors

## Detailed Gap Analysis

### ❌ `vencimento_medio_carteira`
- **Category**: evento_monitoramento
- **Description**: Máximo 90 dias corridos - vencimento médio da carteira
- **Affected Pools**: a55_pool_cartao_2, afa_pool_1, credmei_pool_1, formento_pool_3, lecapital_pool_1, upvendas_pool_2
- **Priority**: HIGH

### ❌ `periodo_formacao_carteira`
- **Category**: evento_monitoramento
- **Description**: 90 dias corridos - período para aplicação dos critérios a cada integralização
- **Affected Pools**: a55_pool_cartao_2, afa_pool_1, formento_pool_3, lecapital_pool_1, supersim_pool_1, upvendas_pool_2
- **Priority**: HIGH

### ❌ `vencimento_protesto_titulos`
- **Category**: vencimento_antecipado
- **Description**: Protesto de títulos da Emissora acima de R$ 500.000,00
- **Affected Pools**: a55_pool_cartao_2, afa_pool_1, credmei_pool_1, formento_pool_3, lecapital_pool_1, upvendas_pool_2
- **Priority**: HIGH

### ❌ `vencimento_inadimplemento_pecuniario`
- **Category**: vencimento_antecipado
- **Description**: Descumprimento de qualquer obrigação pecuniária
- **Affected Pools**: a55_pool_cartao_2, credmei_pool_1, formento_pool_3, upvendas_pool_2
- **Priority**: HIGH

### ❌ `inadimplencia_percentual`
- **Category**: evento_monitoramento
- **Description**: Máximo 4% - direitos creditórios em atraso de 30+ dias
- **Affected Pools**: afa_pool_1, lecapital_pool_1, upvendas_pool_2
- **Priority**: HIGH

### ❌ `inadimplencia_90_dias`
- **Category**: evento_monitoramento
- **Description**: Máximo 2% - direitos creditórios em atraso de 90+ dias
- **Affected Pools**: afa_pool_1, formento_pool_3, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_uso_inadequado_recursos`
- **Category**: vencimento_antecipado
- **Description**: Uso dos recursos em desacordo com a destinação
- **Affected Pools**: afa_pool_1, formento_pool_3, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_interrupcao_atividades_originador`
- **Category**: vencimento_antecipado
- **Description**: Interrupção das atividades do Originador por mais de 20 dias corridos
- **Affected Pools**: afa_pool_1, formento_pool_3, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_incapacidade_originacao`
- **Category**: vencimento_antecipado
- **Description**: Originador sem capacidade de originar novos Direitos Creditórios elegíveis
- **Affected Pools**: afa_pool_1, formento_pool_3, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_inadimplemento_nao_pecuniario`
- **Category**: vencimento_antecipado
- **Description**: Descumprimento de qualquer obrigação não pecuniária
- **Affected Pools**: credmei_pool_1, formento_pool_3, upvendas_pool_2
- **Priority**: HIGH

### ❌ `recovery_substituicao_obrigatoria`
- **Category**: mecanismo_recuperacao
- **Description**: Originador deve substituir direitos creditórios adquiridos em desacordo
- **Affected Pools**: a55_pool_cartao_2, credmei_pool_1
- **Priority**: HIGH

### ❌ `vencimento_gravame_direitos_creditorios`
- **Category**: vencimento_antecipado
- **Description**: Constituição de Gravame sobre os Direitos Creditórios cedidos
- **Affected Pools**: a55_pool_cartao_2, upvendas_pool_2
- **Priority**: HIGH

### ❌ `vencimento_reorganizacao_societaria`
- **Category**: vencimento_antecipado
- **Description**: Qualquer reorganização societária da Emitente sem rebaixamento de rating
- **Affected Pools**: a55_pool_cartao_2, formento_pool_3
- **Priority**: HIGH

### ❌ `composicao_tipos_ativos`
- **Category**: evento_monitoramento
- **Description**: 100% duplicatas mercantis ou de serviço performadas
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `fundos_reserva`
- **Category**: evento_monitoramento
- **Description**: Reserva de Despesas R$ 25.000 + Reserva Extraordinária R$ 30.000
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `eventos_aceleracao`
- **Category**: evento_monitoramento
- **Description**: Eventos que causam vencimento antecipado automático ou com prazo de cura
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `criterios_elegibilidade`
- **Category**: evento_monitoramento
- **Description**: Verificação se novos ativos atendem todos os critérios de elegibilidade
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `investimentos_permitidos`
- **Category**: evento_monitoramento
- **Description**: Verificação se aplicações estão em ativos permitidos
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `conta_centralizadora`
- **Category**: evento_monitoramento
- **Description**: Verificação de funcionamento e movimentações da conta do Patrimônio Separado
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `contas_vinculadas`
- **Category**: evento_monitoramento
- **Description**: Monitoramento das contas escrow vinculadas ao Patrimônio Separado
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `valor_minimo_direito_creditorio`
- **Category**: evento_monitoramento
- **Description**: Valor mínimo de R$ 100,00 por Direito Creditório
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `taxa_minima_financiamento`
- **Category**: evento_monitoramento
- **Description**: Taxa mínima de 150% do CDI mensal
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_descumprimento_obrigacao_pecuniaria`
- **Category**: vencimento_antecipado
- **Description**: Descumprimento de qualquer obrigação pecuniária
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_descumprimento_obrigacao_nao_pecuniaria`
- **Category**: vencimento_antecipado
- **Description**: Descumprimento de qualquer obrigação não pecuniária
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_falencia_recuperacao_judicial`
- **Category**: vencimento_antecipado
- **Description**: Decretação de falência, recuperação judicial, liquidação ou dissolução
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_sentenca_judicial_nao_cumprida`
- **Category**: vencimento_antecipado
- **Description**: Não cumprimento de decisão judicial acima de R$ 10 milhões
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_nao_pagamento_direitos_creditorios`
- **Category**: vencimento_antecipado
- **Description**: Não pagamento de Direitos Creditórios que somam mais da metade do Valor Total da Emissão
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_constituicao_lastro_insuficiente`
- **Category**: vencimento_antecipado
- **Description**: Não constituição de lastro com ao menos 75% dos recursos em 90 dias
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_reducao_capital_social`
- **Category**: vencimento_antecipado
- **Description**: Redução de capital social, exceto para absorção de prejuízos
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_alteracao_transferencia_controle`
- **Category**: vencimento_antecipado
- **Description**: Alteração ou transferência do controle direto ou indireto
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_declaracoes_falsas`
- **Category**: vencimento_antecipado
- **Description**: Comprovação de declarações falsas, inconsistentes ou incorretas
- **Affected Pools**: afa_pool_1, lecapital_pool_1
- **Priority**: HIGH

### ❌ `vencimento_individual_minimo`
- **Category**: evento_monitoramento
- **Description**: Vencimento mínimo 3 dias da submissão
- **Affected Pools**: credmei_pool_1, supersim_pool_1
- **Priority**: HIGH

### ❌ `vencimento_individual_maximo`
- **Category**: evento_monitoramento
- **Description**: Vencimento máximo 230 dias da submissão
- **Affected Pools**: credmei_pool_1, supersim_pool_1
- **Priority**: HIGH

### ❌ `valor_individual_minimo_urs`
- **Category**: evento_monitoramento
- **Description**: Valor mínimo R$ 1,00 por UR
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `valor_individual_maximo_urs`
- **Category**: evento_monitoramento
- **Description**: Valor máximo R$ 300.000,00 por UR
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `vencimento_individual_minimo_urs`
- **Category**: evento_monitoramento
- **Description**: Vencimento mínimo 5 dias da submissão
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `vencimento_individual_maximo_urs`
- **Category**: evento_monitoramento
- **Description**: Vencimento máximo 360 dias da submissão
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `taxa_media_minima_carteira`
- **Category**: evento_monitoramento
- **Description**: Taxa média mínima CDI + 5.5% a.a. ponderada pelo valor
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `investimentos_permitidos_limite`
- **Category**: evento_monitoramento
- **Description**: Máximo 20% do patrimônio em investimentos permitidos por 4 semanas consecutivas
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `vencimento_dividas_financeiras`
- **Category**: vencimento_antecipado
- **Description**: Dívidas financeiras acima de R$ 500.000,00 (individual ou agregado)
- **Affected Pools**: a55_pool_cartao_2
- **Priority**: MEDIUM

### ❌ `cura_recompra_direitos_creditorios`
- **Category**: obrigacao_cura
- **Description**: Cure obligation: recompra_direitos_creditorios
- **Affected Pools**: afa_pool_1
- **Priority**: MEDIUM

### ❌ `taxa_media_carteira`
- **Category**: evento_monitoramento
- **Description**: Taxa média mínima 1.8% ao mês ponderada pelo valor
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `valor_individual_minimo`
- **Category**: evento_monitoramento
- **Description**: Valor mínimo R$ 100,00 por Direito Creditório
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `valor_individual_maximo`
- **Category**: evento_monitoramento
- **Description**: Valor máximo R$ 500.000,00 por Direito Creditório
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `taxa_individual_minima`
- **Category**: evento_monitoramento
- **Description**: Taxa mínima 1.55% ao mês por Direito Creditório
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `prazo_substituicao_inelegivel`
- **Category**: evento_monitoramento
- **Description**: Emissora deve substituir direitos inelegíveis em 10 dias úteis
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `recovery_obrigacao_recompra_cedente`
- **Category**: mecanismo_recuperacao
- **Description**: Duplicatas mercantis com obrigação de recompra do cedente original
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `recovery_cobranca_contrapartes`
- **Category**: mecanismo_recuperacao
- **Description**: Reenquadramento através de cobrança das contrapartes
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `vencimento_alteracao_controle_acionario`
- **Category**: vencimento_antecipado
- **Description**: Alteração do controle acionário da Emissora
- **Affected Pools**: credmei_pool_1
- **Priority**: MEDIUM

### ❌ `inadimplencia_30_dias`
- **Category**: evento_monitoramento
- **Description**: Máximo 2% - direitos creditórios em atraso de 30+ dias (veto aquisições)
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `recovery_procedimentos_cobranca`
- **Category**: mecanismo_recuperacao
- **Description**: Recovery mechanism: procedimentos_cobranca
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `vencimento_falencia_liquidacao`
- **Category**: vencimento_antecipado
- **Description**: Decretação de falência ou liquidação da Emissora ou Originador
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `vencimento_sentenca_judicial`
- **Category**: vencimento_antecipado
- **Description**: Decisão judicial não cumprida acima de R$ 10 milhões
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `vencimento_inadimplencia_maior`
- **Category**: vencimento_antecipado
- **Description**: Inadimplência superior a 50% do Valor Total da Emissão
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `vencimento_falha_reenquadramento`
- **Category**: vencimento_antecipado
- **Description**: Não realização de ações para reenquadramento do Índice de Subordinação
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `vencimento_lastro_insuficiente`
- **Category**: vencimento_antecipado
- **Description**: Não constituição de lastro com ao menos 75% dos recursos em 90 dias
- **Affected Pools**: formento_pool_3
- **Priority**: MEDIUM

### ❌ `ordem_alocacao_recursos`
- **Category**: evento_monitoramento
- **Description**: Sequência obrigatória de pagamentos (15 prioridades)
- **Affected Pools**: lecapital_pool_1
- **Priority**: MEDIUM

### ❌ `substituicoes_obrigatorias`
- **Category**: evento_monitoramento
- **Description**: Substituição obrigatória por desconformidade com critérios
- **Affected Pools**: lecapital_pool_1
- **Priority**: MEDIUM

### ❌ `amortizacao_excedente_subordinada`
- **Category**: evento_monitoramento
- **Description**: Direito de amortização quando subordinação 5% acima do mínimo
- **Affected Pools**: lecapital_pool_1
- **Priority**: MEDIUM

### ❌ `cura_substituicao_direitos_creditorios`
- **Category**: obrigacao_cura
- **Description**: Cure obligation: substituicao_direitos_creditorios
- **Affected Pools**: lecapital_pool_1
- **Priority**: MEDIUM

### ❌ `atraso_30_dias_direito_regresso`
- **Category**: evento_monitoramento
- **Description**: Direitos creditórios com 30+ dias de atraso elegíveis para regresso por fraude ou má formalização
- **Affected Pools**: supersim_pool_1
- **Priority**: MEDIUM

### ❌ `prazo_recompra_inelegivel`
- **Category**: evento_monitoramento
- **Description**: Originador deve recomprar/substituir direitos inelegíveis em 5 dias úteis
- **Affected Pools**: supersim_pool_1
- **Priority**: MEDIUM

### ❌ `recovery_direito_regresso`
- **Category**: mecanismo_recuperacao
- **Description**: Regresso contra o Originador em casos de inadimplências após 30 dias do vencimento por fraude ou má formalização
- **Affected Pools**: supersim_pool_1
- **Priority**: MEDIUM

### ❌ `recovery_recompra_obrigatoria`
- **Category**: mecanismo_recuperacao
- **Description**: Originador deve recomprar ou substituir direitos creditórios inelegíveis
- **Affected Pools**: supersim_pool_1
- **Priority**: MEDIUM

### ❌ `recovery_conta_cobranca`
- **Category**: mecanismo_recuperacao
- **Description**: Originador atua como cobrador em nome da Emissora
- **Affected Pools**: supersim_pool_1
- **Priority**: MEDIUM

### ❌ `substituicao_pix_parcelado`
- **Category**: evento_monitoramento
- **Description**: PIX Parcelado inadimplente deve ser substituído por URs em 5 dias úteis
- **Affected Pools**: upvendas_pool_2
- **Priority**: MEDIUM

### ❌ `recovery_recompra_pix_parcelado`
- **Category**: mecanismo_recuperacao
- **Description**: PIX Parcelado com obrigação de recompra do originador em caso de inadimplência
- **Affected Pools**: upvendas_pool_2
- **Priority**: MEDIUM

### ❌ `recovery_substituicao_pix_por_urs`
- **Category**: mecanismo_recuperacao
- **Description**: Originador deve substituir PIX Parcelado inadimplente por URs
- **Affected Pools**: upvendas_pool_2
- **Priority**: MEDIUM

### ❌ `vencimento_encerramento_conta_centralizadora`
- **Category**: vencimento_antecipado
- **Description**: Encerramento da conta centralizadora sem substituição adequada
- **Affected Pools**: upvendas_pool_2
- **Priority**: MEDIUM

### ❌ `vencimento_falencia_recuperacao`
- **Category**: vencimento_antecipado
- **Description**: Decretação de falência ou recuperação judicial da Emissora
- **Affected Pools**: upvendas_pool_2
- **Priority**: MEDIUM

### ❌ `vencimento_renuncia_destituicao_originador`
- **Category**: vencimento_antecipado
- **Description**: Renúncia ou destituição do Originador sem substituição em 15 dias
- **Affected Pools**: upvendas_pool_2
- **Priority**: MEDIUM


## 📝 Implementation Checklist

### evento_monitoramento
- [ ] Implement `vencimento_medio_carteira` for: a55_pool_cartao_2, afa_pool_1, credmei_pool_1, formento_pool_3, lecapital_pool_1, upvendas_pool_2
- [ ] Implement `valor_individual_minimo_urs` for: a55_pool_cartao_2
- [ ] Implement `valor_individual_maximo_urs` for: a55_pool_cartao_2
- [ ] Implement `vencimento_individual_minimo_urs` for: a55_pool_cartao_2
- [ ] Implement `vencimento_individual_maximo_urs` for: a55_pool_cartao_2
- [ ] Implement `taxa_media_minima_carteira` for: a55_pool_cartao_2
- [ ] Implement `periodo_formacao_carteira` for: a55_pool_cartao_2, afa_pool_1, formento_pool_3, lecapital_pool_1, supersim_pool_1, upvendas_pool_2
- [ ] Implement `investimentos_permitidos_limite` for: a55_pool_cartao_2
- [ ] Implement `inadimplencia_percentual` for: afa_pool_1, lecapital_pool_1, upvendas_pool_2
- [ ] Implement `inadimplencia_90_dias` for: afa_pool_1, formento_pool_3, lecapital_pool_1
- [ ] Implement `composicao_tipos_ativos` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `fundos_reserva` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `eventos_aceleracao` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `criterios_elegibilidade` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `investimentos_permitidos` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `conta_centralizadora` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `contas_vinculadas` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `valor_minimo_direito_creditorio` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `taxa_minima_financiamento` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `taxa_media_carteira` for: credmei_pool_1
- [ ] Implement `valor_individual_minimo` for: credmei_pool_1
- [ ] Implement `valor_individual_maximo` for: credmei_pool_1
- [ ] Implement `vencimento_individual_minimo` for: credmei_pool_1, supersim_pool_1
- [ ] Implement `vencimento_individual_maximo` for: credmei_pool_1, supersim_pool_1
- [ ] Implement `taxa_individual_minima` for: credmei_pool_1
- [ ] Implement `prazo_substituicao_inelegivel` for: credmei_pool_1
- [ ] Implement `inadimplencia_30_dias` for: formento_pool_3
- [ ] Implement `ordem_alocacao_recursos` for: lecapital_pool_1
- [ ] Implement `substituicoes_obrigatorias` for: lecapital_pool_1
- [ ] Implement `amortizacao_excedente_subordinada` for: lecapital_pool_1
- [ ] Implement `atraso_30_dias_direito_regresso` for: supersim_pool_1
- [ ] Implement `prazo_recompra_inelegivel` for: supersim_pool_1
- [ ] Implement `substituicao_pix_parcelado` for: upvendas_pool_2
### mecanismo_recuperacao
- [ ] Implement `recovery_substituicao_obrigatoria` for: a55_pool_cartao_2, credmei_pool_1
- [ ] Implement `recovery_obrigacao_recompra_cedente` for: credmei_pool_1
- [ ] Implement `recovery_cobranca_contrapartes` for: credmei_pool_1
- [ ] Implement `recovery_procedimentos_cobranca` for: formento_pool_3
- [ ] Implement `recovery_direito_regresso` for: supersim_pool_1
- [ ] Implement `recovery_recompra_obrigatoria` for: supersim_pool_1
- [ ] Implement `recovery_conta_cobranca` for: supersim_pool_1
- [ ] Implement `recovery_recompra_pix_parcelado` for: upvendas_pool_2
- [ ] Implement `recovery_substituicao_pix_por_urs` for: upvendas_pool_2
### vencimento_antecipado
- [ ] Implement `vencimento_gravame_direitos_creditorios` for: a55_pool_cartao_2, upvendas_pool_2
- [ ] Implement `vencimento_inadimplemento_pecuniario` for: a55_pool_cartao_2, credmei_pool_1, formento_pool_3, upvendas_pool_2
- [ ] Implement `vencimento_dividas_financeiras` for: a55_pool_cartao_2
- [ ] Implement `vencimento_protesto_titulos` for: a55_pool_cartao_2, afa_pool_1, credmei_pool_1, formento_pool_3, lecapital_pool_1, upvendas_pool_2
- [ ] Implement `vencimento_reorganizacao_societaria` for: a55_pool_cartao_2, formento_pool_3
- [ ] Implement `vencimento_descumprimento_obrigacao_pecuniaria` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_descumprimento_obrigacao_nao_pecuniaria` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_falencia_recuperacao_judicial` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_sentenca_judicial_nao_cumprida` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_uso_inadequado_recursos` for: afa_pool_1, formento_pool_3, lecapital_pool_1
- [ ] Implement `vencimento_nao_pagamento_direitos_creditorios` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_constituicao_lastro_insuficiente` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_interrupcao_atividades_originador` for: afa_pool_1, formento_pool_3, lecapital_pool_1
- [ ] Implement `vencimento_incapacidade_originacao` for: afa_pool_1, formento_pool_3, lecapital_pool_1
- [ ] Implement `vencimento_reducao_capital_social` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_alteracao_transferencia_controle` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_declaracoes_falsas` for: afa_pool_1, lecapital_pool_1
- [ ] Implement `vencimento_inadimplemento_nao_pecuniario` for: credmei_pool_1, formento_pool_3, upvendas_pool_2
- [ ] Implement `vencimento_alteracao_controle_acionario` for: credmei_pool_1
- [ ] Implement `vencimento_falencia_liquidacao` for: formento_pool_3
- [ ] Implement `vencimento_sentenca_judicial` for: formento_pool_3
- [ ] Implement `vencimento_inadimplencia_maior` for: formento_pool_3
- [ ] Implement `vencimento_falha_reenquadramento` for: formento_pool_3
- [ ] Implement `vencimento_lastro_insuficiente` for: formento_pool_3
- [ ] Implement `vencimento_encerramento_conta_centralizadora` for: upvendas_pool_2
- [ ] Implement `vencimento_falencia_recuperacao` for: upvendas_pool_2
- [ ] Implement `vencimento_renuncia_destituicao_originador` for: upvendas_pool_2
### obrigacao_cura
- [ ] Implement `cura_recompra_direitos_creditorios` for: afa_pool_1
- [ ] Implement `cura_substituicao_direitos_creditorios` for: lecapital_pool_1