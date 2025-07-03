"""
UDF Result Cache - Optimização para evitar recálculos desnecessários no Excel
"""
import hashlib
import json
import time
from functools import wraps
from typing import Any, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Cache global para resultados de UDFs
_UDF_RESULT_CACHE: Dict[str, Tuple[Any, float]] = {}

# Configurações de cache
CACHE_TTL_SECONDS = 300  # 5 minutos por padrão
MAX_CACHE_SIZE = 1000  # Máximo de entradas no cache


def _generate_cache_key(*args, **kwargs) -> str:
    """
    Gera uma chave única baseada nos argumentos da função.
    Converte ranges Excel e outros objetos em strings estáveis.
    """
    key_parts = []
    
    for arg in args:
        if arg is None:
            key_parts.append("None")
        elif hasattr(arg, '__iter__') and not isinstance(arg, str):
            # Range Excel ou lista - converter para tuple ordenado
            try:
                items = []
                for item in arg:
                    if hasattr(item, '__iter__') and not isinstance(item, str):
                        # Nested range
                        items.append(tuple(str(cell) for cell in item))
                    else:
                        items.append(str(item))
                key_parts.append(str(tuple(items)))
            except:
                key_parts.append(str(arg))
        else:
            key_parts.append(str(arg))
    
    # Adicionar kwargs ordenados
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    # Criar hash MD5 da representação em string
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def _clean_old_cache_entries():
    """Remove entradas expiradas do cache."""
    global _UDF_RESULT_CACHE
    current_time = time.time()
    
    # Limpar entradas expiradas
    expired_keys = [
        key for key, (_, timestamp) in _UDF_RESULT_CACHE.items()
        if current_time - timestamp > CACHE_TTL_SECONDS
    ]
    
    for key in expired_keys:
        del _UDF_RESULT_CACHE[key]
    
    # Se ainda estiver muito grande, remover as mais antigas
    if len(_UDF_RESULT_CACHE) > MAX_CACHE_SIZE:
        # Ordenar por timestamp e manter apenas as mais recentes
        sorted_items = sorted(
            _UDF_RESULT_CACHE.items(),
            key=lambda x: x[1][1],  # timestamp
            reverse=True
        )
        _UDF_RESULT_CACHE = dict(sorted_items[:MAX_CACHE_SIZE // 2])


def cache_udf_result(ttl_seconds: Optional[int] = None):
    """
    Decorator para cachear resultados de UDFs.
    
    Args:
        ttl_seconds: Tempo de vida do cache em segundos (padrão: 300)
    
    Uso:
        @cache_udf_result(ttl_seconds=60)
        @xw.func
        def MinhaFuncao(arg1, arg2):
            # processamento pesado
            return resultado
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = f"{func.__name__}:{_generate_cache_key(*args, **kwargs)}"
            
            # Verificar se existe no cache e não expirou
            current_time = time.time()
            if cache_key in _UDF_RESULT_CACHE:
                result, timestamp = _UDF_RESULT_CACHE[cache_key]
                cache_age = current_time - timestamp
                ttl = ttl_seconds or CACHE_TTL_SECONDS
                
                if cache_age < ttl:
                    logger.debug(f"Cache hit for {func.__name__} (age: {cache_age:.1f}s)")
                    return result
            
            # Executar função e cachear resultado
            logger.debug(f"Cache miss for {func.__name__} - executing")
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            _UDF_RESULT_CACHE[cache_key] = (result, current_time)
            
            # Limpeza periódica
            if len(_UDF_RESULT_CACHE) % 50 == 0:
                _clean_old_cache_entries()
            
            return result
        
        return wrapper
    return decorator


def clear_udf_cache(function_name: Optional[str] = None):
    """
    Limpa o cache de resultados UDF.
    
    Args:
        function_name: Nome da função específica para limpar (None = limpar tudo)
    """
    global _UDF_RESULT_CACHE
    
    if function_name is None:
        # Limpar todo o cache
        count = len(_UDF_RESULT_CACHE)
        _UDF_RESULT_CACHE.clear()
        return f"Cache UDF limpo. {count} entradas removidas."
    else:
        # Limpar apenas função específica
        keys_to_remove = [
            key for key in _UDF_RESULT_CACHE
            if key.startswith(f"{function_name}:")
        ]
        
        for key in keys_to_remove:
            del _UDF_RESULT_CACHE[key]
        
        return f"Cache da função {function_name} limpo. {len(keys_to_remove)} entradas removidas."


def get_udf_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache UDF."""
    current_time = time.time()
    
    # Agrupar por função
    function_stats = {}
    total_size = 0
    
    for key, (result, timestamp) in _UDF_RESULT_CACHE.items():
        function_name = key.split(':')[0]
        age = current_time - timestamp
        
        if function_name not in function_stats:
            function_stats[function_name] = {
                'count': 0,
                'oldest_age': 0,
                'newest_age': float('inf')
            }
        
        stats = function_stats[function_name]
        stats['count'] += 1
        stats['oldest_age'] = max(stats['oldest_age'], age)
        stats['newest_age'] = min(stats['newest_age'], age)
    
    return {
        'total_entries': len(_UDF_RESULT_CACHE),
        'functions': function_stats,
        'cache_size_limit': MAX_CACHE_SIZE,
        'ttl_seconds': CACHE_TTL_SECONDS
    }


# Funções auxiliares para uso direto no Excel
def format_cache_stats() -> str:
    """Formata estatísticas do cache para exibição."""
    stats = get_udf_cache_stats()
    
    lines = [f"Cache UDF: {stats['total_entries']} entradas (máx: {stats['cache_size_limit']})"]
    
    for func, fstats in stats['functions'].items():
        lines.append(
            f"  {func}: {fstats['count']} entradas "
            f"(idade: {fstats['newest_age']:.0f}s - {fstats['oldest_age']:.0f}s)"
        )
    
    return "\n".join(lines)