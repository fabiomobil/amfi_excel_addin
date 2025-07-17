"""
Template Inheritance Engine
============================

Sistema de herança de templates em 3 camadas para configurações de pools.
Implementa o padrão de templates hierárquicos com resolução automática de
placeholders e validação de integridade.

Arquitetura:
- Tier 1: Universal Base (campos 100% comuns)  
- Tier 2: Escritura Patterns (especializações por tipo)
- Tier 3: Pool Overrides (customizações específicas)
"""

import json
import os
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TemplateResolution:
    """Resultado da resolução de template."""
    resolved_config: Dict[str, Any]
    tier1_template: str
    tier2_template: Optional[str]
    tier3_overrides: Optional[Dict[str, Any]]
    placeholders_resolved: Dict[str, Any]
    unresolved_placeholders: List[str]
    validation_errors: List[str]


class TemplateEngine:
    """
    Engine de herança de templates para configurações de pools.
    """
    
    def __init__(self, templates_base_path: str = "/mnt/c/amfi/config/templates"):
        self.templates_path = Path(templates_base_path)
        self.tier1_path = self.templates_path / "tier1"
        self.tier2_path = self.templates_path / "tier2"
        self.tier3_path = self.templates_path / "tier3"
        
        # Cache de templates carregados
        self.template_cache = {}
        
        # Mapeamento de tipos de escritura para templates tier2
        self.escritura_template_mapping = {
            "corporate_credit": "traditional_corporate.json",
            "fintech_digital": "fintech_simplified.json", 
            "agronegocio": "agronegocio_specialty.json",
            "mixed_model": "mixed_model.json"
        }
    
    def load_template_config(self, pool_id: str, escritura_type: str, 
                           tier3_overrides: Optional[Dict[str, Any]] = None,
                           variable_values: Optional[Dict[str, Any]] = None) -> TemplateResolution:
        """
        Carrega e resolve configuração completa do template.
        
        Args:
            pool_id: ID do pool
            escritura_type: Tipo de escritura detectado
            tier3_overrides: Customizações específicas do pool
            variable_values: Valores para resolução de placeholders
            
        Returns:
            TemplateResolution com configuração resolvida
        """
        # 1. Carregar template base (tier1)
        tier1_template = self._load_tier1_template()
        
        # 2. Carregar template de escritura (tier2)
        tier2_template = self._load_tier2_template(escritura_type)
        
        # 3. Resolver herança tier2 -> tier1
        base_config = self._resolve_inheritance(tier1_template, tier2_template)
        
        # 4. Aplicar overrides tier3
        if tier3_overrides:
            base_config = self._apply_tier3_overrides(base_config, tier3_overrides)
        
        # 5. Resolver placeholders
        variables = variable_values or {}
        resolved_config, placeholders_resolved, unresolved = self._resolve_placeholders(
            base_config, variables
        )
        
        # 6. Validar configuração final
        validation_errors = self._validate_resolved_config(resolved_config)
        
        return TemplateResolution(
            resolved_config=resolved_config,
            tier1_template="universal_base.json",
            tier2_template=self.escritura_template_mapping.get(escritura_type),
            tier3_overrides=tier3_overrides,
            placeholders_resolved=placeholders_resolved,
            unresolved_placeholders=unresolved,
            validation_errors=validation_errors
        )
    
    def _load_tier1_template(self) -> Dict[str, Any]:
        """Carrega template base universal."""
        template_path = self.tier1_path / "universal_base.json"
        return self._load_json_template(str(template_path))
    
    def _load_tier2_template(self, escritura_type: str) -> Optional[Dict[str, Any]]:
        """Carrega template de escritura específico."""
        template_file = self.escritura_template_mapping.get(escritura_type)
        if not template_file:
            return None
        
        template_path = self.tier2_path / template_file
        return self._load_json_template(str(template_path))
    
    def _load_json_template(self, template_path: str) -> Dict[str, Any]:
        """Carrega template JSON com cache."""
        if template_path in self.template_cache:
            return self.template_cache[template_path]
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comentários JSON (linhas iniciando com //)
                content = self._remove_json_comments(content)
                template = json.loads(content)
                
            self.template_cache[template_path] = template
            return template
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar template {template_path}: {e}")
    
    def _remove_json_comments(self, content: str) -> str:
        """Remove comentários de JSON estendido."""
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Remove linhas que são só comentários
            stripped = line.strip()
            if stripped.startswith('"//'):
                # Manter linhas de comentário como strings vazias para preservar estrutura
                if stripped.endswith('": "",'):
                    filtered_lines.append(line)
                # Pular comentários que não são parte da estrutura JSON
                continue
            else:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _resolve_inheritance(self, tier1: Dict[str, Any], 
                           tier2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve herança tier2 -> tier1."""
        if not tier2:
            return tier1.copy()
        
        # Fazer deep copy do tier1
        result = self._deep_copy(tier1)
        
        # Aplicar extensões do tier2
        for key, value in tier2.items():
            if key.startswith('//') or key == 'extends' or key == 'template_metadata':
                continue
                
            if key in result:
                # Merge inteligente para listas e dicionários
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_dicts(result[key], value)
                elif isinstance(value, list) and isinstance(result[key], list):
                    result[key] = self._merge_lists(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def _apply_tier3_overrides(self, config: Dict[str, Any], 
                              overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica overrides específicos do pool (tier3)."""
        result = self._deep_copy(config)
        
        for key, value in overrides.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _resolve_placeholders(self, config: Dict[str, Any], 
                            variables: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any], List[str]]:
        """Resolve placeholders no formato {{VARIABLE|default:value}}."""
        resolved_config = self._deep_copy(config)
        placeholders_resolved = {}
        unresolved_placeholders = []
        
        def resolve_value(value: Any) -> Any:
            if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                return self._resolve_single_placeholder(value, variables, placeholders_resolved, unresolved_placeholders)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            else:
                return value
        
        resolved_config = resolve_value(resolved_config)
        return resolved_config, placeholders_resolved, unresolved_placeholders
    
    def _resolve_single_placeholder(self, placeholder: str, variables: Dict[str, Any],
                                  resolved: Dict[str, Any], unresolved: List[str]) -> Any:
        """Resolve um placeholder individual."""
        # Extrair variável e valor padrão
        content = placeholder[2:-2]  # Remove {{ }}
        
        if '|default:' in content:
            var_name, default_value = content.split('|default:', 1)
            var_name = var_name.strip()
            default_value = default_value.strip()
        else:
            var_name = content.strip()
            default_value = None
        
        # Resolver valor
        if var_name in variables:
            resolved_value = variables[var_name]
            resolved[var_name] = resolved_value
            return resolved_value
        elif default_value is not None:
            # Tentar converter valor padrão para tipo apropriado
            converted_default = self._convert_default_value(default_value)
            resolved[var_name] = converted_default
            return converted_default
        else:
            unresolved.append(var_name)
            return placeholder  # Manter placeholder se não resolvido
    
    def _convert_default_value(self, value: str) -> Any:
        """Converte valor padrão string para tipo apropriado."""
        value = value.strip()
        
        # Boolean
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        
        # Null
        elif value.lower() == 'null':
            return None
        
        # Number
        elif value.replace('.', '').replace('-', '').isdigit():
            if '.' in value:
                return float(value)
            else:
                return int(value)
        
        # Array
        elif value.startswith('[') and value.endswith(']'):
            try:
                return json.loads(value)
            except:
                return value
        
        # Object
        elif value.startswith('{') and value.endswith('}'):
            try:
                return json.loads(value)
            except:
                return value
        
        # String (remove quotes if present)
        else:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
            return value
    
    def _validate_resolved_config(self, config: Dict[str, Any]) -> List[str]:
        """Valida configuração resolvida."""
        errors = []
        
        # Validações básicas
        required_fields = ['pool_id', 'pool_name', 'data_emissao', 'data_vencimento']
        for field in required_fields:
            if field not in config or config[field] is None:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Validar estrutura financeira
        if 'valores' in config:
            valores = config['valores']
            if isinstance(valores, dict):
                total_emissao = valores.get('total_emissao')
                senior = valores.get('senior')
                subordinada = valores.get('subordinada')
                
                if total_emissao and senior and subordinada:
                    try:
                        total_emissao = float(total_emissao) if isinstance(total_emissao, str) else total_emissao
                        senior = float(senior) if isinstance(senior, str) else senior
                        subordinada = float(subordinada) if isinstance(subordinada, str) else subordinada
                        
                        total = senior + subordinada
                        if abs(total - total_emissao) > 0.01:  # Tolerância para floating point
                            errors.append("Valores senior + subordinada não somam total_emissao")
                    except (ValueError, TypeError):
                        # Skip validation if values can't be converted to numbers
                        pass
        
        # Validar monitoramentos
        if 'monitoramentos_ativos' in config:
            monitores = config['monitoramentos_ativos']
            if isinstance(monitores, list):
                for monitor in monitores:
                    if isinstance(monitor, dict):
                        if 'id' not in monitor:
                            errors.append("Monitor sem ID definido")
                        if 'tipo' not in monitor:
                            errors.append(f"Monitor {monitor.get('id', 'unknown')} sem tipo")
        
        return errors
    
    def _merge_dicts(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Merge inteligente de dicionários."""
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def _merge_lists(self, base: List[Any], overlay: List[Any]) -> List[Any]:
        """Merge inteligente de listas."""
        # Por enquanto, sobrescrever lista base com overlay
        # Pode ser refinado no futuro para merge mais inteligente
        return overlay
    
    def _deep_copy(self, obj: Any) -> Any:
        """Cópia profunda de objeto."""
        if isinstance(obj, dict):
            return {key: self._deep_copy(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def generate_pool_config_from_template(self, pool_id: str, escritura_type: str,
                                         pool_values: Dict[str, Any],
                                         tier3_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gera configuração completa do pool a partir de templates.
        
        Args:
            pool_id: ID do pool
            escritura_type: Tipo de escritura
            pool_values: Valores específicos do pool
            tier3_overrides: Customizações específicas
            
        Returns:
            Configuração completa do pool
        """
        resolution = self.load_template_config(
            pool_id=pool_id,
            escritura_type=escritura_type,
            tier3_overrides=tier3_overrides,
            variable_values=pool_values
        )
        
        if resolution.validation_errors:
            raise ValueError(f"Erro de validação: {'; '.join(resolution.validation_errors)}")
        
        return resolution.resolved_config
    
    def validate_template_coverage(self, pools_directory: str = "/mnt/c/amfi/config/pools/") -> Dict[str, Any]:
        """
        Valida cobertura dos templates para pools existentes.
        
        Returns:
            Relatório de cobertura
        """
        import sys
        sys.path.append("/mnt/c/amfi/monitor/utils")
        from escritura_detector import analyze_all_pools
        
        # Analisar pools existentes
        pool_analyses = analyze_all_pools(pools_directory)
        
        coverage_report = {
            "total_pools": len(pool_analyses),
            "template_coverage": {},
            "pools_by_template": {},
            "coverage_percentage": 0,
            "missing_templates": [],
            "validation_summary": {}
        }
        
        supported_types = set(self.escritura_template_mapping.keys())
        pools_covered = 0
        
        for pool_file, analysis in pool_analyses.items():
            escritura_type = analysis.primary_type
            
            if escritura_type in supported_types:
                pools_covered += 1
                if escritura_type not in coverage_report["pools_by_template"]:
                    coverage_report["pools_by_template"][escritura_type] = []
                coverage_report["pools_by_template"][escritura_type].append(pool_file)
            else:
                coverage_report["missing_templates"].append({
                    "pool": pool_file,
                    "escritura_type": escritura_type,
                    "confidence": analysis.confidence_score
                })
        
        coverage_report["coverage_percentage"] = (pools_covered / len(pool_analyses)) * 100
        
        # Testar geração de template para pools cobertos
        validation_errors = []
        for escritura_type, pools in coverage_report["pools_by_template"].items():
            try:
                # Teste básico de carregamento
                test_resolution = self.load_template_config(
                    pool_id="TEST_POOL",
                    escritura_type=escritura_type,
                    variable_values={"POOL_ID": "TEST", "POOL_NAME": "Test Pool"}
                )
                coverage_report["validation_summary"][escritura_type] = {
                    "template_loads": True,
                    "validation_errors": len(test_resolution.validation_errors),
                    "unresolved_placeholders": len(test_resolution.unresolved_placeholders)
                }
            except Exception as e:
                validation_errors.append(f"Erro no template {escritura_type}: {e}")
                coverage_report["validation_summary"][escritura_type] = {
                    "template_loads": False,
                    "error": str(e)
                }
        
        coverage_report["global_validation_errors"] = validation_errors
        
        return coverage_report


# Funções de conveniência
def create_pool_from_template(pool_id: str, escritura_type: str, 
                            pool_values: Dict[str, Any],
                            tier3_overrides: Optional[Dict[str, Any]] = None,
                            output_path: Optional[str] = None) -> str:
    """Cria arquivo de configuração de pool a partir de template."""
    engine = TemplateEngine()
    
    config = engine.generate_pool_config_from_template(
        pool_id=pool_id,
        escritura_type=escritura_type,
        pool_values=pool_values,
        tier3_overrides=tier3_overrides
    )
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return output_path
    else:
        return json.dumps(config, indent=2, ensure_ascii=False)


def generate_template_coverage_report(pools_directory: str = "/mnt/c/amfi/config/pools/") -> str:
    """Gera relatório de cobertura dos templates."""
    engine = TemplateEngine()
    
    try:
        coverage = engine.validate_template_coverage(pools_directory)
    except Exception as e:
        return f"Erro ao gerar relatório: {e}"
    
    report = ["# RELATÓRIO DE COBERTURA DOS TEMPLATES", ""]
    report.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Pools Analisados:** {coverage['total_pools']}")
    report.append(f"**Cobertura:** {coverage['coverage_percentage']:.1f}%")
    report.append("")
    
    # Pools cobertos por template
    report.append("## 📋 POOLS COBERTOS POR TEMPLATE")
    for template, pools in coverage["pools_by_template"].items():
        report.append(f"### {template.replace('_', ' ').title()}")
        for pool in pools:
            report.append(f"- {pool}")
        report.append("")
    
    # Templates faltando
    if coverage["missing_templates"]:
        report.append("## ⚠️ TEMPLATES FALTANDO")
        for missing in coverage["missing_templates"]:
            report.append(f"- **{missing['pool']}**: {missing['escritura_type']} (confiança: {missing['confidence']:.1%})")
        report.append("")
    
    # Validação dos templates
    report.append("## ✅ VALIDAÇÃO DOS TEMPLATES")
    for template, validation in coverage["validation_summary"].items():
        if validation.get("template_loads"):
            status = "✅ OK"
            if validation.get("validation_errors", 0) > 0:
                status += f" ({validation['validation_errors']} avisos)"
            if validation.get("unresolved_placeholders", 0) > 0:
                status += f" ({validation['unresolved_placeholders']} placeholders)"
        else:
            status = f"❌ ERRO: {validation.get('error', 'Unknown')}"
        
        report.append(f"- **{template}**: {status}")
    
    if coverage["global_validation_errors"]:
        report.append("")
        report.append("## 🚨 ERROS GLOBAIS")
        for error in coverage["global_validation_errors"]:
            report.append(f"- {error}")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Exemplo de uso
    print("🔧 TESTANDO TEMPLATE ENGINE...")
    
    try:
        engine = TemplateEngine()
        
        # Testar carregamento de template
        resolution = engine.load_template_config(
            pool_id="TEST_POOL",
            escritura_type="corporate_credit",
            variable_values={
                "POOL_ID": "TEST_POOL_001", 
                "POOL_NAME": "Test Corporate Pool",
                "DATA_EMISSAO": "2025-01-01",
                "DATA_VENCIMENTO": "2028-01-01"
            }
        )
        
        print(f"✅ Template carregado com sucesso!")
        print(f"📊 Placeholders resolvidos: {len(resolution.placeholders_resolved)}")
        print(f"⚠️ Placeholders não resolvidos: {len(resolution.unresolved_placeholders)}")
        print(f"❌ Erros de validação: {len(resolution.validation_errors)}")
        
        # Gerar relatório de cobertura
        print("\n📈 GERANDO RELATÓRIO DE COBERTURA...")
        coverage_report = generate_template_coverage_report()
        print(coverage_report)
        
    except Exception as e:
        print(f"❌ Erro: {e}")