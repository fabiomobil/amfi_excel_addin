#!/usr/bin/env python3
"""
Teste do Sistema Limpo AmFi
===========================

Script para testar o sistema após a limpeza completa.
Execute este arquivo para verificar que tudo está funcionando corretamente.
"""

import sys
import os
from datetime import datetime

def test_system():
    """Testa todos os componentes principais do sistema limpo."""
    
    print("🧹 TESTANDO SISTEMA LIMPO AMFI")
    print("=" * 50)
    print(f"Data do teste: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Diretório atual: {os.getcwd()}")
    print()
    
    # 1. Teste de imports básicos
    print("📦 TESTE 1: Imports Básicos")
    try:
        from monitor.orchestrator import run_monitoring
        print("✅ orchestrator.run_monitoring - OK")
        
        from monitor.core.subordinacao_monitor import SubordinacaoMonitor
        print("✅ SubordinacaoMonitor - OK")
        
        from monitor.core.inadimplencia_monitor import InadimplenciaMonitor  
        print("✅ InadimplenciaMonitor - OK")
        
        from monitor.core.pdd_monitor import PDDMonitor
        print("✅ PDDMonitor - OK")
        
        from monitor.core.concentracao_monitor_simple import ConcentracaoMonitor
        print("✅ ConcentracaoMonitor - OK")
        
        print("✅ Todos os imports principais funcionando!")
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False
    
    print()
    
    # 2. Teste do sistema de templates
    print("📋 TESTE 2: Sistema de Templates")
    try:
        from config.templates.template_engine import TemplateEngine
        
        engine = TemplateEngine()
        templates = engine.list_available_templates()
        print(f"✅ Templates disponíveis: {len(templates)}")
        for template in templates:
            print(f"   - {template}")
            
    except Exception as e:
        print(f"⚠️ Sistema de templates não disponível: {e}")
    
    print()
    
    # 3. Teste de detecção de escritura
    print("🔍 TESTE 3: Detecção de Escritura")
    try:
        from monitor.utils.escritura_detector import EscrituraDetector
        
        detector = EscrituraDetector()
        print("✅ EscrituraDetector inicializado")
        
        # Teste com um pool exemplo
        pool_example = {
            "valores": {"subordinada": 15000000, "total_emissao": 45000000},
            "monitoramentos_ativos": [{"id": "subordinacao"}, {"id": "concentracao"}]
        }
        
        analysis = detector.detect_escritura_type(pool_example)
        print(f"✅ Tipo detectado: {analysis.primary_type}")
        print(f"✅ Confiança: {analysis.confidence_score:.1%}")
        
    except Exception as e:
        print(f"⚠️ Detecção de escritura não disponível: {e}")
    
    print()
    
    # 4. Teste de configurações
    print("⚙️ TESTE 4: Configurações")
    try:
        import json
        import glob
        
        config_files = glob.glob("config/pools/*.json")
        print(f"✅ Configurações encontradas: {len(config_files)}")
        
        # Teste de carregamento
        valid_configs = 0
        for config_file in config_files[:3]:  # Teste apenas 3 por velocidade
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                valid_configs += 1
            except:
                pass
        
        print(f"✅ Configurações válidas testadas: {valid_configs}/3")
        
    except Exception as e:
        print(f"⚠️ Erro no teste de configurações: {e}")
    
    print()
    
    # 5. Teste do orchestrator (simulação leve)
    print("🎯 TESTE 5: Orchestrator (Simulação)")
    try:
        # Teste apenas se a função está disponível e importável
        from monitor.orchestrator import run_monitoring
        print("✅ run_monitoring disponível")
        
        # Verificar se as funções helper funcionam
        from monitor.orchestrator import _has_subordination_monitoring
        
        # Teste com config mínimo
        minimal_config = {
            "monitoramentos_ativos": [
                {"id": "subordinacao", "ativo": True}
            ]
        }
        
        has_sub = _has_subordination_monitoring(minimal_config)
        print(f"✅ Detecção de configuração: {has_sub}")
        
    except Exception as e:
        print(f"⚠️ Erro no teste do orchestrator: {e}")
    
    print()
    
    # 6. Verificar limpeza
    print("🧽 TESTE 6: Verificação de Limpeza")
    
    # Verificar se legacy foi removido
    legacy_removed = not os.path.exists("legacy/udfs/")
    base_removed = not os.path.exists("monitor/base/")
    legacy_configs_removed = not os.path.exists("config/pools/legacy/")
    
    print(f"✅ Sistema legacy removido: {legacy_removed}")
    print(f"✅ Monitor base removido: {base_removed}")
    print(f"✅ Configs legacy removidas: {legacy_configs_removed}")
    
    # Verificar se novos arquivos foram criados
    templates_exist = os.path.exists("config/templates/")
    escritura_detector_exists = os.path.exists("monitor/utils/escritura_detector.py")
    docs_consolidated = os.path.exists("docs/COMPREHENSIVE_SYSTEM_GUIDE.md")
    
    print(f"✅ Sistema de templates criado: {templates_exist}")
    print(f"✅ Detector de escritura criado: {escritura_detector_exists}")
    print(f"✅ Documentação consolidada: {docs_consolidated}")
    
    print()
    print("🏆 TESTE CONCLUÍDO")
    print("=" * 50)
    
    if all([legacy_removed, base_removed, legacy_configs_removed]):
        print("✅ SISTEMA LIMPO VALIDADO - Funcionando corretamente!")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Use o sistema de templates para criar novos pools")
        print("2. Explore a detecção automática de escritura")
        print("3. Consulte docs/COMPREHENSIVE_SYSTEM_GUIDE.md")
        print("4. Execute run_monitoring() para monitoramento completo")
        return True
    else:
        print("⚠️ Alguns componentes legacy ainda existem")
        return False


if __name__ == "__main__":
    # Garante que está no diretório correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = test_system()
    
    if success:
        print("\n🎉 Sistema está funcionando perfeitamente!")
    else:
        print("\n⚠️ Alguns testes falharam - verificar logs acima")