"""
Detector Automático de Tipos de Escritura
==========================================

Sistema que detecta automaticamente o tipo de escritura baseado nos padrões
de configuração dos pools, permitindo classificação automática e recomendação
de templates.
"""

import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class EscrituraAnalysis:
    """Resultado da análise de escritura."""
    primary_type: str
    confidence_score: float
    detected_patterns: Dict[str, str]
    risk_profile: str
    complexity_level: str
    hybrid_characteristics: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None


class EscrituraDetector:
    """
    Detector automático de tipos de escritura baseado em padrões configuracionais.
    """
    
    def __init__(self):
        self.pattern_weights = {
            "financial_structure": 30,
            "asset_types": 25, 
            "operational_complexity": 25,
            "term_structure": 20
        }
        
        self.escritura_templates = {
            "corporate_credit": {
                "subordinada_ratio_range": (0.15, 0.35),
                "monitor_count_min": 6,
                "term_months_min": 24,
                "asset_keywords": ["duplicata", "sacados_elegiveis"],
                "complexity_level": "high"
            },
            "fintech_digital": {
                "subordinada_ratio_range": (0.30, 0.50),
                "monitor_count_max": 5,
                "term_months_max": 24,
                "asset_keywords": ["ccb", "unidades_recebiveis", "pix"],
                "complexity_level": "simplified"
            },
            "agronegocio": {
                "subordinada_ratio_range": (0.15, 0.30),
                "monitor_count_min": 5,
                "term_months_range": (12, 48),
                "asset_keywords": ["cpr", "agricola", "setores"],
                "complexity_level": "medium"
            }
        }
    
    def detect_escritura_type(self, pool_config: Dict[str, Any]) -> EscrituraAnalysis:
        """
        Detecta o tipo de escritura principal para um pool.
        
        Args:
            pool_config: Configuração completa do pool
            
        Returns:
            EscrituraAnalysis com tipo detectado e metadados
        """
        # Calcular scores para cada tipo
        scores = self._calculate_type_scores(pool_config)
        
        # Determinar tipo principal
        primary_type = max(scores.keys(), key=lambda k: scores[k])
        confidence_score = scores[primary_type] / 100.0
        
        # Detectar padrões específicos
        patterns = {
            "financial_pattern": self._detect_financial_pattern(pool_config),
            "operational_pattern": self._detect_operational_complexity(pool_config),
            "asset_pattern": self._detect_asset_specialization(pool_config),
            "term_pattern": self._detect_term_structure(pool_config)
        }
        
        # Avaliar perfil de risco
        risk_profile = self._assess_risk_profile(pool_config, primary_type)
        
        # Detectar características híbridas
        hybrid_chars = self._detect_hybrid_characteristics(scores)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(primary_type, patterns, confidence_score)
        
        return EscrituraAnalysis(
            primary_type=primary_type,
            confidence_score=confidence_score,
            detected_patterns=patterns,
            risk_profile=risk_profile,
            complexity_level=patterns["operational_pattern"],
            hybrid_characteristics=hybrid_chars,
            recommendations=recommendations
        )
    
    def _calculate_type_scores(self, pool_config: Dict[str, Any]) -> Dict[str, float]:
        """Calcula scores para cada tipo de escritura."""
        scores = {
            "corporate_credit": 0,
            "fintech_digital": 0,
            "agronegocio": 0,
            "mixed_model": 0
        }
        
        # 1. Estrutura Financeira (30 pontos)
        subordinada_ratio = self._calculate_subordinada_ratio(pool_config)
        
        if subordinada_ratio <= 0.20:
            scores["corporate_credit"] += 25
            scores["agronegocio"] += 20
        elif subordinada_ratio <= 0.30:
            scores["corporate_credit"] += 30
            scores["agronegocio"] += 25
            scores["mixed_model"] += 15
        elif subordinada_ratio <= 0.35:
            scores["mixed_model"] += 30
            scores["fintech_digital"] += 20
        else:
            scores["fintech_digital"] += 30
            scores["mixed_model"] += 10
        
        # 2. Tipos de Ativos (25 pontos)
        asset_scores = self._score_asset_types(pool_config)
        for escritura_type, score in asset_scores.items():
            scores[escritura_type] += score
        
        # 3. Complexidade Operacional (25 pontos)
        complexity_scores = self._score_operational_complexity(pool_config)
        for escritura_type, score in complexity_scores.items():
            scores[escritura_type] += score
        
        # 4. Estrutura de Prazo (20 pontos)
        term_scores = self._score_term_structure(pool_config)
        for escritura_type, score in term_scores.items():
            scores[escritura_type] += score
        
        return scores
    
    def _calculate_subordinada_ratio(self, pool_config: Dict[str, Any]) -> float:
        """Calcula o ratio subordinada/total."""
        valores = pool_config.get("valores", {})
        subordinada = valores.get("subordinada", 0)
        total = valores.get("total_emissao", 1)  # Evitar divisão por zero
        return subordinada / total if total > 0 else 0
    
    def _score_asset_types(self, pool_config: Dict[str, Any]) -> Dict[str, float]:
        """Score baseado nos tipos de ativos."""
        scores = {"corporate_credit": 0, "fintech_digital": 0, "agronegocio": 0, "mixed_model": 0}
        
        # Verificar sacados elegíveis
        sacados = pool_config.get("sacados_elegiveis", [])
        if len(sacados) > 15:
            scores["corporate_credit"] += 20
        elif len(sacados) > 5:
            scores["mixed_model"] += 15
        
        # Verificar tipos de ativos específicos
        config_str = json.dumps(pool_config).lower()
        
        if any(keyword in config_str for keyword in ["ccb", "pix", "unidades_recebiveis"]):
            scores["fintech_digital"] += 25
        
        if any(keyword in config_str for keyword in ["cpr", "agricola", "agronegocio"]):
            scores["agronegocio"] += 25
        
        if any(keyword in config_str for keyword in ["duplicata", "titulo"]):
            scores["corporate_credit"] += 15
        
        return scores
    
    def _score_operational_complexity(self, pool_config: Dict[str, Any]) -> Dict[str, float]:
        """Score baseado na complexidade operacional."""
        scores = {"corporate_credit": 0, "fintech_digital": 0, "agronegocio": 0, "mixed_model": 0}
        
        monitor_count = len(pool_config.get("monitoramentos_ativos", []))
        
        if monitor_count >= 7:
            scores["corporate_credit"] += 25
        elif monitor_count >= 5:
            scores["agronegocio"] += 20
            scores["mixed_model"] += 15
        else:
            scores["fintech_digital"] += 25
        
        return scores
    
    def _score_term_structure(self, pool_config: Dict[str, Any]) -> Dict[str, float]:
        """Score baseado na estrutura de prazo."""
        scores = {"corporate_credit": 0, "fintech_digital": 0, "agronegocio": 0, "mixed_model": 0}
        
        term_months = self._calculate_term_months(pool_config)
        
        if term_months >= 36:
            scores["corporate_credit"] += 20
            scores["agronegocio"] += 15
        elif term_months >= 24:
            scores["agronegocio"] += 20
            scores["mixed_model"] += 15
        else:
            scores["fintech_digital"] += 20
        
        # Verificar carência
        carencia = pool_config.get("cronograma_pagamentos", {}).get("carencia_meses", 0)
        if carencia >= 6:
            scores["agronegocio"] += 5
            scores["corporate_credit"] += 3
        
        return scores
    
    def _calculate_term_months(self, pool_config: Dict[str, Any]) -> int:
        """Calcula o prazo em meses."""
        try:
            emissao_str = pool_config.get("data_emissao", "")
            vencimento_str = pool_config.get("data_vencimento", "")
            
            emissao = datetime.strptime(emissao_str, "%Y-%m-%d")
            vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d")
            
            # Aproximação de meses
            diff = vencimento - emissao
            return int(diff.days / 30.44)  # Média de dias por mês
        except:
            return 0
    
    def _detect_financial_pattern(self, pool_config: Dict[str, Any]) -> str:
        """Detecta padrão financeiro."""
        subordinada_ratio = self._calculate_subordinada_ratio(pool_config)
        
        if subordinada_ratio < 0.15:
            return "ultra_conservative"
        elif subordinada_ratio < 0.25:
            return "conservative"
        elif subordinada_ratio < 0.35:
            return "moderate"
        else:
            return "aggressive"
    
    def _detect_operational_complexity(self, pool_config: Dict[str, Any]) -> str:
        """Detecta complexidade operacional."""
        monitor_count = len(pool_config.get("monitoramentos_ativos", []))
        
        if monitor_count >= 7:
            return "high_sophistication"
        elif monitor_count >= 5:
            return "medium_sophistication"
        else:
            return "simplified"
    
    def _detect_asset_specialization(self, pool_config: Dict[str, Any]) -> str:
        """Detecta especialização de ativos."""
        config_str = json.dumps(pool_config).lower()
        
        if any(keyword in config_str for keyword in ["ccb", "pix", "unidades_recebiveis"]):
            return "fintech_assets"
        elif any(keyword in config_str for keyword in ["cpr", "agricola", "agronegocio"]):
            return "agro_assets"
        elif any(keyword in config_str for keyword in ["duplicata", "titulo"]):
            return "traditional_assets"
        else:
            return "mixed_assets"
    
    def _detect_term_structure(self, pool_config: Dict[str, Any]) -> str:
        """Detecta estrutura de prazo."""
        term_months = self._calculate_term_months(pool_config)
        
        if term_months <= 12:
            return "short_term"
        elif term_months <= 36:
            return "medium_term"
        else:
            return "long_term"
    
    def _assess_risk_profile(self, pool_config: Dict[str, Any], primary_type: str) -> str:
        """Avalia perfil de risco."""
        subordinada_ratio = self._calculate_subordinada_ratio(pool_config)
        
        # Concentração (se disponível)
        concentracao_individual = self._extract_concentration_limit(pool_config)
        
        risk_factors = []
        
        if subordinada_ratio < 0.20:
            risk_factors.append("low_subordination")
        elif subordinada_ratio > 0.40:
            risk_factors.append("high_subordination")
        
        if concentracao_individual and concentracao_individual < 0.05:
            risk_factors.append("ultra_conservative_concentration")
        elif concentracao_individual and concentracao_individual > 0.25:
            risk_factors.append("liberal_concentration")
        
        if len(risk_factors) == 0:
            return "balanced"
        elif "low_subordination" in risk_factors or "ultra_conservative" in risk_factors:
            return "conservative"
        else:
            return "aggressive"
    
    def _extract_concentration_limit(self, pool_config: Dict[str, Any]) -> Optional[float]:
        """Extrai limite de concentração individual."""
        try:
            monitores = pool_config.get("monitoramentos_ativos", [])
            for monitor in monitores:
                if monitor.get("id") == "concentracao":
                    config = monitor.get("configuracao", {})
                    return config.get("limite_individual_cedente") or config.get("limite_individual_sacado")
        except:
            pass
        return None
    
    def _detect_hybrid_characteristics(self, scores: Dict[str, float]) -> Optional[List[str]]:
        """Detecta características híbridas."""
        high_scores = [tipo for tipo, score in scores.items() if score > 60]
        
        if len(high_scores) > 1:
            return [f"hybrid_{tipo}" for tipo in high_scores]
        return None
    
    def _generate_recommendations(self, primary_type: str, patterns: Dict[str, str], confidence: float) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []
        
        if confidence < 0.7:
            recommendations.append("🔍 Baixa confiança na classificação - revisar configuração manualmente")
        
        template_mapping = {
            "corporate_credit": "Usar template 'Traditional Corporate' como base",
            "fintech_digital": "Usar template 'Fintech Simplified' como base", 
            "agronegocio": "Usar template 'Agronegócio Specialty' como base",
            "mixed_model": "Considerar template híbrido ou customização específica"
        }
        
        recommendations.append(f"📋 {template_mapping.get(primary_type, 'Template personalizado recomendado')}")
        
        if patterns["operational_pattern"] == "simplified" and primary_type == "corporate_credit":
            recommendations.append("⚠️ Complexidade operacional baixa para Corporate Credit - considerar mais monitores")
        
        if patterns["financial_pattern"] == "aggressive" and primary_type != "fintech_digital":
            recommendations.append("🔻 Ratio subordinada alto - avaliar adequação ao perfil de risco")
        
        return recommendations


