# Systematic Legal Document Extraction Process

## Purpose
This document defines the systematic process to prevent missing critical monitoring features when converting legal documents (escrituras de emissão) to JSON monitoring structures. This process was developed after discovering that SuperSim's "direito de regresso" (right of recourse) recovery feature was initially missed.

## Problem Statement
Legal documents contain pool-specific monitoring requirements that aren't immediately obvious. Important business rules can be buried in complex clauses, annexes, or tables. Without a systematic approach:
- Critical monitoring features get overlooked
- Pool-specific risks aren't properly tracked
- Compliance violations can go undetected
- Recovery mechanisms may not be implemented

## Solution Framework

### 1. Pre-Extraction Preparation

#### Document Inventory
```bash
# List all MD files that need processing
find /mnt/c/amfi/data/escrituras_md/ -name "*.md" -type f

# Check for existing JSON files
find /mnt/c/amfi/data/escrituras/ -name "*.json" -type f

# Identify version control needs
ls -la /mnt/c/amfi/data/escrituras_archive/
```

#### Tool Setup
- [ ] Feature Extraction Checklist loaded
- [ ] Schema Validation Guidelines available
- [ ] Comparison pool JSONs ready (AFA, LeCapital as benchmarks)
- [ ] Text search tools prepared for systematic keyword searching

### 2. Systematic Document Analysis

#### Phase A: Keyword-Based Discovery
Use the mandatory search terms from the Feature Extraction Checklist:

```bash
# Example search commands for recovery-related terms
grep -n -i "direito de regresso\|recovery\|recompra\|fraud\|fraude" document.md
grep -n -i "recovery rate\|taxa de recuperação" document.md
grep -n -i "má formalização\|poor formalization" document.md
```

#### Phase B: Numerical Pattern Analysis
```bash
# Find all percentages
grep -n -E "[0-9]+(\.[0-9]+)?%" document.md

# Find all day periods
grep -n -i "[0-9]+ dias?" document.md

# Find all month periods  
grep -n -i "[0-9]+ meses?" document.md

# Find monetary values
grep -n -E "R\$[0-9,.]+" document.md
```

#### Phase C: Structural Analysis
- Extract all clause numbers and titles
- Identify all annexes and their contents
- Map table structures and formulas
- Catalog all defined terms and their meanings

### 3. Feature Extraction Workflow

#### Step 1: Basic Information Extraction
```json
{
  "info_escritura": {
    "nome_completo": "...",
    "nome_admin": "...",
    "numero_emissao": "...",
    "data_emissao": "YYYY-MM-DD",
    "data_vencimento": "YYYY-MM-DD",
    "valor_total": 0.0,
    "emissora": "...",
    "status": "ativo",
    "lei_aplicavel": "Lei 14.430/22"
  }
}
```

#### Step 2: Financial Structure Mapping
- Series identification and hierarchy
- Subordination relationships and indices
- Payment schedules and amortization
- Interest rate structures

#### Step 3: Monitoring Events Discovery
This is the CRITICAL phase where features are most commonly missed:

```json
{
  "eventos_de_monitoramento": [
    {
      "tipo": "event_type",
      "descricao": "Clear description",
      "limite": 0.0,  // ALWAYS decimal for percentages
      "unidade": "percentual|dias|meses|valor",
      "ativo": true,
      "clausula_escritura": "Exact clause reference"
    }
  ]
}
```

#### Step 4: Recovery Mechanisms Analysis
**CRITICAL**: This is where SuperSim's features were missed initially.

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
      "formula": "exact_formula",
      "limite_minimo": 0.0,
      "janela_avaliacao_meses": 0,
      "evento_gatilho": "..."
    }
  }
}
```

### 4. Quality Assurance Process

#### Validation Checks
1. **Completeness Check**: All checklist items verified
2. **Format Check**: Data types conform to schema
3. **Consistency Check**: Field names match other pools
4. **Reference Check**: All clause references accurate

#### Cross-Pool Comparison
```python
# Compare monitoring events count
afa_events = len(afa_pool["eventos_de_monitoramento"])
supersim_events = len(supersim_pool["eventos_de_monitoramento"])

# Flag significant differences
if abs(afa_events - supersim_events) > 5:
    print("WARNING: Significant difference in monitoring events count")

# Compare unique features
afa_features = set(event["tipo"] for event in afa_pool["eventos_de_monitoramento"])
supersim_features = set(event["tipo"] for event in supersim_pool["eventos_de_monitoramento"])
unique_to_supersim = supersim_features - afa_features
```

#### Missing Feature Detection
```python
# Required sections check
required_sections = [
    "info_escritura",
    "estrutura_financeira", 
    "criterios_elegibilidade",
    "eventos_de_monitoramento",
    "vencimento_antecipado"
]

