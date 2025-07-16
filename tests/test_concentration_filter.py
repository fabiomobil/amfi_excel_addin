"""
Teste do filtro de concentração para ignorar Amfi Digital Assets LTDA
"""
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.base.monitor_concentracao import (
    _load_concentration_filters,
    _should_ignore_entity,
    _filter_concentration_data,
    run_concentration_monitoring
)

def test_filter_functions():
    """Testa as funções de filtro isoladamente."""
    print("🧪 TESTE 1: Funções de Filtro")
    print("-" * 50)
    
    # Carregar configuração
    filters_config = _load_concentration_filters()
    print(f"✅ Configuração carregada: {filters_config}")
    
    # Testar _should_ignore_entity
    test_cases = [
        ("Amfi Digital Assets LTDA", "cedente", True),
        ("Amfi Digital Assets LTDA", "sacado", True),
        ("amfi digital assets ltda", "cedente", True),  # case insensitive
        ("AMFI DIGITAL ASSETS LTDA", "sacado", True),   # case insensitive
        ("Empresa ABC", "cedente", False),
        ("Empresa XYZ", "sacado", False),
    ]
    
    for entity, entity_type, expected in test_cases:
        result = _should_ignore_entity(entity, entity_type, filters_config)
        status = "✅" if result == expected else "❌"
        print(f"{status} {entity} ({entity_type}): {'ignorar' if result else 'manter'}")
    
    print()

def test_filter_dataframe():
    """Testa o filtro em um DataFrame."""
    print("🧪 TESTE 2: Filtro em DataFrame")
    print("-" * 50)
    
    # Criar DataFrame de teste
    df = pd.DataFrame({
        'pool': ['Test Pool'] * 8,
        'nome_do_cedente': [
            'Cedente A',
            'Amfi Digital Assets LTDA',
            'Cedente B',
            'amfi digital assets ltda',  # lowercase
            'Cedente C'
        ] + ['Cedente D'] * 3,
        'nome_do_sacado': [
            'Sacado 1',
            'Sacado 2',
            'Amfi Digital Assets LTDA',
            'Sacado 3',
            'AMFI DIGITAL ASSETS LTDA'  # uppercase
        ] + ['Sacado 4'] * 3,
        'valor_presente': [100000, 200000, 150000, 175000, 125000, 50000, 75000, 80000]
    })
    
    print(f"DataFrame original: {len(df)} registros")
    print(f"Cedentes únicos: {df['nome_do_cedente'].nunique()}")
    print(f"Sacados únicos: {df['nome_do_sacado'].nunique()}")
    
    # Carregar filtros e aplicar
    filters_config = _load_concentration_filters()
    
    # Filtrar cedentes
    df_filtered_cedentes = _filter_concentration_data(df, "cedente", filters_config)
    print(f"\nApós filtrar cedentes: {len(df_filtered_cedentes)} registros")
    print(f"Cedentes únicos: {df_filtered_cedentes['nome_do_cedente'].nunique()}")
    
    # Filtrar sacados
    df_filtered_sacados = _filter_concentration_data(df, "sacado", filters_config)
    print(f"\nApós filtrar sacados: {len(df_filtered_sacados)} registros")
    print(f"Sacados únicos: {df_filtered_sacados['nome_do_sacado'].nunique()}")
    
    # Verificar se Amfi foi removida
    amfi_in_cedentes = df_filtered_cedentes['nome_do_cedente'].str.lower().str.contains('amfi digital').any()
    amfi_in_sacados = df_filtered_sacados['nome_do_sacado'].str.lower().str.contains('amfi digital').any()
    
    print(f"\n{'✅' if not amfi_in_cedentes else '❌'} Amfi Digital Assets removida dos cedentes")
    print(f"{'✅' if not amfi_in_sacados else '❌'} Amfi Digital Assets removida dos sacados")
    
    print()

