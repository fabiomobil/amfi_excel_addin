# Configurações de Pools - Escrituras JSON

Esta pasta contém as configurações JSON para monitoramento de cada pool, baseadas nas escrituras de debêntures originais.

## 📋 Status dos Pools

| Pool | Status | Versão | Auditoria | Última Atualização |
|------|--------|--------|-----------|-------------------|
| AFA Pool #1 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |
| Credmei Pool #1 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |
| Formento Pool #3 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |
| LeCapital Pool #1 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |
| SuperSim Pool #1 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |
| Up Vendas Pool #2 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |
| a55 Pool #2 | ✅ Ativo | v2.2 | 100% | 2025-07-11 |

**Total**: 7 pools ativos, 100% auditados contra escrituras originais

## 🏗️ Estrutura dos JSONs (Template v2.3)

Todos os JSONs seguem a estrutura padronizada v2.3, organizada em **6 seções lógicas**:

### 1. 🆔 IDENTIFICAÇÃO E METADADOS
Dados básicos de identificação do pool e metadados de auditoria

### 2. 💰 ESTRUTURA FINANCEIRA  
Core financeiro: valores, cronograma de pagamentos, remuneração das séries

### 3. 📏 REGRAS DE NEGÓCIO
Critérios específicos: provisões PDD, sacados elegíveis, períodos especiais

### 4. 🔍 SISTEMA DE MONITORAMENTO
Engine de monitoramento: 7 monitores base + triggers de aceleração + monitores customizados

### 5. ⚖️ PROCESSOS LEGAIS
Documentação detalhada de processos pós-violação extraídos das escrituras originais

### 6. 🏢 DADOS OPERACIONAIS
Entidades: prestador de serviços, originador, debenturistas

## 🎯 Monitores Implementados

### Monitores Base (7 eventos - 80% comum)
Presentes na maioria dos pools (limites variam por escritura):

1. **Subordinação** - Índice mínimo e crítico (ex: 25% e 20%, mas podem variar)
2. **Concentração** - Limites por sacado/cedente individual e top N (específicos por pool)
   - ✅ **Filtro automático**: Ignora "Amfi Digital Assets LTDA" (considerada "caixa")
   - ✅ **Análise sequencial**: Capacidade incremental com matriz de sobra
3. **Inadimplência + PDD** - Prazos variáveis (comumente 30d/90d) + Provisões por grupos de risco
4. **Vencimento Médio** - Prazo médio ponderado da carteira (limite específico por pool)
5. **Critérios de Elegibilidade** - Validação de ativos elegíveis (critérios por escritura)
6. **Operacional** - Reservas, triggers e outros (específicos por escritura)

**⚠️ IMPORTANTE**: Os limites e configurações são **específicos de cada escritura** - não há padrões fixos!

### Monitores Customizados (20+ identificados)
Específicos por pool conforme escritura:

- **SuperSim**: Recovery rate mensal (95%), limites BMP/SOCINAL
- **AFA**: Sacados específicos com limites diferenciados
- **UpVendas**: Substituição PIX→URs, despesas adicionais
- **Outros**: Vencimentos individuais, fundos de reserva, etc.

## 📋 Template para Novos Pools

