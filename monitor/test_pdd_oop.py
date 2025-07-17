#!/usr/bin/env python3
"""
Script de teste para Monitor PDD OOP.

Valida implementação OOP da classe PDDMonitor:
- Lógica crítica por cedente
- Cálculos de provisão
- Análise por cedente
- Comparação metodológica
- Validações específicas

Diferentemente dos testes de inadimplência, este script foca em validar
a lógica PDD específica, já que o sistema funcional será removido.
"""

import sys
import os
import pandas as pd
from typing import Dict, Any
import json

# Adicionar path para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

# Imports do sistema OOP
try:
    from base.monitor_pdd_oop import PDDMonitor
    print("✅ Monitor PDD OOP importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar monitor PDD OOP: {e}")
    exit(1)

# Imports do sistema de inadimplência para enriquecimento
try:
    from base.monitor_inadimplencia_oop import DelinquencyMonitor
    print("✅ Monitor de Inadimplência OOP importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar monitor de inadimplência: {e}")
    exit(1)

# Data loader para dados reais
try:
    from utils.data_loader import load_pool_data
    print("✅ Data loader importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar data loader: {e}")
    exit(1)


def load_test_data():
    """Carrega dados reais para teste."""
    try:
        print("🔄 Carregando dados reais...")
        dados = load_pool_data()
        print(f"✅ Dados carregados: {len(dados['pools_processados'])} pools")
        return dados
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None


def enrich_test_data(dados: Dict[str, Any], pool_name: str) -> pd.DataFrame:
    """
    Enriquece dados de teste usando monitor de inadimplência.
    
    Args:
        dados: Dados carregados do sistema
        pool_name: Nome do pool para enriquecer
        
    Returns:
        DataFrame enriquecido
    """
    try:
        print(f"🔄 Enriquecendo dados para {pool_name}...")
        
        # Preparar dados para o pool
        nome_col = 'nome' if 'nome' in dados["csv_data"].columns else 'Nome'
        pool_csv = dados["csv_data"][dados["csv_data"][nome_col] == pool_name]
        
        if pool_csv.empty:
            raise ValueError(f"Pool '{pool_name}' não encontrado no CSV")
        
        pool_config = dados["pools_configs"].get(pool_name)
        if not pool_config:
            raise ValueError(f"Configuração do pool '{pool_name}' não encontrada")
        
        # Enriquecer usando monitor de inadimplência
        xlsx_data = dados["xlsx_data"].copy()
        delinquency_monitor = DelinquencyMonitor(pool_config)
        
        # Executar enriquecimento
        delinquency_monitor.run_monitoring(pool_csv, xlsx_data)
        
        # Verificar se enriquecimento funcionou
        if 'dias_atraso' not in xlsx_data.columns:
            raise ValueError("Enriquecimento falhou - 'dias_atraso' não foi adicionado")
        
        if 'grupo_de_risco' not in xlsx_data.columns:
            raise ValueError("Enriquecimento falhou - 'grupo_de_risco' não foi adicionado")
        
        print(f"✅ Dados enriquecidos: {len(xlsx_data)} registros")
        return xlsx_data
        
    except Exception as e:
        print(f"❌ Erro no enriquecimento: {e}")
        raise


