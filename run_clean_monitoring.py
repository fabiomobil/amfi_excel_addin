#!/usr/bin/env python3
"""
AmFi Clean Monitoring System
============================

Sistema de monitoramento limpo após a limpeza completa.
Use este arquivo como ponto de entrada principal.
"""

import os
import sys
from datetime import datetime

def run_amfi_monitoring(pool_name=None):
    """
    Execute o sistema de monitoramento AmFi limpo.
    
    Args:
        pool_name (str, optional): Nome do pool específico para processar
        
    Returns:
        dict: Resultados do monitoramento
    """
    
    print("🎯 SISTEMA DE MONITORAMENTO AMFI - VERSÃO LIMPA")
    print("=" * 60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if pool_name:
        print(f"Pool específico: {pool_name}")
    else:
        print("Modo: Todos os pools")
    
    print()
    
    try:
        # Import do sistema limpo
        from monitor.orchestrator import run_monitoring
        
        print("✅ Sistema de monitoramento carregado")
        print("🔄 Iniciando execução...")
        print()
        
        # Executar monitoramento
        resultado = run_monitoring(pool_name)
        
        print("✅ MONITORAMENTO CONCLUÍDO")
        print("=" * 60)
        
        # Mostrar resultados resumidos
        if resultado.get("sucesso"):
            stats = resultado["estatisticas"]
            print(f"📊 Pools processados: {stats['total']}")
            print(f"✅ Sucessos: {stats['sucesso']}")
            print(f"❌ Erros: {stats['erro']}")
            print(f"📈 Taxa de sucesso: {stats['taxa_sucesso']}%")
            
            print("\n📋 RESULTADOS POR POOL:")
            for pool_name, pool_result in resultado["resultados"].items():
                print(f"\n🏦 {pool_name}:")
                print(f"   Status: {'✅' if pool_result.get('sucesso') else '❌'}")
                
                monitores = pool_result.get('monitores_executados', [])
                print(f"   Monitores: {', '.join(monitores)}")
                
                # Mostrar alguns resultados específicos
                resultados = pool_result.get('resultados', {})
                
                if 'subordinacao' in resultados:
                    sub_result = resultados['subordinacao']
                    if 'subordination_ratio_percent' in sub_result:
                        ratio = sub_result['subordination_ratio_percent']
                        status = sub_result.get('status_limite_minimo', 'N/A')
                        print(f"   📈 Subordinação: {ratio}% ({status})")
                
                if 'inadimplencia' in resultados:
                    print(f"   🔍 Inadimplência: Processada com enriquecimento")
                
                if 'pdd' in resultados:
                    print(f"   💰 PDD: Calculado usando dados enriquecidos")
                
                if 'concentracao' in resultados:
                    conc_result = resultados['concentracao']
                    status = conc_result.get('status_geral', 'N/A')
                    print(f"   🎯 Concentração: {status}")
        
        else:
            print(f"❌ Falha no monitoramento: {resultado.get('erro', 'Erro desconhecido')}")
        
        return resultado
        
    except Exception as e:
        print(f"❌ ERRO NA EXECUÇÃO: {e}")
        print()
        print("🔧 DIAGNÓSTICO:")
        print("- Verifique se está no diretório correto (/mnt/c/amfi/)")
        print("- Verifique se o sistema foi limpo corretamente")
        print("- Execute test_cleaned_system.py para validação")
        
        import traceback
        print("\n📝 DETALHES DO ERRO:")
        traceback.print_exc()
        
        return {"sucesso": False, "erro": str(e)}


def test_escritura_detection():
    """Testa o sistema de detecção de escritura."""
    
    print("🔍 TESTE DE DETECÇÃO DE ESCRITURA")
    print("=" * 40)
    
    try:
        from monitor.utils.escritura_detector import analyze_all_pools
        
        print("🔄 Analisando todos os pools...")
        resultados = analyze_all_pools()
        
        print(f"✅ {len(resultados)} pools analisados")
        print()
        
        for filename, analysis in resultados.items():
            pool_name = filename.replace('.json', '')
            print(f"🏦 {pool_name}:")
            print(f"   Tipo: {analysis.primary_type.replace('_', ' ').title()}")
            print(f"   Confiança: {analysis.confidence_score:.1%}")
            print(f"   Complexidade: {analysis.complexity_level}")
            
            if analysis.recommendations:
                print(f"   Recomendação: {analysis.recommendations[0][:50]}...")
            print()
        
        return resultados
        
    except Exception as e:
        print(f"❌ Erro na detecção: {e}")
        return {}


def show_template_system():
    """Mostra o sistema de templates disponível."""
    
    print("📋 SISTEMA DE TEMPLATES")
    print("=" * 30)
    
    try:
        import os
        import glob
        
        # Listar templates disponíveis
        templates_dir = "config/templates"
        
        if os.path.exists(templates_dir):
            tier1_templates = glob.glob(f"{templates_dir}/tier1/*.json")
            tier2_templates = glob.glob(f"{templates_dir}/tier2/*.json")
            
            print("📁 Templates Tier 1 (Base Universal):")
            for template in tier1_templates:
                name = os.path.basename(template)
                print(f"   - {name}")
            
            print("\n📁 Templates Tier 2 (Por Escritura):")
            for template in tier2_templates:
                name = os.path.basename(template)
                escritura = name.replace('.json', '').replace('_', ' ').title()
                print(f"   - {escritura}")
            
            print(f"\n✅ Sistema de templates operacional")
            print("💡 Use template_engine.py para criar novos pools")
            
        else:
            print("⚠️ Diretório de templates não encontrado")
            
    except Exception as e:
        print(f"❌ Erro no sistema de templates: {e}")


def main():
    """Função principal com menu interativo."""
    
    print("🚀 AMFI CLEAN MONITORING SYSTEM")
    print("=" * 50)
    print("Sistema limpo e otimizado - Versão 2.0")
    print()
    
    while True:
        print("📋 OPÇÕES DISPONÍVEIS:")
        print("1. Executar monitoramento completo")
        print("2. Executar monitoramento de pool específico")
        print("3. Testar detecção de escritura")
        print("4. Mostrar sistema de templates")
        print("5. Validar sistema limpo")
        print("0. Sair")
        print()
        
        try:
            opcao = input("Escolha uma opção (0-5): ").strip()
            
            if opcao == "0":
                print("👋 Até logo!")
                break
                
            elif opcao == "1":
                print()
                run_amfi_monitoring()
                
            elif opcao == "2":
                print()
                pool_name = input("Digite o nome do pool: ").strip()
                if pool_name:
                    run_amfi_monitoring(pool_name)
                else:
                    print("❌ Nome do pool não pode estar vazio")
                
            elif opcao == "3":
                print()
                test_escritura_detection()
                
            elif opcao == "4":
                print()
                show_template_system()
                
            elif opcao == "5":
                print()
                os.system("python3 test_cleaned_system.py")
                
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Interrompido pelo usuário")
            break
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    # Garante que está no diretório correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    main()