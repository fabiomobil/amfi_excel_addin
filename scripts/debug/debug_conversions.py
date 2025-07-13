"""
Utilitário de Debug para Conversões de Tipo
===========================================

Ajuda a diagnosticar por que colunas não estão sendo convertidas.
"""

import pandas as pd
from typing import List, Dict


def diagnosticar_dataframe(df: pd.DataFrame) -> Dict:
    """
    Analisa um DataFrame e identifica colunas que deveriam ser numéricas.
    
    Args:
        df: DataFrame para analisar
        
    Returns:
        Dict com diagnóstico detalhado
    """
    diagnostico = {
        'colunas_texto': [],
        'colunas_numericas': [],
        'colunas_suspeitas': [],
        'sugestoes': []
    }
    
    # Separar colunas por tipo
    for col in df.columns:
        dtype = str(df[col].dtype)
        
        if dtype == 'object':
            diagnostico['colunas_texto'].append({
                'nome': col,
                'tipo': dtype,
                'amostra': list(df[col].dropna().head(3).values)
            })
            
            # Verificar se deveria ser numérica
            col_lower = col.lower()
            if any(palavra in col_lower for palavra in ['valor', 'taxa', 'juros', 'saldo', 'montante']) or '(r$)' in col_lower:
                diagnostico['colunas_suspeitas'].append(col)
                
        elif pd.api.types.is_numeric_dtype(df[col]):
            diagnostico['colunas_numericas'].append({
                'nome': col,
                'tipo': dtype
            })
    
    # Gerar sugestões
    if diagnostico['colunas_suspeitas']:
        diagnostico['sugestoes'].append(
            f"Adicione estas colunas às listas de conversão: {diagnostico['colunas_suspeitas']}"
        )
    
    return diagnostico


def exibir_diagnostico(df: pd.DataFrame) -> None:
    """
    Exibe diagnóstico formatado do DataFrame.
    
    Args:
        df: DataFrame para analisar
    """
    diag = diagnosticar_dataframe(df)
    
    print("=" * 60)
    print("DIAGNÓSTICO DE CONVERSÕES")
    print("=" * 60)
    
    print(f"\n📊 Total de colunas: {len(df.columns)}")
    print(f"📝 Colunas texto: {len(diag['colunas_texto'])}")
    print(f"🔢 Colunas numéricas: {len(diag['colunas_numericas'])}")
    
    if diag['colunas_suspeitas']:
        print(f"\n⚠️  COLUNAS SUSPEITAS (deveriam ser numéricas):")
        for col in diag['colunas_suspeitas']:
            print(f"   - {col}")
            # Mostrar amostra
            texto_cols = [c for c in diag['colunas_texto'] if c['nome'] == col]
            if texto_cols:
                print(f"     Amostra: {texto_cols[0]['amostra']}")
    
    print("\n💡 SUGESTÕES:")
    for sugestao in diag['sugestoes']:
        print(f"   {sugestao}")
    
    print("\n" + "=" * 60)


def listar_colunas_por_tipo(df: pd.DataFrame) -> None:
    """
    Lista todas as colunas agrupadas por tipo de dado.
    
    Args:
        df: DataFrame para analisar
    """
    print("\n📋 COLUNAS POR TIPO DE DADO:")
    print("-" * 40)
    
    # Agrupar por dtype
    tipos = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        if dtype not in tipos:
            tipos[dtype] = []
        tipos[dtype].append(col)
    
    # Exibir
    for tipo, colunas in sorted(tipos.items()):
        print(f"\n{tipo} ({len(colunas)} colunas):")
        for col in sorted(colunas)[:10]:  # Mostrar até 10
            print(f"  - {col}")
        if len(colunas) > 10:
            print(f"  ... e mais {len(colunas) - 10} colunas")


# Função principal para usar no Spyder
def debug_conversoes(df: pd.DataFrame) -> None:
    """
    Função principal para debugar conversões no Spyder.
    
    Uso:
        from monitor.utils.debug_conversions import debug_conversoes
        debug_conversoes(df)
    """
    exibir_diagnostico(df)
    listar_colunas_por_tipo(df)
    
    # Verificar colunas específicas do screenshot
    colunas_screenshot = ['Taxa de Juros a.m.', 'Valor de Aquisição (R$)', 'Valor presente (R$)']
    print(f"\n🔍 VERIFICANDO COLUNAS DO SCREENSHOT:")
    print("-" * 40)
    
    for col in colunas_screenshot:
        if col in df.columns:
            dtype = df[col].dtype
            status = "✅ OK" if pd.api.types.is_numeric_dtype(df[col]) else "❌ TEXTO"
            print(f"{col}: {dtype} {status}")
        else:
            print(f"{col}: ⚠️ NÃO ENCONTRADA")


if __name__ == "__main__":
    print("Use este módulo no Spyder com:")
    print("from monitor.utils.debug_conversions import debug_conversoes")
    print("debug_conversoes(df)")