def test_pdd_monitor_creation(pool_config: Dict[str, Any]) -> bool:
    """
    Testa criação do monitor PDD.
    
    Args:
        pool_config: Configuração do pool
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando criação do monitor PDD...")
        
        # Criar monitor
        monitor = PDDMonitor(pool_config)
        
        # Verificar propriedades básicas
        assert monitor.monitor_id == "pdd", f"Monitor ID incorreto: {monitor.monitor_id}"
        assert monitor.config == pool_config, "Configuração não foi salva corretamente"
        
        # Verificar se está ativo
        is_active = monitor.is_active()
        print(f"Monitor ativo: {is_active}")
        
        # Verificar colunas obrigatórias
        required_columns = monitor.get_required_columns()
        expected_columns = ['dias_atraso', 'grupo_de_risco', 'valor_presente', 'nome_do_cedente']
        assert set(required_columns) == set(expected_columns), f"Colunas obrigatórias incorretas: {required_columns}"
        
        print("✅ Criação do monitor PDD passou")
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação do monitor: {e}")
        return False


def test_cedente_logic(monitor: PDDMonitor, xlsx_enriched: pd.DataFrame) -> bool:
    """
    Testa lógica crítica por cedente.
    
    Args:
        monitor: Monitor PDD
        xlsx_enriched: DataFrame enriquecido
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando lógica crítica por cedente...")
        
        # Aplicar lógica por cedente
        df_with_logic = monitor._apply_cedente_logic(xlsx_enriched)
        
        # Verificar se colunas foram adicionadas
        assert 'grupo_pdd_cedente' in df_with_logic.columns, "Coluna 'grupo_pdd_cedente' não foi adicionada"
        assert 'provisao_pct' in df_with_logic.columns, "Coluna 'provisao_pct' não foi adicionada"
        assert 'provisao_valor' in df_with_logic.columns, "Coluna 'provisao_valor' não foi adicionada"
        
        # Testar lógica por cedente: todos os títulos de um cedente devem ter mesmo grupo PDD
        for cedente in df_with_logic['nome_do_cedente'].unique():
            if pd.isna(cedente):
                continue
                
            titulos_cedente = df_with_logic[df_with_logic['nome_do_cedente'] == cedente]
            
            # Todos os títulos do cedente devem ter o mesmo grupo PDD
            grupos_pdd_cedente = titulos_cedente['grupo_pdd_cedente'].unique()
            assert len(grupos_pdd_cedente) == 1, f"Cedente '{cedente}' tem múltiplos grupos PDD: {grupos_pdd_cedente}"
            
            # Grupo PDD deve ser baseado no maior atraso
            max_atraso = titulos_cedente['dias_atraso'].max()
            grupo_esperado = monitor._classify_risk_group_from_days(max_atraso)
            grupo_aplicado = grupos_pdd_cedente[0]
            
            assert grupo_aplicado == grupo_esperado, f"Cedente '{cedente}': grupo aplicado {grupo_aplicado} vs esperado {grupo_esperado}"
        
        print("✅ Lógica por cedente passou")
        return True
        
    except Exception as e:
        print(f"❌ Erro na lógica por cedente: {e}")
        return False


def test_provision_calculations(monitor: PDDMonitor, xlsx_enriched: pd.DataFrame) -> bool:
    """
    Testa cálculos de provisão.
    
    Args:
        monitor: Monitor PDD
        xlsx_enriched: DataFrame enriquecido
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando cálculos de provisão...")
        
        # Aplicar lógica por cedente
        df_with_logic = monitor._apply_cedente_logic(xlsx_enriched)
        
        # Calcular provisões por grupo
        pdd_analysis = monitor._calculate_provisions_by_group(df_with_logic)
        
        # Verificar estrutura
        assert "grupos" in pdd_analysis, "Chave 'grupos' não encontrada"
        assert "totais" in pdd_analysis, "Chave 'totais' não encontrada"
        
        # Verificar se todos os grupos estão presentes
        grupos_config = monitor._grupos_risco.keys()
        grupos_resultado = pdd_analysis["grupos"].keys()
        assert set(grupos_config) == set(grupos_resultado), "Grupos no resultado não coincidem com configuração"
        
        # Verificar cálculos numéricos
        total_carteira_calculado = sum(g["valor_total"] for g in pdd_analysis["grupos"].values())
        total_carteira_esperado = pdd_analysis["totais"]["carteira_valor"]
        
        assert abs(total_carteira_calculado - total_carteira_esperado) < 0.01, "Total da carteira não confere"
        
        # Verificar provisões
        total_provisao_calculado = sum(g["provisao_valor"] for g in pdd_analysis["grupos"].values())
        total_provisao_esperado = pdd_analysis["totais"]["provisao_valor"]
        
        # Usar tolerância maior para precisão de ponto flutuante
        assert abs(total_provisao_calculado - total_provisao_esperado) < 0.1, f"Total de provisão não confere: {total_provisao_calculado} vs {total_provisao_esperado}"
        
        print("✅ Cálculos de provisão passaram")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos cálculos de provisão: {e}")
        return False


def test_cedente_analysis(monitor: PDDMonitor, xlsx_enriched: pd.DataFrame) -> bool:
    """
    Testa análise por cedente.
    
    Args:
        monitor: Monitor PDD
        xlsx_enriched: DataFrame enriquecido
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando análise por cedente...")
        
        # Aplicar lógica por cedente
        df_with_logic = monitor._apply_cedente_logic(xlsx_enriched)
        
        # Gerar análise por cedente
        cedente_analysis = monitor._generate_cedente_analysis(df_with_logic)
        
        # Verificar estrutura
        assert "total_cedentes" in cedente_analysis, "Chave 'total_cedentes' não encontrada"
        assert "cedentes" in cedente_analysis, "Chave 'cedentes' não encontrada"
        
        # Verificar se número de cedentes confere
        cedentes_unicos = df_with_logic['nome_do_cedente'].nunique()
        assert cedente_analysis["total_cedentes"] == cedentes_unicos, "Número de cedentes não confere"
        
        # Verificar cada cedente na análise
        for cedente_nome, cedente_info in cedente_analysis["cedentes"].items():
            # Verificar campos obrigatórios
            campos_obrigatorios = ['total_titulos', 'valor_total', 'grupo_pdd_aplicado', 
                                 'provisao_pct', 'provisao_valor', 'titulo_mais_atrasado']
            
            for campo in campos_obrigatorios:
                assert campo in cedente_info, f"Campo '{campo}' não encontrado para cedente '{cedente_nome}'"
            
            # Verificar se grupo PDD está correto
            titulos_cedente = df_with_logic[df_with_logic['nome_do_cedente'] == cedente_nome]
            grupo_esperado = titulos_cedente['grupo_pdd_cedente'].iloc[0]
            grupo_na_analise = cedente_info['grupo_pdd_aplicado']
            
            assert grupo_esperado == grupo_na_analise, f"Grupo PDD inconsistente para '{cedente_nome}'"
        
        print("✅ Análise por cedente passou")
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise por cedente: {e}")
        return False


