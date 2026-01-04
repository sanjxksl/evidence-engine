# Evidence Engine - Synthesizer
# Pattern finding, hypothesis testing, and evidence analysis

from typing import List, Dict, Any, Optional
import json
import logging
from core.reasoning import get_engine

# Import prompts with error handling
try:
    from prompts.hypothesis import (
        SYSTEM_PROMPT_HYPOTHESIS,
        HYPOTHESIS_TEST_PROMPT,
        HYPOTHESIS_CHALLENGE_PROMPT,
    )
except ImportError as e:
    logging.warning(f"Failed to import hypothesis prompts: {e}. Using fallback prompts.")

    SYSTEM_PROMPT_HYPOTHESIS = """You are a hypothesis testing assistant for product managers.
Test hypotheses against available evidence. Be adversarial and look for counter-evidence.
Return JSON with: hypothesis_restated, verdict, confidence, supporting_evidence, counter_evidence, evidence_gaps, reasoning_trace."""

    HYPOTHESIS_TEST_PROMPT = """Test this hypothesis: {hypothesis}

Available evidence: {evidence_chunks}

Respond with JSON including verdict (SUPPORTED/PARTIALLY_SUPPORTED/INCONCLUSIVE/NOT_SUPPORTED/REFUTED) and reasoning."""

    HYPOTHESIS_CHALLENGE_PROMPT = """Re-evaluate this analysis based on challenge: {challenge}

Previous analysis: {previous_analysis}"""

try:
    from prompts.synthesis import (
        SYSTEM_PROMPT_SYNTHESIS,
        PATTERN_SYNTHESIS_PROMPT,
        CLUSTER_EVIDENCE_PROMPT,
        CONFIDENCE_ASSESSMENT_PROMPT,
    )
except ImportError as e:
    logging.warning(f"Failed to import synthesis prompts: {e}. Using fallback prompts.")

    SYSTEM_PROMPT_SYNTHESIS = """You are a synthesis assistant for product managers.
Find patterns, contradictions, and gaps in evidence.
Return JSON with: patterns, contradictions, gaps, synthesis_summary, reasoning_trace."""

    PATTERN_SYNTHESIS_PROMPT = """Find patterns in this evidence: {evidence_chunks}

Context: {context}

Respond with JSON including patterns, contradictions, and gaps."""

    CLUSTER_EVIDENCE_PROMPT = """Cluster this evidence by theme: {evidence_chunks}"""

    CONFIDENCE_ASSESSMENT_PROMPT = """Assess confidence for: {problem_statement}

Evidence: {evidence_chunks}

Respond with JSON including dimensions, overall_confidence, reasoning, and recommendations."""


