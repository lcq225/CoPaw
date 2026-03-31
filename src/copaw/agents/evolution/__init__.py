# -*- coding: utf-8 -*-
"""
Self-Evolution for CoPaw - Self-improving AI agent engine.

This module provides comprehensive self-evolution capabilities:
- Automatic error capture and classification
- Pattern detection and analysis
- AI-powered attribution (5-Why root cause analysis)
- Evolution dashboard and reporting

Example:
    from copaw.agents.evolution import SelfEvolution
    
    evolution = SelfEvolution()
    
    # Capture errors
    with evolution.catch_errors("operation"):
        risky_code()
    
    # Analyze patterns
    patterns = evolution.detect_patterns()
    
    # Get AI attribution
    analysis = evolution.analyze(error_record)
    
    # View dashboard
    dashboard = evolution.get_dashboard()
    dashboard.export_markdown("report.md")
"""

from .pattern_detector import AutoPatternDetector, PatternInfo
from .ai_attributor import AIAttributor, AttributionResult
from .dashboard import EvolutionDashboard, EvolutionMetrics, EvolutionTrend

__version__ = "1.0.0"
__author__ = "CoPaw Contributors"
__license__ = "Apache-2.0"

__all__ = [
    # Pattern Detection
    "AutoPatternDetector",
    "PatternInfo",
    
    # AI Attribution
    "AIAttributor",
    "AttributionResult",
    
    # Dashboard
    "EvolutionDashboard",
    "EvolutionMetrics",
    "EvolutionTrend",
]
