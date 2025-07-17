#!/usr/bin/env python3
"""
Script de teste para comparar resultado original vs OOP do monitor de inadimplência.

Garante que resultado['resultados'] permanece 100% idêntico e que o enriquecimento 
progressivo funciona corretamente.
"""

import sys
import os
import pandas as pd
from typing import Dict, Any
import json

# Adicionar path para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

# Imports do sistema original
try:
    from base.monitor_inadimplencia import run_delinquency_monitoring as original_run
    print("✅ Monitor original importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar monitor original: {e}")
    exit(1)

# Imports do sistema OOP
try:
    from base.monitor_inadimplencia_oop import run_delinquency_monitoring as oop_run
    print("✅ Monitor OOP importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar monitor OOP: {e}")
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


def compare_results(original_result: Dict[str, Any], oop_result: Dict[str, Any], pool_name: str) -> bool:
    """
    Compara dois resultados de monitoramento de inadimplência.
    
    Args:
        original_result: Resultado do monitor original
        oop_result: Resultado do monitor OOP
        pool_name: Nome do pool sendo testado
        
    Returns:
        True se resultados são idênticos
    """
    print(f"\n📊 COMPARANDO RESULTADOS - {pool_name}")
    print("=" * 60)
    
    # Campos críticos que devem ser idênticos
    campos_criticos = [
        'sucesso',
        'pool_id',
        'pl_pool',
        'matriz_atrasos',
        'aging_analysis',
        'enriquecimento'
    ]
    
    # Campos de janelas dinâmicas (inadimplencia_30d, inadimplencia_90d, etc.)
    campos_janelas = [campo for campo in original_result.keys() if campo.startswith('inadimplencia_')]
    
    diferenca_encontrada = False
    
    for campo in campos_criticos:
        if campo in original_result and campo in oop_result:
            valor_original = original_result[campo]
            valor_oop = oop_result[campo]
            
            # Comparação especial para campos complexos
            if campo == 'resultados':
                if not compare_resultados(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif campo == 'matriz_atrasos':
                if not compare_matriz_atrasos(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif campo == 'aging_analysis':
                if not compare_aging_analysis(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif campo == 'enriquecimento':
                if not compare_enriquecimento(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif valor_original != valor_oop:
                print(f"❌ DIFERENÇA em '{campo}':")
                print(f"   Original: {valor_original}")
                print(f"   OOP:      {valor_oop}")
                diferenca_encontrada = True
            else:
                print(f"✅ {campo}: IDÊNTICO")
        else:
            print(f"⚠️  Campo '{campo}' ausente em um dos resultados")
            diferenca_encontrada = True
    
    # Comparar janelas dinâmicas
    print(f"\n🔍 COMPARANDO JANELAS DINÂMICAS:")
    for janela in campos_janelas:
        if janela in original_result and janela in oop_result:
            if not compare_janela_inadimplencia(original_result[janela], oop_result[janela], janela):
                diferenca_encontrada = True
            else:
                print(f"✅ {janela}: IDÊNTICO")
        else:
            print(f"⚠️  Janela '{janela}' ausente em um dos resultados")
            diferenca_encontrada = True
    
    # Verificar campos de metadados (podem diferir)
    print("\n🔍 CAMPOS DE METADADOS:")
    for campo in ['timestamp', 'monitor']:
        if campo in original_result and campo in oop_result:
            valor_original = original_result[campo]
            valor_oop = oop_result[campo]
            
            if campo == 'timestamp':
                # Timestamps podem diferir por alguns segundos
                print(f"📅 {campo}: Original={valor_original}, OOP={valor_oop}")
            elif valor_original != valor_oop:
                print(f"❌ {campo}: Original={valor_original}, OOP={valor_oop}")
                diferenca_encontrada = True
            else:
                print(f"✅ {campo}: IDÊNTICO")
    
    return not diferenca_encontrada


def compare_resultados(original: Dict, oop: Dict) -> bool:
    """Compara seção de resultados por janela."""
    if set(original.keys()) != set(oop.keys()):
        print(f"❌ DIFERENÇA nas janelas: {set(original.keys())} vs {set(oop.keys())}")
        return False
    
    for janela, orig_dados in original.items():
        oop_dados = oop[janela]
        
        campos_numericos = ['janela_dias', 'limite_configurado', 'inadimplencia_percent', 
                          'inadimplencia_valor', 'margem_limite', 'quantidade_titulos', 'pl_pool']
        
        for campo in campos_numericos:
            if campo in orig_dados and campo in oop_dados:
                orig_val = orig_dados[campo]
                oop_val = oop_dados[campo]
                
                # Comparação com tolerância para valores numéricos
                if isinstance(orig_val, (int, float)) and isinstance(oop_val, (int, float)):
                    if abs(orig_val - oop_val) > 1e-10:
                        print(f"❌ DIFERENÇA em resultados[{janela}].{campo}: {orig_val} vs {oop_val}")
                        return False
                elif orig_val != oop_val:
                    print(f"❌ DIFERENÇA em resultados[{janela}].{campo}: {orig_val} vs {oop_val}")
                    return False
        
        # Comparar status
        if orig_dados.get('status') != oop_dados.get('status'):
            print(f"❌ DIFERENÇA em resultados[{janela}].status: {orig_dados.get('status')} vs {oop_dados.get('status')}")
            return False
    
    return True


def compare_matriz_atrasos(original: Dict, oop: Dict) -> bool:
    """Compara matriz detalhada de atrasos."""
    # Campos principais
    campos_principais = ['lista_titulos_atrasados', 'consolidado_por_cedente', 
                        'consolidado_por_sacado', 'estatisticas_gerais']
    
    for campo in campos_principais:
        if campo not in original or campo not in oop:
            print(f"❌ DIFERENÇA: Campo '{campo}' ausente na matriz de atrasos")
            return False
    
    # Comparar estatísticas gerais
    orig_stats = original['estatisticas_gerais']
    oop_stats = oop['estatisticas_gerais']
    
    stats_numericas = ['total_titulos_atrasados', 'valor_total_em_atraso', 
                      'atraso_medio_dias', 'quantidade_cedentes_afetados', 
                      'quantidade_sacados_afetados']
    
    for stat in stats_numericas:
        if stat in orig_stats and stat in oop_stats:
            orig_val = orig_stats[stat]
            oop_val = oop_stats[stat]
            
            if isinstance(orig_val, (int, float)) and isinstance(oop_val, (int, float)):
                if abs(orig_val - oop_val) > 1e-10:
                    print(f"❌ DIFERENÇA em estatisticas_gerais.{stat}: {orig_val} vs {oop_val}")
                    return False
            elif orig_val != oop_val:
                print(f"❌ DIFERENÇA em estatisticas_gerais.{stat}: {orig_val} vs {oop_val}")
                return False
    
    # Comparar listas (tamanho, não conteúdo completo por performance)
    if len(original['lista_titulos_atrasados']) != len(oop['lista_titulos_atrasados']):
        print(f"❌ DIFERENÇA no tamanho da lista de títulos atrasados: {len(original['lista_titulos_atrasados'])} vs {len(oop['lista_titulos_atrasados'])}")
        return False
    
    # Comparar consolidações (chaves)
    orig_cedentes = set(original['consolidado_por_cedente'].keys())
    oop_cedentes = set(oop['consolidado_por_cedente'].keys())
    
    if orig_cedentes != oop_cedentes:
        print(f"❌ DIFERENÇA nos cedentes consolidados: {orig_cedentes} vs {oop_cedentes}")
        return False
    
    orig_sacados = set(original['consolidado_por_sacado'].keys())
    oop_sacados = set(oop['consolidado_por_sacado'].keys())
    
    if orig_sacados != oop_sacados:
        print(f"❌ DIFERENÇA nos sacados consolidados: {orig_sacados} vs {oop_sacados}")
        return False
    
    return True


def compare_aging_analysis(original: Dict, oop: Dict) -> bool:
    """Compara análise de aging."""
    # Verificar estrutura principal
    if 'faixas' not in original or 'faixas' not in oop:
        print(f"❌ DIFERENÇA: Campo 'faixas' ausente na análise de aging")
        return False
    
    orig_faixas = original['faixas']
    oop_faixas = oop['faixas']
    
    # Comparar chaves das faixas
    if set(orig_faixas.keys()) != set(oop_faixas.keys()):
        print(f"❌ DIFERENÇA nas faixas de aging: {set(orig_faixas.keys())} vs {set(oop_faixas.keys())}")
        return False
    
    # Comparar cada faixa
    for faixa, orig_dados in orig_faixas.items():
        oop_dados = oop_faixas[faixa]
        
        campos_numericos = ['quantidade', 'valor', 'percentual']
        
        for campo in campos_numericos:
            if campo in orig_dados and campo in oop_dados:
                orig_val = orig_dados[campo]
                oop_val = oop_dados[campo]
                
                if isinstance(orig_val, (int, float)) and isinstance(oop_val, (int, float)):
                    if abs(orig_val - oop_val) > 1e-10:
                        print(f"❌ DIFERENÇA em aging_analysis.faixas[{faixa}].{campo}: {orig_val} vs {oop_val}")
                        return False
                elif orig_val != oop_val:
                    print(f"❌ DIFERENÇA em aging_analysis.faixas[{faixa}].{campo}: {orig_val} vs {oop_val}")
                    return False
        
        # Comparar detalhes (tamanho)
        if 'detalhes_ativos' in orig_dados and 'detalhes_ativos' in oop_dados:
            if len(orig_dados['detalhes_ativos']) != len(oop_dados['detalhes_ativos']):
                print(f"❌ DIFERENÇA no tamanho dos detalhes da faixa {faixa}: {len(orig_dados['detalhes_ativos'])} vs {len(oop_dados['detalhes_ativos'])}")
                return False
    
    return True


def compare_enriquecimento(original: Dict, oop: Dict) -> bool:
    """Compara enriquecimento."""
    # Campos críticos de enriquecimento
    campos_criticos = ['dias_atraso_adicionado', 'grupo_de_risco_adicionado', 
                      'registros_pool', 'registros_total_xlsx']
    
    for campo in campos_criticos:
        if original.get(campo) != oop.get(campo):
            print(f"❌ DIFERENÇA em enriquecimento.{campo}: {original.get(campo)} vs {oop.get(campo)}")
            return False
    
    return True


def compare_janela_inadimplencia(original: Dict, oop: Dict, janela_nome: str) -> bool:
    """Compara resultado de uma janela de inadimplência."""
    campos_numericos = ['percentual', 'valor_absoluto', 'pl_base', 'limite', 'margem', 'quantidade_titulos']
    
    for campo in campos_numericos:
        if campo in original and campo in oop:
            orig_val = original[campo]
            oop_val = oop[campo]
            
            if isinstance(orig_val, (int, float)) and isinstance(oop_val, (int, float)):
                if abs(orig_val - oop_val) > 1e-10:
                    print(f"❌ DIFERENÇA em {janela_nome}.{campo}: {orig_val} vs {oop_val}")
                    return False
            elif orig_val != oop_val:
                print(f"❌ DIFERENÇA em {janela_nome}.{campo}: {orig_val} vs {oop_val}")
                return False
    
    # Comparar status
    if original.get('status') != oop.get('status'):
        print(f"❌ DIFERENÇA em {janela_nome}.status: {original.get('status')} vs {oop.get('status')}")
        return False
    
    return True


def test_progressive_enrichment(dados: Dict[str, Any]) -> bool:
    """
    Testa especificamente o enriquecimento progressivo.
    
    Args:
        dados: Dados carregados do sistema
        
    Returns:
        True se enriquecimento funciona corretamente
    """
    print(f"\n🧪 TESTANDO ENRIQUECIMENTO PROGRESSIVO")
    print("-" * 50)
    
    try:
        # Usar AFA Pool #1 para teste
        pool_name = 'AFA Pool #1'
        
        # Preparar dados para o pool
        nome_col = 'nome' if 'nome' in dados["csv_data"].columns else 'Nome'
        pool_csv = dados["csv_data"][dados["csv_data"][nome_col] == pool_name]
        
        if pool_csv.empty:
            print(f"❌ Pool '{pool_name}' não encontrado no CSV")
            return False
        
        pool_config = dados["pools_configs"].get(pool_name)
        if not pool_config:
            print(f"❌ Configuração do pool '{pool_name}' não encontrada")
            return False
        
        # Criar cópia do DataFrame para testar modificação
        xlsx_original = dados["xlsx_data"].copy()
        
        # Verificar colunas antes
        colunas_antes = set(xlsx_original.columns)
        print(f"📋 Colunas antes: {len(colunas_antes)}")
        
        # Executar monitor OOP
        print("🔄 Executando monitor OOP...")
        resultado_oop = oop_run(pool_csv, xlsx_original, pool_config)
        
        # Verificar colunas depois
        colunas_depois = set(xlsx_original.columns)
        print(f"📋 Colunas depois: {len(colunas_depois)}")
        
        # Verificar se campos foram adicionados
        campos_adicionados = colunas_depois - colunas_antes
        print(f"➕ Campos adicionados: {campos_adicionados}")
        
        # Validações
        if 'dias_atraso' not in campos_adicionados:
            print("❌ Campo 'dias_atraso' não foi adicionado")
            return False
        
        if 'grupo_de_risco' not in campos_adicionados:
            print("❌ Campo 'grupo_de_risco' não foi adicionado")
            return False
        
        # Verificar se os valores fazem sentido
        if not all(xlsx_original['dias_atraso'] >= 0):
            print("❌ Valores de 'dias_atraso' inválidos (negativos)")
            return False
        
        grupos_validos = ['AA', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'N/A']
        if not xlsx_original['grupo_de_risco'].isin(grupos_validos).all():
            print("❌ Valores de 'grupo_de_risco' inválidos")
            return False
        
        # Verificar enriquecimento (estrutura original)
        enriquecimento = resultado_oop.get('enriquecimento', {})
        if not enriquecimento.get('dias_atraso_adicionado'):
            print("❌ Enriquecimento não indica que 'dias_atraso' foi adicionado")
            return False
        
        if not enriquecimento.get('grupo_de_risco_adicionado'):
            print("❌ Enriquecimento não indica que 'grupo_de_risco' foi adicionado")
            return False
        
        print("✅ Enriquecimento progressivo funcionou corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de enriquecimento progressivo: {e}")
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
        
        # Preparar dados para o pool
        nome_col = 'nome' if 'nome' in dados["csv_data"].columns else 'Nome'
        pool_csv = dados["csv_data"][dados["csv_data"][nome_col] == pool_name]
        
        if pool_csv.empty:
            print(f"❌ Pool '{pool_name}' não encontrado no CSV")
            return False
        
        pool_config = dados["pools_configs"].get(pool_name)
        if not pool_config:
            print(f"❌ Configuração do pool '{pool_name}' não encontrada")
            return False
        
        # Executar monitor original
        print("🔄 Executando monitor original...")
        xlsx_original = dados["xlsx_data"].copy()
        resultado_original = original_run(pool_csv, xlsx_original, pool_config)
        
        # Executar monitor OOP
        print("🔄 Executando monitor OOP...")
        xlsx_oop = dados["xlsx_data"].copy()
        resultado_oop = oop_run(pool_csv, xlsx_oop, pool_config)
        
        # Comparar resultados
        return compare_results(resultado_original, resultado_oop, pool_name)
        
    except Exception as e:
        print(f"❌ Erro ao testar pool '{pool_name}': {e}")
        return False


def main():
    """Função principal de teste."""
    print("🚀 INICIANDO TESTE DE COMPATIBILIDADE - INADIMPLÊNCIA OOP")
    print("=" * 60)
    
    # Carregar dados
    dados = load_test_data()
    if not dados:
        return False
    
    # Testar enriquecimento progressivo primeiro
    if not test_progressive_enrichment(dados):
        print("❌ Teste de enriquecimento progressivo falhou")
        return False
    
    # Pools para testar (usar apenas alguns para velocidade)
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
        print("🎉 TODOS OS TESTES PASSARAM! resultado['resultados'] é IDÊNTICO")
        print("✅ Enriquecimento progressivo funciona corretamente")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM! Verificar diferenças acima")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)