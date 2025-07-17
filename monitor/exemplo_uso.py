#!/usr/bin/env python3
"""
Exemplo de uso do sistema de monitoramento AmFi - Arquitetura OOP
=================================================================

Este arquivo demonstra como usar o sistema refatorado no Spyder/IPython.
"""

# Importar o sistema
import orchestrator

def exemplo_basico():
    """Exemplo básico de uso do sistema"""
    print("🎯 EXEMPLO DE USO - SISTEMA DE MONITORAMENTO AMFI")
    print("=" * 60)
    
    # 1. Executar monitoramento para todos os pools
    print("1. Executando monitoramento para todos os pools...")
    resultado = orchestrator.run_monitoring()
    
    if resultado.get("sucesso"):
        # Mostrar estatísticas gerais
        stats = resultado["estatisticas"]
        print(f"✅ Monitoramento concluído:")
        print(f"   📊 Total de pools: {stats['total']}")
        print(f"   ✅ Sucesso: {stats['sucesso']}")
        print(f"   ❌ Erro: {stats['erro']}")
        print(f"   📈 Taxa de sucesso: {stats['taxa_sucesso']}%")
        
        # Mostrar resultados por pool
        print(f"\n📋 RESULTADOS POR POOL:")
        for pool_name, pool_result in resultado["resultados"].items():
            print(f"\n🏦 {pool_name}:")
            print(f"   ✅ Sucesso: {pool_result.get('sucesso', 'N/A')}")
            print(f"   📊 Monitores executados: {pool_result.get('monitores_executados', [])}")
            
            # Mostrar resultados de subordinação
            if 'subordinacao' in pool_result.get('resultados', {}):
                sub_result = pool_result['resultados']['subordinacao']
                if 'subordination_ratio_percent' in sub_result:
                    sr = sub_result['subordination_ratio_percent']
                    status = sub_result.get('status_limite_minimo', 'N/A')
                    print(f"   📈 Subordinação: {sr}% ({status})")
            
            # Mostrar resultados de inadimplência
            if 'inadimplencia' in pool_result.get('resultados', {}):
                inad_result = pool_result['resultados']['inadimplencia']
                print(f"   🔍 Inadimplência:")
                
                # Procurar por janelas (inadimplencia_30d, inadimplencia_90d, etc.)
                janelas_found = []
                for key, value in inad_result.items():
                    if key.startswith('inadimplencia_') and isinstance(value, dict):
                        if 'percentual' in value:
                            janela = key.replace('inadimplencia_', '').replace('d', ' dias')
                            perc = value['percentual']
                            limite = value.get('limite', 0)
                            status = value.get('status', 'N/A')
                            print(f"     - {janela}: {perc}% (limite: {limite}% | {status})")
                            janelas_found.append(key)
                
                if not janelas_found:
                    print("     - Nenhuma janela de inadimplência encontrada")
            
            # Mostrar resultados de PDD
            if 'pdd' in pool_result.get('resultados', {}):
                pdd_result = pool_result['resultados']['pdd']
                print(f"   💰 PDD (Provisão para Devedores Duvidosos):")
                if 'pdd_analysis' in pdd_result and 'totais' in pdd_result['pdd_analysis']:
                    totais = pdd_result['pdd_analysis']['totais']
                    valor = totais.get('provisao_valor', 0)
                    perc = totais.get('provisao_percentual', 0)
                    print(f"     - Total: R$ {valor:,.2f} ({perc}% da carteira)")
                else:
                    print("     - Dados de PDD não disponíveis")
        
        # Mostrar informações sobre enriquecimento
        print(f"\n🔄 ENRIQUECIMENTO PROGRESSIVO:")
        xlsx_enriched = resultado['xlsx_enriched']
        if 'dias_atraso' in xlsx_enriched.columns:
            print(f"   ✅ Campo 'dias_atraso' adicionado ao XLSX global")
        if 'grupo_de_risco' in xlsx_enriched.columns:
            print(f"   ✅ Campo 'grupo_de_risco' adicionado ao XLSX global")
        print(f"   📊 Total de registros enriquecidos: {len(xlsx_enriched):,}")
        
    else:
        print(f"❌ Erro no monitoramento: {resultado.get('erro', 'Desconhecido')}")
    
    print("\n" + "=" * 60)
    return resultado

def exemplo_pool_especifico():
    """Exemplo de monitoramento para um pool específico"""
    print("\n🎯 EXEMPLO - POOL ESPECÍFICO")
    print("-" * 40)
    
    # Executar para um pool específico
    pool_name = "AFA Pool #1"
    print(f"Executando monitoramento para pool: {pool_name}")
    
    resultado = orchestrator.run_monitoring(pool_name)
    
    if resultado.get("sucesso"):
        pool_result = resultado["resultados"][pool_name]
        print(f"✅ Pool processado com sucesso")
        print(f"📊 Monitores executados: {pool_result.get('monitores_executados', [])}")
    else:
        print(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")
    
    return resultado

if __name__ == "__main__":
    # Executar exemplos
    resultado_geral = exemplo_basico()
    resultado_especifico = exemplo_pool_especifico()
    
    print("\n🎉 EXEMPLOS CONCLUÍDOS!")
    print("Para usar no Spyder/IPython:")
    print("1. Importe: import orchestrator")
    print("2. Execute: resultado = orchestrator.run_monitoring()")
    print("3. Analise os resultados conforme mostrado acima")