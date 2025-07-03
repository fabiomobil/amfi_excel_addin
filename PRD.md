# AmFi Excel Add-in - Product Requirements Document

## 1. Executive Summary

**Product Name**: AmFi (Asset Management Financial Intelligence)  
**Version**: 1.0  
**Document Date**: July 2025  
**Product Type**: Excel Add-in for Financial Data Analysis

### 1.1 Product Vision
AmFi transforms Excel into a powerful financial analysis platform for investment fund management, providing real-time portfolio analytics, compliance monitoring, and advanced financial calculations through seamless Python integration.

### 1.2 Business Objectives
- **Primary**: Enable investment fund managers to perform complex financial analysis directly within Excel
- **Secondary**: Automate compliance monitoring and concentration risk assessment
- **Tertiary**: Reduce analysis time from hours to minutes through cached data processing

## 2. Product Overview

### 2.1 Problem Statement
Investment fund managers struggle with:
- Manual data processing across multiple file formats (CSV, JSON, XLSX)
- Complex concentration analysis requiring custom calculations
- Time-consuming compliance monitoring
- Disconnected tools requiring data export/import cycles
- Limited Excel native capabilities for advanced financial calculations

### 2.2 Solution Overview
AmFi provides a comprehensive Excel add-in that:
- Integrates multiple data sources seamlessly
- Performs advanced financial calculations in real-time
- Monitors compliance limits automatically
- Caches data for optimal performance
- Maintains audit trails and data integrity

## 3. Target Users

### 3.1 Primary Users
**Portfolio Managers**
- Need: Real-time portfolio analysis and performance monitoring
- Goals: Quick decision-making, risk assessment, compliance verification
- Pain Points: Data fragmentation, manual calculations, time constraints

**Risk Analysts**
- Need: Concentration analysis, limit monitoring, scenario modeling
- Goals: Early risk detection, compliance assurance, reporting automation
- Pain Points: Complex calculations, multiple data sources, manual processes

**Fund Administrators**
- Need: Accurate reporting, compliance documentation, data validation
- Goals: Error reduction, process automation, audit readiness
- Pain Points: Data inconsistency, manual reconciliation, reporting delays

### 3.2 Secondary Users
- **Compliance Officers**: Regulatory reporting and limit monitoring
- **Investment Analysts**: Due diligence and investment evaluation
- **Finance Teams**: Financial reporting and performance attribution

## 4. Functional Requirements

### 4.1 Data Processing Functions

#### F1: Dashboard Analytics
**Function**: `AmfiDashboard`
- **Input**: CSV file path, pool names, view type (exec/full)
- **Output**: Formatted investment opportunity matrix
- **Requirements**:
  - Support single and multiple pool selection
  - Executive view (key metrics) vs full view (all columns)
  - Real-time data filtering and aggregation
  - Error handling for invalid file paths/formats

#### F2: Excel Portfolio Analysis
**Function**: `AmfiXLSX`
- **Input**: XLSX file path, pool names, view type
- **Output**: Asset/loan data matrix
- **Requirements**:
  - Parse complex Excel structures
  - Handle large datasets (>10MB files)
  - Support merged cells and complex formatting
  - Maintain data type integrity

#### F3: JSON Configuration Management
**Function**: `AmFiReadJSON`
- **Input**: JSON file path, key name
- **Output**: Extracted data table
- **Requirements**:
  - Deep key search in nested JSON
  - Handle array and object structures
  - Validate JSON format integrity
  - Support multiple encoding formats

#### F4: Pool Management
**Function**: `ListPools`
- **Input**: Data file path
- **Output**: Alphabetically sorted pool list
- **Requirements**:
  - Deduplicate pool names
  - Case-insensitive sorting
  - Handle empty/null values
  - Cross-reference with configuration files

### 4.2 Analysis Functions