class Synthesizer:
    """
    Analyzes evidence: finds patterns, tests hypotheses, assesses confidence.
    All operations are fully transparent with reasoning traces.
    """
    
    def __init__(self, api_key: str = None):
        self.engine = get_engine(api_key)
    
    def _format_evidence_for_prompt(self, chunks: List[Dict]) -> str:
        """Format evidence chunks for inclusion in prompts."""
        formatted = []
        for i, chunk in enumerate(chunks):
            formatted.append(f"""
[Evidence #{i+1}]
ID: {chunk.get('id', i+1)}
Type: {chunk.get('evidence_type', 'unknown')}
Source: {chunk.get('source', 'unknown')}
Strength: {chunk.get('strength', 'unknown')}
Content: {chunk.get('content', '')}
""")
        return "\n".join(formatted)
    
    def test_hypothesis(
        self,
        hypothesis: str,
        evidence_chunks: List[Dict],
    ) -> Dict[str, Any]:
        """
        Test a hypothesis against available evidence.
        
        Args:
            hypothesis: The hypothesis to test
            evidence_chunks: List of evidence chunks to evaluate
            
        Returns:
            Detailed hypothesis test result with full reasoning
        """
        
        evidence_formatted = self._format_evidence_for_prompt(evidence_chunks)
        
        user_prompt = HYPOTHESIS_TEST_PROMPT.format(
            hypothesis=hypothesis,
            evidence_chunks=evidence_formatted,
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_HYPOTHESIS,
            user_prompt=user_prompt,
            action_type="hypothesis_test",
            context={
                "hypothesis": hypothesis[:100],
                "evidence_count": len(evidence_chunks),
            },
        )
        
        return {
            "hypothesis": hypothesis,
            "hypothesis_restated": result["result"].get("hypothesis_restated", hypothesis),
            "verdict": result["result"].get("verdict", "INCONCLUSIVE"),
            "confidence": result["result"].get("confidence", "unknown"),
            "confidence_reasoning": result["result"].get("confidence_reasoning", ""),
            "supporting_evidence": result["result"].get("supporting_evidence", []),
            "counter_evidence": result["result"].get("counter_evidence", []),
            "neutral_evidence": result["result"].get("neutral_evidence", []),
            "evidence_gaps": result["result"].get("evidence_gaps", []),
            "verdict_summary": result["result"].get("verdict_summary", ""),
            "reasoning_trace": result["result"].get("reasoning_trace", result["reasoning_trace"]),
            "call_id": result["call_id"],
        }
    
    def challenge_hypothesis_result(
        self,
        previous_analysis: Dict[str, Any],
        challenge: str,
    ) -> Dict[str, Any]:
        """
        Re-evaluate hypothesis analysis based on PM challenge.
        
        Args:
            previous_analysis: The previous hypothesis test result
            challenge: PM's challenge or additional context
            
        Returns:
            Updated analysis or explanation of why original stands
        """
        
        user_prompt = HYPOTHESIS_CHALLENGE_PROMPT.format(
            challenge=challenge,
            previous_analysis=json.dumps(previous_analysis, indent=2),
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_HYPOTHESIS,
            user_prompt=user_prompt,
            action_type="hypothesis_challenge",
            context={"challenge": challenge[:200]},
        )
        
        return {
            "original_verdict": previous_analysis.get("verdict"),
            "challenge": challenge,
            "response": result["result"],
            "reasoning_trace": result["reasoning_trace"],
            "call_id": result["call_id"],
        }
    
    def find_patterns(
        self,
        evidence_chunks: List[Dict],
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Find patterns and themes in evidence.
        
        Args:
            evidence_chunks: List of evidence to analyze
            context: Optional context about what PM is looking for
            
        Returns:
            Patterns, contradictions, gaps, and surprises
        """
        
        evidence_formatted = self._format_evidence_for_prompt(evidence_chunks)
        
        user_prompt = PATTERN_SYNTHESIS_PROMPT.format(
            evidence_chunks=evidence_formatted,
            context=context or "No specific context provided.",
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_SYNTHESIS,
            user_prompt=user_prompt,
            action_type="pattern_synthesis",
            context={"evidence_count": len(evidence_chunks)},
        )
        
        return {
            "patterns": result["result"].get("patterns", []),
            "contradictions": result["result"].get("contradictions", []),
            "gaps": result["result"].get("gaps", []),
            "surprises": result["result"].get("surprises", []),
            "synthesis_summary": result["result"].get("synthesis_summary", ""),
            "reasoning_trace": result["result"].get("reasoning_trace", result["reasoning_trace"]),
            "call_id": result["call_id"],
        }
    
    def cluster_evidence(
        self,
        evidence_chunks: List[Dict],
    ) -> Dict[str, Any]:
        """
        Group evidence by theme/topic.
        
        Args:
            evidence_chunks: List of evidence to cluster
            
        Returns:
            Clusters with evidence assignments
        """
        
        evidence_formatted = self._format_evidence_for_prompt(evidence_chunks)
        
        user_prompt = CLUSTER_EVIDENCE_PROMPT.format(
            evidence_chunks=evidence_formatted,
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_SYNTHESIS,
            user_prompt=user_prompt,
            action_type="clustering",
            context={"evidence_count": len(evidence_chunks)},
        )
        
        return {
            "clusters": result["result"].get("clusters", []),
            "unclustered": result["result"].get("unclustered", []),
            "cross_cluster_connections": result["result"].get("cross_cluster_connections", []),
            "reasoning_trace": result["result"].get("reasoning_trace", result["reasoning_trace"]),
            "call_id": result["call_id"],
        }
    
    def assess_confidence(
        self,
        problem_statement: str,
        evidence_chunks: List[Dict],
    ) -> Dict[str, Any]:
        """
        Assess overall evidence strength for a problem area.
        
        Args:
            problem_statement: The problem/opportunity being evaluated
            evidence_chunks: Available evidence
            
        Returns:
            Multi-dimensional confidence assessment
        """
        
        evidence_formatted = self._format_evidence_for_prompt(evidence_chunks)
        
        user_prompt = CONFIDENCE_ASSESSMENT_PROMPT.format(
            problem_statement=problem_statement,
            evidence_chunks=evidence_formatted,
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_SYNTHESIS,
            user_prompt=user_prompt,
            action_type="confidence_assessment",
            context={
                "problem": problem_statement[:100],
                "evidence_count": len(evidence_chunks),
            },
        )
        
        return {
            "problem_evaluated": problem_statement,
            "dimensions": result["result"].get("dimensions", {}),
            "overall_confidence": result["result"].get("overall_confidence", "unknown"),
            "overall_reasoning": result["result"].get("overall_reasoning", ""),
            "what_would_increase_confidence": result["result"].get("what_would_increase_confidence", []),
            "what_would_decrease_confidence": result["result"].get("what_would_decrease_confidence", []),
            "recommendation": result["result"].get("recommendation", ""),
            "reasoning_trace": result["reasoning_trace"],
            "call_id": result["call_id"],
        }


# Convenience functions
def test_hypothesis(hypothesis: str, evidence: List[Dict], api_key: str = None) -> Dict[str, Any]:
    """Quick hypothesis test."""
    synthesizer = Synthesizer(api_key)
    return synthesizer.test_hypothesis(hypothesis, evidence)

def find_patterns(evidence: List[Dict], context: str = "", api_key: str = None) -> Dict[str, Any]:
    """Quick pattern finding."""
    synthesizer = Synthesizer(api_key)
    return synthesizer.find_patterns(evidence, context)
