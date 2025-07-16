#!/usr/bin/env python3
"""
Teste da ConcentrationConfig com pools reais
"""

import json
import sys
import os

# Adicionar caminho do monitor
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

from concentration_config import create_concentration_config, ConcentrationConfig

def test_afa_pool():
    """Testa AFA Pool #1 - Complexidade Alta (4 limites)"""
    print("=== Testando AFA Pool #1 ===")
    
    with open('/mnt/c/amfi/config/pools/AFA Pool #1.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    conc_config = create_concentration_config(config)
    
    print(f"Pool ID: {conc_config.pool_id}")
    print(f"Ativo: {conc_config.ativo}")
    print(f"Complexidade: {conc_config.complexidade}")
    print(f"Número de limites: {len(conc_config.limites)}")
    print(f"Campos necessários: {conc_config.campos_necessarios}")
    print(f"Sacados elegíveis: {len(conc_config.sacados_elegiveis) if conc_config.sacados_elegiveis else 0}")
    
    for i, limite in enumerate(conc_config.limites):
        print(f"  Limite {i+1}: {limite.tipo.value} {limite.entidade.value} = {limite.limite*100:.1f}%")
        if limite.n:
            print(f"    Top-N: {limite.n}")
        print(f"    Grupo econômico: {limite.inclui_grupo_economico}")
    
    print()

def test_credmei_pool():
    """Testa Credmei Pool #1 - Simplicidade Máxima (1 limite)"""
    print("=== Testando Credmei Pool #1 ===")
    
    with open('/mnt/c/amfi/config/pools/Credmei Pool #1.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    conc_config = create_concentration_config(config)
    
    print(f"Pool ID: {conc_config.pool_id}")
    print(f"Ativo: {conc_config.ativo}")
    print(f"Complexidade: {conc_config.complexidade}")
    print(f"Número de limites: {len(conc_config.limites)}")
    
    for i, limite in enumerate(conc_config.limites):
        print(f"  Limite {i+1}: {limite.tipo.value} {limite.entidade.value} = {limite.limite*100:.1f}%")
        print(f"    Grupo econômico: {limite.inclui_grupo_economico}")
    
    print()

def test_upvendas_pool():
    """Testa Up Vendas Pool #2 - Sem limites"""
    print("=== Testando Up Vendas Pool #2 ===")
    
    with open('/mnt/c/amfi/config/pools/Up Vendas Pool #2.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    conc_config = create_concentration_config(config)
    
    print(f"Pool ID: {conc_config.pool_id}")
    print(f"Ativo: {conc_config.ativo}")
    print(f"Complexidade: {conc_config.complexidade}")
    print(f"Número de limites: {len(conc_config.limites)}")
    
    print()

def test_formento_pool():
    """Testa Formento Pool #3 - Método específico (8 dígitos CNPJ)"""
    print("=== Testando Formento Pool #3 ===")
    
    with open('/mnt/c/amfi/config/pools/Formento Pool #3.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    conc_config = create_concentration_config(config)
    
    print(f"Pool ID: {conc_config.pool_id}")
    print(f"Ativo: {conc_config.ativo}")
    print(f"Complexidade: {conc_config.complexidade}")
    print(f"Número de limites: {len(conc_config.limites)}")
    
    for i, limite in enumerate(conc_config.limites):
        print(f"  Limite {i+1}: {limite.tipo.value} {limite.entidade.value} = {limite.limite*100:.1f}%")
        print(f"    Grupo econômico: {limite.inclui_grupo_economico}")
        print(f"    Método: {limite.metodo_calculo.value}")
    
    print()

if __name__ == "__main__":
    try:
        test_afa_pool()
        test_credmei_pool()
        test_upvendas_pool()
        test_formento_pool()
        print("✅ Todos os testes passaram!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()