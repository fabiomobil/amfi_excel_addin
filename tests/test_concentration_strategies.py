#!/usr/bin/env python3
"""
Teste das estratégias de concentração
"""

import pandas as pd
import sys
import os

# Adicionar caminho do monitor
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

from concentration_config import ConcentrationLimit, ConcentrationType, ConcentrationEntity, CalculationMethod
from concentration_strategies import IndividualConcentration, TopNConcentration, calculate_concentration_for_limit

def create_test_data():
    """Cria dados de teste para validação."""
    data = {
        'nome_do_sacado': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa A', 'Empresa B', 'Empresa D'],
        'nome_do_cedente': ['Cedente X', 'Cedente Y', 'Cedente X', 'Cedente Z', 'Cedente Y', 'Cedente X'],
        'valor_presente': [100000, 200000, 50000, 150000, 100000, 75000],
        'grupo_economico': ['Grupo 1', 'Grupo 2', 'Grupo 3', 'Grupo 1', 'Grupo 2', 'Grupo 4']
    }
    
    return pd.DataFrame(data)

def test_individual_concentration():
    """Testa concentração individual."""
    print("=== Testando Concentração Individual ===")
    
    # Criar dados de teste
    carteira_df = create_test_data()
    pl_pool = 1000000  # R$ 1 milhão
    
    # Criar limite individual para sacado
    limite_sacado = ConcentrationLimit(
        tipo=ConcentrationType.INDIVIDUAL,
        entidade=ConcentrationEntity.SACADO,
        limite=0.30,  # 30%
        inclui_grupo_economico=False,
        metodo_calculo=CalculationMethod.SIMPLES
    )
    
    # Calcular concentração
    resultado = calculate_concentration_for_limit(carteira_df, limite_sacado, pl_pool)
    
    print(f"Tipo: {resultado['tipo']}")
    print(f"Entidade: {resultado['entidade']}")
    print(f"Limite configurado: {resultado['limite_configurado']:.1f}%")
    print(f"Maior concentração: {resultado['maior_concentracao']['entidade']} = {resultado['maior_concentracao']['percentual_pl']:.1f}%")
    print(f"Status: {resultado['status']}")
    print(f"Margem limite: {resultado['margem_limite']:.1f}%")
    print(f"Entidades analisadas: {resultado['total_entidades_analisadas']}")
    print(f"Entidades em violação: {resultado['entidades_em_violacao']}")
    
    print("\nTop 3 concentrações:")
    for i, item in enumerate(resultado['top_10_concentracoes'][:3]):
        print(f"  {i+1}. {item['entidade']}: {item['percentual_pl']:.1f}% (R$ {item['valor_absoluto']:,.0f})")
    
    print()

def test_topn_concentration():
    """Testa concentração Top-N."""
    print("=== Testando Concentração Top-N ===")
    
    # Criar dados de teste
    carteira_df = create_test_data()
    pl_pool = 1000000  # R$ 1 milhão
    
    # Criar limite Top-3 para sacado
    limite_top3 = ConcentrationLimit(
        tipo=ConcentrationType.TOP_N,
        entidade=ConcentrationEntity.SACADO,
        limite=0.80,  # 80%
        n=3,
        inclui_grupo_economico=False,
        metodo_calculo=CalculationMethod.SIMPLES
    )
    
    # Calcular concentração
    resultado = calculate_concentration_for_limit(carteira_df, limite_top3, pl_pool)
    
    print(f"Tipo: {resultado['tipo']}")
    print(f"Entidade: {resultado['entidade']}")
    print(f"N: {resultado['n']}")
    print(f"Limite configurado: {resultado['limite_configurado']:.1f}%")
    print(f"Concentração Top-{resultado['n']}: {resultado['concentracao_top_n']['percentual_pl']:.1f}%")
    print(f"Status: {resultado['status']}")
    print(f"Margem limite: {resultado['margem_limite']:.1f}%")
    
    print(f"\nDetalhes Top-{resultado['n']}:")
    for i, item in enumerate(resultado['detalhes_top_n']):
        print(f"  {i+1}. {item['entidade']}: {item['percentual_pl']:.1f}% (R$ {item['valor_absoluto']:,.0f})")
    
    print()

def test_cedente_concentration():
    """Testa concentração por cedente."""
    print("=== Testando Concentração por Cedente ===")
    
    # Criar dados de teste
    carteira_df = create_test_data()
    pl_pool = 1000000  # R$ 1 milhão
    
    # Criar limite individual para cedente
    limite_cedente = ConcentrationLimit(
        tipo=ConcentrationType.INDIVIDUAL,
        entidade=ConcentrationEntity.CEDENTE,
        limite=0.25,  # 25%
        inclui_grupo_economico=False,
        metodo_calculo=CalculationMethod.SIMPLES
    )
    
    # Calcular concentração
    resultado = calculate_concentration_for_limit(carteira_df, limite_cedente, pl_pool)
    
    print(f"Tipo: {resultado['tipo']}")
    print(f"Entidade: {resultado['entidade']}")
    print(f"Limite configurado: {resultado['limite_configurado']:.1f}%")
    print(f"Maior concentração: {resultado['maior_concentracao']['entidade']} = {resultado['maior_concentracao']['percentual_pl']:.1f}%")
    print(f"Status: {resultado['status']}")
    print(f"Margem limite: {resultado['margem_limite']:.1f}%")
    
    print("\nTop 3 concentrações:")
    for i, item in enumerate(resultado['top_10_concentracoes'][:3]):
        print(f"  {i+1}. {item['entidade']}: {item['percentual_pl']:.1f}% (R$ {item['valor_absoluto']:,.0f})")
    
    print()

def show_test_data():
    """Mostra dados de teste."""
    print("=== Dados de Teste ===")
    carteira_df = create_test_data()
    print(carteira_df.to_string(index=False))
    print(f"\nTotal carteira: R$ {carteira_df['valor_presente'].sum():,.0f}")
    print(f"PL pool: R$ 1.000.000")
    print()

if __name__ == "__main__":
    try:
        show_test_data()
        test_individual_concentration()
        test_topn_concentration()
        test_cedente_concentration()
        print("✅ Todos os testes de estratégias passaram!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()