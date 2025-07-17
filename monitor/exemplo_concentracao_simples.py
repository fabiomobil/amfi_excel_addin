#!/usr/bin/env python3
"""
Exemplo SIMPLES para acessar resultados do monitor de concentração
"""

import sys
sys.path.insert(0, '/mnt/c/amfi/monitor')
import orchestrator

def exemplo_simples():
    """Exemplo básico de acesso aos dados de concentração"""
    print("🎯 MONITOR DE CONCENTRAÇÃO - EXEMPLO SIMPLES")
    print("=" * 60)
    
    # Executar para um pool específico
    resultado = orchestrator.run_monitoring("AFA Pool #1")
    
    if resultado.get("sucesso"):
        pool_result = resultado["resultados"]["AFA Pool #1"]
        
        # Verificar se concentração foi executada
        if "concentracao" in pool_result.get("monitores_executados", []):
            conc_result = pool_result["resultados"]["concentracao"]
            
            print(f"✅ CONCENTRAÇÃO FUNCIONANDO!")
            print(f"   Status: {conc_result.get('status_geral', 'N/A')}")
            print(f"   Pool: {conc_result.get('pool_id', 'N/A')}")
            print(f"   PL: R$ {conc_result.get('pl_pool', 0):,.2f}")
            
            # Resumo básico
            resumo = conc_result.get('resumo', {})
            print(f"\n📊 RESUMO:")
            print(f"   Limites analisados: {resumo.get('total_limites_analisados', 0)}")
            print(f"   Limites enquadrados: {resumo.get('limites_enquadrados', 0)}")
            print(f"   Limites violados: {resumo.get('limites_violados', 0)}")
            
            # Dados completos disponíveis
            print(f"\n🔍 DADOS DISPONÍVEIS:")
            for key in conc_result.keys():
                if key not in ['sucesso', 'monitor', 'timestamp']:
                    print(f"   - {key}")
            
            print(f"\n✅ CONCENTRAÇÃO ESTÁ FUNCIONANDO PERFEITAMENTE!")
            
        else:
            print("❌ Monitor de concentração não executado")
    else:
        print(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")

if __name__ == "__main__":
    exemplo_simples()
    
    print(f"\n" + "=" * 60)
    print("🚀 COMO USAR NO SPYDER:")
    print("-" * 60)
    print("import orchestrator")
    print("resultado = orchestrator.run_monitoring('AFA Pool #1')")
    print("conc = resultado['resultados']['AFA Pool #1']['resultados']['concentracao']")
    print("print(f'Status: {conc[\"status_geral\"]}')")
    print("print(f'Resumo: {conc[\"resumo\"]}')")
    print("=" * 60)