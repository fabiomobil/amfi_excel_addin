# JSON Schema Validation Guidelines for AmFi Pool Monitoring

## Overview
This document defines validation rules for pool JSON files to ensure Python monitoring code compatibility.

## Data Type Requirements

### Numeric Values
```python
# ✅ Correct - Always use float for monetary values and decimal for percentages
"subordinacao_minima": 0.35      # 35% as decimal
"valor_total": 10000000.0        # Monetary values as float
"premio_risco": 0.08             # 8% as decimal

# ❌ Incorrect - Never use strings or whole numbers for percentages
"subordinacao_minima": "35%"     # String format
"subordinacao_minima": 35.0      # Whole number format
"valor_total": "R$ 10.000.000"  # String format
```

### Missing Values
```python
# ✅ Correct - Use null for missing/non-applicable values
"concentracao_maxima_cedente": null
"vencimento_medio_maximo_dias": null

# ❌ Incorrect - Never use string representations
"concentracao_maxima_cedente": "N/A"
"vencimento_medio_maximo_dias": "NaN"
```

### Boolean Flags
```python
# ✅ Correct - Use boolean for active/inactive states
"ativo": true
"automatico": false

# ❌ Incorrect - Don't use strings or numbers
"ativo": "sim"
"automatico": 1
```

## Field Naming Standards

### Consistent Names Across Pools
```python
# ✅ Standard fields that should be consistent
"atraso_max_dias"      # Never "atraso_maximo" or "atraso_maximo_dias"
"provisao_pct"         # Never "percentual_provisao" or "provisao_percentual" (store as decimal: 0.5 for 50%)
"limite"               # Never "valor_limite" or "limite_percentual" (store as decimal: 0.01 for 1%)
```

### Pool-Specific Rules Structure
```python
# ✅ Correct - Standardized structure for pool-specific rules
"limites_concentracao": {
  "instituicoes_especificas": [
    {
      "nome": "BMP",
      "limite": 1.0,        # 100% as decimal
      "tipo": "parceiro_financeiro",
      "ativo": true
    }
  ]
}

# ❌ Incorrect - Pool-specific field names
"concentracao_maxima_bmp": 100.0       # Wrong: whole number
"concentracao_maxima_socinal": 15.0    # Wrong: whole number
```

## Monitoring-Friendly Structures

### Events Structure
```python
# ✅ Monitoring-friendly - Easy iteration and rule checking
"eventos_de_monitoramento": [
  {
    "tipo": "concentracao_sacado_individual",
    "limite": 0.01,        # 1% as decimal
    "unidade": "percentual",
    "ativo": true
  }
]

# Python monitoring code:
for evento in pool_data["eventos_de_monitoramento"]:
    if evento["ativo"] and portfolio_concentration > evento["limite"]:
        trigger_alert(evento["tipo"])
```

### PDD Structure
```python
# ✅ Consistent structure for automated processing
"provisoes_pdd": {
  "grupos_risco": {
    "AA": {
      "atraso_max_dias": 0,
      "provisao_pct": 0.0    # 0% as decimal
    },
    "A": {
      "atraso_max_dias": 15,
      "provisao_pct": 0.5    # 50% as decimal
    }
  }
}

# Python monitoring code:
for grupo, config in pdd["grupos_risco"].items():
    if days_late > config["atraso_max_dias"]:
        provision_amount = receivable_value * config["provisao_pct"]
        apply_provision(provision_amount)
```

## Python Code Examples

### Generic Pool Monitoring
```python
def check_concentration_limits(pool_data, portfolio):
    """Generic function that works for all pools"""
    limits = pool_data["criterios_elegibilidade"]["limites_concentracao"]
    
    # Check individual limits
    if limits["sacado_individual"]["ativo"]:
        max_concentration = limits["sacado_individual"]["limite"]  # Already in decimal format (0.01 for 1%)
        if portfolio.max_sacado_concentration() > max_concentration:
            return False
    
    # Check institution-specific limits
    for instituicao in limits["instituicoes_especificas"]:
        if instituicao["ativo"]:
            if portfolio.institution_concentration(instituicao["nome"]) > instituicao["limite"]:
                return False
    
    return True
```

### PDD Calculation
```python
def calculate_pdd(pool_data, receivables):
    """Automatic PDD calculation for any pool"""
    pdd_rules = pool_data["provisoes_pdd"]["grupos_risco"]
    total_provision = 0.0
    
    for receivable in receivables:
        days_late = receivable.days_late()
        
        # Find appropriate risk group
        for grupo, config in pdd_rules.items():
            if days_late <= config["atraso_max_dias"]:
                provision = receivable.value * config["provisao_pct"]  # Already in decimal format
                total_provision += provision
                break
    
    return total_provision
```

## Validation Checklist

### Before Creating JSON
- [ ] All monetary values are `float` type
- [ ] All percentages are `float` in decimal format (5% = 0.05, not 5.0 or "5%")
- [ ] Missing values are `null` (not "NaN", "N/A", or empty strings)
- [ ] Boolean flags use `true`/`false` (not strings or numbers)
- [ ] Dates use "YYYY-MM-DD" format
- [ ] Field names follow lowercase_with_underscores convention

### Structure Validation
- [ ] Pool-specific rules use standardized nested structures
- [ ] Arrays are used for lists (not objects with numbered keys)
- [ ] Common monitoring fields are present and consistent
- [ ] `ativo` flags are present for conditional rules

### Python Compatibility Test
```python
# Test that values can be used directly in calculations
subordinacao = pool_data["estrutura_financeira"]["indices_minimos"]["subordinacao_minima"]
assert isinstance(subordinacao, (int, float))
assert 0.0 <= subordinacao <= 1.0  # Should be decimal format

# Test that null values are handled correctly
limite = pool_data["criterios_elegibilidade"]["limites_carteira"]["vencimento_medio_maximo_dias"]
if limite is not None:
    apply_limit(limite)

# Test that iterations work for monitoring rules
for evento in pool_data["eventos_de_monitoramento"]:
    if evento["ativo"]:
        if evento["unidade"] == "percentual":
            assert 0.0 <= evento["limite"] <= 1.0  # Should be decimal
        monitor_event(evento["tipo"], evento["limite"])
```

## Common Mistakes to Avoid

1. **String percentages**: `"35%"` instead of `0.35`
2. **Whole number percentages**: `35.0` instead of `0.35`
3. **Mixed data types**: `1` and `1.0` in the same structure
4. **String nulls**: `"null"` instead of `null`
5. **Pool-specific field names**: Breaking generic monitoring code
6. **Inconsistent structures**: Different pools using different field names for the same concept
7. **Percentage calculation errors**: Using decimals without adjusting calculations (e.g., `value * 0.05` not `value * 0.05 / 100`)

## Future Schema Evolution

When adding new pools or updating existing ones:
1. Always follow these validation rules
2. Add new fields as standardized structures
3. Use `ativo` flags for optional rules
4. Maintain backward compatibility
5. Test with generic monitoring code before deployment