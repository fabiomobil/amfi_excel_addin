# Processamento Histórico - Sistema AmFi

## 📋 Visão Geral

Sistema completo para processamento retroativo de dados históricos com suporte a paralelização e geração de dashboard interativo.

## 🚀 Scripts Disponíveis

### 1. Processamento Paralelo Completo
```bash
python3 run_full_historical_monitoring.py
```

**Características:**
- **Paralelização**: Até 12 workers simultâneos
- **Descoberta Automática**: Encontra todas as datas disponíveis
- **Processamento Completo**: Todos os 77+ pools
- **Técnica de Movimentação**: Usa pastas 'files' para dados históricos

**Opções:**
```bash
# Configurar número de workers
python3 run_full_historical_monitoring.py --max-workers 8

# Pular datas já processadas
python3 run_full_historical_monitoring.py --skip-existing

# Apenas simular (teste)
python3 run_full_historical_monitoring.py --dry-run
```

### 2. Processamento Sequencial
```bash
python3 run_sequential_historical_monitoring.py
```

**Características:**
- **Últimos 5 dias**: Processamento focado
- **Sequencial**: Um arquivo por vez
- **Menor overhead**: Para datasets menores

### 3. Dashboard Interativo
```bash
python3 generate_table_dashboard.py
```

**Recursos:**
- **Interface Web**: HTML responsivo
- **Drilldown**: Análise detalhada por pool
- **Histórico**: Últimos 7 dias
- **Status Visual**: VIOLADO CRÍTICO/MÍNIMO, ENQUADRADO
- **Cálculos Inteligentes**: Aporte para enquadrar vs Saque disponível

## 🏗️ Arquitetura de Dados

### Estrutura de Arquivos
```
data/
├── input/
│   ├── csv/
│   │   ├── files/              # Arquivos históricos
│   │   └── [arquivo_atual]     # Processamento ativo
│   └── xlsx/
│       ├── files/              # Arquivos históricos
│       └── [arquivo_atual]     # Processamento ativo
└── output/
    └── monitoring_results/
        ├── daily_consolidated/  # JSONs por data
        └── dashboard/          # HTML gerado
```

### Técnica de Movimentação de Arquivos

1. **Preparação**: Todos os arquivos históricos em `files/`
2. **Processamento**: Move arquivo específico para pasta raiz
3. **Execução**: Sistema processa arquivo ativo automaticamente
4. **Cleanup**: Move arquivo de volta para `files/`
5. **Próximo**: Repete para próxima data

## 📊 Formato de Dados de Saída

### JSON Daily Consolidated
```json
{
  "2025-07-19": {
    "AFA Pool #1": {
      "subordinacao": {
        "valor_atual": 9.83,
        "limite_minimo": 25.0,
        "limite_critico": 20.0,
        "status": "VIOLADO CRÍTICO",
        "dias_consecutivos": 4,
        "pl_atual": 27117932.91,
        "aporte_enquadrar": 5973648.94
      }
    }
  }
}
```

### Dashboard HTML
- **Tabela Principal**: Status, dias consecutivos, valores financeiros
- **Drilldown**: Dados detalhados + histórico por pool
- **Responsivo**: Funciona em desktop e mobile
- **Auto-refresh**: Atualização automática a cada 5 minutos

## ⚙️ Configurações

### Modo Debug
```json
// config/monitoring/test_pools.json
{
  "debug_pools": []  // Vazio = todos os pools
}
```

### Controle de Paralelização
- **CPU-bound**: Use workers = núcleos da CPU
- **I/O-bound**: Use workers = 2x núcleos da CPU
- **Padrão**: 4 workers
- **Máximo testado**: 12 workers

## 🔍 Monitoramento e Logs

### Logs Detalhados
```bash
tail -f /mnt/c/amfi/logs/full_historical_monitoring.log
```

### Progress Tracking
- **Thread-safe**: Múltiplos workers simultâneos
- **Tempo real**: ETA e estatísticas
- **Relatório final**: Taxa de sucesso detalhada

## 🛠️ Troubleshooting

### Problemas Comuns

**1. Arquivos XLSX corrompidos**
```
❌ Erro: File is not a zip file
```
- **Solução**: Verificar integridade dos arquivos XLSX
- **Workaround**: Use `--skip-existing` para pular

**2. Modo Debug Ativo**
```
📊 4 Pools Monitorados (esperado: 77+)
```
- **Solução**: Remover/renomear `test_pools.json`

**3. Conflitos de Arquivo**
```
❌ Erro: Permission denied
```
- **Solução**: Verificar se arquivos não estão abertos em Excel

### Performance

**Otimizações:**
- **SSD**: Melhora I/O de arquivos significativamente
- **RAM**: 8GB+ recomendado para múltiplos workers
- **CPU**: Paralelização escala até 8-12 cores

## 📈 Resultados Típicos

### Processamento Completo
- **18 datas históricas**: 2025-06-23 a 2025-07-10
- **~73 pools por data**: Total ~1300 processamentos
- **Taxa de sucesso**: 77-85% (dependendo da qualidade dos dados)
- **Tempo total**: 2-4 minutos (12 workers)

### Dashboard Final
- **7+ pools ativos**: Dados mais recentes
- **3-4 pools violados**: Típico em períodos normais
- **Taxa compliance**: 57-70%
- **Histórico completo**: Variação temporal real

## 🚀 Próximos Passos

1. **Automação**: Agendamento via cron/Windows Task Scheduler
2. **Alertas**: Integração com email/Slack para violações
3. **API REST**: Endpoint para consumo externo
4. **Backup**: Versioning automático de dados históricos
5. **Métricas**: Tracking de performance e disponibilidade