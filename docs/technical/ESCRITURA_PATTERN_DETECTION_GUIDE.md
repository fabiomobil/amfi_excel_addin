# 📋 ESCRITURA PATTERN DETECTION GUIDE

## **PROPÓSITO DO DOCUMENTO**

Este documento serve como um **GUIA DE DETECÇÃO AUTOMÁTICA** para identificar tipos de escritura e suas variações em pools de securitização. Permite classificação automática de novos pools baseada em padrões estruturais, financeiros e operacionais.

---

## **🎯 SISTEMA DE CLASSIFICAÇÃO DE ESCRITURAS**

### **CLASSIFICAÇÃO PRIMÁRIA - Modelo de Negócio**

#### **1. CORPORATE CREDIT (Crédito Corporativo)**
**Padrão de Detecção:**
- `sacados_elegiveis`: Lista extensa de grandes empresas (>15 entidades)
- `valores.subordinada`: Ratio conservador (15-35% do total)
- Prazo: Médio/longo prazo (3+ anos)
- Asset types: `duplicata_mercantil`, `duplicata_servico`

**Assinatura Típica:**
```json
{
  "sacados_elegiveis": ["BANCO BV S.A.", "CARGILL AGRÍCOLA S.A.", ...],
  "monitoramentos_ativos": [subordinacao, concentracao, inadimplencia],
  "subordinada_ratio": 0.15-0.35,
  "asset_complexity": "high"
}
```

#### **2. FINTECH/DIGITAL (Tecnologia Financeira)**
**Padrão de Detecção:**
- `valores.subordinada`: Ratio elevado (35%+ do total)
- Prazo: Curto/médio prazo (<2 anos)
- Asset types: `ccb_instituicoes_parceiras`, `unidades_recebiveis`
- Monitoring: Configuração simplificada (3-4 monitores)

**Assinatura Típica:**
```json
{
  "data_vencimento": "<24 meses da emissão",
  "subordinada_ratio": 0.35+,
  "asset_types": ["ccb", "urs", "pix"],
  "monitoring_complexity": "simplified"
}
```

#### **3. AGRONEGÓCIO (Especialização Setorial)**
**Padrão de Detecção:**
- Asset types: `cpr_financeira_registrada`
- `setores_elegíveis`: Focus em agronegócio
- Monitoring: Configurações sazonais específicas
- Prazo: Alinhado com ciclos agrícolas

**Assinatura Típica:**
```json
{
  "asset_types": ["cpr_financeira", "warrants_agricolas"],
  "setores_elegiveis": ["agricultura", "pecuaria", "agrobusiness"],
  "monitoring_seasonal": true
}
```

---

## **🔍 CAMPOS DE DETECÇÃO CRÍTICOS**

### **TIER 1: Discriminadores Primários**

#### **1. Estrutura Financeira**
```python
def detect_financial_pattern(pool_config):
    subordinada_ratio = pool_config["valores"]["subordinada"] / pool_config["valores"]["total_emissao"]
    
    if subordinada_ratio < 0.15:
        return "ultra_conservative"
    elif subordinada_ratio < 0.25:
        return "conservative"  # Corporate Credit típico
    elif subordinada_ratio < 0.35:
        return "moderate"
    else:
        return "aggressive"    # Fintech típico
```

#### **2. Complexidade Operacional**
```python
def detect_operational_complexity(pool_config):
    monitor_count = len(pool_config.get("monitoramentos_ativos", []))
    
    if monitor_count >= 7:
        return "high_sophistication"     # Corporate
    elif monitor_count >= 5:
        return "medium_sophistication"   # Mixed
    else:
        return "simplified"              # Fintech
```

#### **3. Asset Type Signature**
```python
def detect_asset_specialization(pool_config):
    asset_indicators = {
        "traditional": ["duplicata_mercantil", "duplicata_servico"],
        "fintech": ["ccb_instituicoes", "unidades_recebiveis", "pix"],
        "agro": ["cpr_financeira", "warrants", "setores_agricolas"],
        "mixed": ["mix_asset_types"]
    }
    
    # Return the matching pattern
```

### **TIER 2: Discriminadores Secundários**

