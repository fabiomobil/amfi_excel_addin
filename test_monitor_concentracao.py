#!/usr/bin/env python3
"""
Teste completo do monitor de concentração
"""

import json
import pandas as pd
import sys
import os

# Adicionar caminho do monitor
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

from monitor_concentracao import run_concentration_monitoring, _has_concentration_monitoring

def create_test_csv_data():
    """Simula dados CSV com PL dos pools."""
    return pd.DataFrame({
        'pool': ['AFA Pool #1', 'Credmei Pool #1', 'Up Vendas Pool #2'],
        'pl': [8500000, 20000000, 22000000],
        'sr': [6000000, 18000000, 17600000],
        'jr': [2500000, 2000000, 4400000]
    })

def create_test_xlsx_data():
    """Simula dados XLSX com carteira detalhada."""
    return pd.DataFrame({
        'pool': ['AFA Pool #1'] * 6 + ['Credmei Pool #1'] * 4,
        'nome_do_sacado': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa A', 'Empresa B', 'Empresa D',
                           'Empresa X', 'Empresa Y', 'Empresa Z', 'Empresa X'],
        'nome_do_cedente': ['Cedente 1', 'Cedente 2', 'Cedente 1', 'Cedente 3', 'Cedente 2', 'Cedente 1',
                           'Cedente A', 'Cedente B', 'Cedente A', 'Cedente C'],
        'valor_presente': [500000, 800000, 300000, 700000, 600000, 400000,
                          100000, 200000, 150000, 250000],
        'grupo_economico': ['Grupo 1', 'Grupo 2', 'Grupo 3', 'Grupo 1', 'Grupo 2', 'Grupo 4',
                           'Grupo A', 'Grupo B', 'Grupo C', 'Grupo A']
    })

def test_afa_pool_concentration():
    """Testa concentração do AFA Pool #1 (complexidade alta)."""
    print("=== Testando AFA Pool #1 (Complexidade Alta) ===")
    
    # Carregar configuração
    with open('/mnt/c/amfi/config/pools/AFA Pool #1.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Verificar se tem monitoramento ativo
    print(f"Tem monitoramento ativo: {_has_concentration_monitoring(config)}")
    
    # Criar dados de teste
    csv_data = create_test_csv_data()
    xlsx_data = create_test_xlsx_data()
    
    # Filtrar apenas AFA Pool #1
    csv_afa = csv_data[csv_data['pool'] == 'AFA Pool #1']
    
    # Executar monitoramento
    resultado = run_concentration_monitoring(csv_afa, xlsx_data, config)
    
    # Mostrar resultados
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Pool ID: {resultado['pool_id']}")
    print(f"PL Pool: R$ {resultado['pl_pool']:,.0f}")
    print(f"Configuração ativa: {resultado['configuracao']['ativo']}")
    print(f"Complexidade: {resultado['configuracao']['complexidade']}")
    print(f"Número de limites: {resultado['configuracao']['numero_limites']}")
    print(f"Status geral: {resultado['status_geral']}")
    
    print("\nResumo:")
    resumo = resultado['resumo']
    print(f"  Total limites analisados: {resumo['total_limites_analisados']}")
    print(f"  Limites enquadrados: {resumo['limites_enquadrados']}")
    print(f"  Limites violados: {resumo['limites_violados']}")
    
    print("\nResultados por limite:")
    for resultado_limite in resultado['resultados_por_limite']:
        print(f"  {resultado_limite['limite_id']} ({resultado_limite['tipo']} {resultado_limite['entidade']}):")
        print(f"    Status: {resultado_limite['status']}")
        print(f"    Limite: {resultado_limite['limite_configurado']:.1f}%")
        if resultado_limite['status'] != 'erro':
            if 'maior_concentracao' in resultado_limite:
                maior = resultado_limite['maior_concentracao']
                print(f"    Maior concentração: {maior['entidade']} = {maior['percentual_pl']:.1f}%")
            elif 'concentracao_top_n' in resultado_limite:
                top_n = resultado_limite['concentracao_top_n']
                print(f"    Top-{resultado_limite['n']}: {top_n['percentual_pl']:.1f}%")
    
    print()

def test_credmei_pool_concentration():
    """Testa concentração do Credmei Pool #1 (simplicidade máxima)."""
    print("=== Testando Credmei Pool #1 (Simplicidade Máxima) ===")
    
    # Carregar configuração
    with open('/mnt/c/amfi/config/pools/Credmei Pool #1.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Verificar se tem monitoramento ativo
    print(f"Tem monitoramento ativo: {_has_concentration_monitoring(config)}")
    
    # Criar dados de teste
    csv_data = create_test_csv_data()
    xlsx_data = create_test_xlsx_data()
    
    # Filtrar apenas Credmei Pool #1
    csv_credmei = csv_data[csv_data['pool'] == 'Credmei Pool #1']
    
    # Executar monitoramento
    resultado = run_concentration_monitoring(csv_credmei, xlsx_data, config)
    
    # Mostrar resultados
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Pool ID: {resultado['pool_id']}")
    print(f"Status geral: {resultado['status_geral']}")
    
    if resultado['status_geral'] != 'sem_limites':
        print(f"Número de limites: {resultado['configuracao']['numero_limites']}")
        
        print("\nResultados por limite:")
        for resultado_limite in resultado['resultados_por_limite']:
            print(f"  {resultado_limite['limite_id']} ({resultado_limite['tipo']} {resultado_limite['entidade']}):")
            print(f"    Status: {resultado_limite['status']}")
            print(f"    Limite: {resultado_limite['limite_configurado']:.1f}%")
            if resultado_limite['status'] != 'erro':
                maior = resultado_limite['maior_concentracao']
                print(f"    Maior concentração: {maior['entidade']} = {maior['percentual_pl']:.1f}%")
    
    print()

def test_upvendas_pool_concentration():
    """Testa concentração do Up Vendas Pool #2 (sem limites)."""
    print("=== Testando Up Vendas Pool #2 (Sem Limites) ===")
    
    # Carregar configuração
    with open('/mnt/c/amfi/config/pools/Up Vendas Pool #2.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Verificar se tem monitoramento ativo
    print(f"Tem monitoramento ativo: {_has_concentration_monitoring(config)}")
    
    # Criar dados de teste
    csv_data = create_test_csv_data()
    xlsx_data = create_test_xlsx_data()
    
    # Filtrar apenas Up Vendas Pool #2
    csv_upvendas = csv_data[csv_data['pool'] == 'Up Vendas Pool #2']
    
    # Executar monitoramento
    resultado = run_concentration_monitoring(csv_upvendas, xlsx_data, config)
    
    # Mostrar resultados
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Pool ID: {resultado['pool_id']}")
    print(f"Status geral: {resultado['status_geral']}")
    print(f"Número de limites: {resultado['configuracao']['numero_limites']}")
    
    print()

if __name__ == "__main__":
    try:
        test_afa_pool_concentration()
        test_credmei_pool_concentration()
        test_upvendas_pool_concentration()
        print("✅ Todos os testes do monitor de concentração passaram!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()