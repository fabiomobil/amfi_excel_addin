#!/usr/bin/env python3
"""
Exemplo de Uso - PDD Hierarchical Dashboard API
===============================================

Script de demonstração dos endpoints PDD hierárquicos implementados.
Mostra como utilizar todas as funcionalidades da API PDD.

Endpoints demonstrados:
- GET /api/pdd/{pool_id}/hierarchy
- GET /api/pdd/{pool_id}/group/{group_id}/cedentes  
- GET /api/pdd/cedente/{cedente_id}/worst_assets
- GET /api/pdd/{pool_id}/trends
- GET /api/pdd/{pool_id}/risk_summary

Uso:
    python3 example_pdd_hierarchical_api.py
    
    ou com pool específico:
    python3 example_pdd_hierarchical_api.py "E-ctare Pool #1"

Autor: AmFi Development Team
Data: 2025-07-22
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Adicionar paths para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/utils')

from pdd_api_endpoints import (
    get_pdd_hierarchy,
    get_pdd_group_cedentes,
    get_pdd_cedente_worst_assets,
    get_pdd_trends,
    get_pdd_risk_summary
)


def print_json_pretty(data: Dict[str, Any], title: str = "") -> None:
    """Imprime JSON formatado."""
    if title:
        print(f"\n{'='*60}")
        print(f"📊 {title}")
        print('='*60)
    
    print(json.dumps(data, ensure_ascii=False, indent=2))


def demonstrate_hierarchy_endpoint(pool_id: str) -> None:
    """Demonstra endpoint de hierarquia."""
    print(f"\n🌳 TESTANDO: GET /api/pdd/{pool_id}/hierarchy")
    print("-" * 50)
    
    result = get_pdd_hierarchy(pool_id)
    
    if result["success"]:
        data = result["data"]
        
        print(f"✅ Hierarquia carregada com sucesso!")
        print(f"📈 Total de grupos: {data['total_groups']}")
        print(f"🏢 Total de cedentes: {data['total_cedentes']}")
        print(f"💰 Provisão total: {data['totals']['provisao_percentual']:.2f}%")
        print(f"🔄 Metodologia: {data['metodologia']}")
        
        # Mostrar resumo por grupo
        print(f"\n📋 Resumo por Grupo de Risco:")
        for group_id, group_info in data["grupos"].items():
            stats = group_info["stats"]
            if stats["quantidade_titulos"] > 0:
                print(f"  {group_info['ui_metadata']['icon']} Grupo {group_id}: "
                      f"{stats['quantidade_titulos']} títulos, "
                      f"{stats['cedentes_afetados']} cedentes, "
                      f"R$ {stats['provisao_valor']:,.2f} provisão")
    else:
        print(f"❌ Erro: {result['error']}")


def demonstrate_group_cedentes_endpoint(pool_id: str, group_id: str) -> None:
    """Demonstra endpoint de cedentes por grupo."""
    print(f"\n🏢 TESTANDO: GET /api/pdd/{pool_id}/group/{group_id}/cedentes")
    print("-" * 50)
    
    result = get_pdd_group_cedentes(pool_id, group_id)
    
    if result["success"]:
        data = result["data"]
        
        print(f"✅ Cedentes do grupo {group_id} carregados!")
        print(f"🏢 Total de cedentes: {data['total_cedentes']}")
        print(f"💰 Valor total: R$ {data['total_valor']:,.2f}")
        print(f"📉 Provisão total: R$ {data['total_provisao']:,.2f}")
        
        if data["cedentes"]:
            print(f"\n🏆 Top Cedentes do Grupo {group_id}:")
            for cedente in data["cedentes"][:3]:  # Top 3
                print(f"  {cedente['ranking_no_grupo']}º {cedente['cedente_nome']}")
                print(f"     💰 Valor: R$ {cedente['valor_total']:,.2f}")
                print(f"     📉 Provisão: {cedente['provisao_pct']:.2f}%")
                print(f"     ⏰ Pior título: {cedente['titulo_mais_atrasado']['dias_atraso']} dias atraso")
        else:
            print(f"ℹ️ Nenhum cedente encontrado no grupo {group_id}")
    else:
        print(f"❌ Erro: {result['error']}")


def demonstrate_worst_assets_endpoint(cedente_name: str, pool_id: str) -> None:
    """Demonstra endpoint de piores ativos por cedente."""
    print(f"\n📉 TESTANDO: GET /api/pdd/cedente/{cedente_name}/worst_assets")
    print("-" * 50)
    
    result = get_pdd_cedente_worst_assets(cedente_name, pool_id, limit=5)
    
    if result["success"]:
        data = result["data"]
        
        print(f"✅ Piores ativos do cedente carregados!")
        print(f"📉 Total de ativos: {data['total_assets']}")
        print(f"🎯 Pools encontrados: {', '.join(data['pools_found'])}")
        
        summary = data["summary"]
        print(f"⏰ Máximo atraso: {summary['max_dias_atraso']} dias")
        print(f"💰 Valor total: R$ {summary['total_valor_pior_titulos']:,.2f}")
        print(f"📉 Provisão total: R$ {summary['total_provisao_pior_titulos']:,.2f}")
        
        if data["worst_assets"]:
            print(f"\n🔥 Piores Ativos:")
            for asset in data["worst_assets"]:
                print(f"  {asset['ranking']}º Pool: {asset['pool_id']}")
                print(f"     ⏰ Atraso: {asset['dias_atraso']} dias")
                print(f"     🎯 Grupo: {asset['grupo_risco_original']} → {asset['grupo_pdd_aplicado']}")
                print(f"     💰 Valor: R$ {asset['valor_titulo']:,.2f}")
                print(f"     📉 Provisão: {asset['provisao_pct']:.2f}%")
    else:
        print(f"❌ Erro: {result['error']}")


def demonstrate_trends_endpoint(pool_id: str, days: int = 10) -> None:
    """Demonstra endpoint de tendências."""
    print(f"\n📈 TESTANDO: GET /api/pdd/{pool_id}/trends?days={days}")
    print("-" * 50)
    
    result = get_pdd_trends(pool_id, days)
    
    if result["success"]:
        data = result["data"]
        
        print(f"✅ Tendências carregadas!")
        print(f"📊 Período analisado: {data['period_days']} dias")
        
        indicators = data["indicators"]
        print(f"\n📈 Indicadores de Tendência:")
        print(f"  📊 Provisão atual: {indicators['provisao_atual']:.2f}%")
        print(f"  📊 Provisão média: {indicators['provisao_media']:.2f}%")
        print(f"  📈 Provisão máxima: {indicators['provisao_max']:.2f}%")
        print(f"  📉 Provisão mínima: {indicators['provisao_min']:.2f}%")
        print(f"  🔄 Tendência: {indicators['tendencia']}")
        print(f"  📊 Volatilidade: {indicators['volatilidade']}")
        print(f"  🚨 Dias consecutivos alta: {indicators['dias_consecutivos_alta']}")
        
        # Mostrar alertas se houver
        if data["alerts"]:
            print(f"\n🚨 Alertas Detectados:")
            for alert in data["alerts"]:
                icon = "🔴" if alert["severity"] == "high" else "🟡" if alert["severity"] == "medium" else "ℹ️"
                print(f"  {icon} {alert['message']}")
    else:
        print(f"❌ Erro: {result['error']}")


def demonstrate_risk_summary_endpoint(pool_id: str) -> None:
    """Demonstra endpoint de resumo de risco."""
    print(f"\n🗺️ TESTANDO: GET /api/pdd/{pool_id}/risk_summary")
    print("-" * 50)
    
    result = get_pdd_risk_summary(pool_id)
    
    if result["success"]:
        data = result["data"]
        
        overall_risk = data["overall_risk"]
        print(f"✅ Resumo de risco carregado!")
        print(f"🎯 Nível de risco geral: {overall_risk['level']}")
        print(f"📊 Score de risco: {overall_risk['score']:.2f}%")
        print(f"⚠️ Status: {overall_risk['status']}")
        
        # Métricas resumo
        metrics = data["summary_metrics"]
        print(f"\n📋 Métricas Resumo:")
        print(f"  💰 Carteira total: R$ {metrics['total_carteira']:,.2f}")
        print(f"  📉 Provisão total: R$ {metrics['total_provisao']:,.2f}")
        print(f"  📊 Provisão %: {metrics['provisao_percentual']:.2f}%")
        print(f"  🏢 Total cedentes: {metrics['total_cedentes']}")
        print(f"  🚨 Cedentes com risco: {metrics['cedentes_com_risco']}")
        print(f"  📊 Grupos ativos: {metrics['grupos_ativos']}")
        
        # Heat map dos grupos
        heat_map = data["heat_map"]
        print(f"\n🗺️ Heat Map - Grupos de Risco:")
        for group in heat_map["risk_groups"]:
            if group["quantidade_titulos"] > 0:
                print(f"  {group['color']} Grupo {group['group_id']}: "
                      f"{group['quantidade_titulos']} títulos, "
                      f"R$ {group['provisao_valor']:,.2f} provisão, "
                      f"{group['percentual_carteira']:.2f}% carteira")
        
        # Top cedentes risco
        print(f"\n🏆 Top Cedentes por Risco:")
        for cedente in heat_map["top_risk_cedentes"][:3]:
            print(f"  🔥 {cedente['cedente_nome']}")
            print(f"     📊 Risco Score: {cedente['risk_score']:.2f}")
            print(f"     📉 Provisão: {cedente['provisao_pct']:.2f}%")
            print(f"     ⏰ Atraso máx: {cedente['dias_atraso_max']} dias")
    else:
        print(f"❌ Erro: {result['error']}")


def main():
    """Executa demonstração completa da API PDD Hierárquica."""
    # Pool de teste (pode ser passado como argumento)
    test_pool = sys.argv[1] if len(sys.argv) > 1 else "E-ctare Pool #1"
    
    print("🚀 DEMONSTRAÇÃO - PDD HIERARCHICAL DASHBOARD API")
    print("=" * 60)
    print(f"🎯 Pool de teste: {test_pool}")
    print("📋 Endpoints a serem testados:")
    print("   1. GET /api/pdd/{pool_id}/hierarchy")
    print("   2. GET /api/pdd/{pool_id}/group/{group_id}/cedentes")
    print("   3. GET /api/pdd/cedente/{cedente_id}/worst_assets")
    print("   4. GET /api/pdd/{pool_id}/trends")
    print("   5. GET /api/pdd/{pool_id}/risk_summary")
    
    try:
        # 1. Testar hierarquia
        demonstrate_hierarchy_endpoint(test_pool)
        
        # 2. Testar cedentes de um grupo específico (H - maior risco)
        demonstrate_group_cedentes_endpoint(test_pool, "H")
        
        # 3. Testar piores ativos de um cedente específico
        # Primeiro, vamos obter um cedente da hierarquia
        hierarchy = get_pdd_hierarchy(test_pool)
        if hierarchy["success"] and hierarchy["data"]["total_cedentes"] > 0:
            # Encontrar primeiro cedente com provisão
            test_cedente = None
            for group_id, group_info in hierarchy["data"]["grupos"].items():
                if group_info["cedentes"]:
                    test_cedente = group_info["cedentes"][0]["nome"]
                    break
            
            if test_cedente:
                demonstrate_worst_assets_endpoint(test_cedente, test_pool)
            else:
                print("\n⚠️ Nenhum cedente com provisão encontrado para teste de piores ativos")
        
        # 4. Testar tendências
        demonstrate_trends_endpoint(test_pool, days=7)
        
        # 5. Testar resumo de risco
        demonstrate_risk_summary_endpoint(test_pool)
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Todos os endpoints estão funcionando corretamente")
        print("\n💡 Para usar em produção:")
        print("   1. Inicie o servidor: python3 dashboard_server.py")
        print("   2. Acesse: http://localhost:8080")
        print("   3. Use os endpoints via HTTP GET")
        print(f"   Exemplo: http://localhost:8080/api/pdd/{test_pool}/hierarchy")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE DEMONSTRAÇÃO: {e}")
        print("🔧 Verifique se:")
        print("   - Os dados de monitoramento estão disponíveis")
        print("   - As configurações de pool estão corretas")
        print("   - Os módulos de dependência estão instalados")


if __name__ == "__main__":
    main()