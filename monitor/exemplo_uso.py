#!/usr/bin/env python3
"""
Exemplo SIMPLES de uso do sistema de monitoramento AmFi
"""

import orchestrator

def exemplo_basico():
    """Exemplo básico - processar todos os pools"""
    print("🎯 EXEMPLO BÁSICO")
    print("-" * 30)
    
    # Executar monitoramento
    resultado = orchestrator.run_monitoring()
    
    # Verificar resultado
    if resultado.get("sucesso"):
        stats = resultado["estatisticas"]
        print(f"✅ Processados: {stats['total']} pools")
        print(f"📈 Taxa de sucesso: {stats['taxa_sucesso']}%")
        
        # Mostrar pools com concentração
        for pool_name, pool_result in resultado["resultados"].items():
            monitores = pool_result.get("monitores_executados", [])
            if "concentracao" in monitores:
                conc = pool_result["resultados"]["concentracao"]
                print(f"🏦 {pool_name}: {conc['status_geral']}")
    else:
        print(f"❌ Erro: {resultado.get('erro')}")
    
    return resultado

def exemplo_pool_especifico():
    """Exemplo - pool específico"""
    print("\n🎯 EXEMPLO POOL ESPECÍFICO")
    print("-" * 30)
    
    # Executar para pool específico
    resultado = orchestrator.run_monitoring("E-ctare Pool #1")
    
    if resultado.get("sucesso"):
        pool_result = resultado["resultados"]["E-ctare Pool #1"]
        monitores = pool_result.get("monitores_executados", [])
        
        print(f"✅ {len(monitores)} monitores executados")
        
        # Mostrar resultado de cada monitor
        for monitor in monitores:
            result = pool_result["resultados"][monitor]
            if monitor == "concentracao":
                print(f"📊 Concentração: {result['status_geral']}")
            elif monitor == "subordinacao":
                print(f"📈 Subordinação: {result['subordination_ratio_percent']}%")
    else:
        print(f"❌ Erro: {resultado.get('erro')}")
    
    return resultado

def exemplo_dados_detalhados():
    """Exemplo - acessar dados detalhados"""
    print("\n🎯 EXEMPLO DADOS DETALHADOS")
    print("-" * 30)
    
    resultado = orchestrator.run_monitoring("E-ctare Pool #1")
    
    if resultado.get("sucesso"):
        # Acessar dados de concentração
        conc = resultado["resultados"]["E-ctare Pool #1"]["resultados"]["concentracao"]
        
        print(f"Status: {conc['status_geral']}")
        print(f"PL do pool: R$ {conc['pl_pool']:,.2f}")
        
        # Resumo de limites
        resumo = conc.get('resumo', {})
        print(f"Limites analisados: {resumo.get('total_limites_analisados', 0)}")
        print(f"Limites violados: {resumo.get('limites_violados', 0)}")
        
    return resultado

if __name__ == "__main__":
    df = exemplo_basico()['resultados']
    df_2 = exemplo_pool_especifico()
    df_3 = exemplo_dados_detalhados()
    
    print("\n" + "="*50)
    print("🚀 PRONTO PARA USAR NO SPYDER!")
    print("import orchestrator")
    print("resultado = orchestrator.run_monitoring()")
    print("="*50)