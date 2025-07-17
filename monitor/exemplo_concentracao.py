#!/usr/bin/env python3
"""
Exemplo específico para acessar resultados do monitor de concentração
"""

import sys
sys.path.insert(0, '/mnt/c/amfi/monitor')
import orchestrator

def demonstrar_concentracao():
    """Demonstra como acessar resultados de concentração"""
    print("🎯 EXEMPLO - MONITOR DE CONCENTRAÇÃO")
    print("=" * 50)
    
    # Executar para um pool específico
    pool_name = "AFA Pool #1"
    resultado = orchestrator.run_monitoring(pool_name)
    
    if resultado.get("sucesso"):
        pool_result = resultado["resultados"][pool_name]
        
        # Verificar se concentração foi executada
        if "concentracao" in pool_result.get("monitores_executados", []):
            print(f"✅ Monitor de concentração executado para {pool_name}")
            
            # Acessar resultados de concentração
            conc_result = pool_result["resultados"]["concentracao"]
            
            print(f"\n📊 RESULTADOS DE CONCENTRAÇÃO:")
            print(f"   Sucesso: {conc_result.get('sucesso', 'N/A')}")
            print(f"   Status geral: {conc_result.get('status_geral', 'N/A')}")
            print(f"   Pool ID: {conc_result.get('pool_id', 'N/A')}")
            print(f"   PL do pool: R$ {conc_result.get('pl_pool', 0):,.2f}")
            
            # Resumo da análise
            if 'resumo' in conc_result:
                resumo = conc_result['resumo']
                print(f"\n📋 RESUMO:")
                print(f"   Total de limites analisados: {resumo.get('total_limites_analisados', 0)}")
                print(f"   Limites enquadrados: {resumo.get('limites_enquadrados', 0)}")
                print(f"   Limites violados: {resumo.get('limites_violados', 0)}")
                print(f"   Limites inativos: {resumo.get('limites_inativos', 0)}")
            
            # Resultados por limite
            if 'resultados_por_limite' in conc_result:
                print(f"\n🔍 RESULTADOS POR LIMITE:")
                for limite_id, limite_data in conc_result['resultados_por_limite'].items():
                    print(f"   {limite_id}:")
                    print(f"     Tipo: {limite_data.get('tipo', 'N/A')}")
                    print(f"     Entidade: {limite_data.get('entidade', 'N/A')}")
                    print(f"     Status: {limite_data.get('status', 'N/A')}")
                    print(f"     Utilização: {limite_data.get('utilizacao_percentual', 0):.1f}%")
                    print(f"     Limite: {limite_data.get('limite_percentual', 0)*100:.1f}%")
                    print(f"     Margem: {limite_data.get('margem_percentual', 0)*100:.1f}%")
            
            # Análise de capacidade
            if 'analises_capacidade' in conc_result:
                print(f"\n💰 ANÁLISE DE CAPACIDADE:")
                for limite_id, capacidade in conc_result['analises_capacidade'].items():
                    print(f"   {limite_id}:")
                    print(f"     Capacidade adicional: R$ {capacidade.get('capacidade_adicional', 0):,.2f}")
                    print(f"     Próximo evento: {capacidade.get('proximo_evento', 'N/A')}")
                    
        else:
            print(f"❌ Monitor de concentração não foi executado para {pool_name}")
    else:
        print(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")

def exemplo_todos_pools():
    """Exemplo para todos os pools"""
    print(f"\n\n🎯 EXEMPLO - TODOS OS POOLS")
    print("=" * 50)
    
    resultado = orchestrator.run_monitoring()
    
    if resultado.get("sucesso"):
        print(f"✅ Processados {resultado['estatisticas']['total']} pools")
        
        for pool_name, pool_result in resultado["resultados"].items():
            if "concentracao" in pool_result.get("monitores_executados", []):
                conc_result = pool_result["resultados"]["concentracao"]
                status = conc_result.get("status_geral", "N/A")
                limites_total = conc_result.get("resumo", {}).get("total_limites_analisados", 0)
                limites_violados = conc_result.get("resumo", {}).get("limites_violados", 0)
                
                print(f"\n🏦 {pool_name}:")
                print(f"   Status: {status}")
                print(f"   Limites analisados: {limites_total}")
                print(f"   Limites violados: {limites_violados}")
                
                if limites_violados > 0:
                    print(f"   ⚠️  ATENÇÃO: {limites_violados} limite(s) violado(s)")
                else:
                    print(f"   ✅ Todos os limites enquadrados")
    else:
        print(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")

if __name__ == "__main__":
    demonstrar_concentracao()
    exemplo_todos_pools()
    
    print(f"\n" + "=" * 50)
    print("🎯 COMO ACESSAR NO SPYDER:")
    print("=" * 50)
    print("import orchestrator")
    print("resultado = orchestrator.run_monitoring('AFA Pool #1')")
    print("conc_result = resultado['resultados']['AFA Pool #1']['resultados']['concentracao']")
    print("print(conc_result['status_geral'])")
    print("print(conc_result['resumo'])")
    print("=" * 50)