# Funções de conveniência
def analyze_pool_file(pool_file_path: str) -> EscrituraAnalysis:
    """Analisa um arquivo de pool e retorna a classificação."""
    detector = EscrituraDetector()
    
    with open(pool_file_path, 'r', encoding='utf-8') as f:
        pool_config = json.load(f)
    
    return detector.detect_escritura_type(pool_config)


def analyze_all_pools(pools_directory: str = "/mnt/c/amfi/config/pools/") -> Dict[str, EscrituraAnalysis]:
    """Analisa todos os pools em um diretório."""
    results = {}
    
    for filename in os.listdir(pools_directory):
        if filename.endswith('.json'):
            pool_path = os.path.join(pools_directory, filename)
            try:
                results[filename] = analyze_pool_file(pool_path)
            except Exception as e:
                print(f"Erro ao analisar {filename}: {e}")
    
    return results


def generate_escritura_report(pools_directory: str = "/mnt/c/amfi/config/pools/") -> str:
    """Gera relatório completo de classificação de escrituras."""
    analyses = analyze_all_pools(pools_directory)
    
    report = ["# RELATÓRIO DE CLASSIFICAÇÃO DE ESCRITURAS", ""]
    report.append(f"**Data da Análise:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Pools Analisados:** {len(analyses)}")
    report.append("")
    
    # Resumo por tipo
    type_summary = {}
    for filename, analysis in analyses.items():
        tipo = analysis.primary_type
        type_summary[tipo] = type_summary.get(tipo, 0) + 1
    
    report.append("## 📊 DISTRIBUIÇÃO POR TIPO")
    for tipo, count in sorted(type_summary.items()):
        report.append(f"- **{tipo.replace('_', ' ').title()}**: {count} pools")
    
    report.append("")
    report.append("## 📋 ANÁLISE DETALHADA POR POOL")
    
    for filename, analysis in sorted(analyses.items()):
        pool_name = filename.replace('.json', '')
        report.append(f"### {pool_name}")
        report.append(f"- **Tipo:** {analysis.primary_type.replace('_', ' ').title()}")
        report.append(f"- **Confiança:** {analysis.confidence_score:.1%}")
        report.append(f"- **Perfil de Risco:** {analysis.risk_profile}")
        report.append(f"- **Complexidade:** {analysis.complexity_level}")
        
        if analysis.hybrid_characteristics:
            report.append(f"- **Características Híbridas:** {', '.join(analysis.hybrid_characteristics)}")
        
        if analysis.recommendations:
            report.append("- **Recomendações:**")
            for rec in analysis.recommendations:
                report.append(f"  - {rec}")
        
        report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Exemplo de uso
    print("🔍 ANALISANDO ESCRITURAS DOS POOLS...")
    report = generate_escritura_report()
    print(report)