```json
{
  "// ================================================": "",
  "// SEÇÃO 1: IDENTIFICAÇÃO E METADADOS": "",
  "// ================================================": "",

  "pool_id": "// OBRIGATÓRIO: {Originador} Pool #{numero}",
  "pool_name": "// OBRIGATÓRIO: Nome amigável do pool",
  "status": "ativo",
  "data_emissao": "// OBRIGATÓRIO: YYYY-MM-DD",
  "data_vencimento": "// OBRIGATÓRIO: YYYY-MM-DD",

  "metadata": {
    "versao": "2.3",
    "data_atualizacao": "// OBRIGATÓRIO: YYYY-MM-DD",
    "fonte_original": "// OBRIGATÓRIO: Nome do PDF da escritura",
    "schema_version": "monitoring_v2",
    "completude": "// OBRIGATÓRIO: ex: '100%'",
    "// INSTRUÇÃO_AUDITORIA": "SEMPRE usar escritura original como fonte única de verdade"
  },

  "// ================================================": "",
  "// SEÇÃO 2: ESTRUTURA FINANCEIRA": "",
  "// ================================================": "",

  "valores": {
    "total_emissao": "// OBRIGATÓRIO: float sem separadores",
    "senior": "// OBRIGATÓRIO: float",
    "subordinada": "// OBRIGATÓRIO: float",
    "reserva_despesas": "// OPCIONAL: float ou null",
    "reserva_extraordinaria": "// OPCIONAL: float ou null"
  },

  "cronograma_pagamentos": {
    "carencia_meses": "// OPCIONAL: integer ou null",
    "inicio_amortizacao": "// OBRIGATÓRIO: YYYY-MM-DD",
    "cronograma_amortizacao": [
      {
        "// FORMATO_CRÍTICO": "Percentual SEMPRE em decimal: 1.0 = 100%",
        "data": "// OBRIGATÓRIO: YYYY-MM-DD",
        "percentual": "// OBRIGATÓRIO: decimal ex: 0.055556"
      }
    ]
  },

  "remuneracao": {
    "series_senior": {
      "tipo": "// OBRIGATÓRIO: 'pos_fixado' ou 'pre_fixado'",
      "indexador": "// OBRIGATÓRIO: ex: 'Taxa_DI'",
      "premio_risco": "// OBRIGATÓRIO: decimal ex: 0.065",
      "base_calculo": "// OBRIGATÓRIO: ex: 252",
      "formula": "// OPCIONAL: descrição textual"
    },
    "series_subordinadas": {
      "tipo": "// OBRIGATÓRIO: geralmente 'residual'",
      "descricao": "// OBRIGATÓRIO: descrição do cálculo"
    }
  },

  "// ================================================": "",
  "// SEÇÃO 3: REGRAS DE NEGÓCIO": "",
  "// ================================================": "",

  "provisoes_pdd": {
    "grupos_risco": {
      "AA": {"atraso_max_dias": 0, "provisao_pct": 0.000},
      "A": {"atraso_max_dias": 15, "provisao_pct": 0.005},
      "B": {"atraso_max_dias": 30, "provisao_pct": 0.010},
      "C": {"atraso_max_dias": 60, "provisao_pct": 0.030},
      "D": {"atraso_max_dias": 90, "provisao_pct": 0.100},
      "E": {"atraso_max_dias": 120, "provisao_pct": 0.300},
      "F": {"atraso_max_dias": 150, "provisao_pct": 0.500},
      "G": {"atraso_max_dias": 180, "provisao_pct": 0.700},
      "H": {"atraso_max_dias": 999, "provisao_pct": 1.000}
    }
  },

  "sacados_elegiveis": [
    "// OPCIONAL: Array de strings com sacados pré-aprovados"
  ],

  "periodos_especiais": {
    "formacao_carteira": {
      "dias": "// integer: duração",
      "inicio": "// YYYY-MM-DD",
      "fim": "// YYYY-MM-DD",
      "regras_especiais": ["// array de regras especiais"]
    },
    "carencia_amortizacao": {
      "meses": "// integer",
      "inicio": "// YYYY-MM-DD", 
      "fim": "// YYYY-MM-DD"
    },
    "limite_aquisicoes": {
      "meses": "// integer",
      "data_limite": "// YYYY-MM-DD"
    }
  },

  "// ================================================": "",
  "// SEÇÃO 4: SISTEMA DE MONITORAMENTO": "",
  "// ================================================": "",

  "monitoramentos_ativos": [
    {
      "id": "subordinacao",
      "tipo": "subordinacao",
      "ativo": true,
      "frequencia": "diaria",
      "prioridade": "critica",
      "limites": {
        "minimo": "// OBRIGATÓRIO: decimal ex: 0.25",
        "critico": "// OBRIGATÓRIO: decimal ex: 0.20",
        "calculo": "subordinada / (senior + subordinada)",
        "acao_violacao": "amortizacao_extraordinaria",
        "prazo_cura_dias": "// integer ex: 5",
        "tipo_prazo": "// 'uteis' ou 'corridos'"
      },
      "campos_necessarios": ["sr", "jr"],
      "funcao_calculo": "calc_subordinacao"
    },
    {
      "id": "concentracao",
      "tipo": "concentracao", 
      "ativo": true,
      "frequencia": "diaria",
      "prioridade": "alta",
      "limites": [
        {
          "tipo": "individual",
          "entidade": "sacado",
          "limite": "// decimal ex: 0.35"
        },
        {
          "tipo": "top_n",
          "entidade": "sacado",
          "n": 10,
          "limite": "// decimal ex: 1.00"
        }
      ],
      "campos_necessarios": ["sacado", "cedente", "valor_presente"],
      "funcao_calculo": "calc_concentracao"
    }
    // ... outros monitores base
  ],

  "triggers_aceleracao": {
    "obrigacao_pecuniaria": {
      "prazo_cura_dias": "// integer",
      "tipo_prazo": "// 'uteis' ou 'corridos'",
      "automatico": "// boolean",
      "notificacao_requerida": "// boolean"
    },
    "concentracao_violacao": {
      "prazo_cura_dias": "// integer ex: 30",
      "tipo_prazo": "// 'uteis' ou 'corridos'",
      "automatico": "// boolean - geralmente false",
      "processo_detalhado_ref": "// string: 'processos_legais.concentracao_violacao'"
    }
    // ... outros triggers
  },

  "// ================================================": "",
  "// SEÇÃO 5: PROCESSOS LEGAIS": "",
  "// ================================================": "",

  "processos_legais": {
    "// DOCUMENTAÇÃO": "Processos legais detalhados extraídos das escrituras originais",
    "// FONTE_VERDADE": "SEMPRE usar escritura original como fonte única de verdade",
    
    "concentracao_violacao": {
      "tipo_evento": "// string: ex: 'evento_avaliacao'",
      "classificacao": "// string: ex: 'Anexo V - Eventos de Avaliação, item (viii)'",
      "prazo_cura": {
        "dias": "// integer: dias para corrigir violação",
        "tipo": "// string: 'uteis' ou 'corridos'",
        "descricao": "// string: descrição do prazo"
      },
      "pos_violacao": {
        "assembleia": {
          "convocacao_prazo_dias": "// integer: ex: 3",
          "tipo_prazo": "// string: 'uteis' ou 'corridos'",
          "responsavel": "// string: ex: 'emissora'",
          "descricao": "// string: descrição do processo"
        },
        "votacao": {
          "votantes": "// string: ex: 'serie_senior'", 
          "maioria_requerida": "// string: ex: 'simples'",
          "objeto_decisao": "// string: ex: 'vencimento_antecipado'",
          "descricao": "// string: descrição do processo"
        },
        "renuncia": {
          "prazo_dias": "// integer: ex: 5",
          "tipo_prazo": "// string: 'uteis' ou 'corridos'",
          "direito_de": "// string: ex: 'serie_senior'",
          "descricao": "// string: descrição do direito"
        }
      },
      "base_legal": "// string: referência exata da escritura",
      "aditamentos": [
        "// array: lista de aditamentos que alteram o processo"
      ],
      "texto_original": "// string: texto exato da escritura (opcional)"
    },
    "subordinacao_violacao": {
      "// TEMPLATE": "Mesmo padrão acima para outros tipos de violação",
      "tipo_evento": "// ex: 'evento_vencimento_antecipado'",
      "prazo_cura": {"dias": "// ex: 5", "tipo": "// ex: 'uteis'"},
      "pos_violacao": {
        "// ADAPTAR": "Conforme processo específico na escritura"
      }
    }
  },

  "// ================================================": "",
  "// SEÇÃO 6: DADOS OPERACIONAIS": "",
  "// ================================================": "",

  "monitores_customizados": {
    "// SEÇÃO_CRÍTICA": "Monitores específicos do pool (20%)",
    "arquivos_necessarios": [
      "// Se houver regras específicas: {pool_id}_{funcionalidade}.py"
    ],
    "descricoes": [
      "// Descrição breve de cada monitor customizado"
    ]
  },

  "// ================================================": "",
  "// SEÇÃO 5: DADOS OPERACIONAIS": "",
  "// ================================================": "",

  "prestador_servicos_operacionais": {
    "nome": "// OPCIONAL: ou null",
    "cnpj": "// OPCIONAL: ou null",
    "contrato_data": "// OPCIONAL: YYYY-MM-DD ou null"
  },

  "originador_detalhado": {
    "// FONTE_VERDADE": "SEMPRE extrair da escritura original",
    "razao_social": "// OBRIGATÓRIO: razão social completa",
    "cnpj": "// OBRIGATÓRIO: CNPJ",
    "endereco": "// OBRIGATÓRIO: endereço completo - MANTER EXATO",
    "email_contato": "// OPCIONAL: ou null",
    "responsavel": "// OPCIONAL: ou null"
  },

  "debenturistas_detalhados": {
    "serie_senior": {
      "nome": "// OBRIGATÓRIO: nome completo",
      "cnpj": "// OPCIONAL: ou null",
      "tipo": "// OBRIGATÓRIO: ex: 'fundo_investimento'",
      "endereco": "// OPCIONAL: ou null"
    },
    "serie_subordinada": {
      "nome": "// OBRIGATÓRIO: nome completo", 
      "cnpj": "// OPCIONAL: ou null",
      "tipo": "// OBRIGATÓRIO: ex: 'originador'",
      "endereco": "// OPCIONAL: ou null"
    }
  }
}
```

