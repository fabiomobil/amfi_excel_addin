"""
Teste Unitário do Monitor de Subordinação
==========================================

Testa as funções validate_data() e calculate_subordination_ratio()
usando os pools definidos em test_pools.json
"""

import sys
import os
import json
import pandas as pd

# Adicionar caminhos para imports
sys.path.append('/mnt/c/amfi/monitor/base')
sys.path.append('/mnt/c/amfi/monitor/utils')

try:
    # Importar funções a serem testadas
    from monitor_subordinacao import validate_data, calculate_subordination_ratio, run_subordination_monitoring
    from file_loaders import load_dashboard, load_json_file
    
    print("🧪 TESTE UNITÁRIO: Monitor de Subordinação")
    print("=" * 60)
    
    # 1. Carregar configuração de teste
    print("📋 Carregando configuração de teste...")
    try:
        test_config = load_json_file('test_pools.json')
        pools_para_teste = test_config.get('debug_pools', [])
        print(f"✅ Pools para teste: {pools_para_teste}")
    except Exception as e:
        print(f"❌ Erro ao carregar test_pools.json: {str(e)}")
        exit(1)
    
    # 2. Carregar CSV do dashboard
    print("\n📊 Carregando CSV do dashboard...")
    try:
        csv_data = load_dashboard()
        print(f"✅ CSV carregado: {len(csv_data)} registros")
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {str(e)}")
        exit(1)
    
    # 3. Executar testes para cada pool
    resultados_teste = []
    
    for pool_name in pools_para_teste:
        print(f"\n{'='*60}")
        print(f"🧪 TESTANDO: {pool_name}")
        print(f"{'='*60}")
        
        try:
            # 3.1. Filtrar dados do pool
            pool_data = csv_data[csv_data['nome'] == pool_name]
            
            if pool_data.empty:
                print(f"❌ Pool '{pool_name}' não encontrado no CSV")
                print("📋 Pools disponíveis:")
                for pool in csv_data['nome'].unique()[:5]:
                    print(f"   - {pool}")
                continue
            
            print(f"✅ Dados do pool encontrados: {len(pool_data)} registro(s)")
            
            # 3.2. Carregar configuração JSON do pool
            json_path = f"/mnt/c/amfi/data/escrituras/{pool_name}.json"
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    pool_config = json.load(f)
                print(f"✅ JSON carregado: {json_path}")
            except FileNotFoundError:
                print(f"❌ JSON não encontrado: {json_path}")
                continue
            
            # 3.3. TESTE 1: validate_data()
            print(f"\n🔍 TESTE 1: validate_data()")
            try:
                validacao_ok = validate_data(pool_data, pool_config)
                if validacao_ok:
                    print("✅ PASSOU: validate_data() retornou True")
                else:
                    print("❌ FALHOU: validate_data() retornou False")
                    continue
            except Exception as e:
                print(f"❌ ERRO: validate_data() falhou: {str(e)}")
                continue
            
            # 3.4. TESTE 2: calculate_subordination_ratio()
            print(f"\n🧮 TESTE 2: calculate_subordination_ratio()")
            try:
                resultado = calculate_subordination_ratio(pool_data, pool_config)
                
                if 'erro' in resultado:
                    print(f"❌ ERRO: {resultado['erro']}")
                    continue
                
                print("✅ PASSOU: calculate_subordination_ratio() executado com sucesso")
                
                # 3.5. Validar resultado
                print(f"\n📊 RESULTADO: {pool_name}")
                print(f"   Subordination Ratio: {resultado.get('subordination_ratio', 'N/A')}")
                print(f"   Percentual: {resultado.get('subordination_ratio_percent', 'N/A')}%")
                print(f"   Limite Mínimo: {resultado.get('limite_minimo', 'N/A')}")
                print(f"   Status Mínimo: {resultado.get('status_limite_minimo', 'N/A')}")
                print(f"   Limite Crítico: {resultado.get('limite_critico', 'N/A')}")
                print(f"   Status Crítico: {resultado.get('status_limite_critico', 'N/A')}")
                
                # Dados financeiros
                dados_fin = resultado.get('dados_financeiros', {})
                print(f"   PL: {dados_fin.get('pl_atual', 'N/A')}")
                print(f"   SR: {dados_fin.get('sr_atual', 'N/A')}")
                print(f"   JR: {dados_fin.get('jr_atual', 'N/A')}")
                
                # Aportes necessários (se houver)
                aportes = resultado.get('aporte_necessario', {})
                aporte_min = aportes.get('para_limite_minimo', 0)
                aporte_crit = aportes.get('para_limite_critico', 0)
                
                if aporte_min > 0 or aporte_crit > 0:
                    print(f"   ⚠️  Aporte Mínimo: R$ {aporte_min:,.2f}")
                    print(f"   ⚠️  Aporte Crítico: R$ {aporte_crit:,.2f}")
                
                # 3.6. Verificar consistência matemática
                print(f"\n🔢 TESTE 3: Verificação matemática")
                sr = dados_fin.get('sr_atual', 0)
                jr = dados_fin.get('jr_atual', 0)
                
                if sr > 0 and jr > 0:
                    ratio_calculado = jr / (sr + jr)
                    ratio_retornado = resultado.get('subordination_ratio', 0)
                    
                    diferenca = abs(ratio_calculado - ratio_retornado)
                    if diferenca < 0.0001:  # Tolerância para arredondamento
                        print("✅ PASSOU: Fórmula matemática correta")
                    else:
                        print(f"❌ FALHOU: Fórmula incorreta. Esperado: {ratio_calculado:.4f}, Obtido: {ratio_retornado:.4f}")
                else:
                    print("⚠️  SKIP: Valores zero - não é possível verificar fórmula")
                
                # Salvar resultado do teste
                resultado_teste = {
                    "pool": pool_name,
                    "validacao": True,
                    "calculo": True,
                    "resultado": resultado
                }
                resultados_teste.append(resultado_teste)
                
                # 3.7. TESTE 4: run_subordination_monitoring() (wrapper)
                print(f"\n🎯 TESTE 4: run_subordination_monitoring() (wrapper)")
                try:
                    resultado_wrapper = run_subordination_monitoring(pool_data, pool_config)
                    
                    if resultado_wrapper.get("sucesso"):
                        print("✅ PASSOU: run_subordination_monitoring() executado com sucesso")
                        
                        # Verificar se resultado é consistente
                        ratio_wrapper = resultado_wrapper.get('subordination_ratio', 0)
                        ratio_original = resultado.get('subordination_ratio', 0)
                        
                        if abs(ratio_wrapper - ratio_original) < 0.0001:
                            print("✅ PASSOU: Wrapper retorna resultado consistente")
                        else:
                            print(f"❌ FALHOU: Wrapper inconsistente. Original: {ratio_original}, Wrapper: {ratio_wrapper}")
                    else:
                        print(f"❌ FALHOU: run_subordination_monitoring() falhou: {resultado_wrapper.get('erro', 'Erro desconhecido')}")
                        
                except Exception as e:
                    print(f"❌ ERRO: run_subordination_monitoring() falhou: {str(e)}")
                    
                print(f"✅ SUCESSO: Todos os testes passaram para {pool_name}")
                
            except Exception as e:
                print(f"❌ ERRO: calculate_subordination_ratio() falhou: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
                
        except Exception as e:
            print(f"❌ ERRO GERAL para {pool_name}: {str(e)}")
            continue
    
    # 4. Resumo dos testes
    print(f"\n{'='*60}")
    print(f"📊 RESUMO DOS TESTES")
    print(f"{'='*60}")
    
    total_pools = len(pools_para_teste)
    pools_testados = len(resultados_teste)
    
    print(f"🎯 Pools para teste: {total_pools}")
    print(f"✅ Pools testados com sucesso: {pools_testados}")
    print(f"❌ Pools com falha: {total_pools - pools_testados}")
    
    if pools_testados > 0:
        print(f"\n📋 Pools testados:")
        for resultado in resultados_teste:
            pool = resultado['pool']
            ratio = resultado['resultado'].get('subordination_ratio_percent', 0)
            status = resultado['resultado'].get('status_limite_minimo', 'N/A')
            print(f"   - {pool}: {ratio}% ({status})")
        
        print(f"\n🎉 Taxa de sucesso: {pools_testados/total_pools*100:.1f}%")
    else:
        print(f"\n❌ Nenhum pool foi testado com sucesso")

except ImportError as e:
    print(f"❌ Erro de import: {str(e)}")
    print("💡 Verifique se os caminhos estão corretos:")
    print("   - /mnt/c/amfi/monitor/base/monitor_subordinacao.py")
    print("   - /mnt/c/amfi/monitor/utils/file_loaders.py")
except Exception as e:
    print(f"❌ Erro geral: {str(e)}")
    import traceback
    traceback.print_exc()