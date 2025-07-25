# Exemplos Práticos de Uso - run_monitoring()

## Interface Única do Sistema AmFi

A função `run_monitoring()` é a **ÚNICA interface oficial** do sistema de monitoramento AmFi. Todas as funções legacy foram removidas em 2025-07-14.

### Execução via Scripts (Recomendado)
```bash
# Executar monitoramento completo
python scripts/run_monitoring.py

# Gerar dashboard após monitoramento
python scripts/generate_dashboard.py

# Servir dashboard via web (http://localhost:8080)
python scripts/run_dashboard.py
```

### Monitores Disponíveis (2025-07-14)
- ✅ **Subordinação**: Índice de subordinação com limites
- ✅ **Inadimplência**: Janelas customizáveis (30d, 90d, etc.)
- ✅ **PDD**: Provisão para Devedores Duvidosos (grupos AA-H)
- 🔄 **Concentração**: Sacados/cedentes (planejado)
- 🔄 **Elegibilidade**: Critérios de ativos (planejado)

## 1. Uso Básico

### Via Script (Mais Simples)
```bash
# Executar via linha de comando
cd C:\amfi

# Executar monitoramento
python scripts/run_monitoring.py

# Gerar dashboard
python scripts/generate_dashboard.py

# Servir dashboard (opcional)
python scripts/run_dashboard.py
```

### Via Import Python

### Processar Todos os Pools (Modo Debug)
```python
from src.monitor.orchestrator import run_monitoring

# Executa todos os pools configurados em _test_pools.json
resultado = run_monitoring()

# Verificar sucesso geral
if resultado['sucesso']:
    print(f"✅ {resultado['estatisticas']['total']} pools processados")
    print(f"📊 Taxa de sucesso: {resultado['estatisticas']['taxa_sucesso']}%")
else:
    print(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")
```

### Processar Pool Específico
```python
# Executa apenas um pool específico
resultado = run_monitoring("LeCapital Pool #1")

if resultado['sucesso']:
    pool_result = resultado['resultados']['LeCapital Pool #1']
    print(f"✅ Pool processado com sucesso")
    print(f"📋 Monitores executados: {pool_result['monitores_executados']}")
```

## 2. Analisando Resultados de Subordinação

```python
resultado = run_monitoring("AFA Pool #1")

if resultado['sucesso']:
    # Navegar até resultados de subordinação
    pool_result = resultado['resultados']['AFA Pool #1']
    sub_result = pool_result['resultados']['subordinacao']
    
    # Verificar status
    sr_percent = sub_result['subordination_ratio_percent']
    status = sub_result['status_limite_minimo']
    limite_min = sub_result['limite_minimo'] * 100
    
    print(f"🎯 Subordinação: {sr_percent}%")
    print(f"📊 Limite mínimo: {limite_min}%")
    print(f"📋 Status: {status}")
    
    # Se violado, mostrar aporte necessário
    if status == 'violado':
        aporte = sub_result['aporte_necessario']['para_limite_minimo']
        print(f"💰 Aporte necessário: R$ {aporte:,.2f}")
        print("🚨 AÇÃO NECESSÁRIA: Pool em violação!")
```

## 3. Analisando Resultados de Inadimplência

```python
resultado = run_monitoring("LeCapital Pool #1")

if resultado['sucesso']:
    # Navegar até resultados de inadimplência
    pool_result = resultado['resultados']['LeCapital Pool #1']
    inad_result = pool_result['resultados']['inadimplencia']
    
    print("🔍 INADIMPLÊNCIA POR JANELA:")
    print("-" * 40)
    
    # Iterar por todas as janelas configuradas
    for janela_id, dados in inad_result['resultados'].items():
        percentual = dados['inadimplencia_percent']
        limite = dados['limite_configurado'] * 100
        status = dados['status']
        
        # Extrair número de dias da janela
        dias = janela_id.replace('inadimplencia_', '').replace('d', '')
        
        print(f"📅 {dias} dias: {percentual}% (limite: {limite}%) - {status}")
        
        if status == 'violado':
            print(f"   🚨 VIOLAÇÃO: Acima do limite permitido!")
```

## 4. Processamento em Lote com Tratamento de Erros

