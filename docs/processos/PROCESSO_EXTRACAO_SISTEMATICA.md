# Processo Sistemático de Extração de Documentos Legais

> **Documentos Relacionados:**
> - [Checklist de Extração de Features](./CHECKLIST_EXTRACAO_FEATURES.md) - Ferramenta operacional

## Propósito
Este documento define o processo sistemático para evitar a perda de recursos críticos de monitoramento ao converter documentos legais (escrituras de emissão) para estruturas JSON de monitoramento. Este processo foi desenvolvido após descobrir que o recurso de recuperação "direito de regresso" da SuperSim foi inicialmente esquecido.

## Definição do Problema
Documentos legais contêm requisitos de monitoramento específicos do pool que não são imediatamente óbvios. Regras de negócio importantes podem estar enterradas em cláusulas complexas, anexos ou tabelas. Sem uma abordagem sistemática:
- Recursos críticos de monitoramento são negligenciados
- Riscos específicos do pool não são adequadamente rastreados
- Violações de conformidade podem passar despercebidas
- Mecanismos de recuperação podem não ser implementados

## Framework da Solução

### 1. Preparação Pré-Extração

#### Inventário de Documentos
```bash
# Listar todos os arquivos MD que precisam ser processados
find /mnt/c/amfi/data/escrituras_md/ -name "*.md" -type f

# Verificar arquivos JSON existentes
find /mnt/c/amfi/data/escrituras/ -name "*.json" -type f

# Identificar necessidades de controle de versão
ls -la /mnt/c/amfi/data/escrituras_archive/
```

#### Configuração de Ferramentas
- [ ] Checklist de Extração de Features carregado
- [ ] Diretrizes de Validação de Schema disponíveis
- [ ] JSONs de pools de comparação prontos (AFA, escritura JSON template como benchmarks)
- [ ] Ferramentas de busca de texto preparadas para busca sistemática por palavras-chave

### 2. Análise Sistemática de Documentos

#### Fase A: Descoberta Baseada em Palavras-chave
Use os termos de busca obrigatórios do Checklist de Extração de Features:

```bash
# Exemplos de comandos de busca para termos relacionados à recuperação
grep -n -i "direito de regresso\|recovery\|recompra\|fraud\|fraude" documento.md
grep -n -i "recovery rate\|taxa de recuperação" documento.md
grep -n -i "má formalização\|poor formalization" documento.md
```

#### Fase B: Análise de Padrões Numéricos
```bash
# Encontrar todas as porcentagens
grep -n -E "[0-9]+(\.[0-9]+)?%" documento.md

# Encontrar todos os períodos em dias
grep -n -i "[0-9]+ dias?" documento.md

# Encontrar todos os períodos em meses
grep -n -i "[0-9]+ meses?" documento.md

# Encontrar valores monetários
grep -n -E "R\$[0-9,.]+" documento.md
```

#### Fase C: Análise Estrutural
- Extrair todos os números e títulos de cláusulas
- Identificar todos os anexos e seus conteúdos
- Mapear estruturas de tabelas e fórmulas
- Catalogar todos os termos definidos e seus significados

### 3. Fluxo de Trabalho de Extração de Features

#### Passo 1: Extração de Informações Básicas
```json
{
  "info_escritura": {
    "nome_completo": "...",
    "nome_admin": "...",
    "numero_emissao": "...",
    "data_emissao": "AAAA-MM-DD",
    "data_vencimento": "AAAA-MM-DD",
    "valor_total": 0.0,
    "emissora": "...",
    "status": "ativo",
    "lei_aplicavel": "Lei 14.430/22"
  }
}
```

#### Passo 2: Mapeamento da Estrutura Financeira
- Identificação e hierarquia das séries
- Relacionamentos e índices de subordinação
- Cronogramas de pagamento e amortização
- Estruturas de taxas de juros

#### Passo 3: Descoberta de Eventos de Monitoramento
Esta é a fase CRÍTICA onde features são mais comumente perdidas:

```json
{
  "eventos_de_monitoramento": [
    {
      "tipo": "tipo_evento",
      "descricao": "Descrição clara",
      "limite": 0.0,  // SEMPRE decimal para porcentagens
      "unidade": "percentual|dias|meses|valor",
      "ativo": true,
      "clausula_escritura": "Referência exata da cláusula"
    }
  ]
}
```

