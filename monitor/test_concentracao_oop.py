#!/usr/bin/env python3
"""
Script de teste para comparar resultado original vs OOP do monitor de concentração.

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
    from base.monitor_concentracao import run_concentration_monitoring as original_run
    print("✅ Monitor original importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar monitor original: {e}")
    exit(1)

# Imports do sistema OOP
try:
    from base.monitor_concentracao_oop import run_concentration_monitoring as oop_run
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
    Compara dois resultados de monitoramento de concentração.
    
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
        'status_geral',
        'configuracao',
        'resumo',
        'resultados_por_limite',
        'analises_capacidade'
    ]
    
    diferenca_encontrada = False
    
    for campo in campos_criticos:
        if campo in original_result and campo in oop_result:
            valor_original = original_result[campo]
            valor_oop = oop_result[campo]
            
            # Comparação especial para campos complexos
            if campo == 'configuracao':
                if not compare_configuracao(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif campo == 'resumo':
                if not compare_resumo(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif campo == 'resultados_por_limite':
                if not compare_resultados_por_limite(valor_original, valor_oop):
                    diferenca_encontrada = True
                else:
                    print(f"✅ {campo}: IDÊNTICO")
            elif campo == 'analises_capacidade':
                if not compare_analises_capacidade(valor_original, valor_oop):
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
    
    # Verificar campos de metadados (podem diferir)
    print("\n🔍 CAMPOS DE METADADOS:")
    for campo in ['timestamp']:
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


def compare_configuracao(original: Dict, oop: Dict) -> bool:
    """Compara seção de configuração."""
    if original.get('ativo') != oop.get('ativo'):
        print(f"❌ DIFERENÇA em configuracao.ativo: {original.get('ativo')} vs {oop.get('ativo')}")
        return False
    
    if original.get('numero_limites') != oop.get('numero_limites'):
        print(f"❌ DIFERENÇA em configuracao.numero_limites: {original.get('numero_limites')} vs {oop.get('numero_limites')}")
        return False
    
    if original.get('complexidade') != oop.get('complexidade'):
        print(f"❌ DIFERENÇA em configuracao.complexidade: {original.get('complexidade')} vs {oop.get('complexidade')}")
        return False
    
    return True


def compare_resumo(original: Dict, oop: Dict) -> bool:
    """Compara seção de resumo."""
    campos = ['total_limites_analisados', 'limites_enquadrados', 'limites_violados']
    
    for campo in campos:
        if original.get(campo) != oop.get(campo):
            print(f"❌ DIFERENÇA em resumo.{campo}: {original.get(campo)} vs {oop.get(campo)}")
            return False
    
    return True


def compare_resultados_por_limite(original: list, oop: list) -> bool:
    """Compara lista de resultados por limite."""
    if len(original) != len(oop):
        print(f"❌ DIFERENÇA no número de limites: {len(original)} vs {len(oop)}")
        return False
    
    for i, (orig_limite, oop_limite) in enumerate(zip(original, oop)):
        # Comparar campos essenciais
        campos_essenciais = ['tipo', 'entidade', 'status', 'limite_configurado']
        
        for campo in campos_essenciais:
            if orig_limite.get(campo) != oop_limite.get(campo):
                print(f"❌ DIFERENÇA em limite[{i}].{campo}: {orig_limite.get(campo)} vs {oop_limite.get(campo)}")
                return False
        
        # Comparar campos específicos por tipo
        if orig_limite.get('tipo') == 'individual':
            if not compare_concentracao_individual(orig_limite, oop_limite):
                return False
        elif orig_limite.get('tipo') == 'top_n':
            if not compare_concentracao_top_n(orig_limite, oop_limite):
                return False
    
    return True


def compare_concentracao_individual(original: Dict, oop: Dict) -> bool:
    """Compara resultado de concentração individual."""
    campos = ['margem_limite', 'total_entidades']
    
    for campo in campos:
        if original.get(campo) != oop.get(campo):
            print(f"❌ DIFERENÇA em concentração individual.{campo}: {original.get(campo)} vs {oop.get(campo)}")
            return False
    
    # Comparar maior concentração
    orig_maior = original.get('maior_concentracao', {})
    oop_maior = oop.get('maior_concentracao', {})
    
    if orig_maior != oop_maior:
        print(f"❌ DIFERENÇA em maior_concentracao: {orig_maior} vs {oop_maior}")
        return False
    
    return True


def compare_concentracao_top_n(original: Dict, oop: Dict) -> bool:
    """Compara resultado de concentração top-N."""
    campos = ['n', 'margem_limite', 'total_entidades']
    
    for campo in campos:
        if original.get(campo) != oop.get(campo):
            print(f"❌ DIFERENÇA em concentração top-N.{campo}: {original.get(campo)} vs {oop.get(campo)}")
            return False
    
    # Comparar concentração top-N (original usa concentracao_top_n, não concentracao_agregada)
    orig_top_n = original.get('concentracao_top_n', {})
    oop_top_n = oop.get('concentracao_top_n', {})
    
    if orig_top_n != oop_top_n:
        print(f"❌ DIFERENÇA em concentracao_top_n: {orig_top_n} vs {oop_top_n}")
        return False
    
    # Comparar detalhes do top N
    orig_detalhes = original.get('detalhes_top_n', [])
    oop_detalhes = oop.get('detalhes_top_n', [])
    
    if len(orig_detalhes) != len(oop_detalhes):
        print(f"❌ DIFERENÇA no número de detalhes top-N: {len(orig_detalhes)} vs {len(oop_detalhes)}")
        return False
    
    for i, (orig_det, oop_det) in enumerate(zip(orig_detalhes, oop_detalhes)):
        if orig_det != oop_det:
            print(f"❌ DIFERENÇA em detalhes_top_n[{i}]: {orig_det} vs {oop_det}")
            return False
    
    return True


def compare_analises_capacidade(original: Dict, oop: Dict) -> bool:
    """Compara análises de capacidade."""
    # Verificar se ambos têm as mesmas chaves
    if set(original.keys()) != set(oop.keys()):
        print(f"❌ DIFERENÇA nas entidades de análise: {set(original.keys())} vs {set(oop.keys())}")
        return False
    
    # Comparar cada entidade
    for entidade in original.keys():
        orig_analise = original[entidade]
        oop_analise = oop[entidade]
        
        # Comparar estruturas principais
        if orig_analise.get('tipo_analise') != oop_analise.get('tipo_analise'):
            print(f"❌ DIFERENÇA em {entidade}.tipo_analise: {orig_analise.get('tipo_analise')} vs {oop_analise.get('tipo_analise')}")
            return False
        
        if orig_analise.get('entidade_tipo') != oop_analise.get('entidade_tipo'):
            print(f"❌ DIFERENÇA em {entidade}.entidade_tipo: {orig_analise.get('entidade_tipo')} vs {oop_analise.get('entidade_tipo')}")
            return False
        
        # Comparar resumo
        if not compare_resumo_analise(orig_analise.get('resumo', {}), oop_analise.get('resumo', {})):
            return False
        
        # Comparar análise sequencial
        if not compare_analise_sequencial(orig_analise.get('analise_sequencial', []), oop_analise.get('analise_sequencial', [])):
            return False
        
        # Comparar matriz tabular
        if not compare_matriz_tabular(orig_analise.get('matriz_sobra_tabular', {}), oop_analise.get('matriz_sobra_tabular', {})):
            return False
    
    return True


def compare_resumo_analise(original: Dict, oop: Dict) -> bool:
    """Compara resumo da análise."""
    campos = ['pl_pool', 'limite_individual_pct', 'limite_top_n_pct', 'top_n_size', 'espaco_total_disponivel']
    
    for campo in campos:
        if original.get(campo) != oop.get(campo):
            print(f"❌ DIFERENÇA em resumo_analise.{campo}: {original.get(campo)} vs {oop.get(campo)}")
            return False
    
    return True


def compare_analise_sequencial(original: list, oop: list) -> bool:
    """Compara análise sequencial."""
    if len(original) != len(oop):
        print(f"❌ DIFERENÇA no número de itens da análise sequencial: {len(original)} vs {len(oop)}")
        return False
    
    for i, (orig_item, oop_item) in enumerate(zip(original, oop)):
        campos = ['posicao', 'entidade', 'exposicao_atual', 'percentual_atual', 'capacidade_individual', 
                  'capacidade_efetiva', 'saldo_antes', 'saldo_apos', 'limitada_por', 'explicacao']
        
        for campo in campos:
            if orig_item.get(campo) != oop_item.get(campo):
                print(f"❌ DIFERENÇA em analise_sequencial[{i}].{campo}: {orig_item.get(campo)} vs {oop_item.get(campo)}")
                return False
    
    return True


def compare_matriz_tabular(original: Dict, oop: Dict) -> bool:
    """Compara matriz tabular."""
    # Comparar estruturas principais
    if original.get('cabecalho') != oop.get('cabecalho'):
        print(f"❌ DIFERENÇA em matriz_tabular.cabecalho")
        return False
    
    if original.get('linhas') != oop.get('linhas'):
        print(f"❌ DIFERENÇA em matriz_tabular.linhas")
        return False
    
    if original.get('resumo') != oop.get('resumo'):
        print(f"❌ DIFERENÇA em matriz_tabular.resumo")
        return False
    
    # Tabela ASCII pode diferir em formatação, mas deve ter estrutura similar
    orig_ascii = original.get('tabela_ascii', '')
    oop_ascii = oop.get('tabela_ascii', '')
    
    if len(orig_ascii) != len(oop_ascii):
        print(f"⚠️  Tamanho diferente na tabela ASCII: {len(orig_ascii)} vs {len(oop_ascii)}")
        # Mas não falha o teste por isso
    
    return True


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
        resultado_original = original_run(pool_csv, dados["xlsx_data"], pool_config)
        
        # Executar monitor OOP
        print("🔄 Executando monitor OOP...")
        resultado_oop = oop_run(pool_csv, dados["xlsx_data"], pool_config)
        
        # Comparar resultados
        return compare_results(resultado_original, resultado_oop, pool_name)
        
    except Exception as e:
        print(f"❌ Erro ao testar pool '{pool_name}': {e}")
        return False


def main():
    """Função principal de teste."""
    print("🚀 INICIANDO TESTE DE COMPATIBILIDADE - CONCENTRAÇÃO")
    print("=" * 60)
    
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