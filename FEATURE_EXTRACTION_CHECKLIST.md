# Comprehensive Feature Extraction Checklist for Legal Document to JSON Conversion

## Overview
This checklist ensures NO monitoring features are missed when converting legal documents (escrituras) to monitoring-compatible JSON files. Each section must be systematically reviewed for EVERY pool.

## 🔍 **MANDATORY SEARCH TERMS** (Search document for ALL of these)

### Recovery & Recourse Terms
- [ ] "direito de regresso" / "right of recourse"
- [ ] "recovery" / "recuperação" / "recuperar"
- [ ] "recompra" / "repurchase" / "buyback"
- [ ] "substituição" / "substitution"
- [ ] "fraud" / "fraude"
- [ ] "má formalização" / "poor formalization"
- [ ] "recovery rate" / "taxa de recuperação"
- [ ] "cobrança" / "collection"

### Time-Based Monitoring
- [ ] All numbers followed by "dias" (days)
- [ ] All numbers followed by "meses" (months)
- [ ] "prazo" / "deadline" / "período"
- [ ] "vencimento" / "maturity"
- [ ] "antecipado" / "early" / "anticipated"
- [ ] "cura" / "cure" / "remedy"

### Financial Limits & Ratios
- [ ] All percentage symbols (%)
- [ ] "limite" / "limit" / "máximo" / "mínimo"
- [ ] "concentração" / "concentration"
- [ ] "subordinação" / "subordination"
- [ ] "índice" / "index" / "ratio"
- [ ] "inadimplência" / "default" / "delinquency"
- [ ] Numbers with currency symbols (R$, $)

### Compliance & Monitoring
- [ ] "monitoramento" / "monitoring"
- [ ] "evento" / "event" / "trigger"
- [ ] "avaliação" / "evaluation" / "assessment"
- [ ] "violação" / "violation" / "breach"
- [ ] "critério" / "criteria" / "requirement"
- [ ] "elegibilidade" / "eligibility"

### Provisions & Risk
- [ ] "provisão" / "provision" / "PDD"
- [ ] "risco" / "risk" / "grupo de risco"
- [ ] "atraso" / "delay" / "late" / "overdue"
- [ ] "classificação" / "classification"

## 📋 **SYSTEMATIC EXTRACTION PROCESS**

### Phase 1: Document Structure Analysis
1. **Document Type Identification**
   - [ ] Main emission deed (escritura de emissão)
   - [ ] Amendment (aditamento)
   - [ ] Supplementary agreement (termo aditivo)
   - [ ] Version number/date

2. **Table of Contents Review**
   - [ ] Extract all clause numbers and titles
   - [ ] Identify monitoring-related sections
   - [ ] Flag complex/nested clauses for deeper review

3. **Annexes Identification**
   - [ ] List all annexes (Anexo I, II, III, etc.)
   - [ ] Identify monitoring-relevant annexes
   - [ ] Extract annex titles and purposes

### Phase 2: Core Information Extraction

#### A. Basic Pool Information
- [ ] **Pool Name**: Official name and administrative name
- [ ] **Emission Number**: Sequential number in emission series
- [ ] **Emission Date**: Start date of the pool
- [ ] **Maturity Date**: Final maturity date
- [ ] **Total Value**: Total emission value
- [ ] **Issuer**: Emitting company (emissora)
- [ ] **Applicable Law**: Legal framework (Lei 14.430/22, etc.)

#### B. Financial Structure
- [ ] **Senior Series**: Number, value, subordination hierarchy
- [ ] **Subordinated Series**: Number, value, subordination hierarchy
- [ ] **Minimum Subordination Index**: Threshold percentages
- [ ] **Critical Subordination Index**: Emergency thresholds
- [ ] **Payment Schedule**: Amortization timeline and percentages

#### C. Asset Eligibility Criteria
- [ ] **Permitted Asset Types**: CCBs, duplicates, etc. with percentage limits
- [ ] **Individual Limits**: Minimum value, maturity range, interest rates
- [ ] **Portfolio Limits**: Average maturity, concentration limits
- [ ] **Eligible Debtors List**: Pre-approved counterparties
- [ ] **Acquisition Period**: Time limits for new asset acquisition

