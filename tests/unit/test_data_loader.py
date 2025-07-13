#!/usr/bin/env python3
"""
Teste do Sistema de Carregamento de Dados
========================================

Objetivo: Validar funcionamento do data_loader.py
- Testar modo NORMAL e modo DEBUG
- Verificar carregamento de arquivos
- Validar configurações e filtros
- Testar tratamento de erros

Uso:
    python test_data_loader.py
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Importar as funções do data_loader refatorado
try:
    from utils.data_loader import (
        load_pool_data,
        get_dashboard_pools,
        filter_ignored_pools,
        load_json
    )
    from utils.file_loaders import (
        load_dashboard,
        load_portfolio
    )
    from utils.data_handler import (
        data_validation,
        validar_dados_por_pool,
        gerar_metadados_carregamento
    )
    print("✅ Importações realizadas com sucesso")
except ImportError as e:
    print(f"❌ Erro nas importações: {e}")
    sys.exit(1)

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_result(test_name, success, details=None):
    """Imprime resultado do teste"""
    status = "✅ PASSOU" if success else "❌ FALHOU"
    print(f"{status} - {test_name}")
    if details:
        print(f"   Detalhes: {details}")

def test_file_structure():
    """Testa se estrutura de arquivos está correta"""
    print_header("TESTE 1: Estrutura de Arquivos")
    
    # Verificar diretórios (usar caminhos relativos)
    dirs_to_check = [
        "data/csv",
        "data/xlsx", 
        "data/config",
        "data/escrituras"
    ]
    
    for dir_path in dirs_to_check:
        exists = os.path.exists(dir_path)
        print_result(f"Diretório {dir_path}", exists)
        
        if exists:
            files = os.listdir(dir_path)
            print(f"   Arquivos encontrados: {len(files)}")
            if files:
                print(f"   Exemplo: {files[0]}")

def test_config_files():
    """Testa arquivos de configuração"""
    print_header("TESTE 2: Arquivos de Configuração")
    
    # Testar ignore_pools.json
    ignore_path = "data/config/ignore_pools.json"
    try:
        with open(ignore_path, 'r') as f:
            ignore_config = json.load(f)
        print_result("ignore_pools.json", True, f"Pools ignorados: {len(ignore_config.get('ignore_pools', []))}")
    except Exception as e:
        print_result("ignore_pools.json", False, str(e))
    
    # Testar test_pools.json
    test_path = "data/config/test_pools.json"
    try:
        with open(test_path, 'r') as f:
            test_config = json.load(f)
        debug_pools = test_config.get('debug_pools', [])
        monitors = test_config.get('monitor', [])
        print_result("test_pools.json", True, f"Debug pools: {len(debug_pools)}, Monitors: {len(monitors)}")
    except Exception as e:
        print_result("test_pools.json", False, str(e))

def test_individual_functions():
    """Testa funções individuais"""
    print_header("TESTE 3: Funções Individuais")
    
    # Testar load_dashboard
    try:
        csv_df = load_dashboard()
        print_result("load_dashboard()", True, f"Linhas: {len(csv_df)}, Colunas: {len(csv_df.columns)}")
        
        # Testar get_dashboard_pools
        pools = get_dashboard_pools(csv_df)
        print_result("get_dashboard_pools()", True, f"Pools encontrados: {len(pools)}")
        
        # Testar filter_ignored_pools
        filtered_pools = filter_ignored_pools(pools)
        print_result("filter_ignored_pools()", True, f"Pools após filtro: {len(filtered_pools)}")
        
        # Testar load_json
        configs = load_json(filtered_pools[:3])  # Testar apenas 3 primeiros
        print_result("load_json()", True, f"Configs carregadas: {len(configs)}")
        
    except Exception as e:
        print_result("Funções individuais", False, str(e))

def test_xlsx_loading():
    """Testa carregamento de XLSX"""
    print_header("TESTE 4: Carregamento XLSX")
    
    try:
        xlsx_df = load_portfolio()
        print_result("load_portfolio()", True, f"Linhas: {len(xlsx_df)}, Colunas: {len(xlsx_df.columns)}")
        
        # Mostrar algumas colunas
        print(f"   Colunas principais: {list(xlsx_df.columns)[:5]}")
        
    except Exception as e:
        print_result("load_portfolio()", False, str(e))

def test_debug_mode():
    """Testa modo DEBUG"""
    print_header("TESTE 5: Modo DEBUG")
    
    # Verificar se test_pools.json existe
    test_path = "data/config/test_pools.json"
    
    if os.path.exists(test_path):
        try:
            # Tentar carregar individual functions para debug
            csv_df = load_dashboard()
            xlsx_df = load_portfolio()
            
            # Simular validação sem confirmação
            print_result("Carregamento CSV+XLSX", True, f"CSV: {len(csv_df)} linhas, XLSX: {len(xlsx_df)} linhas")
            
            # Testar configurações
            pools = get_dashboard_pools(csv_df)
            pools_filtrados = filter_ignored_pools(pools[:5])  # Testar apenas 5 primeiros
            configs = load_json(pools_filtrados)
            
            print_result("Modo DEBUG (simulado)", True, f"Pools: {len(pools_filtrados)}, Configs: {len(configs)}")
            
        except Exception as e:
            print_result("Modo DEBUG", False, str(e))
    else:
        print_result("Modo DEBUG", False, "test_pools.json não encontrado")

def test_normal_mode():
    """Testa modo NORMAL"""
    print_header("TESTE 6: Modo NORMAL")
    
    # Simular modo normal testando funções individuais
    try:
        csv_df = load_dashboard()
        xlsx_df = load_portfolio()
        
        # Obter pools sem ignorar nenhum
        pools = get_dashboard_pools(csv_df)
        
        # Testar apenas alguns pools para economizar tempo
        pools_teste = pools[:10]
        configs = load_json(pools_teste)
        
        print_result("Modo NORMAL (simulado)", True, f"Pools: {len(pools_teste)}, Configs: {len(configs)}")
        
        # Testar validação por pool
        validacoes = validar_dados_por_pool(xlsx_df, {p: configs.get(p) for p in pools_teste})
        pools_com_validacao = len(validacoes)
        
        print_result("Validação por pool", True, f"Pools validados: {pools_com_validacao}")
        
    except Exception as e:
        print_result("Modo NORMAL", False, str(e))

def test_error_handling():
    """Testa tratamento de erros"""
    print_header("TESTE 7: Tratamento de Erros")
    
    # Testar com data inválida
    try:
        resultado = load_pool_data("data_invalida")
        success = resultado.get('sucesso', False)
        print_result("Data inválida", not success, "Deve falhar com data inválida")
    except Exception as e:
        print_result("Data inválida", True, f"Erro capturado: {str(e)[:50]}")

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES DO DATA_LOADER")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar todos os testes
    test_file_structure()
    test_config_files()
    test_individual_functions()
    test_xlsx_loading()
    test_debug_mode()
    test_normal_mode()
    test_error_handling()
    
    print_header("RESUMO DOS TESTES")
    print("✅ Testes concluídos!")
    print("📋 Verifique os resultados acima para identificar problemas")
    print("🔧 Corrija erros encontrados e execute novamente")

if __name__ == "__main__":
    main()