```python
def monitorar_todos_pools():
    """Executa monitoramento para todos os pools com tratamento robusto."""
    
    resultado = run_monitoring()
    
    if not resultado['sucesso']:
        print(f"❌ Falha crítica: {resultado.get('erro')}")
        return False
    
    stats = resultado['estatisticas']
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total: {stats['total']}")
    print(f"   Sucesso: {stats['sucesso']}")
    print(f"   Erro: {stats['erro']}")
    print(f"   Taxa: {stats['taxa_sucesso']}%")
    
    # Analisar pools com erro
    if stats['erro'] > 0:
        print(f"\n❌ POOLS COM ERRO:")
        for pool_name, pool_result in resultado['resultados'].items():
            if not pool_result.get('sucesso', True):
                erro = pool_result.get('erro', 'Desconhecido')
                print(f"   - {pool_name}: {erro}")
    
    # Analisar violações
    pools_violados = []
    for pool_name, pool_result in resultado['resultados'].items():
        if pool_result.get('sucesso'):
            # Verificar subordinação
            sub_result = pool_result['resultados'].get('subordinacao', {})
            if sub_result.get('status_limite_minimo') == 'violado':
                pools_violados.append((pool_name, 'subordinacao'))
            
            # Verificar inadimplência
            inad_result = pool_result['resultados'].get('inadimplencia', {})
            if 'resultados' in inad_result:
                for janela, dados in inad_result['resultados'].items():
                    if dados.get('status') == 'violado':
                        pools_violados.append((pool_name, f'inadimplencia_{janela}'))
            
            # Verificar PDD (se configurado)
            pdd_result = pool_result['resultados'].get('pdd', {})
            if pdd_result.get('sucesso') and 'pdd_analysis' in pdd_result:
                # PDD não tem "violação" - apenas análise de provisões
    
    if pools_violados:
        print(f"\n🚨 VIOLAÇÕES DETECTADAS:")
        for pool, tipo_violacao in pools_violados:
            print(f"   - {pool}: {tipo_violacao}")
    
    return True

# Executar
if __name__ == "__main__":
    monitorar_todos_pools()
```

## 5. Acessando DataFrame Enriquecido

```python
resultado = run_monitoring()

if resultado['sucesso']:
    # Acessar DataFrame XLSX globalmente enriquecido
    xlsx_enriched = resultado['xlsx_enriched']
    
    print(f"📊 DADOS ENRIQUECIDOS:")
    print(f"   Total de registros: {len(xlsx_enriched):,}")
    print(f"   Colunas originais: 16")
    print(f"   Colunas totais: {len(xlsx_enriched.columns)}")
    
    # Verificar campos adicionados
    campos_novos = []
    if 'dias_atraso' in xlsx_enriched.columns:
        campos_novos.append('dias_atraso')
    if 'grupo_de_risco' in xlsx_enriched.columns:
        campos_novos.append('grupo_de_risco')
    
    print(f"   Campos adicionados: {campos_novos}")
    
    # Análise rápida de dias de atraso
    if 'dias_atraso' in xlsx_enriched.columns:
        max_atraso = xlsx_enriched['dias_atraso'].max()
        atrasados = len(xlsx_enriched[xlsx_enriched['dias_atraso'] > 0])
        print(f"   📈 Máximo atraso: {max_atraso} dias")
        print(f"   📉 Títulos atrasados: {atrasados:,}")
    
    # Análise de grupos de risco
    if 'grupo_de_risco' in xlsx_enriched.columns:
        grupos = xlsx_enriched['grupo_de_risco'].value_counts()
        print(f"   🎯 Distribuição por grupo de risco:")
        for grupo, count in grupos.head().items():
            print(f"      {grupo}: {count:,} títulos")
```

## 6. Configuração de Modo Debug

### Arquivo _test_pools.json
```json
{
  "metadata": {
    "description": "Configuração de debug para sistema de monitoramento",
    "version": "2.0"
  },
  "debug_pools": [
    "AFA Pool #1",
    "LeCapital Pool #1"
  ],
  "monitor": [
    "concentracao_sacados",
    "indice_subordinacao",
    "inadimplencia"
  ]
}
```

### Uso do Modo Debug
```python
# Se _test_pools.json existir, processa apenas pools listados
resultado = run_monitoring()  # Processa apenas AFA e LeCapital

# Para forçar um pool específico (ignora _test_pools.json)
resultado = run_monitoring("Outro Pool #3")
```

## 7. Comparação de Resultados Entre Pools