### Phase 3: Monitoring Events Extraction

#### A. Concentration Limits
- [ ] **Individual Debtor**: Maximum percentage per entity
- [ ] **Individual Assignor**: Maximum percentage per originator
- [ ] **Top N Analysis**: Aggregate limits for largest entities
- [ ] **Institution-Specific**: Special limits for partner institutions
- [ ] **Geographic**: Regional concentration limits (if any)

#### B. Financial Performance Metrics
- [ ] **Subordination Index**: Minimum thresholds and monitoring frequency
- [ ] **Default Rates**: Maximum percentages for different aging buckets
- [ ] **Recovery Rates**: Minimum recovery percentages and calculation methods
- [ ] **Portfolio Quality**: Asset quality metrics and limits

#### C. Time-Based Events
- [ ] **Acquisition Deadlines**: Latest dates for new asset acquisition
- [ ] **Portfolio Formation**: Initial period with relaxed criteria
- [ ] **Maturity Windows**: Individual asset maturity requirements
- [ ] **Cure Periods**: Time allowed to remedy violations

### Phase 4: Recovery Mechanisms Analysis

#### A. Right of Recourse (Direito de Regresso)
- [ ] **Eligibility Conditions**: When recourse can be exercised
- [ ] **Time Triggers**: Days overdue before recourse activation
- [ ] **Cause Categories**: Fraud, poor formalization, other reasons
- [ ] **Recovery Targets**: Against whom recourse can be exercised
- [ ] **Recovery Rates**: Expected recovery percentages

#### B. Mandatory Repurchase
- [ ] **Trigger Events**: Conditions requiring repurchase
- [ ] **Time Limits**: Deadlines for repurchase/substitution
- [ ] **Replacement Criteria**: Requirements for substitute assets
- [ ] **Responsible Party**: Who must execute repurchase
- [ ] **Valuation Method**: How repurchase price is determined

#### C. Collection Mechanisms
- [ ] **Collection Agent**: Who handles collections
- [ ] **Collection Accounts**: Dedicated accounts for recoveries
- [ ] **Collection Performance**: Minimum collection rates
- [ ] **Collection Reporting**: Frequency and format requirements

### Phase 5: Risk Provisioning

#### A. Risk Classification
- [ ] **Risk Groups**: Classification system (AA, A, B, C, etc.)
- [ ] **Aging Buckets**: Days overdue for each risk category
- [ ] **Provision Percentages**: Provision rates for each risk group
- [ ] **Reclassification Rules**: When assets move between risk groups

#### B. Provision Calculation
- [ ] **Calculation Methodology**: How provisions are computed
- [ ] **Frequency**: How often provisions are recalculated
- [ ] **Reporting Requirements**: Provision reporting obligations
- [ ] **Reserve Requirements**: Minimum reserve levels

### Phase 6: Early Maturity Events

#### A. Automatic Events (No Cure Period)
- [ ] **Bankruptcy/Judicial Recovery**: Immediate acceleration triggers
- [ ] **Corporate Changes**: Mergers, splits without approval
- [ ] **Material Litigation**: Court decisions above threshold
- [ ] **Regulatory Issues**: License revocation, sanctions

#### B. Curable Events (With Cure Period)
- [ ] **Payment Defaults**: Monetary obligation breaches
- [ ] **Covenant Violations**: Non-monetary obligation breaches
- [ ] **Limit Breaches**: Concentration or performance limit violations
- [ ] **Documentation Issues**: Missing or incorrect documentation

### Phase 7: Operational Structure

#### A. Accounts and Banking
- [ ] **Central Account**: Main account details and purposes
- [ ] **Linked Accounts**: Escrow and dedicated accounts
- [ ] **Account Restrictions**: Movement limitations and controls
- [ ] **Bank Requirements**: Authorized institutions

#### B. Investment Rules
- [ ] **Permitted Investments**: Allowed investment types
- [ ] **Investment Restrictions**: Prohibited investments
- [ ] **Liquidity Requirements**: Daily liquidity needs
- [ ] **Institution Limitations**: Approved counterparties