# Recovery mechanisms check (critical for SuperSim-type pools)
recovery_indicators = [
    "direito_regresso",
    "recompra_obrigatoria", 
    "recovery_rate",
    "calculo_recovery_rate"
]
```

### 5. Version Control Integration

#### JSON Versioning Strategy
```bash
# Current version
/data/escrituras/supersim_pool_1.json

# Version with recovery features  
/data/escrituras/supersim_pool_1_v2.json

# Archive previous version
/data/escrituras_archive/supersim_pool_1_v1_2025-07-02.json
```

#### Change Documentation
```json
{
  "version_info": {
    "version": "2.0",
    "date_created": "2025-07-02",
    "changes": [
      "Added recovery rate monitoring events",
      "Added direito de regresso mechanisms", 
      "Added mandatory repurchase structures",
      "Enhanced risk provisioning with recovery expectations"
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

### 6. Process Improvement Loop

#### Learning from Missed Features
When features are discovered after initial extraction:

1. **Root Cause Analysis**
   - Why was this feature missed?
   - Which search terms would have found it?
   - What checklist items need enhancement?

2. **Process Updates**
   - Add new search terms to mandatory list
   - Update checklist with new categories
   - Enhance validation criteria
   - Improve cross-reference methods

3. **Retroactive Application**
   - Re-analyze other pools for similar features
   - Update extraction guidelines
   - Train team on new discovery techniques

#### Metrics Tracking
```python
# Track extraction quality over time
extraction_metrics = {
    "pool_name": "supersim_pool_1",
    "extraction_date": "2025-07-02",
    "features_initially_found": 15,
    "features_added_later": 5,
    "completeness_score": 0.75,  # 15/(15+5)
    "missed_feature_types": ["recovery_mechanisms", "time_based_events"]
}
```

### 7. Automated Assistance Tools

#### Validation Scripts
```python
def validate_pool_json(pool_data):
    """Automated validation for common issues"""
    issues = []
    
    # Check for percentage format
    for event in pool_data.get("eventos_de_monitoramento", []):
        if event.get("unidade") == "percentual":
            if event.get("limite", 0) > 1.0:
                issues.append(f"Percentage {event['tipo']} not in decimal format")
    
    # Check for missing recovery mechanisms
    if "mecanismos_recuperacao" not in pool_data:
        issues.append("No recovery mechanisms section found")
    
    return issues
```

#### Feature Comparison Tools
```python
def compare_pool_features(pool1, pool2):
    """Compare features between pools to identify gaps"""
    pool1_events = {e["tipo"] for e in pool1.get("eventos_de_monitoramento", [])}
    pool2_events = {e["tipo"] for e in pool2.get("eventos_de_monitoramento", [])}
    
    only_in_pool1 = pool1_events - pool2_events
    only_in_pool2 = pool2_events - pool1_events
    
    return {
        "unique_to_pool1": only_in_pool1,
        "unique_to_pool2": only_in_pool2,
        "common_features": pool1_events & pool2_events
    }
```

### 8. Success Criteria

#### Extraction Completeness
- [ ] All search terms systematically reviewed
- [ ] All monitoring events identified and structured
- [ ] All recovery mechanisms captured
- [ ] All time-based events with proper deadlines
- [ ] All unique pool features documented

#### Data Quality
- [ ] All percentages in decimal format (0.05 not 5.0)
- [ ] All monetary values as floats
- [ ] All null values properly set (not "NaN")
- [ ] All boolean flags correctly assigned
- [ ] All dates in ISO format

#### Monitoring Compatibility
- [ ] Python monitoring code can iterate through events
- [ ] All limits directly comparable without conversion
- [ ] All pool-specific rules follow standard structure
- [ ] All events have "ativo" flags for conditional processing

### 9. Emergency Recovery Process

If critical features are discovered after deployment:

#### Immediate Actions
1. **Impact Assessment**: Evaluate monitoring gaps
2. **Quick Fix**: Add missing features to JSON
3. **Version Update**: Create new version with changes
4. **Archive Previous**: Preserve old version with timestamp

#### Follow-up Actions
1. **Root Cause Analysis**: Why was feature missed?
2. **Process Enhancement**: Update checklist and guidelines
3. **Retroactive Review**: Check other pools for similar gaps
4. **Team Training**: Share lessons learned

### 10. Conclusion

This systematic process ensures that complex legal documents are thoroughly analyzed for ALL monitoring requirements. The key is methodical, keyword-driven search combined with structured validation against known patterns.

**Remember**: Legal documents are intentionally complex. Features can be hidden in:
- Dense legal language
- Cross-references between clauses
- Tables with embedded conditions
- Annexes with calculation formulas
- Implicit requirements stated only once

The systematic approach prevents these features from being overlooked and ensures robust monitoring systems that capture all pool-specific risks and recovery mechanisms.