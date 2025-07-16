#!/usr/bin/env python3
"""
Validação completa com dados reais - Building Block 8
"""

import sys
import os
import json

# Adicionar caminhos
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

from orchestrator import run_monitoring

def validate_afa_pool_concentration():
    """
    Validação detalhada do AFA Pool #1
    
    Limites esperados:
    - Individual sacado: 27% (com grupo econômico)
    - Individual cedente: 30% (com grupo econômico)
    - Top 10 sacados: 100% (com grupo econômico)
    - Top 10 cedentes: 70% (com grupo econômico)
    """
    print("=== Validação AFA Pool #1 - Concentração Real ===")
    
    # Executar monitoramento
    resultado = run_monitoring("AFA Pool #1")
    
    if not resultado.get('sucesso', False):
        print("❌ Falha no monitoramento geral")
        return False
    
    if "AFA Pool #1" not in resultado.get('resultados', {}):
        print("❌ Pool AFA Pool #1 não encontrado")
        return False
    
    pool_result = resultado['resultados']['AFA Pool #1']
    
    if 'concentracao' not in pool_result.get('resultados', {}):
        print("❌ Monitor de concentração não executado")
        return False
    
    conc_result = pool_result['resultados']['concentracao']
    
    # Validações básicas
    assert conc_result['sucesso'] == True, "Monitor deve ter sucesso"
    assert conc_result['pool_id'] == "AFA Pool #1", "Pool ID deve estar correto"
    assert conc_result['configuracao']['ativo'] == True, "Configuração deve estar ativa"
    assert conc_result['configuracao']['complexidade'] == "alta", "Complexidade deve ser alta"
    assert conc_result['configuracao']['numero_limites'] == 4, "Deve ter 4 limites"
    
    # Validar PL
    assert conc_result['pl_pool'] > 0, "PL deve ser maior que zero"
    
    # Validar resultados por limite
    resultados_limites = conc_result['resultados_por_limite']
    assert len(resultados_limites) == 4, "Deve ter 4 resultados de limite"
    
    # Validar estrutura de cada limite
    for i, limite in enumerate(resultados_limites):
        assert 'limite_id' in limite, f"Limite {i+1} deve ter ID"
        assert 'tipo' in limite, f"Limite {i+1} deve ter tipo"
        assert 'entidade' in limite, f"Limite {i+1} deve ter entidade"
        assert 'status' in limite, f"Limite {i+1} deve ter status"
        assert 'limite_configurado' in limite, f"Limite {i+1} deve ter limite configurado"
        
        # Verificar se status é válido
        assert limite['status'] in ['enquadrado', 'violado', 'erro'], f"Status inválido no limite {i+1}"
    
    # Validar limites específicos
    limites_por_descricao = {}
    for limite in resultados_limites:
        descricao = f"{limite['tipo']}_{limite['entidade']}"
        limites_por_descricao[descricao] = limite
    
    # Verificar individual sacado (27%)
    if 'individual_sacado' in limites_por_descricao:
        limite_sacado = limites_por_descricao['individual_sacado']
        assert limite_sacado['limite_configurado'] == 27.0, "Limite sacado deve ser 27%"
        assert limite_sacado['inclui_grupo_economico'] == True, "Deve incluir grupo econômico"
        print(f"✅ Individual sacado: {limite_sacado['status']} ({limite_sacado['maior_concentracao']['percentual_pl']:.1f}%)")
    
    # Verificar individual cedente (30%)
    if 'individual_cedente' in limites_por_descricao:
        limite_cedente = limites_por_descricao['individual_cedente']
        assert limite_cedente['limite_configurado'] == 30.0, "Limite cedente deve ser 30%"
        assert limite_cedente['inclui_grupo_economico'] == True, "Deve incluir grupo econômico"
        print(f"✅ Individual cedente: {limite_cedente['status']} ({limite_cedente['maior_concentracao']['percentual_pl']:.1f}%)")
    
    # Verificar top 10 sacados (100%)
    if 'top_n_sacado' in limites_por_descricao:
        limite_top_sacado = limites_por_descricao['top_n_sacado']
        assert limite_top_sacado['limite_configurado'] == 100.0, "Limite top sacado deve ser 100%"
        assert limite_top_sacado['n'] == 10, "Deve ser top 10"
        print(f"✅ Top 10 sacados: {limite_top_sacado['status']} ({limite_top_sacado['concentracao_top_n']['percentual_pl']:.1f}%)")
    
    # Verificar top 10 cedentes (70%)
    if 'top_n_cedente' in limites_por_descricao:
        limite_top_cedente = limites_por_descricao['top_n_cedente']
        assert limite_top_cedente['limite_configurado'] == 70.0, "Limite top cedente deve ser 70%"
        assert limite_top_cedente['n'] == 10, "Deve ser top 10"
        print(f"✅ Top 10 cedentes: {limite_top_cedente['status']} ({limite_top_cedente['concentracao_top_n']['percentual_pl']:.1f}%)")
    
    # Validar resumo
    resumo = conc_result['resumo']
    assert resumo['total_limites_analisados'] == 4, "Deve ter analisado 4 limites"
    assert resumo['limites_enquadrados'] + resumo['limites_violados'] == 4, "Soma deve ser 4"
    
    print(f"✅ Resumo: {resumo['limites_enquadrados']} enquadrados, {resumo['limites_violados']} violados")
    print(f"✅ Status geral: {conc_result['status_geral']}")
    
    return True