## 🔧 Processo de Criação de Novos Pools

### 1. Análise da Escritura
- Extrair informações da escritura PDF original
- Identificar monitores base aplicáveis
- Mapear monitores customizados específicos
- Validar dados contra documento fonte

### 2. Criação do JSON
- Copiar template acima
- Preencher campos obrigatórios
- Configurar monitores aplicáveis
- Manter formato decimal para percentuais

### 3. Validação
- Verificar compatibilidade com sistema de descoberta
- Testar carregamento via data_loader
- Validar cálculos de monitores
- Confirmar matching com dados CSV/XLSX

### 4. Integração
- Adicionar à pasta `/data/escrituras/`
- Atualizar tabela de status neste README
- Testar processamento automático
- Documentar monitores customizados se necessário

## 🔗 Como os JSONs Alimentam o Sistema

Os JSONs desta pasta são **consumidos automaticamente** pelo sistema de monitoramento através de convenções de nomenclatura:

### Descoberta Automática de Monitores

#### 1. Monitores Base (Comuns entre pools)
O sistema lê `monitoramentos_ativos` e faz matching pelo campo `tipo`. **O monitor busca exatamente a chave `tipo` correspondente ao seu nome**:

```json
{
  "id": "subordinacao",
  "tipo": "subordinacao",     ← Monitor procura por tipo: "subordinacao"
  "funcao_calculo": "calc_subordinacao"  ← Chama função calc_subordinacao()
}
```

