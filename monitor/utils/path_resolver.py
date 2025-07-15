"""
Path Resolver - Sistema Centralizado de Descoberta de Caminhos
==============================================================

Este módulo centraliza toda a lógica de descoberta de caminhos do sistema,
garantindo compatibilidade entre diferentes ambientes de execução:
- Windows (C:\\amfi\\...)
- WSL (/mnt/c/amfi/...)
- Spyder (paths relativos)
- Linux/Docker (/app/...)

Criado em: 2025-07-14
Motivo: Centralizar lógica duplicada em data_loader.py e orchestrator.py
"""

import os
from typing import List, Optional


def get_possible_paths(tipo: str, nome_base: Optional[str] = None) -> List[str]:
    """
    Gera lista de caminhos possíveis para compatibilidade entre ambientes.
    
    Esta função é essencial para o sistema funcionar em diferentes configurações:
    - Desenvolvimento local no Windows (C:\\amfi\\...)
    - WSL - Windows Subsystem for Linux (/mnt/c/amfi/...)
    - Execução via Spyder com diretórios relativos
    - Servidores Linux com caminhos absolutos
    
    A função testa os caminhos em ordem de prioridade, começando pelos
    mais comuns em desenvolvimento.
    
    Args:
        tipo: Tipo de diretório ('csv', 'xlsx', 'config', 'escrituras')
        nome_base: Nome do arquivo para concatenar ao caminho (opcional)
        
    Returns:
        List[str]: Lista de caminhos possíveis ordenados por prioridade
        
    Examples:
        >>> get_possible_paths('csv')
        ['data/input/csv', 'C:\\amfi\\data\\input\\csv', '/mnt/c/amfi/data/input/csv', '../../data/input/csv']
        
        >>> get_possible_paths('config', 'test_pools.json')  
        ['config/monitoring/test_pools.json', 'C:\\amfi\\config\\monitoring\\test_pools.json', ...]
        
    Raises:
        ValueError: Se tipo não for um dos suportados
    """
    caminhos_base = {
        'csv': [
            "data/input/csv",
            r"C:\amfi\data\input\csv",
            "/mnt/c/amfi/data/input/csv",
            "../../data/input/csv"
        ],
        'xlsx': [
            "data/input/xlsx",
            r"C:\amfi\data\input\xlsx", 
            "/mnt/c/amfi/data/input/xlsx",
            "../../data/input/xlsx"
        ],
        'config': [
            "config/monitoring",
            r"C:\amfi\config\monitoring",
            "/mnt/c/amfi/config/monitoring",
            "../../config/monitoring"
        ],
        'escrituras': [
            "config/pools",
            r"C:\amfi\config\pools",
            "/mnt/c/amfi/config/pools",
            "../../config/pools"
        ]
    }
    
    if tipo not in caminhos_base:
        raise ValueError(f"Tipo '{tipo}' não suportado. Use: {list(caminhos_base.keys())}")
    
    if nome_base:
        return [os.path.join(caminho, nome_base) for caminho in caminhos_base[tipo]]
    else:
        return caminhos_base[tipo]


def find_existing_path(tipo: str, nome_base: Optional[str] = None) -> str:
    """
    Descobre automaticamente qual caminho existe no sistema.
    
    Esta função resolve o problema de compatibilidade entre ambientes diferentes.
    Ela testa cada variante de caminho até encontrar uma que realmente existe.
    
    Args:
        tipo: Tipo de diretório ('csv', 'xlsx', 'config', 'escrituras')
        nome_base: Nome do arquivo (opcional)
        
    Returns:
        str: Caminho absoluto do diretório/arquivo encontrado
        
    Raises:
        FileNotFoundError: Se nenhuma variante de caminho for encontrada
        
    Example:
        >>> find_existing_path('csv')
        'C:\\amfi\\data\\input\\csv'  # Em Windows/Spyder
        
        >>> find_existing_path('escrituras', 'AFA Pool #1.json')
        'C:\\amfi\\config\\pools\\AFA Pool #1.json'
    """
    possible_paths = get_possible_paths(tipo, nome_base)
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    if nome_base:
        raise FileNotFoundError(f"Arquivo {nome_base} não encontrado. Tentados: {possible_paths}")
    else:
        raise FileNotFoundError(f"Pasta {tipo} não encontrada. Tentados: {possible_paths}")


def get_working_directory_info() -> dict:
    """
    Retorna informações sobre o ambiente de execução atual.
    Útil para debugging de problemas de path.
    
    Returns:
        dict: Informações do ambiente
    """
    import platform
    
    return {
        "working_directory": os.getcwd(),
        "platform": platform.system(),
        "python_executable": os.path.abspath(os.sys.executable),
        "file_separator": os.sep,
        "is_windows": platform.system() == "Windows",
        "is_wsl": "microsoft-standard" in platform.uname().release.lower() if hasattr(platform.uname(), 'release') else False
    }


# Exportar funções principais
__all__ = ['get_possible_paths', 'find_existing_path', 'get_working_directory_info']