def test_methodology_comparison(monitor: PDDMonitor, xlsx_enriched: pd.DataFrame) -> bool:
    """
    Testa comparação metodológica.
    
    Args:
        monitor: Monitor PDD
        xlsx_enriched: DataFrame enriquecido
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando comparação metodológica...")
        
        # Aplicar lógica por cedente
        df_with_logic = monitor._apply_cedente_logic(xlsx_enriched)
        
        # Gerar comparação
        comparison = monitor._compare_methodologies(df_with_logic)
        
        # Verificar estrutura
        campos_obrigatorios = ['provisao_por_cedente', 'provisao_individual', 
                             'diferenca_valor', 'diferenca_percentual']
        
        for campo in campos_obrigatorios:
            assert campo in comparison, f"Campo '{campo}' não encontrado na comparação"
        
        # Verificar se diferença faz sentido
        diferenca_calculada = comparison['provisao_por_cedente'] - comparison['provisao_individual']
        diferenca_reportada = comparison['diferenca_valor']
        
        assert abs(diferenca_calculada - diferenca_reportada) < 0.01, "Diferença de valor não confere"
        
        # Verificar percentual
        if comparison['provisao_individual'] > 0:
            percentual_calculado = (diferenca_reportada / comparison['provisao_individual']) * 100
            percentual_reportado = comparison['diferenca_percentual']
            
            assert abs(percentual_calculado - percentual_reportado) < 0.01, "Diferença percentual não confere"
        
        print("✅ Comparação metodológica passou")
        return True
        
    except Exception as e:
        print(f"❌ Erro na comparação metodológica: {e}")
        return False


def test_validation_scenarios(monitor: PDDMonitor) -> bool:
    """
    Testa cenários de validação.
    
    Args:
        monitor: Monitor PDD
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando cenários de validação...")
        
        # Teste 1: DataFrame vazio
        df_empty = pd.DataFrame()
        assert not monitor.validate_data(df_empty), "Validação deveria falhar para DataFrame vazio"
        
        # Teste 2: Colunas faltando
        df_missing_cols = pd.DataFrame({
            'dias_atraso': [0, 30, 60],
            'valor_presente': [1000, 2000, 3000]
            # Faltam 'grupo_de_risco' e 'nome_do_cedente'
        })
        assert not monitor.validate_data(df_missing_cols), "Validação deveria falhar para colunas faltando"
        
        # Teste 3: Dados válidos
        df_valid = pd.DataFrame({
            'dias_atraso': [0, 30, 60],
            'grupo_de_risco': ['AA', 'B', 'C'],
            'valor_presente': [1000, 2000, 3000],
            'nome_do_cedente': ['EMPRESA A', 'EMPRESA B', 'EMPRESA C']
        })
        assert monitor.validate_data(df_valid), "Validação deveria passar para dados válidos"
        
        print("✅ Cenários de validação passaram")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos cenários de validação: {e}")
        return False


