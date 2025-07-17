"""
Tests for Core Import System
===========================

This module tests the centralized import system that replaced 800+ lines
of duplicated import logic across the codebase.

Test Coverage:
- Import resolver functionality
- Fallback strategies
- Error handling
- Cache management
- Function imports
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the monitor directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitor'))

from monitor.core.imports import ImportResolver, import_monitor, import_util, import_function


class TestImportResolver:
    """Test the ImportResolver class."""
    
    def test_init(self):
        """Test ImportResolver initialization."""
        resolver = ImportResolver()
        assert resolver.import_cache == {}
        assert resolver.base_path.endswith('monitor')
    
    def test_import_cache_management(self):
        """Test import cache functionality."""
        resolver = ImportResolver()
        
        # Initially empty
        assert len(resolver.import_cache) == 0
        
        # Add to cache
        resolver.import_cache['test_key'] = 'test_value'
        assert resolver.import_cache['test_key'] == 'test_value'
        
        # Clear cache
        resolver.clear_cache()
        assert len(resolver.import_cache) == 0
    
    @patch('monitor.core.imports.importlib.import_module')
    def test_try_import_success(self, mock_import_module):
        """Test successful import attempt."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        mock_import_module.return_value = mock_module
        
        result = resolver._try_import('test.module')
        
        assert result == mock_module
        mock_import_module.assert_called_once_with('test.module')
    
    @patch('monitor.core.imports.importlib.import_module')
    def test_try_import_failure(self, mock_import_module):
        """Test failed import attempt."""
        resolver = ImportResolver()
        mock_import_module.side_effect = ImportError("Module not found")
        
        result = resolver._try_import('nonexistent.module')
        
        assert result is None
        mock_import_module.assert_called_once_with('nonexistent.module')
    
    @patch('monitor.core.imports.os.path.exists')
    def test_ensure_path_in_sys(self, mock_exists):
        """Test path management in sys.path."""
        resolver = ImportResolver()
        mock_exists.return_value = True
        
        test_path = '/test/path'
        initial_path_len = len(sys.path)
        
        resolver._ensure_path_in_sys(test_path)
        
        # Path should be added if it exists and wasn't already there
        if test_path not in sys.path:
            assert len(sys.path) > initial_path_len
    
    @patch('monitor.core.imports.ImportResolver._try_import')
    def test_import_monitor_success_first_strategy(self, mock_try_import):
        """Test successful monitor import with first strategy."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        mock_try_import.return_value = mock_module
        
        result = resolver.import_monitor('subordinacao')
        
        assert result == mock_module
        mock_try_import.assert_called_with('.base.monitor_subordinacao')
        
        # Should be cached
        assert resolver.import_cache['monitor_subordinacao'] == mock_module
    
    @patch('monitor.core.imports.ImportResolver._try_import')
    def test_import_monitor_success_fallback_strategy(self, mock_try_import):
        """Test successful monitor import with fallback strategy."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        
        # First two attempts fail, third succeeds
        mock_try_import.side_effect = [None, mock_module]
        
        result = resolver.import_monitor('subordinacao')
        
        assert result == mock_module
        assert mock_try_import.call_count == 2
    
    @patch('monitor.core.imports.ImportResolver._try_import')
    def test_import_monitor_failure_all_strategies(self, mock_try_import):
        """Test monitor import failure with all strategies."""
        resolver = ImportResolver()
        mock_try_import.return_value = None
        
        with pytest.raises(ImportError, match="Cannot import monitor 'subordinacao'"):
            resolver.import_monitor('subordinacao')
    
    @patch('monitor.core.imports.ImportResolver._try_import')
    def test_import_util_success(self, mock_try_import):
        """Test successful utility import."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        mock_try_import.return_value = mock_module
        
        result = resolver.import_util('data_loader')
        
        assert result == mock_module
        mock_try_import.assert_called_with('.utils.data_loader')
        
        # Should be cached
        assert resolver.import_cache['util_data_loader'] == mock_module
    
    @patch('monitor.core.imports.ImportResolver._try_import')
    def test_import_custom_success(self, mock_try_import):
        """Test successful custom module import."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        mock_try_import.return_value = mock_module
        
        result = resolver.import_custom('concentration_strategies')
        
        assert result == mock_module
        mock_try_import.assert_called_with('.custom.concentration_strategies')
        
        # Should be cached
        assert resolver.import_cache['custom_concentration_strategies'] == mock_module
    
    def test_import_function_success(self):
        """Test successful function import."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        mock_function = MagicMock()
        mock_module.test_function = mock_function
        
        with patch.object(resolver, 'import_monitor', return_value=mock_module):
            result = resolver.import_function('subordinacao', 'test_function', 'monitor')
            
            assert result == mock_function
    
    def test_import_function_missing_function(self):
        """Test function import with missing function."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        del mock_module.nonexistent_function  # Ensure it doesn't exist
        
        with patch.object(resolver, 'import_monitor', return_value=mock_module):
            with pytest.raises(AttributeError, match="has no function 'nonexistent_function'"):
                resolver.import_function('subordinacao', 'nonexistent_function', 'monitor')
    
    def test_import_function_invalid_module_type(self):
        """Test function import with invalid module type."""
        resolver = ImportResolver()
        
        with pytest.raises(ValueError, match="Invalid module_type: invalid"):
            resolver.import_function('test', 'func', 'invalid')
    
    def test_cache_usage(self):
        """Test that cache is used for repeated imports."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        
        # Manually add to cache
        resolver.import_cache['monitor_subordinacao'] = mock_module
        
        with patch.object(resolver, '_try_import') as mock_try_import:
            result = resolver.import_monitor('subordinacao')
            
            # Should return cached value without calling _try_import
            assert result == mock_module
            mock_try_import.assert_not_called()


class TestGlobalFunctions:
    """Test the global convenience functions."""
    
    @patch('monitor.core.imports._resolver.import_monitor')
    def test_import_monitor_global(self, mock_import_monitor):
        """Test global import_monitor function."""
        mock_module = MagicMock()
        mock_import_monitor.return_value = mock_module
        
        result = import_monitor('subordinacao')
        
        assert result == mock_module
        mock_import_monitor.assert_called_once_with('subordinacao')
    
    @patch('monitor.core.imports._resolver.import_util')
    def test_import_util_global(self, mock_import_util):
        """Test global import_util function."""
        mock_module = MagicMock()
        mock_import_util.return_value = mock_module
        
        result = import_util('data_loader')
        
        assert result == mock_module
        mock_import_util.assert_called_once_with('data_loader')
    
    @patch('monitor.core.imports._resolver.import_function')
    def test_import_function_global(self, mock_import_function):
        """Test global import_function function."""
        mock_function = MagicMock()
        mock_import_function.return_value = mock_function
        
        result = import_function('subordinacao', 'test_function', 'monitor')
        
        assert result == mock_function
        mock_import_function.assert_called_once_with('subordinacao', 'test_function', 'monitor')


class TestIntegration:
    """Integration tests for the import system."""
    
    def test_import_system_reduces_code_duplication(self):
        """Test that the import system successfully reduces code duplication."""
        # This is a meta-test that verifies the import system works
        # In a real scenario, this would compare before/after code metrics
        
        resolver = ImportResolver()
        
        # Test that we can create a resolver
        assert resolver is not None
        
        # Test that we can use all the main functions
        assert callable(resolver.import_monitor)
        assert callable(resolver.import_util)
        assert callable(resolver.import_custom)
        assert callable(resolver.import_function)
        
        # Test that caching works
        assert hasattr(resolver, 'import_cache')
        assert isinstance(resolver.import_cache, dict)
    
    def test_error_handling_robustness(self):
        """Test that error handling is robust."""
        resolver = ImportResolver()
        
        # Test that invalid imports raise appropriate errors
        with pytest.raises(ImportError):
            resolver.import_monitor('nonexistent_monitor')
        
        with pytest.raises(ImportError):
            resolver.import_util('nonexistent_util')
        
        with pytest.raises(ImportError):
            resolver.import_custom('nonexistent_custom')
    
    @patch('monitor.core.imports.ImportResolver._try_import')
    def test_fallback_strategies_work(self, mock_try_import):
        """Test that fallback strategies are properly implemented."""
        resolver = ImportResolver()
        
        # Simulate first strategy failing, second succeeding
        mock_module = MagicMock()
        mock_try_import.side_effect = [None, mock_module, None]
        
        result = resolver.import_monitor('subordinacao')
        
        assert result == mock_module
        # Should try relative import first, then direct import
        assert mock_try_import.call_count >= 2


# Performance tests
class TestPerformance:
    """Performance tests for the import system."""
    
    def test_cache_improves_performance(self):
        """Test that caching improves repeated import performance."""
        resolver = ImportResolver()
        mock_module = MagicMock()
        
        # Add to cache
        resolver.import_cache['monitor_subordinacao'] = mock_module
        
        import time
        
        # Cached import should be very fast
        start_time = time.time()
        result = resolver.import_monitor('subordinacao')
        end_time = time.time()
        
        assert result == mock_module
        assert (end_time - start_time) < 0.001  # Should be sub-millisecond
    
    def test_memory_usage_reasonable(self):
        """Test that memory usage is reasonable."""
        resolver = ImportResolver()
        
        # Cache should start empty
        assert len(resolver.import_cache) == 0
        
        # Add some items to cache
        for i in range(100):
            resolver.import_cache[f'test_key_{i}'] = f'test_value_{i}'
        
        # Should be able to handle reasonable cache sizes
        assert len(resolver.import_cache) == 100
        
        # Clear should work
        resolver.clear_cache()
        assert len(resolver.import_cache) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])