**Mapeamento automático por `tipo`**:
- `"tipo": "subordinacao"` → `/monitor/base/monitor_subordinacao.py`
- `"tipo": "concentracao"` → `/monitor/base/monitor_concentracao.py`
- `"tipo": "inadimplencia"` → `/monitor/base/monitor_inadimplencia.py` (inclui PDD)
- `"tipo": "elegibilidade"` → `/monitor/base/monitor_elegibilidade.py`
- `"tipo": "provisao"` → `/monitor/base/monitor_inadimplencia.py` (consolidado)
- **Qualquer `tipo` genérico** → `/monitor/base/monitor_{tipo}.py`

**⚠️ CRÍTICO**: O monitor **procura especificamente pela chave `tipo`** que corresponde ao seu nome. Alteração na chave `tipo` quebra a descoberta automática!

#### 2. Monitores Customizados (20% específicos)
O sistema lê `monitores_customizados.arquivos_necessarios`:

```json
{
  "monitores_customizados": {
    "arquivos_necessarios": [
      "SuperSim Pool #1_recovery_rate.py"  ← Busca monitor/custom/supersim_pool_1_recovery_rate.py
    ]
  }
}
```

### Fluxo de Integração

1. **Data Loader** (`/monitor/utils/data_loader.py`) descobre pools em CSV/XLSX
2. **Pool Discovery** busca JSON correspondente pelo nome do pool
3. **Config Loader** extrai `monitoramentos_ativos` do JSON
4. **Monitoring Engine** executa monitores base + customizados
5. **Alert Manager** processa resultados e gera alertas

