"""
Helper para resolver imports em diferentes contextos (Spyder, terminal, etc.)
"""

import sys
import os


def setup_imports():
    """
    Configura os caminhos de import para funcionar em diferentes contextos.
    Deve ser chamado no início de cada arquivo que usa imports relativos.
    """
    # Obter o diretório atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Adicionar diretórios necessários ao path
    paths_to_add = [
        current_dir,  # monitor/utils
        os.path.dirname(current_dir),  # monitor
        os.path.dirname(os.path.dirname(current_dir)),  # raiz do projeto
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return current_dir


def safe_import(module_name, fallback_name=None):
    """
    Tenta importar um módulo com fallback para import direto.
    
    Args:
        module_name: Nome do módulo com caminho relativo (ex: '.alerts')
        fallback_name: Nome do módulo sem ponto (ex: 'alerts')
        
    Returns:
        Módulo importado ou None se falhar
    """
    # Se não houver fallback, usar o nome sem ponto
    if fallback_name is None:
        fallback_name = module_name.lstrip('.')
    
    try:
        # Tentar import relativo primeiro
        module = __import__(module_name, fromlist=[''])
        return module
    except (ImportError, ValueError):
        try:
            # Tentar import direto
            module = __import__(fallback_name)
            return module
        except ImportError:
            return None


def get_import_context():
    """
    Detecta o contexto de execução (Spyder, terminal, etc.)
    
    Returns:
        str: 'spyder', 'terminal', 'jupyter' ou 'unknown'
    """
    # Verificar se está no Spyder
    if 'spyder' in sys.modules or 'spyder_kernels' in sys.modules:
        return 'spyder'
    
    # Verificar se está no Jupyter
    if 'ipykernel' in sys.modules or 'jupyter' in sys.executable.lower():
        return 'jupyter'
    
    # Verificar se está sendo executado como script
    if __name__ == '__main__':
        return 'terminal'
    
    return 'unknown'