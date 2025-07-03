"""
Monitoring Gap Detector - Identifies monitoring events defined in JSON but not implemented in code
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import re


class MonitoringGapDetector:
    def __init__(self, json_dir: str = "../data/escrituras", code_dir: str = "."):
        self.json_dir = Path(json_dir)
        self.code_dir = Path(code_dir)
        self.implemented_monitors = set()
        self.defined_monitors = {}
        
    def scan_json_monitors(self) -> Dict[str, List[Dict]]:
        """Extract all monitoring events defined in pool JSONs"""
        all_monitors = {}
        
        for json_file in self.json_dir.glob("*_pool_*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            pool_name = list(data.keys())[0]
            pool_data = data[pool_name]
            
            monitors = []
            
            # Standard monitoring events
            if "eventos_de_monitoramento" in pool_data:
                for evento in pool_data["eventos_de_monitoramento"]:
                    if evento.get("ativo", True):  # Only active monitors
                        monitors.append({
                            "tipo": evento["tipo"],
                            "descricao": evento["descricao"],
                            "categoria": "evento_monitoramento",
                            "fonte": f"{json_file.name}#eventos_de_monitoramento"
                        })
            
            # Recovery mechanisms
            if "mecanismos_recuperacao" in pool_data:
                for mech_type, mech_data in pool_data["mecanismos_recuperacao"].items():
                    if isinstance(mech_data, dict) and mech_data.get("ativo", True):
                        monitors.append({
                            "tipo": f"recovery_{mech_type}",
                            "descricao": mech_data.get("descricao", f"Recovery mechanism: {mech_type}"),
                            "categoria": "mecanismo_recuperacao",
                            "fonte": f"{json_file.name}#mecanismos_recuperacao.{mech_type}"
                        })
            
            # Early maturity events
            if "vencimento_antecipado" in pool_data:
                for evento in pool_data["vencimento_antecipado"]:
                    if evento.get("ativo", True):
                        monitors.append({
                            "tipo": f"vencimento_{evento['tipo']}",
                            "descricao": evento["descricao"],
                            "categoria": "vencimento_antecipado",
                            "fonte": f"{json_file.name}#vencimento_antecipado"
                        })
            
            # Compliance cure events  
            if "obrigacoes_cura" in pool_data:
                for obrigacao in pool_data["obrigacoes_cura"]:
                    if obrigacao.get("ativo", True):
                        monitors.append({
                            "tipo": f"cura_{obrigacao['tipo']}",
                            "descricao": obrigacao.get("descricao", f"Cure obligation: {obrigacao['tipo']}"),
                            "categoria": "obrigacao_cura",
                            "fonte": f"{json_file.name}#obrigacoes_cura"
                        })
            
            all_monitors[pool_name] = monitors
            
        self.defined_monitors = all_monitors
        return all_monitors
    
    def scan_implemented_monitors(self) -> Set[str]:
        """Scan Python code to find implemented monitoring functions"""
        monitor_patterns = [
            # Direct monitor implementations
            r'def\s+monitor_(\w+)\s*\(',
            r'def\s+check_(\w+)\s*\(',
            r'def\s+validate_(\w+)\s*\(',
            r'def\s+calculate_(\w+)\s*\(',
            
            # Monitor type references
            r'monitor_type\s*==?\s*["\'](\w+)["\']',
            r'evento\[["\']tipo["\']\]\s*==?\s*["\'](\w+)["\']',
            r'if\s+["\'](\w+)["\']\s+in\s+monitors',
            
            # Recovery mechanism checks
            r'recovery_(\w+)_check',
            r'check_recovery_(\w+)',
            
            # Concentration checks
            r'concentracao_(\w+)',
            r'check_concentration_(\w+)',
        ]
        
        implemented = set()
        
        # Scan all Python files
        for py_file in self.code_dir.glob("*.py"):
            if py_file.name == "monitoring_gap_detector.py":
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check each pattern
            for pattern in monitor_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                implemented.update(matches)
        
        # Add common monitor implementations
        # These might be implemented generically
        generic_monitors = {
            "subordinacao", "indice_subordinacao",
            "concentracao", "concentracao_sacado", "concentracao_cedente",
            "inadimplencia", "recovery_rate",
            "vencimento", "prazo"
        }
        
        # Check if generic implementations exist
        for monitor in generic_monitors:
            if any(monitor in impl for impl in implemented):
                implemented.add(monitor)
        
        self.implemented_monitors = implemented
        return implemented
    
    def find_monitoring_gaps(self) -> Dict[str, List[Dict]]:
        """Find monitoring events defined but not implemented"""
        self.scan_json_monitors()
        self.scan_implemented_monitors()
        
        gaps = {}
        
        for pool_name, monitors in self.defined_monitors.items():
            pool_gaps = []
            
            for monitor in monitors:
                monitor_type = monitor["tipo"]
                
                # Check if this monitor type is implemented
                is_implemented = False
                
                # Direct match
                if monitor_type in self.implemented_monitors:
                    is_implemented = True
                
                # Partial match (e.g., "concentracao_sacado_individual" matches "concentracao")
                for impl in self.implemented_monitors:
                    if impl in monitor_type or monitor_type in impl:
                        is_implemented = True
                        break
                
                # Check for generic handlers
                monitor_keywords = monitor_type.split('_')
                for keyword in monitor_keywords:
                    if keyword in self.implemented_monitors:
                        is_implemented = True
                        break
                
                if not is_implemented:
                    pool_gaps.append(monitor)
            
            if pool_gaps:
                gaps[pool_name] = pool_gaps
                
        return gaps
    
    def generate_pending_report(self) -> str:
        """Generate a detailed report of monitoring gaps"""
        gaps = self.find_monitoring_gaps()
        
        if not gaps:
            return "✅ All monitoring events are implemented!"
        
        report = ["# 🚨 MONITORING GAPS DETECTED\n"]
        report.append(f"Found {sum(len(g) for g in gaps.values())} unimplemented monitors across {len(gaps)} pools\n")
        
        # Summary by category
        category_counts = {}
        for pool_gaps in gaps.values():
            for gap in pool_gaps:
                cat = gap["categoria"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        report.append("## Summary by Category")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {cat}: {count} monitors")
        
        report.append("\n## Detailed Gap Analysis\n")
        
        # Group by monitor type across pools
        monitor_pools = {}
        for pool_name, pool_gaps in gaps.items():
            for gap in pool_gaps:
                monitor_type = gap["tipo"]
                if monitor_type not in monitor_pools:
                    monitor_pools[monitor_type] = {
                        "pools": [],
                        "categoria": gap["categoria"],
                        "descricao": gap["descricao"]
                    }
                monitor_pools[monitor_type]["pools"].append(pool_name)
        
        # Sort by number of pools affected
        sorted_monitors = sorted(monitor_pools.items(), key=lambda x: len(x[1]["pools"]), reverse=True)
        
        for monitor_type, info in sorted_monitors:
            report.append(f"### ❌ `{monitor_type}`")
            report.append(f"- **Category**: {info['categoria']}")
            report.append(f"- **Description**: {info['descricao']}")
            report.append(f"- **Affected Pools**: {', '.join(info['pools'])}")
            report.append(f"- **Priority**: {'HIGH' if len(info['pools']) > 1 else 'MEDIUM'}")
            report.append("")
        
        # Implementation suggestions
        report.append("\n## 📝 Implementation Checklist\n")
        
        # Group by category for implementation
        by_category = {}
        for monitor_type, info in monitor_pools.items():
            cat = info["categoria"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((monitor_type, info))
        
        for category, monitors in by_category.items():
            report.append(f"### {category}")
            for monitor_type, info in monitors:
                pools = ', '.join(info['pools'])
                report.append(f"- [ ] Implement `{monitor_type}` for: {pools}")
        
        return "\n".join(report)
    
    def generate_implementation_template(self, monitor_type: str) -> str:
        """Generate Python code template for unimplemented monitor"""
        # Find monitor info
        monitor_info = None
        for pool_monitors in self.defined_monitors.values():
            for monitor in pool_monitors:
                if monitor["tipo"] == monitor_type:
                    monitor_info = monitor
                    break
            if monitor_info:
                break
        
        if not monitor_info:
            return f"# Monitor type '{monitor_type}' not found in JSON definitions"
        
        template = f'''def monitor_{monitor_type}(pool_data: dict, portfolio_data: pd.DataFrame) -> dict:
    """
    Monitor: {monitor_info['descricao']}
    Category: {monitor_info['categoria']}
    Source: {monitor_info['fonte']}
    """
    result = {{
        "status": "pending_implementation",
        "monitor_type": "{monitor_type}",
        "timestamp": datetime.now().isoformat(),
        "violations": [],
        "metrics": {{}},
    }}
    
    # TODO: Implement monitoring logic
    # 1. Extract relevant configuration from pool_data
    # 2. Calculate current values from portfolio_data
    # 3. Compare against limits
    # 4. Populate violations if any
    
    return result
'''
        return template


def find_monitoring_gaps(json_dir: str = "../data/escrituras", code_dir: str = ".") -> Dict[str, List[Dict]]:
    """Main function to find monitoring gaps"""
    detector = MonitoringGapDetector(json_dir, code_dir)
    return detector.find_monitoring_gaps()


def generate_gap_report(json_dir: str = "../data/escrituras", code_dir: str = ".") -> str:
    """Generate monitoring gap report"""
    detector = MonitoringGapDetector(json_dir, code_dir)
    return detector.generate_pending_report()


def get_implementation_template(monitor_type: str, json_dir: str = "../data/escrituras") -> str:
    """Get implementation template for specific monitor"""
    detector = MonitoringGapDetector(json_dir, code_dir=".")
    detector.scan_json_monitors()
    return detector.generate_implementation_template(monitor_type)


if __name__ == "__main__":
    # Generate gap report
    report = generate_gap_report()
    print(report)
    
    # Save report
    with open("MONITORING_GAPS.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n📊 Report saved to MONITORING_GAPS.md")
    
    # Example: Get implementation template
    # template = get_implementation_template("recovery_rate_mensal")
    # print("\n📝 Implementation Template:\n")
    # print(template)