#### Passo 4: Análise de Mecanismos de Recuperação
**CRÍTICO**: Foi aqui que as features da SuperSim foram perdidas inicialmente.

```json
{
  "mecanismos_recuperacao": {
    "direito_regresso": {
      "ativo": true|false,
      "prazo_elegibilidade_dias": 0,
      "gatilhos": ["fraude", "ma_formalizacao"],
      "responsavel": "originador",
      "descricao": "..."
    },
    "recompra_obrigatoria": {
      "ativo": true|false,
      "prazo_dias": 0,
      "tipo_prazo": "uteis|corridos",
      "gatilhos": [...],
      "opcoes": [...],
      "descricao": "..."
    },
    "calculo_recovery_rate": {
      "ativo": true|false,
      "frequencia": "mensal|trimestral",
      "formula": "formula_exata",
      "limite_minimo": 0.0,
      "janela_avaliacao_meses": 0,
      "evento_gatilho": "..."
    }
  }
}
```

### 4. Processo de Garantia de Qualidade

#### Verificações de Validação
1. **Verificação de Completude**: Todos os itens do checklist verificados
2. **Verificação de Formato**: Tipos de dados conforme o schema
3. **Verificação de Consistência**: Nomes de campos correspondem a outros pools
4. **Verificação de Referências**: Todas as referências de cláusulas são precisas

#### Comparação Entre Pools
```python
# Comparar contagem de eventos de monitoramento
afa_eventos = len(afa_pool["eventos_de_monitoramento"])
supersim_eventos = len(supersim_pool["eventos_de_monitoramento"])

# Sinalizar diferenças significativas
if abs(afa_eventos - supersim_eventos) > 5:
    print("AVISO: Diferença significativa na contagem de eventos de monitoramento")

# Comparar features únicas
afa_features = set(evento["tipo"] for evento in afa_pool["eventos_de_monitoramento"])
supersim_features = set(evento["tipo"] for evento in supersim_pool["eventos_de_monitoramento"])
unicas_supersim = supersim_features - afa_features
```

#### Detecção de Features Ausentes
```python
# Verificação de seções obrigatórias
secoes_obrigatorias = [
    "info_escritura",
    "estrutura_financeira", 
    "criterios_elegibilidade",
    "eventos_de_monitoramento",
    "vencimento_antecipado"
]

# Verificação de mecanismos de recuperação (crítico para pools tipo SuperSim)
indicadores_recuperacao = [
    "direito_regresso",
    "recompra_obrigatoria", 
    "recovery_rate",
    "calculo_recovery_rate"
]
```

### 5. Integração com Controle de Versão

#### Estratégia de Versionamento JSON
```bash
# Versão atual
/data/escrituras/supersim_pool_1.json

# Versão com features de recuperação
/data/escrituras/supersim_pool_1_v2.json

# Arquivar versão anterior
/data/escrituras_archive/supersim_pool_1_v1_2025-07-02.json
```

#### Documentação de Mudanças
```json
{
  "version_info": {
    "version": "2.0",
    "date_created": "2025-07-02",
    "changes": [
      "Adicionados eventos de monitoramento de taxa de recuperação",
      "Adicionados mecanismos de direito de regresso", 
      "Adicionadas estruturas de recompra obrigatória",
      "Aprimorado provisionamento de risco com expectativas de recuperação"
    ],
    "features_added": [
      "recovery_rate_mensal",
      "atraso_30_dias_direito_regresso",
      "prazo_recompra_inelegivel",
      "cura_subordinacao_violacao"
    ]
  }
}
```

### 6. Loop de Melhoria do Processo

#### Aprendendo com Features Perdidas
Quando features são descobertas após a extração inicial:

1. **Análise de Causa Raiz**
   - Por que esta feature foi perdida?
   - Quais termos de busca a teriam encontrado?
   - Quais itens do checklist precisam ser aprimorados?

2. **Atualizações do Processo**
   - Adicionar novos termos de busca à lista obrigatória
   - Atualizar checklist com novas categorias
   - Aprimorar critérios de validação
   - Melhorar métodos de referência cruzada

3. **Aplicação Retroativa**
   - Re-analisar outros pools para features similares
   - Atualizar diretrizes de extração
   - Treinar equipe em novas técnicas de descoberta