#### **4. Configurações de Monitoring**
```python
def detect_monitoring_sophistication(pool_config):
    monitoring_patterns = {
        "concentration_limits": {
            "ultra_conservative": "< 5%",
            "conservative": "5-15%", 
            "moderate": "15-25%",
            "aggressive": "> 25%"
        },
        "subordination_triggers": {
            "conservative": "> 20%",
            "moderate": "10-20%",
            "aggressive": "< 10%"
        }
    }
```

#### **5. Prazo e Estrutura de Pagamento**
```python
def detect_term_structure(pool_config):
    term_months = calculate_term_months(
        pool_config["data_emissao"], 
        pool_config["data_vencimento"]
    )
    
    carencia = pool_config["cronograma_pagamentos"].get("carencia_meses", 0)
    
    if term_months <= 12:
        return "short_term"      # Fintech
    elif term_months <= 36:
        return "medium_term"     # Mixed
    else:
        return "long_term"       # Corporate
```

---

## **🌳 ÁRVORE DE DECISÃO AUTOMÁTICA**

### **Algoritmo de Classificação**

```python
def classify_escritura(pool_config):
    # Scoring system (0-100 points)
    scores = {
        "corporate_credit": 0,
        "fintech_digital": 0,
        "agronegocio": 0,
        "mixed_model": 0
    }
    
    # Financial Structure (30 points)
    subordinada_ratio = calculate_subordinada_ratio(pool_config)
    if subordinada_ratio < 0.25:
        scores["corporate_credit"] += 30
    elif subordinada_ratio > 0.35:
        scores["fintech_digital"] += 30
    else:
        scores["mixed_model"] += 20
    
    # Asset Types (25 points)
    asset_pattern = detect_asset_pattern(pool_config)
    scores[asset_pattern] += 25
    
    # Operational Complexity (25 points)
    complexity = detect_complexity(pool_config)
    if complexity == "high":
        scores["corporate_credit"] += 25
    elif complexity == "low":
        scores["fintech_digital"] += 25
    
    # Term Structure (20 points)
    term_pattern = detect_term_structure(pool_config)
    scores[term_pattern] += 20
    
    # Return highest scoring pattern
    return max(scores, key=scores.get), max(scores.values())
```

---

## **📊 PADRÕES DE DETECÇÃO POR ESCRITURA**

### **AFA Pool Pattern (Corporate Credit - Conservative)**
```yaml
Financial_Signature:
  subordinada_ratio: 33.3%
  total_emissao: 45M
  term_months: 36
  
Operational_Signature:
  monitor_count: 7
  concentration_individual: 27%
  subordination_minimum: 25%
  
Asset_Signature:
  sacados_count: 50+
  asset_diversity: high
  corporate_focus: true
```

### **SuperSim Pool Pattern (Fintech - Aggressive)**
```yaml
Financial_Signature:
  subordinada_ratio: 35.0%
  total_emissao: 10M
  term_months: 12
  
Operational_Signature:
  monitor_count: 4
  concentration_individual: 1%
  subordination_minimum: 35%
  
Asset_Signature:
  ccb_focus: true
  fintech_assets: true
  simplified_structure: true
```

### **E-ctare Pool Pattern (Agronegócio - Specialized)**
```yaml
Financial_Signature:
  subordinada_ratio: 20.0%
  total_emissao: 10M
  term_months: 36
  carencia_months: 12
  
Operational_Signature:
  monitor_count: 6
  seasonal_monitoring: true
  sector_concentration: agro
  
Asset_Signature:
  cpr_focus: true
  agricultural_sectors: true
  seasonal_cashflow: true
```

---

## **⚡ MOTOR DE DETECÇÃO AUTOMÁTICA**

### **Função Principal de Detecção**

```python
def detect_escritura_type(pool_config_path):
    """
    Detecta automaticamente o tipo de escritura baseado na configuração do pool.
    
    Returns:
        dict: {
            "primary_type": str,
            "confidence_score": float,
            "detected_patterns": list,
            "risk_profile": str,
            "complexity_level": str
        }
    """
    
    pool_config = load_json(pool_config_path)
    
    # Primary Classification
    primary_type, confidence = classify_escritura(pool_config)
    
    # Pattern Detection
    patterns = {
        "financial_pattern": detect_financial_pattern(pool_config),
        "operational_pattern": detect_operational_complexity(pool_config),
        "asset_pattern": detect_asset_specialization(pool_config),
        "term_pattern": detect_term_structure(pool_config)
    }
    
    # Risk Assessment
    risk_profile = assess_risk_profile(pool_config, primary_type)
    
    return {
        "primary_type": primary_type,
        "confidence_score": confidence / 100,
        "detected_patterns": patterns,
        "risk_profile": risk_profile,
        "complexity_level": patterns["operational_pattern"]
    }
```