def test_concentration_monitoring():
    """Testa o monitor de concentração completo com filtro."""
    print("🧪 TESTE 3: Monitor de Concentração Completo")
    print("-" * 50)
    
    # Dados do pool
    pool_csv = pd.DataFrame({
        'pool': ['Test Pool #1'],
        'pl': [10000000],
        'sr': [7000000],
        'jr': [3000000]
    })
    
    # Carteira com Amfi Digital Assets
    carteira_xlsx = pd.DataFrame({
        'pool': ['Test Pool #1'] * 10,
        'nome_do_sacado': [
            'Empresa A',
            'Empresa B',
            'Amfi Digital Assets LTDA',  # Deve ser ignorada
            'Empresa C',
            'Empresa D',
            'AMFI DIGITAL ASSETS LTDA',  # Deve ser ignorada (uppercase)
            'Empresa E',
            'Empresa F',
            'Empresa G',
            'Empresa H'
        ],
        'nome_do_cedente': [
            'Cedente 1',
            'Cedente 2',
            'Cedente 3',
            'Amfi Digital Assets LTDA',  # Deve ser ignorada
            'Cedente 4',
            'Cedente 5',
            'amfi digital assets ltda',  # Deve ser ignorada (lowercase)
            'Cedente 6',
            'Cedente 7',
            'Cedente 8'
        ],
        'valor_presente': [
            1000000,  # 10%
            800000,   # 8%
            2000000,  # 20% - mas será ignorada
            700000,   # 7%
            600000,   # 6%
            1500000,  # 15% - mas será ignorada
            500000,   # 5%
            400000,   # 4%
            300000,   # 3%
            200000    # 2%
        ]
    })
    
    # Configuração do pool
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
                    'limite': 0.15  # 15%
                },
                {
                    'tipo': 'top_n',
                    'entidade': 'sacado',
                    'n': 5,
                    'limite': 0.50  # 50%
                }
            ]
        }]
    }
    
    print("Configuração do teste:")
    print(f"- PL do pool: R$ {pool_csv['pl'].iloc[0]:,.2f}")
    print(f"- Total de registros: {len(carteira_xlsx)}")
    print(f"- Registros com Amfi: {carteira_xlsx['nome_do_sacado'].str.lower().str.contains('amfi digital').sum()}")
    print(f"- Limite individual: 15%")
    print(f"- Limite top-5: 50%")
    
    # Executar monitor
    resultado = run_concentration_monitoring(pool_csv, carteira_xlsx, config)
    
    if resultado['sucesso']:
        print(f"\n✅ Monitor executado com sucesso")
        
        # Analisar resultados
        for limite_result in resultado['resultados_por_limite']:
            tipo = limite_result['tipo']
            status = limite_result['status']
            
            if tipo == 'individual':
                maior = limite_result['maior_concentracao']
                print(f"\n📊 Concentração Individual:")
                print(f"   Maior: {maior['entidade']} ({maior['percentual_pl']:.1f}%)")
                print(f"   Status: {status}")
                print(f"   Limite: {limite_result['limite_configurado']:.0f}%")
                
                # Verificar se Amfi não está no resultado
                if 'amfi' in maior['entidade'].lower():
                    print(f"   ❌ ERRO: Amfi Digital Assets não deveria aparecer!")
                else:
                    print(f"   ✅ Amfi Digital Assets foi corretamente ignorada")
                    
            elif tipo == 'top_n':
                top_n = limite_result['concentracao_top_n']
                print(f"\n📊 Concentração Top-{limite_result['n']}:")
                print(f"   Total: {top_n['percentual_pl']:.1f}%")
                print(f"   Status: {status}")
                print(f"   Limite: {limite_result['limite_configurado']:.0f}%")
                
                # Listar entidades do top-n
                if 'entidades' in limite_result:
                    print(f"   Entidades no top-{limite_result['n']}:")
                    for i, ent in enumerate(limite_result['entidades'][:5], 1):
                        print(f"     {i}. {ent['entidade']} ({ent['percentual_pl']:.1f}%)")
    else:
        print(f"❌ Erro no monitor: {resultado.get('erro', 'Desconhecido')}")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DO FILTRO DE CONCENTRAÇÃO - AMFI DIGITAL ASSETS")
    print("=" * 60)
    print()
    
    test_filter_functions()
    test_filter_dataframe()
    test_concentration_monitoring()
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)