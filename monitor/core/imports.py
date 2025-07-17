"""
Centralized Import System for AmFi Monitoring
============================================

This module provides a unified import system that handles the complex
import fallback logic that was previously duplicated across 15+ files.

Supports multiple execution environments:
- Module execution (relative imports)
- Direct execution (Spyder/IDE)
- Absolute path execution (WSL/Linux)

Usage:
    from monitor.core.imports import import_monitor, import_util
    
    # Import a monitor
    monitor = import_monitor('subordinacao')
    
    # Import a utility
    data_loader = import_util('data_loader')
"""

import os
import sys
import importlib
from typing import Any, Dict, Optional


class ImportResolver:
    """
    Centralized import resolver that handles different execution contexts.
    """
    
    def __init__(self):
        self.import_cache: Dict[str, Any] = {}
        self.base_path = os.path.dirname(os.path.dirname(__file__))  # monitor/
        
    def _try_import(self, module_path: str) -> Optional[Any]:
        """
        Try to import a module with error handling.
        
        Args:
            module_path: Full module path to import
            
        Returns:
            Imported module or None if failed
        """
        try:
            # If it's a relative import, convert to absolute 
            if module_path.startswith('.'):
                # Try absolute import instead
                if module_path.startswith('.utils.'):
                    abs_path = f"monitor.utils.{module_path[7:]}"
                elif module_path.startswith('.core.'):
                    abs_path = f"monitor.core.{module_path[6:]}"
                else:
                    abs_path = f"monitor{module_path[1:]}"
                return importlib.import_module(abs_path)
            else:
                return importlib.import_module(module_path)
        except (ImportError, ValueError, ModuleNotFoundError, TypeError):
            return None
    
    def _ensure_path_in_sys(self, path: str) -> None:
        """Ensure path is in sys.path if it exists."""
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
    
    def import_monitor(self, monitor_name: str) -> Any:
        """
        Import a monitor module using fallback strategy.
        
        Args:
            monitor_name: Name of monitor (e.g., 'subordinacao', 'concentracao')
            
        Returns:
            Imported monitor module
            
        Raises:
            ImportError: If monitor cannot be imported with any method
        """
        cache_key = f"monitor_{monitor_name}"
        if cache_key in self.import_cache:
            return self.import_cache[cache_key]
            
        full_module_name = f"monitor_{monitor_name}"
        
        # Strategy 1: Relative import from core (updated from base)
        module = self._try_import(f".core.{full_module_name}")
        if module:
            self.import_cache[cache_key] = module
            return module
        
        # Strategy 2: Direct import (for Spyder/IDE execution)
        self._ensure_path_in_sys(os.path.join(self.base_path, 'core'))
        module = self._try_import(full_module_name)
        if module:
            self.import_cache[cache_key] = module
            return module
            
        # Strategy 3: Absolute import
        self._ensure_path_in_sys(os.path.dirname(self.base_path))
        module = self._try_import(f"monitor.core.{full_module_name}")
        if module:
            self.import_cache[cache_key] = module
            return module
            
        raise ImportError(f"Cannot import monitor '{monitor_name}'. Tried all import strategies.")
    
    def import_util(self, util_name: str) -> Any:
        """
        Import a utility module using fallback strategy.
        
        Args:
            util_name: Name of utility (e.g., 'data_loader', 'alerts')
            
        Returns:
            Imported utility module
            
        Raises:
            ImportError: If utility cannot be imported with any method
        """
        cache_key = f"util_{util_name}"
        if cache_key in self.import_cache:
            return self.import_cache[cache_key]
        
        # Strategy 1: Relative import from utils
        module = self._try_import(f".utils.{util_name}")
        if module:
            self.import_cache[cache_key] = module
            return module
        
        # Strategy 2: Direct import (for Spyder/IDE execution)
        self._ensure_path_in_sys(os.path.join(self.base_path, 'utils'))
        module = self._try_import(util_name)
        if module:
            self.import_cache[cache_key] = module
            return module
            
        # Strategy 3: Absolute import
        self._ensure_path_in_sys(os.path.dirname(self.base_path))
        module = self._try_import(f"monitor.utils.{util_name}")
        if module:
            self.import_cache[cache_key] = module
            return module
            
        raise ImportError(f"Cannot import utility '{util_name}'. Tried all import strategies.")
    
    def import_custom(self, custom_name: str) -> Any:
        """
        Import a custom module using fallback strategy.
        
        Args:
            custom_name: Name of custom module
            
        Returns:
            Imported custom module
            
        Raises:
            ImportError: If custom module cannot be imported with any method
        """
        cache_key = f"custom_{custom_name}"
        if cache_key in self.import_cache:
            return self.import_cache[cache_key]
        
        # Strategy 1: Relative import from custom
        module = self._try_import(f".custom.{custom_name}")
        if module:
            self.import_cache[cache_key] = module
            return module
        
        # Strategy 2: Direct import (for Spyder/IDE execution)
        self._ensure_path_in_sys(os.path.join(self.base_path, 'custom'))
        module = self._try_import(custom_name)
        if module:
            self.import_cache[cache_key] = module
            return module
            
        # Strategy 3: Absolute import
        self._ensure_path_in_sys(os.path.dirname(self.base_path))
        module = self._try_import(f"monitor.custom.{custom_name}")
        if module:
            self.import_cache[cache_key] = module
            return module
            
        raise ImportError(f"Cannot import custom module '{custom_name}'. Tried all import strategies.")
    
    def import_function(self, module_name: str, function_name: str, module_type: str = 'monitor') -> Any:
        """
        Import a specific function from a module.
        
        Args:
            module_name: Name of the module
            function_name: Name of the function to import
            module_type: Type of module ('monitor', 'util', 'custom')
            
        Returns:
            Imported function
            
        Raises:
            ImportError: If function cannot be imported
            AttributeError: If function doesn't exist in module
        """
        if module_type == 'monitor':
            module = self.import_monitor(module_name)
        elif module_type == 'util':
            module = self.import_util(module_name)
        elif module_type == 'custom':
            module = self.import_custom(module_name)
        else:
            raise ValueError(f"Invalid module_type: {module_type}")
            
        if not hasattr(module, function_name):
            raise AttributeError(f"Module {module_name} has no function '{function_name}'")
            
        return getattr(module, function_name)
    
    def clear_cache(self) -> None:
        """Clear the import cache."""
        self.import_cache.clear()


# Global resolver instance
_resolver = ImportResolver()

# Public API functions
def import_monitor(monitor_name: str) -> Any:
    """Import a monitor module."""
    return _resolver.import_monitor(monitor_name)

def import_util(util_name: str) -> Any:
    """Import a utility module."""
    return _resolver.import_util(util_name)

def import_custom(custom_name: str) -> Any:
    """Import a custom module."""
    return _resolver.import_custom(custom_name)

def import_function(module_name: str, function_name: str, module_type: str = 'monitor') -> Any:
    """Import a specific function from a module."""
    return _resolver.import_function(module_name, function_name, module_type)

def clear_import_cache() -> None:
    """Clear the import cache."""
    _resolver.clear_cache()

def get_import_cache() -> Dict[str, Any]:
    """Get current import cache (for debugging)."""
    return _resolver.import_cache.copy()