# AmFi - Excel Add-in for Investment Fund Management

## Project Overview
AmFi (Asset Management Financial Intelligence) is a comprehensive Excel add-in system for Brazilian investment fund management. It combines a Python backend (via xlwings) with Excel frontend to provide advanced financial analysis, compliance monitoring, and portfolio management capabilities.

## PROJECTS GUIDELINES
1. The project uses xlwings, a Python package that allows Excel users develop in Python language;
2. You are a very senior developer, who codes considering industry best practices;
3. You focus on performance, scalability, documentation and organization;
4. You just don't take face value what I prompt: you cover my blindspots when I dont see them;
5. No only in coding, but also in files architecture and organization;
6. Always discuss and plan changes thoroughly before coding: analyze requirements, discuss implementation approaches, consider edge cases, and wait for explicit confirmation to proceed with code modifications;

## Project Structure
```
/mnt/c/amfi/                    # Project root
├── CLAUDE.md                   # Project documentation for Claude
├── PRD.md                      # Product Requirements Document
├── Monitoramento.xlsm          # Main monitoring workbook
├── udfs/                       # Python UDF implementation
│   └── [Python modules]        # Core functionality
└── data/                       # Data storage
    ├── csv/                    # CSV data files
    ├── xlsx/                   # Excel data files
    └── escrituras/             # Pool configurations & legal docs
```

## Architecture

### Main Entry Point
- **File**: `amfi.py`
- **Purpose**: Contains all Excel-exposed UDF functions
- **Framework**: xlwings for Excel integration

### Core Modules
1. **csv_handler.py** - CSV data processing and dashboard logic
2. **json_handler.py** - JSON file parsing and data extraction
3. **xlsx_handler.py** - Excel file processing for portfolio data  
4. **analysis_handler.py** - Concentration analysis and compliance monitoring
5. **calculus.py** - Financial calculations (IS, JR, subordination)
6. **cache_manager.py** - File caching system for performance optimization

## Available UDF Functions

### Data Processing Functions
- `AmfiDashboard(caminho_arquivo, nomes_pool, visao)` - Investment opportunity dashboard from CSV
- `AmfiXLSX(pool_name, status, date, visao)` - Targeted pool/status filtering from XLSX
- `AmFiReadJSON(caminho_arquivo, chave)` - JSON data extraction with key search
- `ListPools(caminho_arquivo)` - Available pools listing from CSV

### Enhanced XLSX Functions
- `AmfiXLSX(pool_name, status="", date="", visao="exec")` - Targeted receivables data with filtering
  - **pool_name**: Specific pool to retrieve (required)
  - **status**: Filter by receivable status (optional - empty = all statuses)
  - **date**: Target date YYYY-MM-DD (optional - empty = latest file)
  - **visao**: 'exec' for key columns, 'full' for all columns
  - **First column**: File date for data traceability

### Helper Functions
- `AmfiGetPools(date="")` - List available pools in XLSX
- `AmfiGetStatuses(pool_name, date="")` - List available statuses for a pool

### Analysis Functions
- `AmfiConcentracao(arquivo_xlsx, pool, pl_total, tipo, top, limite, ignore_list)` - Concentration analysis with compliance monitoring
  - Supports cedente/sacado analysis
  - Compliance limit checking
  - Top N analysis
  - Ignore list functionality

### Financial Calculations
- `AmfiCalcularIS(pl, jr)` - Subordination Index calculation
- `AmfiCalcularJR(pl, is_percentual)` - JR calculation from PL and desired IS
- `AmfiCalcularAdicionalIS(pl_inicial, is_atual, is_desejado)` - Additional JR needed for target IS

### File Discovery Functions
- `AmfiLatestCSV()` - Get path to most recent CSV file
- `AmfiLatestXLSX()` - Get path to most recent XLSX file
- `AmfiDataStatus()` - Check data freshness and age

### Data Quality Functions
- `AmfiValidateData()` - Comprehensive data validation report

### Utility Functions  
- `ClearCache(tipo)` - Cache management ('all', 'csv', 'json', 'xlsx')
- `CacheStats()` - Cache statistics display

## Data Structure

### File Organization
```
/mnt/c/amfi/
├── udfs/                    # Main UDF code
├── data/                    # Data files (recently reorganized)
│   ├── csv/                 # Daily pool overview files
│   ├── xlsx/                # Daily portfolio detail files
│   ├── escrituras/          # Pool JSON configurations
│   └── escrituras_md/       # Legal documents and metadata
├── Monitoramento.xlsm       # Main Excel workbook
└── pools/                   # Legacy pool configurations (moved to data/)
```

### Data Architecture & Daily Workflow

