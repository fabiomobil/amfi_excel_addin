"""
Teste da função validate_data() do monitor de subordinação
==========================================================

Testa se a validação está funcionando corretamente com dados reais:
- Carregar CSV do dashboard (LeCapital Pool #1)
- Carregar JSON de configuração (LeCapital Pool #1)
- Executar validate_data() e verificar resultado
"""

import sys
import os
import json
import pandas as pd

# Adicionar caminhos para imports
sys.path.append('/mnt/c/amfi/monitor/base')
sys.path.append('/mnt/c/amfi/monitor/utils')

try:
    # Importar funções necessárias
    from monitor_subordinacao import validate_data
    from file_loaders import load_dashboard, load_json_file
    
    print("🚀 TESTE: validate_data() - LeCapital Pool #1")
    print("=" * 60)
    
    # 1. Carregar CSV do dashboard
    print("📊 Carregando CSV do dashboard...")
    try:
        csv_data = load_dashboard()
        print(f"✅ CSV carregado: {len(csv_data)} registros")
        
        # Filtrar apenas LeCapital Pool #1 (nome exato do CSV)
        lecapital_data = csv_data[csv_data['nome'] == 'LeCapital Pool #1']
        
        if lecapital_data.empty:
            print("❌ LeCapital Pool #1 não encontrado no CSV")
            print("📋 Pools disponíveis:")
            for pool in csv_data['nome'].unique():
                print(f"   - {pool}")
            exit(1)
        
        print(f"✅ LeCapital Pool #1 encontrado: {len(lecapital_data)} registro(s)")
        print(f"📋 Colunas disponíveis: {list(lecapital_data.columns)}")
        
        # Verificar se tem as colunas esperadas
        colunas_esperadas = ['sr', 'jr', 'pl']
        colunas_encontradas = [col for col in colunas_esperadas if col in lecapital_data.columns]
        print(f"✅ Colunas esperadas encontradas: {colunas_encontradas}")
        
        if len(colunas_encontradas) != len(colunas_esperadas):
            colunas_faltantes = [col for col in colunas_esperadas if col not in lecapital_data.columns]
            print(f"⚠️ Colunas faltantes: {colunas_faltantes}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {str(e)}")
        exit(1)
    
    # 2. Carregar JSON de configuração do LeCapital
    print(f"\n📋 Carregando JSON de configuração...")
    try:
        # Tentar diferentes caminhos para o JSON
        json_paths = [
            "/mnt/c/amfi/data/escrituras/LeCapital Pool #1.json",
            "data/escrituras/LeCapital Pool #1.json"
        ]
        
        json_config = None
        for path in json_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                print(f"✅ JSON carregado de: {path}")
                break
            except FileNotFoundError:
                continue
        
        if not json_config:
            print(f"❌ JSON não encontrado nos caminhos: {json_paths}")
            exit(1)
        
        # Verificar estrutura do JSON
        if 'monitoramentos_ativos' in json_config:
            print("✅ JSON contém 'monitoramentos_ativos'")
            
            # Buscar monitor de subordinação
            monitor_subordinacao = None
            for monitor in json_config['monitoramentos_ativos']:
                if monitor.get('id') == 'subordinacao':
                    monitor_subordinacao = monitor
                    break
            
            if monitor_subordinacao:
                print("✅ Monitor de subordinação encontrado")
                print(f"📋 Campos necessários: {monitor_subordinacao.get('campos_necessarios', [])}")
                print(f"📋 Ativo: {monitor_subordinacao.get('ativo', False)}")
                print(f"📋 Limites: {monitor_subordinacao.get('limites', {})}")
            else:
                print("❌ Monitor de subordinação não encontrado")
                exit(1)
        else:
            print("❌ JSON não contém 'monitoramentos_ativos'")
            exit(1)
            
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {str(e)}")
        exit(1)
    
    # 3. Executar validate_data()
    print(f"\n🔍 Executando validate_data()...")
    try:
        resultado = validate_data(lecapital_data, json_config)
        
        if resultado:
            print("✅ SUCESSO: validate_data() retornou True")
            print("🎉 Validação passou com sucesso!")
        else:
            print("❌ FALHA: validate_data() retornou False")
            print("💡 Verifique os logs de erro acima")
            
    except Exception as e:
        print(f"❌ ERRO na execução: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 4. Detalhes dos dados para debug
    print(f"\n📊 DETALHES DOS DADOS:")
    print("=" * 40)
    
    if not lecapital_data.empty:
        linha = lecapital_data.iloc[0]
        print(f"Pool: {linha.get('nome', 'N/A')}")
        
        for col in ['sr', 'jr', 'pl']:
            if col in linha:
                valor = linha[col]
                tipo = type(valor).__name__
                print(f"{col.upper()}: {valor} ({tipo})")
            else:
                print(f"{col.upper()}: COLUNA NÃO ENCONTRADA")
    
    if monitor_subordinacao:
        limites = monitor_subordinacao.get('limites', {})
        print(f"\nLimite mínimo: {limites.get('minimo', 'N/A')}")
        print(f"Limite crítico: {limites.get('critico', 'N/A')}")

except ImportError as e:
    print(f"❌ Erro de import: {str(e)}")
    print("💡 Verifique se os caminhos estão corretos:")
    print("   - /mnt/c/amfi/monitor/base/monitor_subordinacao.py")
    print("   - /mnt/c/amfi/monitor/utils/file_loaders.py")
except Exception as e:
    print(f"❌ Erro geral: {str(e)}")
    import traceback
    traceback.print_exc()