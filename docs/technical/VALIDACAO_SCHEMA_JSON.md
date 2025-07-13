# Diretrizes de Validação de Schema JSON para Monitoramento de Pools AmFi

## Visão Geral
Este documento define regras de validação para arquivos JSON de pools para garantir compatibilidade com o código Python de monitoramento.

## Requisitos de Tipos de Dados

### Valores Numéricos
```python
# ✅ Correto - Sempre use float para valores monetários e decimal para porcentagens
"subordinacao_minima": 0.35      # 35% como decimal
"valor_total": 10000000.0        # Valores monetários como float
"premio_risco": 0.08             # 8% como decimal

# ❌ Incorreto - Nunca use strings ou números inteiros para porcentagens
"subordinacao_minima": "35%"     # Formato string
"subordinacao_minima": 35.0      # Formato número inteiro
"valor_total": "R$ 10.000.000"  # Formato string
```

### Valores Ausentes
```python
# ✅ Correto - Use null para valores ausentes/não aplicáveis
"concentracao_maxima_cedente": null
"vencimento_medio_maximo_dias": null

# ❌ Incorreto - Nunca use representações em string
"concentracao_maxima_cedente": "N/A"
"vencimento_medio_maximo_dias": "NaN"
```

### Flags Booleanas
```python
# ✅ Correto - Use boolean para estados ativo/inativo
"ativo": true
"automatico": false

# ❌ Incorreto - Não use strings ou números
"ativo": "sim"
"automatico": 1
```

## Padrões de Nomenclatura de Campos

### Nomes Consistentes Entre Pools
```python
# ✅ Campos padrão que devem ser consistentes
"atraso_max_dias"      # Nunca "atraso_maximo" ou "atraso_maximo_dias"
"provisao_pct"         # Nunca "percentual_provisao" ou "provisao_percentual" (armazenar como decimal: 0.5 para 50%)
"limite"               # Nunca "valor_limite" ou "limite_percentual" (armazenar como decimal: 0.01 para 1%)
```

### Estrutura de Regras Específicas do Pool
```python
# ✅ Correto - Estrutura padronizada para regras específicas do pool
"limites_concentracao": {
  "instituicoes_especificas": [
    {
      "nome": "BMP",
      "limite": 1.0,        # 100% como decimal
      "tipo": "parceiro_financeiro",
      "ativo": true
    }
  ]
}

# ❌ Incorreto - Nomes de campos específicos do pool
"concentracao_maxima_bmp": 100.0       # Errado: número inteiro
"concentracao_maxima_socinal": 15.0    # Errado: número inteiro
```

## Estruturas Amigáveis ao Monitoramento

### Estrutura de Eventos
```python
# ✅ Amigável ao monitoramento - Fácil iteração e verificação de regras
"eventos_de_monitoramento": [
  {
    "tipo": "concentracao_sacado_individual",
    "limite": 0.01,        # 1% como decimal
    "unidade": "percentual",
    "ativo": true
  }
]

# Código Python de monitoramento:
for evento in pool_data["eventos_de_monitoramento"]:
    if evento["ativo"] and portfolio_concentration > evento["limite"]:
        trigger_alert(evento["tipo"])
```

### Estrutura de PDD
```python
# ✅ Estrutura consistente para processamento automatizado
"provisoes_pdd": {
  "grupos_risco": {
    "AA": {
      "atraso_max_dias": 0,
      "provisao_pct": 0.0    # 0% como decimal
    },
    "A": {
      "atraso_max_dias": 15,
      "provisao_pct": 0.5    # 50% como decimal
    }
  }
}

# Código Python de monitoramento:
for grupo, config in pdd["grupos_risco"].items():
    if days_late > config["atraso_max_dias"]:
        provision_amount = receivable_value * config["provisao_pct"]
        apply_provision(provision_amount)
```

## Exemplos de Código Python

