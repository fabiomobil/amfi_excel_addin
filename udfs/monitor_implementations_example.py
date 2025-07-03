"""
Example implementations of monitoring functions for the most critical gaps
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


def monitor_indice_subordinacao(pool_data: dict, portfolio_data: pd.DataFrame) -> dict:
    """
    Monitor: Mínimo 25% - razão entre saldo devedor subordinado e total
    Category: evento_monitoramento
    Pools: afa_pool_1, lecapital_pool_1, supersim_pool_1
    """
    result = {
        "status": "OK",
        "monitor_type": "indice_subordinacao",
        "timestamp": datetime.now().isoformat(),
        "violations": [],
        "metrics": {},
    }
    
    try:
        # Get pool configuration
        pool_config = list(pool_data.values())[0]
        min_subordinacao = pool_config["estrutura_financeira"]["indices_minimos"]["subordinacao_minima"]
        
        # Calculate current subordination index
        valor_senior = pool_config["estrutura_financeira"]["series_senior"]["valor_total_senior"]
        valor_subordinada = pool_config["estrutura_financeira"]["series_subordinadas"]["valor_total_subordinada"]
        valor_total = valor_senior + valor_subordinada
        
        # Account for portfolio losses/defaults
        if "valor_presente" in portfolio_data.columns:
            total_defaults = portfolio_data[portfolio_data["status"] == "inadimplente"]["valor_presente"].sum()
            valor_total -= total_defaults
        
        # Calculate index
        indice_atual = valor_subordinada / valor_total if valor_total > 0 else 0
        
        result["metrics"] = {
            "indice_atual": indice_atual,
            "indice_minimo": min_subordinacao,
            "valor_senior": valor_senior,
            "valor_subordinada": valor_subordinada,
            "valor_total": valor_total,
            "margem": indice_atual - min_subordinacao
        }
        
        # Check violation
        if indice_atual < min_subordinacao:
            result["status"] = "VIOLATION"
            result["violations"].append({
                "type": "subordinacao_abaixo_minimo",
                "severity": "HIGH",
                "current_value": indice_atual,
                "limit": min_subordinacao,
                "deficit": min_subordinacao - indice_atual,
                "cure_period_days": 15,
                "actions_required": ["cobranca_contrapartes", "recompra_direitos", "aportes_patrimonio"]
            })
            
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result


def monitor_recovery_rate_mensal(pool_data: dict, portfolio_data: pd.DataFrame, 
                                historical_data: Optional[List[pd.DataFrame]] = None) -> dict:
    """
    Monitor: Taxa de recuperação mensal mínima 95% - 3 ocorrências simultâneas abaixo do limite
    Category: evento_monitoramento
    Pool: supersim_pool_1
    """
    result = {
        "status": "OK",
        "monitor_type": "recovery_rate_mensal",
        "timestamp": datetime.now().isoformat(),
        "violations": [],
        "metrics": {},
    }
    
    try:
        # Get configuration
        pool_config = list(pool_data.values())[0]
        recovery_config = None
        
        # Find recovery rate configuration
        for evento in pool_config.get("eventos_de_monitoramento", []):
            if evento["tipo"] == "recovery_rate_mensal":
                recovery_config = evento
                break
        
        if not recovery_config:
            result["status"] = "CONFIG_ERROR"
            result["error"] = "Recovery rate configuration not found"
            return result
        
        min_recovery = recovery_config["limite"]  # 0.95
        window_months = recovery_config["janela_monitoramento"]  # 3
        
        # Calculate current month recovery rate
        if "data_pagamento" in portfolio_data.columns and "valor_aquisicao" in portfolio_data.columns:
            current_month = datetime.now().replace(day=1)
            last_month = current_month - timedelta(days=1)
            
            # Filter paid receivables this month
            portfolio_data["data_pagamento"] = pd.to_datetime(portfolio_data["data_pagamento"])
            paid_this_month = portfolio_data[
                (portfolio_data["data_pagamento"].dt.year == last_month.year) &
                (portfolio_data["data_pagamento"].dt.month == last_month.month)
            ]
            
            valor_pago = paid_this_month["valor_pago"].sum() if "valor_pago" in paid_this_month.columns else 0
            valor_aquisicao = paid_this_month["valor_aquisicao"].sum()
            
            recovery_rate = valor_pago / valor_aquisicao if valor_aquisicao > 0 else 0
        else:
            recovery_rate = 0.95  # Default if columns missing
        
        result["metrics"]["recovery_rate_atual"] = recovery_rate
        result["metrics"]["limite_minimo"] = min_recovery
        
        # Check historical window (would need historical data in real implementation)
        if historical_data and len(historical_data) >= window_months - 1:
            consecutive_violations = 0
            for hist_df in historical_data[-2:]:  # Last 2 months + current
                # Calculate historical recovery rates
                # (simplified - would need same calculation as above)
                hist_recovery = 0.94  # Placeholder
                if hist_recovery < min_recovery:
                    consecutive_violations += 1
            
            if recovery_rate < min_recovery:
                consecutive_violations += 1
            
            result["metrics"]["consecutive_violations"] = consecutive_violations
            
            if consecutive_violations >= window_months:
                result["status"] = "VIOLATION"
                result["violations"].append({
                    "type": "recovery_rate_abaixo_limite_consecutivo",
                    "severity": "CRITICAL",
                    "current_value": recovery_rate,
                    "limit": min_recovery,
                    "consecutive_months": consecutive_violations,
                    "trigger_event": "vencimento_antecipado_automatico"
                })
        
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result


def monitor_concentracao_sacado_individual(pool_data: dict, portfolio_data: pd.DataFrame) -> dict:
    """
    Monitor: Concentração máxima por sacado individual
    Category: evento_monitoramento
    Applicable to all pools with different limits
    """
    result = {
        "status": "OK",
        "monitor_type": "concentracao_sacado_individual",
        "timestamp": datetime.now().isoformat(),
        "violations": [],
        "metrics": {},
    }
    
    try:
        pool_config = list(pool_data.values())[0]
        
        # Find concentration limit
        limite_sacado = None
        limites = pool_config.get("criterios_elegibilidade", {}).get("limites_concentracao", {})
        
        if "sacado_individual" in limites:
            limite_sacado = limites["sacado_individual"]["limite"]
        else:
            # Legacy format
            limite_sacado = pool_config.get("criterios_elegibilidade", {}).get(
                "limites_carteira", {}
            ).get("concentracao_maxima_sacado", 0.27) / 100  # Convert to decimal
        
        if not portfolio_data.empty and "nome_sacado" in portfolio_data.columns:
            # Calculate total portfolio value
            total_portfolio = portfolio_data["valor_presente"].sum()
            
            # Group by sacado
            sacado_concentration = portfolio_data.groupby("nome_sacado")["valor_presente"].sum()
            sacado_concentration_pct = sacado_concentration / total_portfolio
            
            # Find violations
            violations = sacado_concentration_pct[sacado_concentration_pct > limite_sacado]
            
            result["metrics"] = {
                "limite_concentracao": limite_sacado,
                "total_portfolio": total_portfolio,
                "num_sacados": len(sacado_concentration),
                "max_concentracao": sacado_concentration_pct.max(),
                "sacado_max_concentracao": sacado_concentration_pct.idxmax()
            }
            
            if not violations.empty:
                result["status"] = "VIOLATION"
                for sacado, concentracao in violations.items():
                    result["violations"].append({
                        "type": "concentracao_sacado_excedida",
                        "severity": "HIGH",
                        "sacado": sacado,
                        "concentracao_atual": concentracao,
                        "limite": limite_sacado,
                        "excesso": concentracao - limite_sacado,
                        "valor_excedente": (concentracao - limite_sacado) * total_portfolio
                    })
        
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result


def monitor_direito_regresso_30_dias(pool_data: dict, portfolio_data: pd.DataFrame) -> dict:
    """
    Monitor: Direitos creditórios com 30+ dias de atraso elegíveis para regresso
    Category: evento_monitoramento / mecanismo_recuperacao
    Pool: supersim_pool_1
    """
    result = {
        "status": "OK",
        "monitor_type": "atraso_30_dias_direito_regresso",
        "timestamp": datetime.now().isoformat(),
        "violations": [],
        "metrics": {},
        "regresso_elegiveis": []
    }
    
    try:
        pool_config = list(pool_data.values())[0]
        
        # Check if pool has direito de regresso
        mecanismos = pool_config.get("mecanismos_recuperacao", {})
        direito_regresso = mecanismos.get("direito_regresso", {})
        
        if not direito_regresso.get("ativo", False):
            result["status"] = "NOT_APPLICABLE"
            return result
        
        prazo_elegibilidade = direito_regresso.get("prazo_elegibilidade_dias", 30)
        gatilhos = direito_regresso.get("gatilhos", ["fraude", "ma_formalizacao"])
        
        # Find overdue receivables
        if not portfolio_data.empty and "dias_atraso" in portfolio_data.columns:
            overdue_30 = portfolio_data[portfolio_data["dias_atraso"] >= prazo_elegibilidade]
            
            # Filter by trigger conditions (would need additional columns in real data)
            # For now, assume all 30+ day overdue are eligible
            
            if not overdue_30.empty:
                total_eligible = overdue_30["valor_presente"].sum()
                
                result["metrics"] = {
                    "prazo_elegibilidade_dias": prazo_elegibilidade,
                    "num_direitos_elegiveis": len(overdue_30),
                    "valor_total_elegivel": total_eligible,
                    "gatilhos_ativos": gatilhos
                }
                
                # List eligible receivables
                for _, row in overdue_30.iterrows():
                    result["regresso_elegiveis"].append({
                        "sacado": row.get("nome_sacado", "N/A"),
                        "cedente": row.get("nome_cedente", "N/A"),
                        "valor": row["valor_presente"],
                        "dias_atraso": row["dias_atraso"],
                        "data_vencimento": row.get("vencimento", "N/A"),
                        "acao_requerida": "direito_regresso_originador"
                    })
                
                result["status"] = "ACTION_REQUIRED"
                result["violations"].append({
                    "type": "direitos_elegiveis_regresso",
                    "severity": "MEDIUM",
                    "num_casos": len(overdue_30),
                    "valor_total": total_eligible,
                    "responsavel": "originador",
                    "prazo_acao": "imediato"
                })
        
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result


def run_all_monitors(pool_name: str, pool_data: dict, portfolio_data: pd.DataFrame) -> Dict[str, dict]:
    """
    Run all applicable monitors for a pool
    """
    results = {}
    
    # Define monitor mappings
    monitors = {
        "indice_subordinacao": monitor_indice_subordinacao,
        "recovery_rate_mensal": monitor_recovery_rate_mensal,
        "concentracao_sacado_individual": monitor_concentracao_sacado_individual,
        "atraso_30_dias_direito_regresso": monitor_direito_regresso_30_dias,
    }
    
    # Get active monitors for this pool
    pool_config = list(pool_data.values())[0]
    active_monitors = set()
    
    # Check eventos_de_monitoramento
    for evento in pool_config.get("eventos_de_monitoramento", []):
        if evento.get("ativo", True):
            active_monitors.add(evento["tipo"])
    
    # Check mecanismos_recuperacao
    for mech_name, mech_data in pool_config.get("mecanismos_recuperacao", {}).items():
        if isinstance(mech_data, dict) and mech_data.get("ativo", True):
            active_monitors.add(f"recovery_{mech_name}")
    
    # Run applicable monitors
    for monitor_type, monitor_func in monitors.items():
        if monitor_type in active_monitors or monitor_type in str(active_monitors):
            try:
                results[monitor_type] = monitor_func(pool_data, portfolio_data)
            except Exception as e:
                results[monitor_type] = {
                    "status": "ERROR",
                    "error": f"Failed to run monitor: {str(e)}"
                }
    
    return results


def generate_monitoring_report(results: Dict[str, dict]) -> str:
    """
    Generate a summary report from monitoring results
    """
    report = []
    report.append(f"# Monitoring Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    total_monitors = len(results)
    violations = sum(1 for r in results.values() if r.get("status") == "VIOLATION")
    errors = sum(1 for r in results.values() if r.get("status") == "ERROR")
    actions = sum(1 for r in results.values() if r.get("status") == "ACTION_REQUIRED")
    
    report.append("## Summary")
    report.append(f"- Total Monitors Run: {total_monitors}")
    report.append(f"- ✅ OK: {total_monitors - violations - errors - actions}")
    report.append(f"- ❌ Violations: {violations}")
    report.append(f"- ⚠️ Actions Required: {actions}")
    report.append(f"- 🚨 Errors: {errors}")
    report.append("")
    
    # Details
    if violations > 0 or actions > 0:
        report.append("## Critical Issues")
        for monitor_type, result in results.items():
            if result.get("status") in ["VIOLATION", "ACTION_REQUIRED"]:
                report.append(f"\n### {monitor_type}")
                report.append(f"**Status**: {result['status']}")
                
                if "metrics" in result:
                    report.append("**Metrics**:")
                    for key, value in result["metrics"].items():
                        report.append(f"- {key}: {value}")
                
                if "violations" in result:
                    report.append("**Violations**:")
                    for v in result["violations"]:
                        report.append(f"- {v.get('type', 'Unknown')}: {v.get('severity', 'N/A')}")
                        if "current_value" in v and "limit" in v:
                            report.append(f"  - Current: {v['current_value']:.2%}, Limit: {v['limit']:.2%}")
    
    return "\n".join(report)