"""
AmFi Monitor Constants
=====================

Centralized constants for all monitoring functions, eliminating magic numbers
and providing a single source of truth for configuration values.

This file consolidates the following scattered constants:
- Default subordination limits (0.05, 0.03)
- Default concentration limits (0.25, 0.30, 0.70)
- Default PDD percentages (0.03)
- Risk classification thresholds

Usage:
    from monitor.constants import SUBORDINATION_LIMITS, CONCENTRATION_LIMITS
    
    limit_min = SUBORDINATION_LIMITS.MINIMUM_DEFAULT
    conc_limit = CONCENTRATION_LIMITS.INDIVIDUAL_DEFAULT
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class SubordinationLimits:
    """Default subordination ratio limits."""
    MINIMUM_DEFAULT: float = 0.05  # 5% minimum subordination
    CRITICAL_DEFAULT: float = 0.03  # 3% critical subordination
    

@dataclass 
class ConcentrationLimits:
    """Default concentration limits."""
    INDIVIDUAL_DEFAULT: float = 0.25  # 25% individual concentration
    CEDENTE_DEFAULT: float = 0.30     # 30% single cedente concentration
    TOP_10_DEFAULT: float = 0.70      # 70% top 10 cedentes concentration
    

@dataclass
class PDDRates:
    """Default PDD (Provisão para Devedores Duvidosos) rates."""
    LEVEL_1_DEFAULT: float = 0.01  # AA: 1%
    LEVEL_2_DEFAULT: float = 0.03  # BB: 3%
    LEVEL_3_DEFAULT: float = 0.10  # CC: 10%
    LEVEL_4_DEFAULT: float = 0.30  # DD and below: 30%


@dataclass
class RiskThresholds:
    """Risk classification thresholds in days."""
    LOW_RISK_MAX: int = 30      # <= 30 days: AA/AAA
    MEDIUM_RISK_MAX: int = 90   # 31-90 days: BB/BBB  
    HIGH_RISK_MAX: int = 180    # 91-180 days: CC/CCC
    CRITICAL_RISK_MIN: int = 181 # 180+ days: DD/DDD


@dataclass
class DataValidation:
    """Data validation constants."""
    MIN_PORTFOLIO_VALUE: float = 1000.0  # Minimum portfolio value for analysis
    MAX_CONCENTRATION: float = 1.0       # 100% maximum concentration
    MIN_SUBORDINATION: float = 0.0       # 0% minimum subordination
    

# Create singleton instances
SUBORDINATION_LIMITS = SubordinationLimits()
CONCENTRATION_LIMITS = ConcentrationLimits()
PDD_RATES = PDDRates()
RISK_THRESHOLDS = RiskThresholds()
DATA_VALIDATION = DataValidation()


# Legacy mapping for backward compatibility
LEGACY_CONSTANTS = {
    # Subordination
    'limite_subordinacao_minimo': SUBORDINATION_LIMITS.MINIMUM_DEFAULT,
    'limite_subordinacao_critico': SUBORDINATION_LIMITS.CRITICAL_DEFAULT,
    
    # Concentration
    'limite_concentracao_individual': CONCENTRATION_LIMITS.INDIVIDUAL_DEFAULT,
    'limite_concentracao_cedente': CONCENTRATION_LIMITS.CEDENTE_DEFAULT,
    'limite_concentracao_top10': CONCENTRATION_LIMITS.TOP_10_DEFAULT,
    
    # PDD
    'taxa_pdd_nivel_1': PDD_RATES.LEVEL_1_DEFAULT,
    'taxa_pdd_nivel_2': PDD_RATES.LEVEL_2_DEFAULT,
    'taxa_pdd_nivel_3': PDD_RATES.LEVEL_3_DEFAULT,
    'taxa_pdd_nivel_4': PDD_RATES.LEVEL_4_DEFAULT,
}


def get_constant(key: str, default: Any = None) -> Any:
    """
    Get a constant value by key with fallback.
    
    Args:
        key: Constant key name
        default: Default value if key not found
        
    Returns:
        Constant value or default
    """
    return LEGACY_CONSTANTS.get(key, default)


def get_subordination_limit(limit_type: str = 'minimum') -> float:
    """
    Get subordination limit by type.
    
    Args:
        limit_type: 'minimum' or 'critical'
        
    Returns:
        Subordination limit as decimal (0.05 = 5%)
    """
    if limit_type.lower() == 'critical':
        return SUBORDINATION_LIMITS.CRITICAL_DEFAULT
    return SUBORDINATION_LIMITS.MINIMUM_DEFAULT


def get_concentration_limit(limit_type: str = 'individual') -> float:
    """
    Get concentration limit by type.
    
    Args:
        limit_type: 'individual', 'cedente', or 'top_10'
        
    Returns:
        Concentration limit as decimal (0.25 = 25%)
    """
    limit_map = {
        'individual': CONCENTRATION_LIMITS.INDIVIDUAL_DEFAULT,
        'cedente': CONCENTRATION_LIMITS.CEDENTE_DEFAULT,
        'top_10': CONCENTRATION_LIMITS.TOP_10_DEFAULT,
        'top10': CONCENTRATION_LIMITS.TOP_10_DEFAULT,  # Alternative spelling
    }
    return limit_map.get(limit_type.lower(), CONCENTRATION_LIMITS.INDIVIDUAL_DEFAULT)


def get_pdd_rate(risk_level: str) -> float:
    """
    Get PDD rate by risk level.
    
    Args:
        risk_level: 'AA', 'BB', 'CC', 'DD', etc.
        
    Returns:
        PDD rate as decimal (0.03 = 3%)
    """
    rate_map = {
        'AA': PDD_RATES.LEVEL_1_DEFAULT,
        'AAA': PDD_RATES.LEVEL_1_DEFAULT,
        'BB': PDD_RATES.LEVEL_2_DEFAULT, 
        'BBB': PDD_RATES.LEVEL_2_DEFAULT,
        'CC': PDD_RATES.LEVEL_3_DEFAULT,
        'CCC': PDD_RATES.LEVEL_3_DEFAULT,
        'DD': PDD_RATES.LEVEL_4_DEFAULT,
        'DDD': PDD_RATES.LEVEL_4_DEFAULT,
        'E': PDD_RATES.LEVEL_4_DEFAULT,
        'F': PDD_RATES.LEVEL_4_DEFAULT,
        'G': PDD_RATES.LEVEL_4_DEFAULT,
        'H': PDD_RATES.LEVEL_4_DEFAULT,
    }
    return rate_map.get(risk_level.upper(), PDD_RATES.LEVEL_4_DEFAULT)


# Export main constants for easy import
__all__ = [
    'SUBORDINATION_LIMITS',
    'CONCENTRATION_LIMITS', 
    'PDD_RATES',
    'RISK_THRESHOLDS',
    'DATA_VALIDATION',
    'get_constant',
    'get_subordination_limit',
    'get_concentration_limit',
    'get_pdd_rate',
]