```python
def comparar_subordinacao_pools():
    """Compara índices de subordinação entre pools."""
    
    resultado = run_monitoring()
    
    if not resultado['sucesso']:
        return
    
    subordinacoes = []
    
    for pool_name, pool_result in resultado['resultados'].items():
        if pool_result.get('sucesso'):
            sub_result = pool_result['resultados'].get('subordinacao', {})
            if 'subordination_ratio_percent' in sub_result:
                sr = sub_result['subordination_ratio_percent']
                limite = sub_result.get('limite_minimo', 0) * 100
                status = sub_result.get('status_limite_minimo', 'N/A')
                
                subordinacoes.append({
                    'pool': pool_name,
                    'sr': sr,
                    'limite': limite,
                    'status': status,
                    'margem': sr - limite
                })
    
    # Ordenar por subordinação (menor para maior - mais crítico primeiro)
    subordinacoes.sort(key=lambda x: x['sr'])
    
    print("📊 RANKING DE SUBORDINAÇÃO (MAIS CRÍTICO PRIMEIRO):")
    print("=" * 80)
    
    for i, dados in enumerate(subordinacoes, 1):
        pool = dados['pool']
        sr = dados['sr']
        limite = dados['limite']
        status = dados['status']
        margem = dados['margem']
        
        status_icon = "🚨" if status == 'violado' else "✅"
        
        print(f"{i:2d}. {status_icon} {pool}")
        print(f"     SR: {sr:5.1f}% | Limite: {limite:5.1f}% | Margem: {margem:+5.1f}%")
        print()

# Executar comparação
comparar_subordinacao_pools()
```

## 8. Analisando Resultados de PDD (Provisão para Devedores Duvidosos)

```python
def analisar_pdd_detalhado(pool_name):
    """Análise detalhada de PDD para um pool específico."""
    
    resultado = run_monitoring(pool_name)
    
    if not resultado['sucesso']:
        print(f"❌ Erro ao processar {pool_name}")
        return
    
    pool_result = resultado['resultados'][pool_name]
    
    if 'pdd' not in pool_result['resultados']:
        print(f"ℹ️ Pool {pool_name} não possui monitor PDD configurado")
        return
    
    pdd_result = pool_result['resultados']['pdd']
    
    if not pdd_result.get('sucesso'):
        print(f"❌ Erro no monitor PDD: {pdd_result.get('erro')}")
        return
    
    pdd_analysis = pdd_result['pdd_analysis']
    
    print(f"💰 PDD - {pool_name}")
    print("=" * 50)
    
    # Totais consolidados
    totais = pdd_analysis['totais']
    print(f"📊 TOTAIS:")
    print(f"   Carteira Total: R$ {totais['carteira_valor']:,.2f}")
    print(f"   Provisão Total: R$ {totais['provisao_valor']:,.2f}")
    print(f"   Provisão %: {totais['provisao_percentual']}%")
    
    # Análise por grupo de risco
    print(f"\n🎯 ANÁLISE POR GRUPO DE RISCO:")
    grupos = pdd_analysis['grupos']
    
    for grupo in sorted(grupos.keys()):
        dados = grupos[grupo]
        if dados['quantidade'] > 0:  # Apenas grupos com exposição
            print(f"   📈 Grupo {grupo}:")
            print(f"      Títulos: {dados['quantidade']:,}")
            print(f"      Valor: R$ {dados['valor_total']:,.2f}")
            print(f"      Provisão %: {dados['provisao_pct']}%")
            print(f"      Provisão R$: R$ {dados['provisao_valor']:,.2f}")
            print(f"      Atraso máx: {dados['atraso_max_dias']} dias")
    
    # Estatísticas complementares
    if 'estatisticas' in pdd_analysis:
        stats = pdd_analysis['estatisticas']
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total de títulos: {stats['titulos_total']:,}")
        print(f"   Títulos c/ provisão: {stats['titulos_com_provisao']:,}")
        print(f"   Grupo modal: {stats['grupo_risco_modal']}")
        print(f"   Provisão média: R$ {stats['provisao_media_por_titulo']:,.2f}/título")

# Executar análise
analisar_pdd_detalhado("LeCapital Pool #1")
```

## 9. Dashboard Executivo - Visão Consolidada

