#!/usr/bin/env python3
"""
Teste específico para verificar se a análise sequencial está aplicando o filtro corretamente.
"""
import pandas as pd
import sys
import os
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor.base.monitor_concentracao import run_concentration_monitoring

def test_sequential_analysis_filter():
    """Testa se a análise sequencial está aplicando o filtro corretamente."""
    print("🔍 TESTE ESPECÍFICO: Análise Sequencial com Filtro")
    print("=" * 60)
    
    # Dados do pool
    pool_csv = pd.DataFrame({
        'pool': ['Test Pool #1'],
        'pl': [10000000],  # R$ 10M
        'sr': [7000000],
        'jr': [3000000]
    })
    
    # Carteira com Amfi Digital Assets sendo o maior sacado
    carteira_xlsx = pd.DataFrame({
        'pool': ['Test Pool #1'] * 6,
        'nome_do_sacado': [
            'Amfi Digital Assets LTDA',  # 30% - DEVE SER IGNORADA
            'Empresa A',                  # 20%
            'Empresa B',                  # 15%
            'Empresa C',                  # 10%
            'Empresa D',                  # 8%
            'Empresa E'                   # 5%
        ],
        'nome_do_cedente': [
            'Cedente 1',
            'Cedente 2',
            'Cedente 3',
            'Cedente 4',
            'Cedente 5',
            'Cedente 6'
        ],
        'valor_presente': [
            3000000,  # 30% - Amfi (deve ser ignorada)
            2000000,  # 20% - Empresa A (deve ser a maior)
            1500000,  # 15% - Empresa B
            1000000,  # 10% - Empresa C
            800000,   # 8%  - Empresa D
            500000    # 5%  - Empresa E
        ]
    })
    
    # Configuração com limites individual e top-N
    config = {
        'pool_id': 'Test Pool #1',
        'monitoramentos_ativos': [{
            'id': 'concentracao',
            'tipo': 'concentracao',
            'ativo': True,
            'limites': [
                {
                    'tipo': 'individual',
                    'entidade': 'sacado',
                    'limite': 0.25  # 25%
                },
                {
                    'tipo': 'top_n',
                    'entidade': 'sacado',
                    'n': 3,
                    'limite': 0.60  # 60%
                }
            ]
        }]
    }
    
    print("📊 DADOS DO TESTE:")
    print(f"- PL do pool: R$ {pool_csv['pl'].iloc[0]:,.2f}")
    print(f"- Limite individual: 25%")
    print(f"- Limite top-3: 60%")
    print()
    
    print("📋 CARTEIRA (antes do filtro):")
    for i, row in carteira_xlsx.iterrows():
        percentual = (row['valor_presente'] / pool_csv['pl'].iloc[0]) * 100
        print(f"   {i+1}. {row['nome_do_sacado']}: R$ {row['valor_presente']:,.2f} ({percentual:.1f}%)")
    print()
    
    # Executar monitor
    resultado = run_concentration_monitoring(pool_csv, carteira_xlsx, config)
    
    if resultado['sucesso']:
        print("✅ Monitor executado com sucesso\n")
        
        # Verificar resultados por limite
        for limite_result in resultado['resultados_por_limite']:
            tipo = limite_result['tipo']
            
            if tipo == 'individual':
                maior = limite_result['maior_concentracao']
                print(f"📊 CONCENTRAÇÃO INDIVIDUAL:")
                print(f"   Maior: {maior['entidade']} ({maior['percentual_pl']:.1f}%)")
                print(f"   Status: {limite_result['status']}")
                
                # Verificar se Amfi foi filtrada
                if 'amfi' in maior['entidade'].lower():
                    print(f"   ❌ ERRO: Amfi Digital Assets não deveria aparecer!")
                else:
                    print(f"   ✅ Amfi Digital Assets foi corretamente ignorada")
                print()
                
            elif tipo == 'top_n':
                top_n = limite_result['concentracao_top_n']
                print(f"📊 CONCENTRAÇÃO TOP-{limite_result['n']}:")
                print(f"   Total: {top_n['percentual_pl']:.1f}%")
                print(f"   Status: {limite_result['status']}")
                print()
        
        # Verificar análise sequencial
        if 'analises_capacidade' in resultado:
            if 'sacado' in resultado['analises_capacidade']:
                print("🔍 ANÁLISE SEQUENCIAL:")
                analise_sacado = resultado['analises_capacidade']['sacado']
                
                if analise_sacado.get('tipo_analise') == 'sequencial':
                    print("   Tipo: Análise Sequencial Ativa")
                    
                    # Verificar se Amfi aparece na análise sequencial
                    entidades_na_analise = []
                    for item in analise_sacado.get('analise_sequencial', []):
                        entidade = item['entidade']
                        entidades_na_analise.append(entidade)
                        print(f"   {item['posicao']}. {entidade}: {item['percentual_atual']:.1f}%")
                    
                    print()
                    
                    # Verificar se Amfi está presente (BUG)
                    amfi_presente = any('amfi' in ent.lower() for ent in entidades_na_analise)
                    if amfi_presente:
                        print("   ❌ BUG ENCONTRADO: Amfi Digital Assets aparece na análise sequencial!")
                        print("   💡 A análise sequencial não está usando dados filtrados!")
                    else:
                        print("   ✅ Amfi Digital Assets corretamente ignorada na análise sequencial")
                    
                    # Mostrar matriz de sobra tabular se disponível
                    if 'matriz_sobra_tabular' in analise_sacado:
                        print("\n📊 MATRIZ DE SOBRA TABULAR:")
                        print(analise_sacado['matriz_sobra_tabular']['tabela_ascii'])
                        
                        # Verificar se Amfi está na matriz
                        tabela_ascii = analise_sacado['matriz_sobra_tabular']['tabela_ascii']
                        if 'amfi' in tabela_ascii.lower():
                            print("   ❌ BUG: Amfi Digital Assets aparece na matriz de sobra!")
                        else:
                            print("   ✅ Amfi Digital Assets não aparece na matriz de sobra")
                else:
                    print("   ⚠️ Análise sequencial não disponível")
            else:
                print("   ⚠️ Análise de capacidade para sacado não encontrada")
        else:
            print("   ⚠️ Análises de capacidade não encontradas")
    else:
        print(f"❌ Erro no monitor: {resultado.get('erro', 'Desconhecido')}")

if __name__ == "__main__":
    test_sequential_analysis_filter()