#### Rastreamento de Métricas
```python
# Rastrear qualidade da extração ao longo do tempo
metricas_extracao = {
    "nome_pool": "supersim_pool_1",
    "data_extracao": "2025-07-02",
    "features_encontradas_inicialmente": 15,
    "features_adicionadas_depois": 5,
    "score_completude": 0.75,  # 15/(15+5)
    "tipos_features_perdidas": ["mecanismos_recuperacao", "eventos_baseados_tempo"]
}
```

### 7. Ferramentas de Assistência Automatizada

#### Scripts de Validação
```python
def validar_json_pool(dados_pool):
    """Validação automatizada para problemas comuns"""
    problemas = []
    
    # Verificar formato de porcentagem
    for evento in dados_pool.get("eventos_de_monitoramento", []):
        if evento.get("unidade") == "percentual":
            if evento.get("limite", 0) > 1.0:
                problemas.append(f"Porcentagem {evento['tipo']} não está em formato decimal")
    
    # Verificar mecanismos de recuperação ausentes
    if "mecanismos_recuperacao" not in dados_pool:
        problemas.append("Nenhuma seção de mecanismos de recuperação encontrada")
    
    return problemas
```

#### Ferramentas de Comparação de Features
```python
def comparar_features_pools(pool1, pool2):
    """Comparar features entre pools para identificar lacunas"""
    eventos_pool1 = {e["tipo"] for e in pool1.get("eventos_de_monitoramento", [])}
    eventos_pool2 = {e["tipo"] for e in pool2.get("eventos_de_monitoramento", [])}
    
    apenas_pool1 = eventos_pool1 - eventos_pool2
    apenas_pool2 = eventos_pool2 - eventos_pool1
    
    return {
        "unico_pool1": apenas_pool1,
        "unico_pool2": apenas_pool2,
        "features_comuns": eventos_pool1 & eventos_pool2
    }
```

### 8. Critérios de Sucesso

#### Completude da Extração
- [ ] Todos os termos de busca sistematicamente revisados
- [ ] Todos os eventos de monitoramento identificados e estruturados
- [ ] Todos os mecanismos de recuperação capturados
- [ ] Todos os eventos baseados em tempo com prazos adequados
- [ ] Todas as features únicas do pool documentadas

#### Qualidade dos Dados
- [ ] Todas as porcentagens em formato decimal (0.05 não 5.0)
- [ ] Todos os valores monetários como floats
- [ ] Todos os valores nulos adequadamente definidos (não "NaN")
- [ ] Todas as flags booleanas corretamente atribuídas
- [ ] Todas as datas em formato ISO

#### Compatibilidade de Monitoramento
- [ ] Código Python de monitoramento pode iterar pelos eventos
- [ ] Todos os limites diretamente comparáveis sem conversão
- [ ] Todas as regras específicas do pool seguem estrutura padrão
- [ ] Todos os eventos têm flags "ativo" para processamento condicional

### 9. Processo de Recuperação de Emergência

Se features críticas são descobertas após implantação:

#### Ações Imediatas
1. **Avaliação de Impacto**: Avaliar lacunas de monitoramento
2. **Correção Rápida**: Adicionar features ausentes ao JSON
3. **Atualização de Versão**: Criar nova versão com mudanças
4. **Arquivar Anterior**: Preservar versão antiga com timestamp

#### Ações de Acompanhamento
1. **Análise de Causa Raiz**: Por que a feature foi perdida?
2. **Aprimoramento do Processo**: Atualizar checklist e diretrizes
3. **Revisão Retroativa**: Verificar outros pools para lacunas similares
4. **Treinamento da Equipe**: Compartilhar lições aprendidas

### 10. Conclusão

Este processo sistemático garante que documentos legais complexos sejam completamente analisados para TODOS os requisitos de monitoramento. A chave é a busca metódica e orientada por palavras-chave combinada com validação estruturada contra padrões conhecidos.

**Lembre-se**: Documentos legais são intencionalmente complexos. Features podem estar escondidas em:
- Linguagem legal densa
- Referências cruzadas entre cláusulas
- Tabelas com condições embutidas
- Anexos com fórmulas de cálculo
- Requisitos implícitos declarados apenas uma vez

A abordagem sistemática evita que essas features sejam negligenciadas e garante sistemas de monitoramento robustos que capturam todos os riscos específicos do pool e mecanismos de recuperação.