#### F5: Concentration Analysis
**Function**: `AmfiConcentracao`
- **Input**: XLSX file, pool, total PL, analysis type, limits, ignore list
- **Output**: Concentration report with compliance status
- **Requirements**:
  - **Analysis Types**:
    - Cedente (assignor) concentration
    - Sacado (debtor) concentration  
    - Combined cedente/sacado analysis
  - **Limit Monitoring**:
    - Individual entity limits (%)
    - Top N aggregate limits (%)
    - Combined limit scenarios
  - **Compliance Features**:
    - Real-time status calculation
    - Excess/available space reporting
    - Color-coded status indicators
  - **Ignore Functionality**:
    - String-based entity exclusion
    - Excel range-based exclusion
    - Pipe-separated multiple exclusions
  - **Top N Analysis**:
    - Configurable top entity count
    - Aggregate compliance checking
    - Summary row with total status

### 4.3 Financial Calculations

#### F6: Subordination Index (IS)
**Function**: `AmfiCalcularIS`
- **Input**: Patrimônio Líquido (PL), Juros Remuneratórios (JR)
- **Output**: IS percentage
- **Requirements**:
  - Precision to 6 decimal places
  - Handle edge cases (zero values)
  - Input validation and error messages

#### F7: JR Calculation
**Function**: `AmfiCalcularJR`
- **Input**: PL, desired IS percentage
- **Output**: Required JR value
- **Requirements**:
  - Reverse calculation accuracy
  - Support percentage and decimal inputs
  - Boundary condition handling

#### F8: IS Adjustment Analysis
**Function**: `AmfiCalcularAdicionalIS`
- **Input**: Initial PL, current IS, target IS
- **Output**: Comprehensive adjustment report
- **Requirements**:
  - **Report Components**:
    - Current state (PL, JR, SR, IS)
    - Required additional amount
    - Final state projections
  - **Calculation Accuracy**: Financial-grade precision
  - **Scenario Analysis**: Multiple target IS support

### 4.4 System Functions

#### F9: Cache Management
**Functions**: `ClearCache`, `CacheStats`
- **Requirements**:
  - **Cache Types**: CSV, JSON, XLSX, All
  - **Statistics**: File count per type, memory usage, hit rates

### 4.5 Document Processing Functions

#### F10: Legal Document Processing & Version Management
**Function**: `ProcessEscrituras`
- **Input**: MD files from escrituras_md directory
- **Output**: Structured JSON files with version control
- **Requirements**:
  - **Document Parsing**:
    - Extract pool information from legal documents (escrituras de emissão)
    - Handle multiple document formats and structural variations
    - Support Portuguese language processing for legal terminology
    - Identify document types (main deeds vs. amendments)
  - **Data Extraction**:
    - Pool identification and naming normalization
    - Financial terms (emission values, series structure, rates)
    - Party information (emissora, debenturistas, originador)
    - Compliance criteria (concentration limits, eligibility rules)
    - Legal clauses (monitoring events, early maturity conditions)
  - **Version Management**:
    - Track document versions and amendments with complete audit trail
    - Create versioned JSON files for amendments (e.g., pool_v2.json)
    - Maintain historical JSON archives in escrituras_archive directory
    - Prevent data loss during updates and overwrites
  - **Data Validation**:
    - Ensure JSON schema compliance with existing structure
    - Validate extracted financial data for completeness and accuracy
    - Cross-reference with existing pool data for consistency
    - Flag missing or incomplete information for manual review
  - **Data Standardization**:
    - Enforce consistent data types across all pool JSONs
    - Standardize field names for monitoring compatibility
    - Normalize pool-specific rules into common structure
    - Validate Python-accessible format for automated monitoring
  - **Quality Assurance**:
    - Provide parsing confidence scores for extracted data
    - Log all extraction decisions and assumptions made
    - Enable manual override capabilities for complex cases
    - Generate validation reports highlighting potential issues
  - **Error Handling**:
    - Log parsing errors and incomplete extractions with detailed context
    - Provide manual review flags for complex or ambiguous documents
    - Maintain system stability during processing failures
    - Rollback capabilities for failed conversions

