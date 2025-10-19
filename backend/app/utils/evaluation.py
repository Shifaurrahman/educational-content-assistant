"""
Evaluation and metrics module for assessing lesson plan quality.
"""
from typing import List, Dict, Any, Tuple
from app.utils.logger import logger
import re


class LessonEvaluator:
    """Evaluates lesson plan quality with various metrics"""
    
    def __init__(self):
        self.relevance_threshold = 0.7
        self.citation_keywords = [
            "according to", "based on", "as stated in", "the document shows",
            "research indicates", "studies show", "as mentioned", "source"
        ]
    
    def evaluate_lesson(
        self, 
        lesson_plan: Dict[str, Any], 
        search_results: List[str] = None,
        agent_steps: List[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a lesson plan.
        
        Returns metrics including:
        - Relevance score
        - Citation accuracy
        - Completeness score
        - Quality score
        """
        try:
            metrics = {
                "relevance_score": self._calculate_relevance_score(lesson_plan, search_results),
                "citation_accuracy": self._calculate_citation_accuracy(lesson_plan, search_results),
                "completeness_score": self._calculate_completeness_score(lesson_plan),
                "quality_score": 0.0,
                "agent_efficiency": self._calculate_agent_efficiency(agent_steps)
            }
            
            # Overall quality score (weighted average)
            metrics["quality_score"] = (
                metrics["relevance_score"] * 0.3 +
                metrics["citation_accuracy"] * 0.2 +
                metrics["completeness_score"] * 0.3 +
                metrics["agent_efficiency"] * 0.2
            )
            
            metrics["quality_rating"] = self._get_quality_rating(metrics["quality_score"])
            
            logger.info(f"Evaluation completed: Quality Score = {metrics['quality_score']:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating lesson: {e}")
            return self._get_default_metrics()
    
    def _calculate_relevance_score(
        self, 
        lesson_plan: Dict[str, Any], 
        search_results: List[str]
    ) -> float:
        """
        Calculate how relevant the lesson content is to the source material.
        
        Method: Compare keywords and concepts between lesson and sources.
        Score: 0.0 (not relevant) to 1.0 (highly relevant)
        """
        if not search_results:
            return 0.5  # Neutral score if no search results available
        
        try:
            # Extract lesson content
            lesson_text = self._extract_lesson_text(lesson_plan)
            source_text = " ".join(search_results).lower()
            
            # Extract keywords (simple approach: words > 4 chars)
            lesson_keywords = set(re.findall(r'\b\w{5,}\b', lesson_text.lower()))
            source_keywords = set(re.findall(r'\b\w{5,}\b', source_text))
            
            if not source_keywords:
                return 0.5
            
            # Calculate overlap
            common_keywords = lesson_keywords.intersection(source_keywords)
            relevance = len(common_keywords) / len(source_keywords)
            
            # Normalize to 0.3 - 1.0 range (avoid too low scores)
            normalized_score = 0.3 + (relevance * 0.7)
            
            logger.info(f"Relevance score calculated: {normalized_score:.2f} ({len(common_keywords)} common keywords)")
            
            return min(normalized_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.5
    
    def _calculate_citation_accuracy(
        self, 
        lesson_plan: Dict[str, Any], 
        search_results: List[str]
    ) -> float:
        """
        Calculate citation accuracy - how well the lesson references sources.
        
        Method: 
        - Check for citation indicators
        - Verify cited content exists in sources
        Score: 0.0 (no citations) to 1.0 (accurate citations)
        """
        if not search_results:
            return 0.0
        
        try:
            lesson_text = self._extract_lesson_text(lesson_plan)
            
            # Count citation indicators
            citation_count = sum(
                1 for keyword in self.citation_keywords 
                if keyword in lesson_text.lower()
            )
            
            # Check if content outline mentions sources
            has_source_references = any(
                "source" in str(section).lower() or "document" in str(section).lower()
                for section in lesson_plan.get("content_outline", [])
            )
            
            # Check resources section
            resources = lesson_plan.get("resources", [])
            has_material_references = len(resources) > 0
            
            # Calculate score
            base_score = 0.0
            
            if citation_count > 0:
                base_score += 0.4
            if citation_count >= 3:
                base_score += 0.2
            if has_source_references:
                base_score += 0.2
            if has_material_references:
                base_score += 0.2
            
            logger.info(f"Citation accuracy: {base_score:.2f} ({citation_count} citations found)")
            
            return min(base_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating citation accuracy: {e}")
            return 0.0
    
    def _calculate_completeness_score(self, lesson_plan: Dict[str, Any]) -> float:
        """
        Calculate how complete the lesson plan is.
        
        Checks for:
        - Objectives (required)
        - Prerequisites (required)
        - Content outline (required)
        - Activities (required)
        - Assessments (required)
        - Resources (required)
        """
        try:
            required_fields = [
                ("objectives", 3),      # Min 3 objectives
                ("prerequisites", 2),    # Min 2 prerequisites
                ("content_outline", 3),  # Min 3 sections
                ("activities", 3),       # Min 3 activities
                ("assessments", 2),      # Min 2 assessments
                ("resources", 2)         # Min 2 resources
            ]
            
            score = 0.0
            total_checks = len(required_fields)
            
            for field, min_count in required_fields:
                field_value = lesson_plan.get(field, [])
                if isinstance(field_value, list) and len(field_value) >= min_count:
                    score += 1.0
                elif isinstance(field_value, list) and len(field_value) > 0:
                    score += 0.5  # Partial credit
            
            completeness = score / total_checks
            
            logger.info(f"Completeness score: {completeness:.2f}")
            
            return completeness
            
        except Exception as e:
            logger.error(f"Error calculating completeness: {e}")
            return 0.5
    
    def _calculate_agent_efficiency(self, agent_steps: List[str]) -> float:
        """
        Calculate how efficiently the agent completed the task.
        
        Checks:
        - Number of steps (fewer is better, but not too few)
        - Tool usage pattern
        - Completion status
        """
        if not agent_steps:
            return 0.5
        
        try:
            num_steps = len(agent_steps)
            
            # Optimal range: 3-6 steps
            if 3 <= num_steps <= 6:
                efficiency = 1.0
            elif num_steps < 3:
                efficiency = 0.6  # Too few steps, might be incomplete
            elif num_steps <= 10:
                efficiency = 0.8  # Acceptable
            else:
                efficiency = 0.5  # Too many steps, inefficient
            
            logger.info(f"Agent efficiency: {efficiency:.2f} ({num_steps} steps)")
            
            return efficiency
            
        except Exception as e:
            logger.error(f"Error calculating agent efficiency: {e}")
            return 0.5
    
    def _extract_lesson_text(self, lesson_plan: Dict[str, Any]) -> str:
        """Extract all text content from lesson plan"""
        text_parts = []
        
        # Objectives
        text_parts.extend(lesson_plan.get("objectives", []))
        
        # Prerequisites
        text_parts.extend(lesson_plan.get("prerequisites", []))
        
        # Content outline
        for section in lesson_plan.get("content_outline", []):
            if isinstance(section, dict):
                text_parts.append(section.get("title", ""))
                text_parts.append(section.get("content", ""))
        
        # Activities
        text_parts.extend(lesson_plan.get("activities", []))
        
        # Assessments
        text_parts.extend(lesson_plan.get("assessments", []))
        
        return " ".join(str(part) for part in text_parts)
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert quality score to rating"""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Very Good"
        elif score >= 0.7:
            return "Good"
        elif score >= 0.6:
            return "Satisfactory"
        else:
            return "Needs Improvement"
    
    def _get_default_metrics(self) -> Dict[str, Any]:
        """Return default metrics on error"""
        return {
            "relevance_score": 0.0,
            "citation_accuracy": 0.0,
            "completeness_score": 0.0,
            "quality_score": 0.0,
            "agent_efficiency": 0.0,
            "quality_rating": "Unknown"
        }


# Global evaluator instance
_evaluator = None

def get_evaluator() -> LessonEvaluator:
    """Get or create evaluator instance"""
    global _evaluator
    if _evaluator is None:
        _evaluator = LessonEvaluator()
    return _evaluator