def test_full_monitoring_workflow(monitor: PDDMonitor, xlsx_enriched: pd.DataFrame) -> bool:
    """
    Testa workflow completo do monitor.
    
    Args:
        monitor: Monitor PDD
        xlsx_enriched: DataFrame enriquecido
        
    Returns:
        True se teste passou
    """
    try:
        print("🧪 Testando workflow completo...")
        
        # Executar monitoramento completo
        resultado = monitor.run_monitoring(xlsx_enriched)
        
        # Verificar estrutura básica
        assert "sucesso" in resultado, "Campo 'sucesso' não encontrado"
        assert resultado["sucesso"], f"Monitoramento falhou: {resultado.get('erro', 'Erro desconhecido')}"
        
        # Verificar campos obrigatórios
        campos_obrigatorios = ['monitor', 'pool_id', 'data_analise', 'pdd_analysis', 
                             'cedente_analysis', 'comparacao_metodologica', 'metodologia', 'compliance']
        
        for campo in campos_obrigatorios:
            assert campo in resultado, f"Campo '{campo}' não encontrado no resultado"
        
        # Verificar se monitor está correto
        assert resultado["monitor"] == "pdd", f"Monitor incorreto: {resultado['monitor']}"
        
        # Verificar se análise PDD está completa
        pdd_analysis = resultado["pdd_analysis"]
        assert "grupos" in pdd_analysis, "Grupos não encontrados na análise PDD"
        assert "totais" in pdd_analysis, "Totais não encontrados na análise PDD"
        
        # Verificar compliance
        compliance = resultado["compliance"]
        assert "grupos_configurados" in compliance, "Grupos configurados não encontrados"
        assert "provisao_total_percentual" in compliance, "Provisão total percentual não encontrada"
        
        print("✅ Workflow completo passou")
        return True
        
    except Exception as e:
        print(f"❌ Erro no workflow completo: {e}")
        return False


def test_single_pool(pool_name: str, dados: Dict[str, Any]) -> bool:
    """
    Testa um pool específico.
    
    Args:
        pool_name: Nome do pool para testar
        dados: Dados carregados do sistema
        
    Returns:
        True se teste passou
    """
    try:
        print(f"\n🧪 TESTANDO POOL: {pool_name}")
        print("-" * 40)
        
        # Obter configuração do pool
        pool_config = dados["pools_configs"].get(pool_name)
        if not pool_config:
            print(f"❌ Configuração do pool '{pool_name}' não encontrada")
            return False
        
        # Criar monitor
        monitor = PDDMonitor(pool_config)
        
        # Teste 1: Criação do monitor
        if not test_pdd_monitor_creation(pool_config):
            return False
        
        # Verificar se monitor está ativo
        if not monitor.is_active():
            print(f"⚠️  Monitor PDD não está ativo para pool '{pool_name}'")
            return True  # Não é erro se não estiver ativo
        
        # Enriquecer dados
        xlsx_enriched = enrich_test_data(dados, pool_name)
        
        # Teste 2: Lógica por cedente
        if not test_cedente_logic(monitor, xlsx_enriched):
            return False
        
        # Teste 3: Cálculos de provisão
        if not test_provision_calculations(monitor, xlsx_enriched):
            return False
        
        # Teste 4: Análise por cedente
        if not test_cedente_analysis(monitor, xlsx_enriched):
            return False
        
        # Teste 5: Comparação metodológica
        if not test_methodology_comparison(monitor, xlsx_enriched):
            return False
        
        # Teste 6: Cenários de validação
        if not test_validation_scenarios(monitor):
            return False
        
        # Teste 7: Workflow completo
        if not test_full_monitoring_workflow(monitor, xlsx_enriched):
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar pool '{pool_name}': {e}")
        return False


def main():
    """Função principal de teste."""
    print("🚀 INICIANDO TESTES DO MONITOR PDD OOP")
    print("=" * 50)
    
    # Carregar dados
    dados = load_test_data()
    if not dados:
        return False
    
    # Pools para testar
    pools_para_testar = ['AFA Pool #1', 'LeCapital Pool #1']
    
    testes_passou = 0
    testes_total = len(pools_para_testar)
    
    for pool_name in pools_para_testar:
        if test_single_pool(pool_name, dados):
            testes_passou += 1
            print(f"✅ Pool '{pool_name}': PASSOU")
        else:
            print(f"❌ Pool '{pool_name}': FALHOU")
    
    # Resultado final
    print(f"\n📋 RESUMO DOS TESTES")
    print("=" * 30)
    print(f"Total de pools testados: {testes_total}")
    print(f"Testes que passaram: {testes_passou}")
    print(f"Testes que falharam: {testes_total - testes_passou}")
    print(f"Taxa de sucesso: {testes_passou/testes_total*100:.1f}%")
    
    if testes_passou == testes_total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Monitor PDD OOP está funcionando corretamente")
        print("✅ Lógica por cedente implementada corretamente")
        print("✅ Cálculos de provisão estão corretos")
        print("✅ Análises e comparações funcionando")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM! Verificar erros acima")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)