### F11: JSON Schema Standardization for Python Monitoring
**Function**: `StandardizePoolJSON`
- **Input**: Extracted pool data from MD documents
- **Output**: Monitoring-optimized JSON structure
- **Requirements**:
  - **Data Type Enforcement**:
    - Use `null` for missing values (never `"NaN"`, `"N/A"`, or empty strings)
    - Use `float` for all monetary values
    - Use `float` in decimal format for percentage values (5% = 0.05, not 5.0)
    - Use `boolean` for active/inactive rule flags
    - Use consistent date format: `"YYYY-MM-DD"`
  - **Standardized Field Structure**:
    - Common field names across all pools for generic monitoring code
    - Pool-specific rules normalized into standard nested structures
    - Consistent naming: lowercase_with_underscores
  - **Monitoring Compatibility**:
    - Direct field access without type checking or conversion
    - Iteration-friendly structures for automated rule checking
    - Null-safe operations for optional parameters
    - Generic monitoring loops without pool-specific logic
  - **Schema Validation**:
    - JSON schema validation before file creation
    - Automated detection of data type inconsistencies
    - Field name standardization verification
    - Monitoring code compatibility testing

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **Data Loading**: <5 seconds for files up to 50MB
- **Calculation Response**: <2 seconds for concentration analysis
- **Cache Hit Rate**: >85% for repeated operations
- **Memory Usage**: <500MB peak for typical workloads
- **Concurrent Users**: Support 10+ simultaneous Excel sessions

### 5.2 Reliability Requirements
- **Uptime**: 99.9% availability during business hours
- **Error Recovery**: Graceful handling of corrupted/missing files
- **Data Integrity**: 100% calculation accuracy vs manual verification
- **Fault Tolerance**: Continue operation with partial data unavailability

### 5.3 Usability Requirements
- **Learning Curve**: <2 hours for experienced Excel users
- **Error Messages**: Clear, actionable guidance in Portuguese/English
- **Documentation**: Comprehensive function reference with examples
- **Integration**: Seamless Excel experience without external dependencies

### 5.4 Security Requirements
- **Data Privacy**: No data transmission outside local environment
- **File Access**: Read-only access to source files
- **Audit Trail**: Log all function calls with parameters
- **Validation**: Input sanitization and type checking

### 5.5 Compatibility Requirements
- **Excel Versions**: 2016, 2019, 365 (Windows)
- **Python Versions**: 3.8+
- **Operating Systems**: Windows 10/11, WSL2 support
- **File Formats**: CSV (UTF-8/ANSI), JSON, XLSX/XLS

## 6. Technical Architecture

### 6.1 System Architecture
```
Excel Frontend (xlwings)
    ↓
AmFi UDF Layer (amfi.py)
    ↓
Business Logic Layer
    ├── Data Handlers (csv_handler, json_handler, xlsx_handler)
    ├── Analysis Engine (analysis_handler)
    ├── Calculation Engine (calculus)
    └── Cache Manager (cache_manager)
    ↓
Data Storage Layer
    ├── CSV Files (../data/csv/)
    ├── JSON Configs (../data/escrituras/)
    └── XLSX Files (../data/xlsx/)
```

### 6.2 Data Flow
1. **Input**: Excel function call with parameters
2. **Validation**: Parameter type and range checking
3. **Cache Check**: Verify if processed data exists
4. **Data Loading**: File parsing and validation
5. **Processing**: Business logic execution
6. **Caching**: Store results for future use
7. **Output**: Formatted Excel-compatible data structure

### 6.3 Data Processing Architecture

#### Daily Data Pipeline
```
1. Data Generation (External System)
   ├── CSV: AcompanhamentoDeOportunidades-YYYY-MM-DD HH_MM_SS -0300.csv
   └── XLSX: Carteira Global YYYY-MM-DD HHMMSS.xlsx

2. Data Discovery (AmFi)
   ├── Automatic file detection by timestamp
   ├── Validation of file structure
   └── Cache invalidation of previous day

3. Data Processing
   ├── CSV → Pool overview and filtering
   └── XLSX → Detailed portfolio analysis

4. Output Generation
   └── Excel formulas consume processed data
```