### Campos Críticos para Integração

#### Obrigatórios para Descoberta
- `pool_id` - Deve bater exatamente com nome nos dados CSV/XLSX
- `monitoramentos_ativos[].tipo` - Define qual monitor base executar
- `monitoramentos_ativos[].ativo` - Liga/desliga monitor
- `monitoramentos_ativos[].funcao_calculo` - Função Python a chamar

#### Opcionais para Customização
- `monitores_customizados.arquivos_necessarios` - Monitores específicos do pool
- `triggers_aceleracao` - Configurações de eventos críticos

### Exemplo Prático
Para pool "LeCapital Pool #1":

1. Sistema encontra dados em `AcompanhamentoDeOportunidades-*.csv`
2. Busca `/data/escrituras/LeCapital Pool #1.json`
3. Lê monitores ativos configurados no JSON (subordinacao, concentracao, etc.)
4. Executa `/monitor/base/monitor_subordinacao.py` → `calc_subordinacao()`
5. Executa `/monitor/base/monitor_concentracao.py` → `calc_concentracao()`
6. Consolida resultados e gera relatório com limites específicos da escritura

⚠️ **IMPORTANTE**: Qualquer mudança em `pool_id` ou `tipo` quebra a descoberta automática!

## 📚 Referências

- **Documentação Técnica**: `/docs/CLAUDE.md`
- **Arquitetura de Monitoramento**: `/monitor/README.md`
- **Escrituras Fonte**: `/data/escrituras_md/` (documentos originais)
- **Processo de Extração**: `/docs/processos/PROCESSO_EXTRACAO_SISTEMATICA.md`

## 🆕 **NOVIDADES VERSÃO 2.3 (2025-07-15)**

### **Nova Seção: Processos Legais**
- **Estrutura Híbrida**: `triggers_aceleracao` (sistema) + `processos_legais` (compliance)
- **Documentação Legal**: Processos pós-violação extraídos das escrituras
- **Auditabilidade**: Rastro completo para compliance e auditoria
- **Referência Cruzada**: Links entre seções técnica e legal

### **Exemplo Implementado: Union Pool #5**
- **Problema Corrigido**: Top 10 Cedentes 60% → 70% (2º Aditamento)
- **Processo Detalhado**: Assembleia (3 dias) → Votação (Sênior) → Renúncia (5 dias)
- **Base Legal**: Anexo V, item (viii) - Eventos de Avaliação

### **Nova Funcionalidade: Análise Sequencial de Capacidade**
- **Monitor de Concentração v2.1**: Análise sequencial implementada
- **Capacidade Incremental**: Mostra quanto cada sacado/cedente pode crescer
- **Análise Cascata**: Saldo restante após cada alocação sequencial  
- **Limitações Claras**: Identifica se restrição é individual ou top-N

### **Benefícios da Estrutura Híbrida**
- **Sistema**: Usa `triggers_aceleracao` simples para monitoramento automático
- **Compliance**: `processos_legais` detalhados para auditoria e processos manuais
- **Manutenção**: Evita duplicação via referência cruzada
- **Escalabilidade**: Template padrão para todos os novos pools

---
**Última atualização**: 2025-07-15 | **Versão Template**: v2.3 | **Estrutura Híbrida**: ✅ Implementada