#### C. Service Providers
- [ ] **Operational Services**: Service provider details
- [ ] **Originator**: Originator responsibilities and obligations
- [ ] **Debenture Holders**: Rights and obligations
- [ ] **Other Parties**: Additional service providers

### Phase 8: Special Features Identification

#### A. Pool-Specific Rules
- [ ] **Unique Concentration Limits**: Pool-specific concentration rules
- [ ] **Special Relationships**: Partner institution arrangements
- [ ] **Unique Asset Types**: Pool-specific eligible assets
- [ ] **Special Calculation Methods**: Pool-specific formulas

#### B. Enhanced Monitoring
- [ ] **Additional Metrics**: Pool-specific performance indicators
- [ ] **Special Events**: Unique monitoring events
- [ ] **Enhanced Reporting**: Additional reporting requirements
- [ ] **Stress Testing**: Special stress test requirements

## ✅ **VALIDATION CHECKLIST**

### Completeness Check
- [ ] All search terms have been systematically reviewed
- [ ] Every annex has been analyzed for monitoring content
- [ ] All tables and formulas have been extracted
- [ ] All time periods and deadlines have been captured
- [ ] All percentage limits have been identified

### Accuracy Check
- [ ] All percentages converted to decimal format (5% = 0.05)
- [ ] All monetary values in float format
- [ ] All null values properly set (not "NaN" or "N/A")
- [ ] All dates in YYYY-MM-DD format
- [ ] All boolean flags properly set

### Monitoring Compatibility Check
- [ ] All monitoring events have "ativo" flags
- [ ] All limits have proper "unidade" specifications
- [ ] All time-based events have clear deadlines
- [ ] All formulas are in monitoring-friendly format
- [ ] All pool-specific rules use standardized structure

### Cross-Reference Check
- [ ] Compare with other pools to identify missing features
- [ ] Verify all events have corresponding clause references
- [ ] Check for consistency in field naming
- [ ] Validate against schema requirements

## 🚨 **RED FLAGS** (Indicators of Missing Features)

### Warning Signs
- [ ] Pool has significantly fewer monitoring events than others
- [ ] No recovery mechanisms identified
- [ ] Missing time-based deadlines
- [ ] No institution-specific rules
- [ ] Unusually simple structure compared to similar pools

### Common Oversights
- [ ] Recovery rate calculations buried in event descriptions
- [ ] Multiple deadline types (business vs. calendar days)
- [ ] Implicit concentration limits not explicitly stated
- [ ] Collection mechanisms mentioned without details
- [ ] Risk provisioning rules scattered across multiple clauses

## 📊 **QUALITY SCORE**

### Scoring Criteria (Total: 100 points)
- **Basic Information**: 20 points (complete pool identification)
- **Financial Structure**: 15 points (series, subordination, schedules)
- **Monitoring Events**: 25 points (comprehensive event coverage)
- **Recovery Mechanisms**: 20 points (all recovery features captured)
- **Risk Provisioning**: 10 points (complete PDD structure)
- **Validation**: 10 points (format compliance and cross-checks)

### Quality Thresholds
- **95-100 points**: Excellent - Ready for production
- **85-94 points**: Good - Minor adjustments needed
- **75-84 points**: Acceptable - Some features may be missing
- **Below 75 points**: Incomplete - Requires comprehensive review

## 🔄 **CONTINUOUS IMPROVEMENT**

### Learning from Missed Features
- [ ] Document any features missed during initial extraction
- [ ] Update search terms based on new discoveries
- [ ] Enhance checklist with pool-specific patterns
- [ ] Improve validation criteria based on errors found

### Process Refinement
- [ ] Track time spent on each extraction phase
- [ ] Identify most commonly missed feature types
- [ ] Develop automated validation scripts
- [ ] Create pool comparison tools for consistency checking

---

**Note**: This checklist must be used for EVERY pool conversion. Each checkbox must be explicitly verified. Missing features in monitoring systems can lead to significant compliance and financial risks.