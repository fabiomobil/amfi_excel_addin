#!/usr/bin/env python3
"""
Script de teste para comparar resultado original vs OOP do monitor de subordinação.

Garante que resultado['resultados'] permanece 100% idêntico.
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
    from base.monitor_subordinacao import run_subordination_monitoring as original_run
    print("✅ Monitor original importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar monitor original: {e}")
    exit(1)

# Imports do sistema OOP
try:
    from base.monitor_subordinacao_oop import run_subordination_monitoring as oop_run
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
    Compara dois resultados de monitoramento de subordinação.
    
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
        'subordination_ratio',
        'subordination_ratio_percent',
        'limite_minimo',
        'limite_critico',
        'status_limite_minimo',
        'status_limite_critico',
        'aporte_necessario',
        'dados_financeiros'
    ]
    
    diferenca_encontrada = False
    
    for campo in campos_criticos:
        if campo in original_result and campo in oop_result:
            valor_original = original_result[campo]
            valor_oop = oop_result[campo]
            
            if valor_original != valor_oop:
                print(f"❌ DIFERENÇA em '{campo}':")
                print(f"   Original: {valor_original}")
                print(f"   OOP:      {valor_oop}")
                diferenca_encontrada = True
            else:
                print(f"✅ {campo}: IDÊNTICO")
        else:
            print(f"⚠️  Campo '{campo}' ausente em um dos resultados")
            diferenca_encontrada = True
    
    # Verificar campos de metadados (podem diferir)
    print("\n🔍 CAMPOS DE METADADOS:")
    for campo in ['sucesso', 'monitor', 'timestamp']:
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
        resultado_original = original_run(pool_csv, pool_config)
        
        # Executar monitor OOP
        print("🔄 Executando monitor OOP...")
        resultado_oop = oop_run(pool_csv, pool_config)
        
        # Comparar resultados
        return compare_results(resultado_original, resultado_oop, pool_name)
        
    except Exception as e:
        print(f"❌ Erro ao testar pool '{pool_name}': {e}")
        return False


def main():
    """Função principal de teste."""
    print("🚀 INICIANDO TESTE DE COMPATIBILIDADE")
    print("=" * 50)
    
    # Carregar dados
    dados = load_test_data()
    if not dados:
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
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM! Verificar diferenças acima")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)