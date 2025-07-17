"""
Template System for Pool Configurations
========================================

Sistema de herança de templates em 3 camadas para configurações de escrituras.

Módulos:
- template_engine: Engine principal de herança e resolução
"""

from .template_engine import (
    TemplateEngine,
    TemplateResolution,
    create_pool_from_template,
    generate_template_coverage_report
)

__all__ = [
    'TemplateEngine',
    'TemplateResolution', 
    'create_pool_from_template',
    'generate_template_coverage_report'
]