def validate_lecapital_pool_concentration():
    """
    Validação detalhada do LeCapital Pool #1
    
    Limites esperados:
    - Individual sacado: 35% (com grupo econômico)
    - Individual cedente: 50% (com grupo econômico)
    - Top 10 sacados: 100% (com grupo econômico)
    - Top 10 cedentes: 70% (com grupo econômico)
    """
    print("\n=== Validação LeCapital Pool #1 - Concentração Real ===")
    
    # Executar monitoramento
    resultado = run_monitoring("LeCapital Pool #1")
    
    if not resultado.get('sucesso', False):
        print("❌ Falha no monitoramento geral")
        return False
    
    if "LeCapital Pool #1" not in resultado.get('resultados', {}):
        print("❌ Pool LeCapital Pool #1 não encontrado")
        return False
    
    pool_result = resultado['resultados']['LeCapital Pool #1']
    
    if 'concentracao' not in pool_result.get('resultados', {}):
        print("❌ Monitor de concentração não executado")
        return False
    
    conc_result = pool_result['resultados']['concentracao']
    
    # Validações básicas
    assert conc_result['sucesso'] == True, "Monitor deve ter sucesso"
    assert conc_result['pool_id'] == "LeCapital Pool #1", "Pool ID deve estar correto"
    assert conc_result['configuracao']['ativo'] == True, "Configuração deve estar ativa"
    assert conc_result['configuracao']['complexidade'] == "alta", "Complexidade deve ser alta"
    assert conc_result['configuracao']['numero_limites'] == 4, "Deve ter 4 limites"
    
    # Validar resultados por limite
    resultados_limites = conc_result['resultados_por_limite']
    assert len(resultados_limites) == 4, "Deve ter 4 resultados de limite"
    
    # Validar limites específicos
    limites_por_descricao = {}
    for limite in resultados_limites:
        descricao = f"{limite['tipo']}_{limite['entidade']}"
        limites_por_descricao[descricao] = limite
    
    # Verificar individual sacado (35%)
    if 'individual_sacado' in limites_por_descricao:
        limite_sacado = limites_por_descricao['individual_sacado']
        assert limite_sacado['limite_configurado'] == 35.0, "Limite sacado deve ser 35%"
        print(f"✅ Individual sacado: {limite_sacado['status']} ({limite_sacado['maior_concentracao']['percentual_pl']:.1f}%)")
    
    # Verificar individual cedente (50%)
    if 'individual_cedente' in limites_por_descricao:
        limite_cedente = limites_por_descricao['individual_cedente']
        assert limite_cedente['limite_configurado'] == 50.0, "Limite cedente deve ser 50%"
        print(f"✅ Individual cedente: {limite_cedente['status']} ({limite_cedente['maior_concentracao']['percentual_pl']:.1f}%)")
    
    # Validar resumo
    resumo = conc_result['resumo']
    print(f"✅ Resumo: {resumo['limites_enquadrados']} enquadrados, {resumo['limites_violados']} violados")
    print(f"✅ Status geral: {conc_result['status_geral']}")
    
    return True

def validate_upvendas_pool_no_concentration():
    """
    Validação do Up Vendas Pool #2 (sem concentração)
    """
    print("\n=== Validação Up Vendas Pool #2 - Sem Concentração ===")
    
    # Executar monitoramento
    resultado = run_monitoring("Up Vendas Pool #2")
    
    if not resultado.get('sucesso', False):
        print("❌ Falha no monitoramento geral")
        return False
    
    if "Up Vendas Pool #2" not in resultado.get('resultados', {}):
        print("❌ Pool Up Vendas Pool #2 não encontrado")
        return False
    
    pool_result = resultado['resultados']['Up Vendas Pool #2']
    
    # Verificar que monitor de concentração NÃO foi executado
    if 'concentracao' in pool_result.get('resultados', {}):
        print("⚠️ Monitor de concentração foi executado (inesperado)")
        conc_result = pool_result['resultados']['concentracao']
        assert conc_result['status_geral'] == "sem_limites", "Status deve ser sem_limites"
        print("✅ Status correto: sem_limites")
    else:
        print("✅ Monitor de concentração não executado (esperado)")
    
    return True

def run_comprehensive_validation():
    """Executar validação completa de todos os casos."""
    print("🧪 VALIDAÇÃO COMPLETA - Building Block 8")
    print("=" * 50)
    
    try:
        # Validar AFA Pool #1
        success_afa = validate_afa_pool_concentration()
        
        # Validar LeCapital Pool #1
        success_lecapital = validate_lecapital_pool_concentration()
        
        # Validar Up Vendas Pool #2
        success_upvendas = validate_upvendas_pool_no_concentration()
        
        # Resumo final
        print("\n" + "=" * 50)
        print("📊 RESUMO DA VALIDAÇÃO")
        print(f"✅ AFA Pool #1: {'PASSOU' if success_afa else 'FALHOU'}")
        print(f"✅ LeCapital Pool #1: {'PASSOU' if success_lecapital else 'FALHOU'}")
        print(f"✅ Up Vendas Pool #2: {'PASSOU' if success_upvendas else 'FALHOU'}")
        
        if success_afa and success_lecapital and success_upvendas:
            print("\n🎉 VALIDAÇÃO COMPLETA: TODOS OS TESTES PASSARAM!")
            print("✅ Building Block 8: CONCLUÍDO")
            return True
        else:
            print("\n❌ VALIDAÇÃO FALHOU: Alguns testes não passaram")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO DURANTE VALIDAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_comprehensive_validation()