---

## **🔮 DETECÇÃO DE VARIAÇÕES E EVOLUÇÃO**

### **Hybrid Models Detection**
```python
def detect_hybrid_patterns(pool_config):
    """Detecta padrões híbridos que combinam características de múltiplas escrituras."""
    
    pattern_scores = calculate_all_pattern_scores(pool_config)
    
    # Se múltiplos padrões têm score alto (>60), é híbrido
    high_scores = [p for p, s in pattern_scores.items() if s > 60]
    
    if len(high_scores) > 1:
        return {
            "type": "hybrid",
            "dominant_patterns": high_scores,
            "hybrid_characteristics": extract_hybrid_features(pool_config)
        }
```

### **Evolution Pattern Detection**
```python
def detect_evolution_pattern(pool_config, historical_pools):
    """Detecta padrões de evolução comparando com pools históricos."""
    
    evolution_indicators = {
        "increased_digitalization": check_digital_features(pool_config),
        "enhanced_monitoring": check_monitoring_evolution(pool_config),
        "asset_diversification": check_asset_evolution(pool_config),
        "regulatory_adaptation": check_regulatory_changes(pool_config)
    }
    
    return evolution_indicators
```

---

## **🎯 CASOS DE USO DO SISTEMA**

### **1. Classificação Automática de Novos Pools**
```python
# Exemplo de uso
new_pool_analysis = detect_escritura_type("config/pools/NewPool.json")
print(f"Tipo detectado: {new_pool_analysis['primary_type']}")
print(f"Confiança: {new_pool_analysis['confidence_score']:.2%}")
```

### **2. Validação de Configuração**
```python
def validate_pool_consistency(pool_config):
    """Valida se a configuração é consistente com o tipo de escritura detectado."""
    
    detected_type = detect_escritura_type(pool_config)
    
    # Verifica inconsistências
    inconsistencies = check_configuration_consistency(
        pool_config, 
        detected_type["primary_type"]
    )
    
    return inconsistencies
```

### **3. Template Recommendation**
```python
def recommend_template(pool_characteristics):
    """Recomenda template baseado nas características do pool."""
    
    escritura_type = detect_escritura_type(pool_characteristics)
    
    template_mapping = {
        "corporate_credit": "tier2_traditional_corporate.json",
        "fintech_digital": "tier2_fintech_simplified.json", 
        "agronegocio": "tier2_agronegocio_specialty.json"
    }
    
    return template_mapping[escritura_type["primary_type"]]
```

---

## **📋 CHECKLIST DE DETECÇÃO**

### **Para Futuras Análises:**

- [ ] **Estrutura Financeira**: Verificar ratio senior/subordinada
- [ ] **Tipo de Ativos**: Identificar categorias principais
- [ ] **Complexidade Operacional**: Contar monitores ativos
- [ ] **Perfil de Risco**: Analisar limites de concentração
- [ ] **Prazo de Operação**: Calcular term structure
- [ ] **Especialização Setorial**: Verificar focus de negócio
- [ ] **Padrões Híbridos**: Detectar características mistas
- [ ] **Evolução Temporal**: Comparar com padrões históricos

### **Campos Obrigatórios para Detecção:**
1. `valores.subordinada` / `valores.total_emissao`
2. `monitoramentos_ativos` (contagem e tipos)
3. `data_emissao` e `data_vencimento`
4. Asset type indicators (`sacados_elegiveis`, asset specifications)
5. Monitoring configurations (limits, thresholds)

---

**Este documento deve ser atualizado sempre que:**
- Novos tipos de escritura forem identificados
- Padrões evoluírem significativamente  
- Novas características discriminantes forem descobertas
- Híbridos complexos emergirem no mercado

**Versão:** 1.0 | **Data:** 2025-07-17 | **Próxima Revisão:** 2025-10-17