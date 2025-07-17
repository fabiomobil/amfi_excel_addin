#!/usr/bin/env python3
"""
Debug script para Monitor PDD OOP.
"""

import sys
import os
import pandas as pd
import numpy as np

# Adicionar path para imports
sys.path.insert(0, '/mnt/c/amfi/monitor')
sys.path.insert(0, '/mnt/c/amfi/monitor/base')

from base.monitor_pdd_oop import PDDMonitor
from base.monitor_inadimplencia_oop import DelinquencyMonitor
from utils.data_loader import load_pool_data

def debug_pdd_calculations():
    """Debug dos cálculos de PDD."""
    print("🔍 DEBUG: Cálculos de PDD")
    
    # Carregar dados
    dados = load_pool_data()
    pool_config = dados["pools_configs"]["AFA Pool #1"]
    
    # Enriquecer dados
    xlsx_data = dados["xlsx_data"].copy()
    pool_csv = dados["csv_data"][dados["csv_data"]["nome"] == "AFA Pool #1"]
    
    delinquency_monitor = DelinquencyMonitor(pool_config)
    delinquency_monitor.run_monitoring(pool_csv, xlsx_data)
    
    # Criar monitor PDD
    pdd_monitor = PDDMonitor(pool_config)
    
    # Aplicar lógica por cedente
    df_with_logic = pdd_monitor._apply_cedente_logic(xlsx_data)
    
    # Debug: verificar alguns valores
    print(f"Total de registros: {len(df_with_logic)}")
    print(f"Registros com provisão > 0: {len(df_with_logic[df_with_logic['provisao_valor'] > 0])}")
    
    # Calcular totais manualmente
    total_provisao_manual = df_with_logic['provisao_valor'].sum()
    total_carteira_manual = df_with_logic['valor_presente'].sum()
    
    print(f"Total provisão manual: {total_provisao_manual}")
    print(f"Total carteira manual: {total_carteira_manual}")
    
    # Calcular por grupo
    pdd_analysis = pdd_monitor._calculate_provisions_by_group(df_with_logic)
    
    print(f"Total provisão por grupo: {pdd_analysis['totais']['provisao_valor']}")
    print(f"Total carteira por grupo: {pdd_analysis['totais']['carteira_valor']}")
    
    # Verificar soma por grupo
    soma_provisao_grupos = sum(g["provisao_valor"] for g in pdd_analysis["grupos"].values())
    soma_carteira_grupos = sum(g["valor_total"] for g in pdd_analysis["grupos"].values())
    
    print(f"Soma provisão grupos: {soma_provisao_grupos}")
    print(f"Soma carteira grupos: {soma_carteira_grupos}")
    
    # Verificar se há diferenças
    if abs(total_provisao_manual - soma_provisao_grupos) > 0.01:
        print(f"❌ DIFERENÇA EM PROVISÃO: {total_provisao_manual} vs {soma_provisao_grupos}")
        
        # Investigar mais profundamente
        print("\n🔍 Investigando por grupo:")
        for grupo, info in pdd_analysis["grupos"].items():
            titulos_grupo = df_with_logic[df_with_logic['grupo_pdd_cedente'] == grupo]
            provisao_manual = titulos_grupo['provisao_valor'].sum()
            
            print(f"Grupo {grupo}: {info['provisao_valor']} vs {provisao_manual} (manual)")
            
            if abs(info['provisao_valor'] - provisao_manual) > 0.01:
                print(f"  ❌ DIFERENÇA: {info['provisao_valor']} vs {provisao_manual}")
    
    if abs(total_carteira_manual - soma_carteira_grupos) > 0.01:
        print(f"❌ DIFERENÇA EM CARTEIRA: {total_carteira_manual} vs {soma_carteira_grupos}")

if __name__ == "__main__":
    debug_pdd_calculations()