### Monitoramento Genérico de Pool
```python
def verificar_limites_concentracao(pool_data, portfolio):
    """Função genérica que funciona para todos os pools"""
    limites = pool_data["criterios_elegibilidade"]["limites_concentracao"]
    
    # Verificar limites individuais
    if limites["sacado_individual"]["ativo"]:
        max_concentracao = limites["sacado_individual"]["limite"]  # Já em formato decimal (0.01 para 1%)
        if portfolio.max_sacado_concentration() > max_concentracao:
            return False
    
    # Verificar limites específicos de instituições
    for instituicao in limites["instituicoes_especificas"]:
        if instituicao["ativo"]:
            if portfolio.institution_concentration(instituicao["nome"]) > instituicao["limite"]:
                return False
    
    return True
```

### Cálculo de PDD
```python
def calcular_pdd(pool_data, recebiveis):
    """Cálculo automático de PDD para qualquer pool"""
    regras_pdd = pool_data["provisoes_pdd"]["grupos_risco"]
    provisao_total = 0.0
    
    for recebivel in recebiveis:
        dias_atraso = recebivel.dias_atraso()
        
        # Encontrar grupo de risco apropriado
        for grupo, config in regras_pdd.items():
            if dias_atraso <= config["atraso_max_dias"]:
                provisao = recebivel.valor * config["provisao_pct"]  # Já em formato decimal
                provisao_total += provisao
                break
    
    return provisao_total
```

## Checklist de Validação

### Antes de Criar o JSON
- [ ] Todos os valores monetários são tipo `float`
- [ ] Todas as porcentagens são `float` em formato decimal (5% = 0.05, não 5.0 ou "5%")
- [ ] Valores ausentes são `null` (não "NaN", "N/A", ou strings vazias)
- [ ] Flags booleanas usam `true`/`false` (não strings ou números)
- [ ] Datas usam formato "AAAA-MM-DD"
- [ ] Nomes de campos seguem convenção minusculas_com_underscores

### Validação de Estrutura
- [ ] Regras específicas do pool usam estruturas aninhadas padronizadas
- [ ] Arrays são usados para listas (não objetos com chaves numeradas)
- [ ] Campos comuns de monitoramento estão presentes e consistentes
- [ ] Flags `ativo` estão presentes para regras condicionais

### Teste de Compatibilidade Python
```python
# Testar que valores podem ser usados diretamente em cálculos
subordinacao = pool_data["estrutura_financeira"]["indices_minimos"]["subordinacao_minima"]
assert isinstance(subordinacao, (int, float))
assert 0.0 <= subordinacao <= 1.0  # Deve estar em formato decimal

# Testar que valores null são tratados corretamente
limite = pool_data["criterios_elegibilidade"]["limites_carteira"]["vencimento_medio_maximo_dias"]
if limite is not None:
    aplicar_limite(limite)

# Testar que iterações funcionam para regras de monitoramento
for evento in pool_data["eventos_de_monitoramento"]:
    if evento["ativo"]:
        if evento["unidade"] == "percentual":
            assert 0.0 <= evento["limite"] <= 1.0  # Deve ser decimal
        monitorar_evento(evento["tipo"], evento["limite"])
```

## Erros Comuns a Evitar

1. **Porcentagens em string**: `"35%"` ao invés de `0.35`
2. **Porcentagens em número inteiro**: `35.0` ao invés de `0.35`
3. **Tipos de dados mistos**: `1` e `1.0` na mesma estrutura
4. **Nulls em string**: `"null"` ao invés de `null`
5. **Nomes de campos específicos do pool**: Quebrando código genérico de monitoramento
6. **Estruturas inconsistentes**: Pools diferentes usando nomes de campos diferentes para o mesmo conceito
7. **Erros de cálculo de porcentagem**: Usar decimais sem ajustar cálculos (ex: `valor * 0.05` não `valor * 0.05 / 100`)

## Evolução Futura do Schema

Ao adicionar novos pools ou atualizar existentes:
1. Sempre siga estas regras de validação
2. Adicione novos campos como estruturas padronizadas
3. Use flags `ativo` para regras opcionais
4. Mantenha compatibilidade retroativa
5. Teste com código genérico de monitoramento antes da implantação