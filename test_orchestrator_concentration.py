#!/usr/bin/env python3
"""
Teste da integração do monitor de concentração com o orquestrador
"""

import sys
import os

# Adicionar caminho do monitor
sys.path.insert(0, '/mnt/c/amfi/monitor')

# Tentar import do orquestrador
try:
    from orchestrator import run_monitoring
    print("✅ Orquestrador importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar orquestrador: {e}")
    sys.exit(1)

def test_afa_pool_with_concentration():
    """Testa AFA Pool #1 com monitor de concentração integrado."""
    print("=== Testando AFA Pool #1 com Monitor de Concentração ===")
    
    try:
        # Executar monitoramento para AFA Pool #1
        resultado = run_monitoring("AFA Pool #1")
        
        # Verificar sucesso geral
        print(f"Sucesso geral: {resultado.get('sucesso', False)}")
        
        # Verificar se pool foi processado
        if "AFA Pool #1" in resultado.get('resultados', {}):
            pool_result = resultado['resultados']['AFA Pool #1']
            print(f"Pool processado: {pool_result.get('sucesso', False)}")
            print(f"Monitores executados: {pool_result.get('monitores_executados', [])}")
            
            # Verificar se monitor de concentração foi executado
            if 'concentracao' in pool_result.get('resultados', {}):
                conc_result = pool_result['resultados']['concentracao']
                print(f"\n--- Monitor de Concentração ---")
                print(f"Sucesso: {conc_result.get('sucesso', False)}")
                print(f"Status geral: {conc_result.get('status_geral', 'desconhecido')}")
                print(f"Complexidade: {conc_result.get('configuracao', {}).get('complexidade', 'desconhecida')}")
                print(f"Número de limites: {conc_result.get('configuracao', {}).get('numero_limites', 0)}")
                
                # Mostrar resumo
                resumo = conc_result.get('resumo', {})
                print(f"Resumo:")
                print(f"  Total limites analisados: {resumo.get('total_limites_analisados', 0)}")
                print(f"  Limites enquadrados: {resumo.get('limites_enquadrados', 0)}")
                print(f"  Limites violados: {resumo.get('limites_violados', 0)}")
                
                # Mostrar resultados por limite
                print(f"\nResultados por limite:")
                for resultado_limite in conc_result.get('resultados_por_limite', []):
                    print(f"  {resultado_limite.get('limite_id', 'N/A')} - {resultado_limite.get('status', 'N/A')}")
                
            else:
                print("⚠️ Monitor de concentração não foi executado")
            
            # Verificar outros monitores
            resultados = pool_result.get('resultados', {})
            print(f"\nOutros monitores executados:")
            for monitor_name in resultados.keys():
                if monitor_name != 'concentracao':
                    monitor_result = resultados[monitor_name]
                    print(f"  {monitor_name}: {monitor_result.get('sucesso', False)}")
                    
        else:
            print("❌ Pool AFA Pool #1 não foi processado")
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

def test_credmei_pool_with_concentration():
    """Testa Credmei Pool #1 com monitor de concentração integrado."""
    print("\n=== Testando Credmei Pool #1 com Monitor de Concentração ===")
    
    try:
        # Executar monitoramento para Credmei Pool #1
        resultado = run_monitoring("Credmei Pool #1")
        
        # Verificar sucesso geral
        print(f"Sucesso geral: {resultado.get('sucesso', False)}")
        
        # Verificar se pool foi processado
        if "Credmei Pool #1" in resultado.get('resultados', {}):
            pool_result = resultado['resultados']['Credmei Pool #1']
            print(f"Pool processado: {pool_result.get('sucesso', False)}")
            print(f"Monitores executados: {pool_result.get('monitores_executados', [])}")
            
            # Verificar se monitor de concentração foi executado
            if 'concentracao' in pool_result.get('resultados', {}):
                conc_result = pool_result['resultados']['concentracao']
                print(f"\n--- Monitor de Concentração ---")
                print(f"Sucesso: {conc_result.get('sucesso', False)}")
                print(f"Status geral: {conc_result.get('status_geral', 'desconhecido')}")
                print(f"Complexidade: {conc_result.get('configuracao', {}).get('complexidade', 'desconhecida')}")
                print(f"Número de limites: {conc_result.get('configuracao', {}).get('numero_limites', 0)}")
                
            else:
                print("⚠️ Monitor de concentração não foi executado")
                    
        else:
            print("❌ Pool Credmei Pool #1 não foi processado")
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

def test_upvendas_pool_without_concentration():
    """Testa Up Vendas Pool #2 sem monitor de concentração."""
    print("\n=== Testando Up Vendas Pool #2 (sem concentração) ===")
    
    try:
        # Executar monitoramento para Up Vendas Pool #2
        resultado = run_monitoring("Up Vendas Pool #2")
        
        # Verificar sucesso geral
        print(f"Sucesso geral: {resultado.get('sucesso', False)}")
        
        # Verificar se pool foi processado
        if "Up Vendas Pool #2" in resultado.get('resultados', {}):
            pool_result = resultado['resultados']['Up Vendas Pool #2']
            print(f"Pool processado: {pool_result.get('sucesso', False)}")
            print(f"Monitores executados: {pool_result.get('monitores_executados', [])}")
            
            # Verificar se monitor de concentração foi executado
            if 'concentracao' in pool_result.get('resultados', {}):
                conc_result = pool_result['resultados']['concentracao']
                print(f"\n--- Monitor de Concentração ---")
                print(f"Sucesso: {conc_result.get('sucesso', False)}")
                print(f"Status geral: {conc_result.get('status_geral', 'desconhecido')}")
                print(f"Número de limites: {conc_result.get('configuracao', {}).get('numero_limites', 0)}")
                
            else:
                print("ℹ️ Monitor de concentração não foi executado (esperado - sem configuração)")
                    
        else:
            print("❌ Pool Up Vendas Pool #2 não foi processado")
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_afa_pool_with_concentration()
    test_credmei_pool_with_concentration()
    test_upvendas_pool_without_concentration()
    print("\n✅ Testes de integração do monitor de concentração concluídos!")