#### Daily Data Files
1. **CSV Files** (`AcompanhamentoDeOportunidades-YYYY-MM-DD HH_MM_SS -0300.csv`)
   - **Purpose**: Macro-level pool/fund overview
   - **Key Fields**: Nome (pool name), PL, SR, JR, IS%, compliance status, asset types
   - **Update Frequency**: Daily with timestamp
   - **Use Case**: Pool selection, dashboard views, investment opportunities

2. **XLSX Files** (`Carteira Global YYYY-MM-DD HHMMSS.xlsx`)
   - **Purpose**: Detailed credit portfolio with all receivables
   - **Key Fields**: Nome do Sacado (debtor), Nome do Cedente (assignor), Valor presente, dates
   - **Update Frequency**: Daily with timestamp
   - **Use Case**: Concentration analysis, risk assessment, compliance monitoring

#### Data Flow
```
CSV (Pool Overview) → User selects pools → XLSX (Asset Details) → Analysis/Calculations
         ↓                                           ↓
   Dashboard View                          Concentration Analysis
```

### Key Data Files
- **Pool Configurations**: JSON files defining fund pools (afa_pool_1.json, lecapital_pool_1.json)
- **Daily CSV**: Investment opportunity data with pool summaries
- **Daily XLSX**: Granular portfolio data with individual receivables
- **Legal Documents**: Debenture agreements and compliance docs

## Development Context

### Recent Changes
- Migrated from pools/ to data/ directory structure
- Added concentration analysis functionality
- Implemented comprehensive caching system
- Enhanced financial calculation capabilities

### Technology Stack
- **Python**: Core language
- **xlwings**: Excel integration
- **pandas**: Data processing (implied from functionality)
- **json**: Configuration and data handling
- **csv**: Data import/export

### Performance Features
- Multi-level caching system (CSV, JSON, XLSX)
- Cache statistics and management
- Optimized file reading with selective column loading
- Memory-efficient data processing

## Testing and Validation

### Current Status
- No formal test suite identified
- Manual testing through Excel integration
- Error handling implemented in UDF wrapper functions

### Recommended Testing Commands
```bash
# No specific test commands identified - manual Excel testing required
# Consider adding: pytest, unittest, or similar framework
```

### Common Issues
- File path handling between Windows/WSL environments
- Excel range processing for multi-cell inputs
- Cache invalidation timing
- Memory usage with large datasets
- **xlwings Reserved Keywords**: Parameter names `status`, `date`, `time`, `type`, `value`, `name`, `range`, `selection` cause MacroOptions 1004 error. Use underscores (`status_`, `date_`) to avoid conflicts

## Usage Patterns

### Typical Workflows
1. **Dashboard Analysis**: Load CSV → Filter by pools → Generate executive/full view
2. **Concentration Monitoring**: Load XLSX → Analyze cedente/sacado concentration → Check compliance
3. **Financial Calculations**: Input PL/JR values → Calculate subordination metrics → Plan adjustments
4. **Cache Management**: Monitor cache stats → Clear specific caches → Optimize performance

### Integration Points
- Excel workbook: `Monitoramento.xlsm`
- Data sources: CSV files in `../data/csv/`
- Pool configurations: JSON files in `../data/escrituras/`
- Output: Direct Excel cell population via xlwings

## Business Domain

### Financial Concepts
- **IS (Índice de Subordinação)**: Subordination Index for risk assessment
- **JR (Juros Remuneratórios)**: Remuneration Interest calculations
- **PL (Patrimônio Líquido)**: Net Worth/Equity calculations
- **Cedente/Sacado**: Assignor/Debtor concentration analysis
- **Pool Management**: Investment fund portfolio groupings

### Compliance Features
- Concentration limit monitoring
- Top N entity analysis
- Individual and aggregate limit checking
- Compliance status reporting

## Development Notes

### Code Quality
- Comprehensive docstrings with examples
- Error handling with user-friendly messages
- Type hints partially implemented
- Modular architecture with clear separation of concerns

### Missing Infrastructure
- **No requirements.txt**: Dependencies not documented
- **No setup scripts**: Manual installation process
- **No tests**: No test suite or coverage
- **No .gitignore**: Temporary Excel files tracked
- **No root README**: Project documentation scattered

### Future Enhancements
- Unit test implementation
- Enhanced error logging
- Configuration file externalization
- Additional financial metrics
- Performance optimization for large datasets
- Proper dependency management
- Installation automation
- CI/CD pipeline setup

### Git Status
- Clean working directory in udfs/
- Untracked files in ../data/ (data migration)
- New monitoring workbook: ../Monitoramento.xlsm
- Deleted installation scripts need replacement

## Excel Integration Method
- **Direct xlwings**: UDFs accessed directly via xlwings without .xlam
- **Monitoramento.xlsm**: Primary workbook containing formulas
- **Installation**: xlwings configuration and Python environment setup
- **Dependencies**: xlwings must be installed and configured
- **Note**: amfi.xlam deprecated - no longer in use