#### Data Schema

**CSV Schema (Pool Overview)**
- Nome: Pool identifier
- PL: Patrimônio Líquido (Net Worth)
- SR/JR: Senior/Junior tranches
- IS%: Subordination index
- Status: Pool operational status
- Compliance indicators

**XLSX Schema (Portfolio Details)**
- Pool: Pool identifier (links to CSV)
- Nome do Sacado: Debtor name
- Nome do Cedente: Assignor name
- Valor presente (R$): Present value
- Data de aquisição: Acquisition date
- Vencimento: Maturity date

### 6.4 Error Handling Strategy
- **Input Validation**: Pre-execution parameter checking
- **Graceful Degradation**: Partial results when possible
- **User Feedback**: Clear error messages with resolution steps
- **Logging**: Detailed error logs for debugging
- **Recovery**: Automatic retry for transient failures
- **Data Freshness**: Alert when using stale data

## 7. Success Metrics

### 7.1 User Adoption Metrics
- **Primary Users**: 100% portfolio manager adoption within 3 months
- **Function Usage**: Average 50+ function calls per user per day
- **User Satisfaction**: >4.5/5 rating on usability survey
- **Training Completion**: <2 hours average onboarding time

### 7.2 Performance Metrics
- **Speed Improvement**: 80% reduction in analysis time vs manual methods
- **Accuracy**: Zero calculation errors in production use
- **Reliability**: <0.1% function failure rate
- **Cache Efficiency**: >85% cache hit rate for repeated operations

### 7.3 Business Impact Metrics
- **Time Savings**: 20+ hours per week per analyst
- **Error Reduction**: 95% decrease in manual calculation errors
- **Compliance**: 100% automated limit monitoring coverage
- **Decision Speed**: 50% faster investment decision cycles

## 8. Implementation Timeline

### Phase 1: Core Foundation (Complete)
- ✅ Basic UDF framework
- ✅ Data handlers implementation
- ✅ Cache management system
- ✅ Financial calculations

### Phase 2: Advanced Analytics (Complete)
- ✅ Concentration analysis
- ✅ Compliance monitoring
- ✅ Multi-format data support
- ✅ Error handling framework

### Phase 3: Enhancement & Scale (Next)
- 🔄 Unit testing implementation
- 🔄 Performance optimization
- 🔄 Enhanced documentation
- 🔄 User training materials

### Phase 4: Enterprise Features (Future)
- 📋 Multi-language support
- 📋 Advanced reporting
- 📋 API integration capabilities
- 📋 Real-time data connections

## 9. Risk Assessment

### 9.1 Technical Risks
- **High**: xlwings compatibility with future Excel versions
- **Medium**: Python environment management complexity
- **Low**: File format evolution requiring updates

### 9.2 Business Risks
- **High**: User adoption resistance to new tools
- **Medium**: Regulatory requirement changes
- **Low**: Competition from commercial solutions

### 9.3 Mitigation Strategies
- **Technical**: Version pinning, comprehensive testing, fallback options
- **Business**: Change management, training programs, stakeholder engagement
- **Operational**: Documentation, support processes, maintenance procedures

## 10. Support and Maintenance

### 10.1 Support Model
- **Tier 1**: User documentation and self-service resources
- **Tier 2**: Technical support for function usage and troubleshooting
- **Tier 3**: Development team for bug fixes and enhancements

### 10.2 Maintenance Schedule
- **Daily**: Cache cleanup and performance monitoring
- **Weekly**: Error log review and user feedback analysis
- **Monthly**: Performance optimization and minor updates
- **Quarterly**: Major feature releases and dependency updates

### 10.3 Documentation Requirements
- **User Manual**: Function reference with examples
- **Technical Guide**: Installation and configuration
- **API Documentation**: Developer reference for extensions
- **Troubleshooting Guide**: Common issues and solutions

---

**Document Control**
- **Version**: 1.0
- **Last Updated**: July 2025
- **Next Review**: October 2025
- **Approvers**: Product Manager, Technical Lead, Business Stakeholders