```python
def dashboard_executivo():
    """Dashboard executivo com visão consolidada de todos os monitores."""
    
    resultado = run_monitoring()
    
    if not resultado['sucesso']:
        print(f"❌ Falha crítica: {resultado.get('erro')}")
        return
    
    print("📊 DASHBOARD EXECUTIVO - AmFi Monitoring")
    print("=" * 60)
    
    stats = resultado['estatisticas']
    print(f"🎯 RESUMO GERAL:")
    print(f"   Pools processados: {stats['total']}")
    print(f"   Taxa de sucesso: {stats['taxa_sucesso']}%")
    
    # Análise por pool
    violacoes_totais = 0
    provisoes_totais = 0
    
    for pool_name, pool_result in resultado['resultados'].items():
        if not pool_result.get('sucesso'):
            continue
            
        print(f"\n🏦 {pool_name}:")
        monitores = pool_result.get('monitores_executados', [])
        print(f"   Monitores: {', '.join(monitores)}")
        
        resultados = pool_result.get('resultados', {})
        
        # Subordinação
        if 'subordinacao' in resultados:
            sub = resultados['subordinacao']
            sr = sub.get('subordination_ratio_percent', 0)
            status = sub.get('status_limite_minimo', 'N/A')
            emoji = "🟢" if status == "enquadrado" else "🔴"
            print(f"   {emoji} Subordinação: {sr}% ({status})")
            if status == "violado":
                violacoes_totais += 1
        
        # Inadimplência
        if 'inadimplencia' in resultados:
            inad = resultados['inadimplencia']
            if 'resultados' in inad:
                for janela, dados in inad['resultados'].items():
                    perc = dados.get('inadimplencia_percent', 0)
                    status = dados.get('status', 'N/A')
                    emoji = "🟢" if status == "enquadrado" else "🔴"
                    janela_nome = janela.replace('inadimplencia_', '').replace('d', ' dias')
                    print(f"   {emoji} Inadimpl. {janela_nome}: {perc}% ({status})")
                    if status == "violado":
                        violacoes_totais += 1
        
        # PDD
        if 'pdd' in resultados:
            pdd = resultados['pdd']
            if pdd.get('sucesso') and 'pdd_analysis' in pdd:
                totais = pdd['pdd_analysis']['totais']
                provisao_valor = totais.get('provisao_valor', 0)
                provisao_perc = totais.get('provisao_percentual', 0)
                print(f"   💰 PDD: R$ {provisao_valor:,.2f} ({provisao_perc}%)")
                provisoes_totais += provisao_valor
    
    # Resumo final
    print(f"\n📈 RESUMO FINAL:")
    print(f"   🚨 Total de violações: {violacoes_totais}")
    print(f"   💰 Provisões totais: R$ {provisoes_totais:,.2f}")
    
    # Acesso aos dados enriquecidos
    xlsx_enriched = resultado['xlsx_enriched']
    print(f"   📊 Registros enriquecidos: {len(xlsx_enriched):,}")

# Executar dashboard
dashboard_executivo()
```

## Compatibilidade

A função `run_monitoring()` funciona em todos os ambientes:

- ✅ **Windows**: `C:\amfi\...` (ambiente atual)
- ✅ **WSL**: `/mnt/c/amfi/...` (legacy)
- ✅ **Spyder**: Descoberta automática de caminhos
- ✅ **Linha de comando**: Python direto
- ✅ **Jupyter**: Notebooks compatíveis

### Novos Scripts (2025-07-24)
- `scripts/run_monitoring.py`: Interface para execução de monitoramento
- `scripts/generate_dashboard.py`: Geração de dashboard HTML
- `scripts/run_dashboard.py`: Servidor web para dashboard

## Observações Importantes

1. **Interface única**: `run_monitoring()` é a única função oficial
2. **Funções legacy removidas**: Não use funções antigas do orchestrator
3. **Enriquecimento automático**: DataFrame XLSX é automaticamente enriquecido
4. **Modo debug**: Use `_test_pools.json` para limitar pools processados
5. **Tratamento robusto**: Falha de um pool não para a execução dos outros

## Melhorias Implementadas (2025-07-24)

### Estrutura Reorganizada
- Scripts movidos para pasta `scripts/` para melhor organização
- Arquivos obsoletos removidos (dashboard_server.py, generate_table_dashboard.py)
- Imports reorganizados com prefixo `src.` para maior clareza

### Novos Recursos
- **Scripts simplificados**: Comandos mais intuitivos para usuários
- **Documentação melhorada**: Tratamento de exceções documentado
- **Sistema mais estável**: Remoção de código legacy e duplicado
- **Interface consistente**: Mesma funcionalidade com caminhos atualizados

### Comandos Atualizados
```bash
# ANTES (descontinuado)
python dashboard_server.py
python generate_table_dashboard.py

# AGORA (estrutura atual)
python scripts/run_dashboard.py
python scripts/generate_dashboard.py
python scripts/run_monitoring.py
```

### Funcionalidades Mantidas
- Dashboard web continua em `http://localhost:8080`
- Interface `run_monitoring()` permanece igual
- Todos os monitores funcionam identicamente
- Compatibilidade com ambientes Windows/WSL mantida