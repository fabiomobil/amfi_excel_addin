"""
Teste Específico para Ver Resultados de Inadimplência
====================================================

Este script executa o orchestrator e mostra especificamente
os resultados do monitor de inadimplência.
"""

import sys
sys.path.append('/mnt/c/amfi/monitor')

from orchestrator import run_monitoring

print("=" * 60)
print("TESTE ESPECÍFICO: RESULTADOS DE INADIMPLÊNCIA")
print("=" * 60)

# Executar monitoramento para AFA Pool #1
print("\n🧪 Executando monitoramento para AFA Pool #1...")
resultado = run_monitoring('AFA Pool #1')

if resultado['sucesso']:
    pool_result = resultado['resultados']['AFA Pool #1']
    
    print(f"\n✅ Monitoramento executado com sucesso!")
    print(f"📊 Monitores executados: {pool_result['monitores_executados']}")
    
    # Verificar se inadimplência foi executada
    if 'inadimplencia' in pool_result['resultados']:
        print(f"\n🎯 RESULTADOS DO MONITOR DE INADIMPLÊNCIA:")
        print("-" * 50)
        
        inad_result = pool_result['resultados']['inadimplencia']
        
        # Mostrar informações básicas
        print(f"✅ Sucesso: {inad_result.get('sucesso', 'N/A')}")
        print(f"📊 Pool: {inad_result.get('pool', 'N/A')}")
        print(f"🕐 Timestamp: {inad_result.get('timestamp', 'N/A')}")
        
        # Mostrar monitores específicos executados
        if 'monitores_executados' in inad_result:
            monitores = inad_result['monitores_executados']
            print(f"\n📋 Monitores de inadimplência executados: {monitores}")
            
            # Mostrar resultados de cada monitor
            if 'resultados' in inad_result:
                for monitor_id, monitor_result in inad_result['resultados'].items():
                    print(f"\n  🔍 {monitor_id}:")
                    print(f"    ✅ Sucesso: {monitor_result.get('sucesso', 'N/A')}")
                    
                    if 'inadimplencia_percent' in monitor_result:
                        percent = monitor_result['inadimplencia_percent']
                        limite = monitor_result.get('limite_configurado', 'N/A')
                        status = monitor_result.get('status', 'N/A')
                        print(f"    📊 Inadimplência: {percent}%")
                        print(f"    🎯 Limite: {limite}")
                        print(f"    📋 Status: {status}")
                        
                        if status == 'violado':
                            print(f"    🚨 VIOLAÇÃO DETECTADA!")
                        
        else:
            print(f"\n📋 Estrutura completa do resultado:")
            for key, value in inad_result.items():
                print(f"  {key}: {value}")
    else:
        print(f"\n❌ Monitor de inadimplência NÃO foi executado!")
        print(f"   Monitores disponíveis: {list(pool_result['resultados'].keys())}")
        
else:
    print(f"\n❌ Falha no monitoramento: {resultado.get('erro', 'Erro desconhecido')}")

print(f"\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)