#!/usr/bin/env python3
"""
Teste de Performance das Conversões Otimizadas
==============================================

Para usar no Spyder:
1. Execute este arquivo
2. Ou copie e cole no console do Spyder
"""

import time
import sys
import os
sys.path.insert(0, 'monitor/utils')

print("⚡ TESTE DE PERFORMANCE - CONVERSÕES OTIMIZADAS")
print("=" * 60)

try:
    # Importar função otimizada
    from file_loaders import load_portfolio
    
    print("🚀 Carregando portfolio com conversões otimizadas...")
    
    # Medir tempo de execução
    start_time = time.time()
    
    df = load_portfolio()
    
    end_time = time.time()
    tempo_execucao = end_time - start_time
    
    print(f"\n⏱️  TEMPO TOTAL: {tempo_execucao:.2f} segundos")
    print(f"📊 DATASET: {len(df):,} registros × {len(df.columns)} colunas")
    
    # Verificar resultados das conversões
    print(f"\n🔍 VERIFICAÇÃO DOS TIPOS DE DADOS:")
    print("-" * 40)
    
    colunas_teste = {
        'taxa_de_juros_am': 'percentual',
        'valor_de_aquisicao': 'monetário', 
        'valor_presente': 'monetário',
        'valor_recebido': 'monetário'
    }
    
    conversoes_ok = 0
    total_colunas = len(colunas_teste)
    
    for col, tipo in colunas_teste.items():
        if col in df.columns:
            dtype = str(df[col].dtype)
            is_numeric = dtype.startswith(('int', 'float'))
            status = "✅" if is_numeric else "❌"
            
            if is_numeric:
                conversoes_ok += 1
                amostra = df[col].dropna().head(3).tolist()
                print(f"{col}: {dtype} {status}")
                print(f"   Amostra: {amostra}")
            else:
                print(f"{col}: {dtype} {status} (FALHOU)")
        else:
            print(f"{col}: ⚠️ NÃO ENCONTRADA")
    
    # Resumo final
    print(f"\n" + "=" * 60)
    print(f"📈 PERFORMANCE: {len(df)/tempo_execucao:,.0f} registros/segundo")
    print(f"✅ CONVERSÕES: {conversoes_ok}/{total_colunas} bem-sucedidas")
    
    if conversoes_ok == total_colunas:
        print("🎉 SUCESSO: Todas as conversões funcionaram!")
    else:
        print("⚠️  ATENÇÃO: Algumas conversões falharam")
        
    if len(df) > 1000:
        print("⚡ Modo performance foi ativado para este dataset")
    else:
        print("🐌 Modo normal usado (dataset pequeno)")

except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 60)
print("Teste concluído! 🏁")