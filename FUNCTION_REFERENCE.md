# AmFi Excel Functions - Complete Reference Guide

## Overview
This document provides comprehensive usage instructions for all AmFi Excel UDF functions. These functions integrate Python processing power directly into Excel spreadsheets for investment fund management and analysis.

## Table of Contents
1. [Data Processing Functions](#data-processing-functions)
2. [Enhanced XLSX Functions](#enhanced-xlsx-functions)
3. [Analysis Functions](#analysis-functions)
4. [Financial Calculation Functions](#financial-calculation-functions)
5. [File Discovery Functions](#file-discovery-functions)
6. [Data Quality Functions](#data-quality-functions)
7. [Utility Functions](#utility-functions)
8. [Common Usage Patterns](#common-usage-patterns)
9. [Troubleshooting](#troubleshooting)

---

## Data Processing Functions

### AmfiDashboard
**Purpose**: Investment opportunity dashboard from CSV files  
**Syntax**: `=AmfiDashboard(caminho_arquivo, nomes_pool, visao)`

**Parameters**:
- `caminho_arquivo` (string): Path to CSV file
- `nomes_pool` (string/range): Pool name(s) to filter
- `visao` (string): "exec" for executive view, "full" for all columns

**Examples**:
```excel
=AmfiDashboard("C:\data\csv\AcompanhamentoDeOportunidades-2025-06-30.csv", "Blipay Pool #1", "exec")
=AmfiDashboard(AmfiLatestCSV(), A1:A3, "full")  # Multiple pools from range
```

**Returns**: Formatted table with pool overview data

---

### AmfiXLSX (Enhanced)
**Purpose**: Targeted receivables data with pool and status filtering  
**Syntax**: `=AmfiXLSX(pool_name, [status], [date], [visao])`

**Parameters**:
- `pool_name` (string, required): Specific pool to retrieve
- `status` (string, optional): Filter by receivable status (empty = all statuses)
- `date` (string, optional): Target date "YYYY-MM-DD" (empty = latest file)
- `visao` (string, optional): "exec" or "full" view (default: "exec")

**Examples**:
```excel
=AmfiXLSX("Blipay Pool #1")                           # Latest file, all statuses
=AmfiXLSX("Blipay Pool #1", "Vencido")                # Only overdue receivables
=AmfiXLSX("Blipay Pool #1", "", "2025-06-30")        # Specific date, all statuses
=AmfiXLSX("Blipay Pool #1", "Vigente", "2025-06-30", "full")  # Complete view
```

**Returns**: Filtered receivables data with file date as first column

**Key Features**:
- ✅ **Performance**: Only loads data for specified pool
- ✅ **Traceability**: File date shown in first column
- ✅ **Flexibility**: Optional status and date filtering
- ✅ **Smart Discovery**: Auto-finds files by date

---


---

### AmFiReadJSON
**Purpose**: Extract data from JSON configuration files  
**Syntax**: `=AmFiReadJSON(caminho_arquivo, chave)`

**Parameters**:
- `caminho_arquivo` (string): Path to JSON file
- `chave` (string): Key name to search for

**Examples**:
```excel
=AmFiReadJSON("../data/escrituras/afa_pool_1.json", "eligibility_criteria")
=AmFiReadJSON("../data/escrituras/lecapital_pool_1.json", "limits")
```

**Returns**: Formatted table with extracted JSON data

---

### ListPools
**Purpose**: List available pools from CSV files  
**Syntax**: `=ListPools(caminho_arquivo)`

**Parameters**:
- `caminho_arquivo` (string): Path to CSV file

**Examples**:
```excel
=ListPools(AmfiLatestCSV())
=ListPools("C:\data\csv\AcompanhamentoDeOportunidades-2025-06-30.csv")
```

**Returns**: Alphabetically sorted list of unique pool names

---

## Enhanced XLSX Functions

### AmfiGetPools
**Purpose**: List available pools in XLSX files  
**Syntax**: `=AmfiGetPools([date])`

**Parameters**:
- `date` (string, optional): Target date "YYYY-MM-DD" (empty = latest file)

**Examples**:
```excel
=AmfiGetPools()                    # Pools from latest file
=AmfiGetPools("2025-06-30")        # Pools from specific date
```

**Returns**: List of unique pools available in the XLSX file

---

### AmfiGetStatuses
**Purpose**: List available statuses for a specific pool  
**Syntax**: `=AmfiGetStatuses(pool_name, [date])`

**Parameters**:
- `pool_name` (string): Name of the pool
- `date` (string, optional): Target date "YYYY-MM-DD" (empty = latest file)

**Examples**:
```excel
=AmfiGetStatuses("Blipay Pool #1")              # Statuses from latest file
=AmfiGetStatuses("Blipay Pool #1", "2025-06-30") # Statuses from specific date
```

**Returns**: List of unique status values for the specified pool

---

## Analysis Functions

### AmfiConcentracao
**Purpose**: Concentration analysis with compliance monitoring  
**Syntax**: `=AmfiConcentracao(arquivo_xlsx, pool, pl_total, [tipo], [top], [limite], [ignore_list])`

**Parameters**:
- `arquivo_xlsx` (string): Path to XLSX file
- `pool` (string): Pool name to analyze
- `pl_total` (number): Total PL value for percentage calculations
- `tipo` (string, optional): "sacado", "cedente", or empty for combined
- `top` (string, optional): "top=X" to limit results (e.g., "top=10")
- `limite` (string, optional): Compliance limits (e.g., "individual=15,top3=30")
- `ignore_list` (string/range, optional): Entities to exclude from analysis

**Examples**:
```excel
=AmfiConcentracao(AmfiLatestXLSX(), "Blipay Pool #1", 5000000)
=AmfiConcentracao(AmfiLatestXLSX(), "Blipay Pool #1", 5000000, "sacado", "top=10")
=AmfiConcentracao(AmfiLatestXLSX(), "Blipay Pool #1", 5000000, "cedente", "top=5", "individual=15,top3=30")
=AmfiConcentracao(AmfiLatestXLSX(), "Blipay Pool #1", 5000000, , , "individual=12", "EMPRESA_X|EMPRESA_Y")
```

**Returns**: Concentration analysis table with:
- Entity names (Sacado/Cedente)
- Values and percentages
- Available space or excess amounts
- Compliance status (enquadrado/violado)

**Compliance Features**:
- **Individual limits**: Maximum percentage per entity
- **Aggregate limits**: Maximum for top N entities combined
- **Status indicators**: Clear compliance messaging
- **Ignore functionality**: Exclude specific entities

---

## Financial Calculation Functions

### AmfiCalcularIS
**Purpose**: Calculate Subordination Index (IS)  
**Syntax**: `=AmfiCalcularIS(pl, jr)`

**Parameters**:
- `pl` (number): Patrimônio Líquido (Net Worth)
- `jr` (number): Juros Remuneratórios (Remuneration Interest)

**Examples**:
```excel
=AmfiCalcularIS(1000000, 800000)    # Returns 20% (200000/1000000)
=AmfiCalcularIS(B2, C2)             # Using cell references
```

**Returns**: IS percentage value

**Formula**: IS = (PL - JR) / PL × 100

---

### AmfiCalcularJR
**Purpose**: Calculate JR needed for target IS  
**Syntax**: `=AmfiCalcularJR(pl, is_percentual)`

**Parameters**:
- `pl` (number): Patrimônio Líquido
- `is_percentual` (number): Target IS percentage (e.g., 20 for 20%)

**Examples**:
```excel
=AmfiCalcularJR(1000000, 20)       # Returns 800000 (JR needed for 20% IS)
=AmfiCalcularJR(B2, 15)            # 15% target IS
```

**Returns**: Required JR value

**Formula**: JR = PL × (1 - IS/100)

---

### AmfiCalcularAdicionalIS
**Purpose**: Calculate additional JR needed to reach target IS  
**Syntax**: `=AmfiCalcularAdicionalIS(pl_inicial, is_atual, is_desejado)`

**Parameters**:
- `pl_inicial` (number): Initial Patrimônio Líquido
- `is_atual` (number): Current IS in decimal (e.g., 0.15 for 15%)
- `is_desejado` (number): Target IS in decimal (e.g., 0.20 for 20%)

**Examples**:
```excel
=AmfiCalcularAdicionalIS(1000000, 0.15, 0.20)
=AmfiCalcularAdicionalIS(B2, 0.12, 0.18)
```

**Returns**: Detailed calculation table showing:
- Initial state (PL, JR, SR, IS)
- Required additional amount
- Final projected state

---

## File Discovery Functions

### AmfiLatestCSV
**Purpose**: Get path to most recent CSV file  
**Syntax**: `=AmfiLatestCSV()`

**Examples**:
```excel
=AmfiLatestCSV()
=AmfiDashboard(AmfiLatestCSV(), "Pool ABC", "exec")  # Use with other functions
```

**Returns**: Full path to the latest CSV file

---

### AmfiLatestXLSX
**Purpose**: Get path to most recent XLSX file  
**Syntax**: `=AmfiLatestXLSX()`

**Examples**:
```excel
=AmfiLatestXLSX()
=AmfiConcentracao(AmfiLatestXLSX(), "Pool ABC", 1000000)  # Use with other functions
```

**Returns**: Full path to the latest XLSX file

---

### AmfiDataStatus
**Purpose**: Check data freshness and age  
**Syntax**: `=AmfiDataStatus()`

**Examples**:
```excel
=AmfiDataStatus()
```

**Returns**: Status string showing age of CSV and XLSX files
- Example: "CSV: Fresh | XLSX: 2h old"
- Helps identify stale data issues

---

## Data Quality Functions

### AmfiValidateData
**Purpose**: Comprehensive data validation report  
**Syntax**: `=AmfiValidateData()`

**Examples**:
```excel
=AmfiValidateData()
```

**Returns**: Detailed validation report including:
- File structure validation
- Data consistency checks
- Cross-file validation
- Day-over-day comparisons
- Overall status (VALID/WARNING/ERROR)

**Validation Checks**:
- ✅ Required columns present
- ✅ Data type consistency
- ✅ Pool name matching between CSV and XLSX
- ✅ Value consistency checks
- ✅ Significant change detection

---

## Utility Functions

### ClearCache
**Purpose**: Manage file cache for performance  
**Syntax**: `=ClearCache([tipo])`

**Parameters**:
- `tipo` (string, optional): "csv", "json", "xlsx", or "all" (default)

**Examples**:
```excel
=ClearCache()           # Clear all caches
=ClearCache("csv")      # Clear only CSV cache
=ClearCache("xlsx")     # Clear only XLSX cache
```

**Returns**: Status message with count of files removed

**When to Use**:
- After updating data files
- When experiencing performance issues
- Daily maintenance routines

---

### CacheStats
**Purpose**: Display cache statistics  
**Syntax**: `=CacheStats()`

**Examples**:
```excel
=CacheStats()
```

**Returns**: Cache statistics summary
- Example: "Cache: 5 arquivos (CSV: 2, JSON: 1, XLSX: 2)"

---

## Common Usage Patterns

### 1. Daily Monitoring Dashboard
```excel
# Check data freshness
=AmfiDataStatus()

# Get latest pools
=AmfiGetPools()

# Monitor specific pool
=AmfiXLSX("Blipay Pool #1")

# Check concentration limits
=AmfiConcentracao(AmfiLatestXLSX(), "Blipay Pool #1", 5000000, , "top=5", "individual=10,top3=25")
```

### 2. Historical Analysis
```excel
# Compare different dates
=AmfiXLSX("Pool ABC", "", "2025-06-30")
=AmfiXLSX("Pool ABC", "", "2025-06-29")

# Historical pool availability
=AmfiGetPools("2025-06-30")
=AmfiGetPools("2025-06-29")
```

### 3. Status-based Analysis
```excel
# Get available statuses
=AmfiGetStatuses("Pool ABC")

# Filter by status
=AmfiXLSX("Pool ABC", "Vencido")      # Overdue only
=AmfiXLSX("Pool ABC", "Vigente")      # Current only
```

### 4. Financial Planning
```excel
# Current IS calculation
=AmfiCalcularIS(B2, C2)

# Plan JR adjustments
=AmfiCalcularJR(B2, 20)  # Target 20% IS

# Calculate required additional JR
=AmfiCalcularAdicionalIS(B2, 0.15, 0.20)
```

### 5. Performance Optimization
```excel
# Check cache status
=CacheStats()

# Clear cache when needed
=ClearCache("xlsx")

# Validate data quality
=AmfiValidateData()
```

---

## Troubleshooting

### Common Issues and Solutions

#### "Arquivo não encontrado" (File not found)
**Cause**: File path incorrect or file doesn't exist  
**Solution**:
```excel
# Use auto-discovery functions
=AmfiLatestCSV()
=AmfiLatestXLSX()

# Check data status
=AmfiDataStatus()
```

#### "Pool não encontrado" (Pool not found)
**Cause**: Pool name doesn't exist in data  
**Solution**:
```excel
# Check available pools
=AmfiGetPools()

# Verify exact pool name spelling
```

#### "Coluna não encontrada" (Column not found)
**Cause**: Required columns missing from file  
**Solution**:
```excel
# Run validation
=AmfiValidateData()

# Check file structure
```

#### Slow Performance
**Cause**: Large datasets or cache issues  
**Solution**:
```excel
# Clear cache
=ClearCache()

# Use targeted queries
=AmfiXLSX("Specific Pool")  # Instead of loading all data
```

#### "Status não encontrado" (Status not found)
**Cause**: Status value doesn't exist for the pool  
**Solution**:
```excel
# Check available statuses
=AmfiGetStatuses("Pool Name")

# Use empty string for all statuses
=AmfiXLSX("Pool Name", "")
```

### Error Messages Reference

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| "No CSV file found" | No CSV files in data directory | Check file location and naming |
| "No XLSX file found" | No XLSX files in data directory | Check file location and naming |
| "Pool 'X' não encontrado" | Pool doesn't exist | Use `AmfiGetPools()` to see available |
| "Status 'X' não encontrado" | Status doesn't exist for pool | Use `AmfiGetStatuses()` to see available |
| "Coluna 'Pool' não encontrada" | XLSX missing Pool column | Check file format |
| "Arquivo XLSX está vazio" | Empty XLSX file | Check file content |

### Best Practices

1. **Always use auto-discovery functions** when possible:
   ```excel
   =AmfiXLSX("Pool") instead of =AmfiXLSXLegacy("C:\long\path\file.xlsx", "Pool")
   ```

2. **Check data status regularly**:
   ```excel
   =AmfiDataStatus()  # Monitor data freshness
   ```

3. **Use validation before analysis**:
   ```excel
   =AmfiValidateData()  # Ensure data quality
   ```

4. **Leverage helper functions**:
   ```excel
   =AmfiGetPools()      # Discover available pools
   =AmfiGetStatuses()   # Discover available statuses
   ```

5. **Clear cache when needed**:
   ```excel
   =ClearCache()  # After data updates
   ```

---

## Function Summary Table

| Category | Function | Purpose | Key Parameters |
|----------|----------|---------|----------------|
| **Data Processing** | `AmfiDashboard` | CSV pool overview | `file, pools, view` |
| | `AmfiXLSX` | Targeted XLSX data | `pool, status, date, view` |
| | `AmFiReadJSON` | JSON data extraction | `file, key` |
| | `ListPools` | Available pools | `file` |
| **Discovery** | `AmfiGetPools` | List XLSX pools | `date` |
| | `AmfiGetStatuses` | Pool statuses | `pool, date` |
| | `AmfiLatestCSV` | Latest CSV path | none |
| | `AmfiLatestXLSX` | Latest XLSX path | none |
| **Analysis** | `AmfiConcentracao` | Concentration analysis | `file, pool, pl_total, type, top, limits` |
| **Financial** | `AmfiCalcularIS` | Subordination Index | `pl, jr` |
| | `AmfiCalcularJR` | Required JR | `pl, is_target` |
| | `AmfiCalcularAdicionalIS` | Additional JR needed | `pl, is_current, is_target` |
| **Quality** | `AmfiValidateData` | Data validation | none |
| | `AmfiDataStatus` | Data freshness | none |
| **Utility** | `ClearCache` | Cache management | `type` |
| | `CacheStats` | Cache statistics | none |

---

*This reference guide covers all AmFi Excel functions. For technical details, see CLAUDE.md and PRD.md in the project root.*