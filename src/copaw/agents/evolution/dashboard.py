# -*- coding: utf-8 -*-
"""
Evolution Dashboard - Visual analytics for self-evolution progress.

Features:
- Progress tracking
- Analytics visualization
- Trend reports
- Export to markdown/PDF

Usage:
    dashboard = EvolutionDashboard()
    dashboard.add_metrics(metrics)
    dashboard.generate_report()
    dashboard.export_markdown("report.md")
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class EvolutionMetrics:
    """Evolution metrics data structure"""
    
    timestamp: str
    total_errors: int = 0
    errors_captured: int = 0
    patterns_detected: int = 0
    suggestions_generated: int = 0
    improvements_applied: int = 0
    avg_confidence: float = 0.0
    evolution_score: float = 0.0


@dataclass
class EvolutionTrend:
    """Evolution trend data"""
    
    period: str  # daily, weekly, monthly
    start_date: str
    end_date: str
    metrics: List[EvolutionMetrics] = field(default_factory=list)
    trend_direction: str = "stable"  # improving, declining, stable
    key_insights: List[str] = field(default_factory=list)


class EvolutionDashboard:
    """
    Evolution dashboard for tracking self-improvement progress.
    
    Example:
        dashboard = EvolutionDashboard()
        dashboard.add_metrics(metrics)
        report = dashboard.generate_report()
        dashboard.export_markdown("evolution_report.md")
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize evolution dashboard.
        
        Args:
            db_path: Database path for persistence (optional)
        """
        self.db_path = db_path
        self.metrics_history: List[EvolutionMetrics] = []
        self.trends: Dict[str, EvolutionTrend] = {}
    
    def add_metrics(self, metrics: EvolutionMetrics) -> None:
        """
        Add metrics to dashboard.
        
        Args:
            metrics: EvolutionMetrics instance
        """
        self.metrics_history.append(metrics)
        logger.info(
            f"Added metrics: {metrics.errors_captured} errors, "
            f"{metrics.patterns_detected} patterns"
        )
    
    def add_metrics_dict(self, metrics_dict: Dict[str, Any]) -> None:
        """
        Add metrics from dictionary.
        
        Args:
            metrics_dict: Metrics dictionary
        """
        metrics = EvolutionMetrics(
            timestamp=metrics_dict.get("timestamp", datetime.now().isoformat()),
            total_errors=metrics_dict.get("total_errors", 0),
            errors_captured=metrics_dict.get("errors_captured", 0),
            patterns_detected=metrics_dict.get("patterns_detected", 0),
            suggestions_generated=metrics_dict.get("suggestions_generated", 0),
            improvements_applied=metrics_dict.get("improvements_applied", 0),
            avg_confidence=metrics_dict.get("avg_confidence", 0.0),
            evolution_score=metrics_dict.get("evolution_score", 0.0)
        )
        self.add_metrics(metrics)
    
    def calculate_evolution_score(self) -> float:
        """
        Calculate overall evolution score.
        
        Returns:
            Score from 0.0 to 100.0
        """
        if not self.metrics_history:
            return 0.0
        
        latest = self.metrics_history[-1]
        
        # Calculate score components
        error_handling_score = min(100, latest.errors_captured * 2)
        pattern_score = min(100, latest.patterns_detected * 10)
        suggestion_score = min(100, latest.suggestions_generated * 5)
        improvement_score = min(100, latest.improvements_applied * 20)
        
        # Weighted average
        score = (
            error_handling_score * 0.2 +
            pattern_score * 0.3 +
            suggestion_score * 0.2 +
            improvement_score * 0.3
        )
        
        return min(100.0, score)
    
    def analyze_trend(self, period: str = "daily") -> EvolutionTrend:
        """
        Analyze evolution trend.
        
        Args:
            period: Trend period (daily, weekly, monthly)
        
        Returns:
            EvolutionTrend instance
        """
        if not self.metrics_history:
            return EvolutionTrend(
                period=period,
                start_date="N/A",
                end_date="N/A"
            )
        
        # Filter metrics by period
        now = datetime.now()
        if period == "daily":
            delta = timedelta(days=1)
        elif period == "weekly":
            delta = timedelta(weeks=1)
        elif period == "monthly":
            delta = timedelta(days=30)
        else:
            delta = timedelta(days=1)
        
        start_time = now - delta
        
        filtered_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= start_time
        ]
        
        if not filtered_metrics:
            return EvolutionTrend(
                period=period,
                start_date=start_time.isoformat(),
                end_date=now.isoformat()
            )
        
        # Create trend
        trend = EvolutionTrend(
            period=period,
            start_date=filtered_metrics[0].timestamp,
            end_date=filtered_metrics[-1].timestamp,
            metrics=filtered_metrics
        )
        
        # Analyze trend direction
        if len(filtered_metrics) >= 2:
            first_score = self._calculate_metrics_score(filtered_metrics[0])
            last_score = self._calculate_metrics_score(filtered_metrics[-1])
            
            if last_score > first_score * 1.2:
                trend.trend_direction = "improving"
            elif last_score < first_score * 0.8:
                trend.trend_direction = "declining"
            else:
                trend.trend_direction = "stable"
        
        # Generate insights
        trend.key_insights = self._generate_insights(filtered_metrics)
        
        self.trends[period] = trend
        return trend
    
    def _calculate_metrics_score(self, metrics: EvolutionMetrics) -> float:
        """Calculate score for a single metrics instance"""
        return (
            metrics.errors_captured * 2 +
            metrics.patterns_detected * 10 +
            metrics.suggestions_generated * 5 +
            metrics.improvements_applied * 20
        )
    
    def _generate_insights(self, metrics: List[EvolutionMetrics]) -> List[str]:
        """Generate key insights from metrics"""
        insights = []
        
        if not metrics:
            return insights
        
        latest = metrics[-1]
        
        # Error handling insight
        if latest.errors_captured > 10:
            insights.append(
                f"Captured {latest.errors_captured} errors - "
                "excellent error monitoring!"
            )
        
        # Pattern detection insight
        if latest.patterns_detected > 5:
            insights.append(
                f"Detected {latest.patterns_detected} patterns - "
                "good pattern recognition!"
            )
        
        # Improvement insight
        if latest.improvements_applied > 0:
            insights.append(
                f"Applied {latest.improvements_applied} improvements - "
                "active self-evolution in progress!"
            )
        
        # Confidence insight
        if latest.avg_confidence > 0.8:
            insights.append(
                f"High confidence ({latest.avg_confidence:.2f}) - "
                "reliable analysis!"
            )
        
        if not insights:
            insights.append("Continue monitoring and improving!")
        
        return insights
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive evolution report.
        
        Returns:
            Report dictionary
        """
        report = {
            "summary": self._generate_summary(),
            "current_metrics": self._get_latest_metrics(),
            "trends": {},
            "insights": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add trends
        for period in ["daily", "weekly", "monthly"]:
            trend = self.analyze_trend(period)
            report["trends"][period] = {
                "direction": trend.trend_direction,
                "insights": trend.key_insights
            }
        
        # Add insights
        for trend in self.trends.values():
            report["insights"].extend(trend.key_insights)
        
        # Add recommendations
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        total_errors = sum(m.total_errors for m in self.metrics_history)
        total_captured = sum(m.errors_captured for m in self.metrics_history)
        total_patterns = sum(m.patterns_detected for m in self.metrics_history)
        total_improvements = sum(m.improvements_applied for m in self.metrics_history)
        
        return {
            "total_errors": total_errors,
            "total_captured": total_captured,
            "total_patterns": total_patterns,
            "total_improvements": total_improvements,
            "evolution_score": self.calculate_evolution_score(),
            "data_points": len(self.metrics_history)
        }
    
    def _get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get latest metrics"""
        if not self.metrics_history:
            return None
        
        latest = self.metrics_history[-1]
        return {
            "timestamp": latest.timestamp,
            "total_errors": latest.total_errors,
            "errors_captured": latest.errors_captured,
            "patterns_detected": latest.patterns_detected,
            "suggestions_generated": latest.suggestions_generated,
            "improvements_applied": latest.improvements_applied,
            "avg_confidence": latest.avg_confidence,
            "evolution_score": self.calculate_evolution_score()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if not self.metrics_history:
            return ["Start collecting evolution metrics"]
        
        latest = self.metrics_history[-1]
        
        if latest.errors_captured < 5:
            recommendations.append(
                "Increase error capture coverage - aim for 10+ errors/hour"
            )
        
        if latest.patterns_detected < 3:
            recommendations.append(
                "Enable pattern detection - look for recurring issues"
            )
        
        if latest.improvements_applied == 0:
            recommendations.append(
                "Apply improvements based on suggestions"
            )
        
        if latest.avg_confidence < 0.7:
            recommendations.append(
                "Improve analysis confidence with more data"
            )
        
        if not recommendations:
            recommendations.append(
                "Excellent progress! Continue monitoring and improving."
            )
        
        return recommendations
    
    def export_markdown(self, filepath: str) -> None:
        """
        Export report to markdown file.
        
        Args:
            filepath: Output file path
        """
        report = self.generate_report()
        
        md_content = self._generate_markdown(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Exported report to {filepath}")
    
    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """Generate markdown content"""
        md = []
        
        # Title
        md.append("# 🚀 Self-Evolution Progress Report\n")
        md.append(f"**Generated:** {report['timestamp']}\n")
        
        # Summary
        md.append("## 📊 Summary\n")
        summary = report.get('summary', {})
        md.append(f"- **Evolution Score:** {summary.get('evolution_score', 0):.1f}/100")
        md.append(f"- **Total Errors Captured:** {summary.get('total_captured', 0)}")
        md.append(f"- **Patterns Detected:** {summary.get('total_patterns', 0)}")
        md.append(f"- **Improvements Applied:** {summary.get('total_improvements', 0)}\n")
        
        # Current Metrics
        md.append("## 📈 Current Metrics\n")
        metrics = report.get('current_metrics', {})
        if metrics:
            for key, value in metrics.items():
                md.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        else:
            md.append("No metrics available yet.\n")
        md.append("")
        
        # Trends
        md.append("## 📉 Trends\n")
        trends = report.get('trends', {})
        for period, trend_data in trends.items():
            direction = trend_data.get('direction', 'stable')
            emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(direction, "➡️")
            md.append(f"- **{period.title()}:** {emoji} {direction}")
        md.append("")
        
        # Insights
        md.append("## 💡 Insights\n")
        for insight in report.get('insights', []):
            md.append(f"- {insight}")
        md.append("")
        
        # Recommendations
        md.append("## 🎯 Recommendations\n")
        for rec in report.get('recommendations', []):
            md.append(f"- {rec}")
        md.append("")
        
        return "\n".join(md)
    
    def to_json(self) -> str:
        """Export report to JSON"""
        report = self.generate_report()
        return json.dumps(report, indent=2, ensure_ascii=False)
