# Evidence Engine - Output Generator
# Creates stakeholder-ready summaries and other outputs

from typing import List, Dict, Any, Optional
import json
import logging
from core.reasoning import get_engine

# Import prompts with error handling
try:
    from prompts.stakeholder import (
        SYSTEM_PROMPT_STAKEHOLDER,
        STAKEHOLDER_SUMMARY_PROMPT,
        CONVINCE_STAKEHOLDER_PROMPT,
        RESEARCH_GAPS_PROMPT,
        COUNTER_EVIDENCE_PROMPT,
    )
except ImportError as e:
    logging.warning(f"Failed to import stakeholder prompts: {e}. Using fallback prompts.")

    SYSTEM_PROMPT_STAKEHOLDER = """You are a communication assistant helping product managers create clear, defensible summaries.
Lead with insight, be concise, acknowledge uncertainty, and make findings defensible."""

    STAKEHOLDER_SUMMARY_PROMPT = """Generate stakeholder summary for:

Topic: {topic}
Evidence: {evidence_summary}
Patterns: {patterns}
Stakeholder: {stakeholder_context}

Respond with JSON: headline, evidence_base, key_findings, confidence, caveats, next_steps, reasoning_trace."""

    CONVINCE_STAKEHOLDER_PROMPT = """Help convince stakeholder:

Recommendation: {recommendation}
Evidence: {evidence}
Objections: {objections}
Context: {context}

Respond with JSON: objection_responses, suggested_framing, fallback_position."""

    RESEARCH_GAPS_PROMPT = """Identify research gaps:

Topic: {topic}
Evidence: {evidence_chunks}
Decisions: {decisions}

Respond with JSON: critical_gaps, important_gaps, nice_to_have_gaps, sufficient_evidence_areas."""

    COUNTER_EVIDENCE_PROMPT = """Find counter-evidence for:

Assumption: {assumption}
Evidence: {evidence_chunks}

Respond with JSON: counter_evidence, alternative_explanations, devil_advocate_summary, honest_assessment."""


class OutputGenerator:
    """
    Generates various outputs from analysis results.
    All outputs include full reasoning traces for transparency.
    """
    
    def __init__(self, api_key: str = None):
        self.engine = get_engine(api_key)
    
    def generate_stakeholder_summary(
        self,
        topic: str,
        evidence_summary: str,
        patterns: List[Dict],
        stakeholder_context: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a stakeholder-ready summary.
        
        Args:
            topic: What the research was about
            evidence_summary: Summary of evidence analyzed
            patterns: Key patterns found
            stakeholder_context: Who the stakeholder is, what they care about
            
        Returns:
            Formatted summary with full reasoning trace
        """
        
        patterns_formatted = json.dumps(patterns, indent=2) if patterns else "No patterns provided."
        
        user_prompt = STAKEHOLDER_SUMMARY_PROMPT.format(
            topic=topic,
            evidence_summary=evidence_summary,
            patterns=patterns_formatted,
            stakeholder_context=stakeholder_context or "No specific stakeholder context provided.",
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_STAKEHOLDER,
            user_prompt=user_prompt,
            action_type="stakeholder_summary",
            context={
                "topic": topic[:100],
                "pattern_count": len(patterns) if patterns else 0,
            },
        )
        
        return {
            "headline": result["result"].get("headline", ""),
            "evidence_base": result["result"].get("evidence_base", ""),
            "key_findings": result["result"].get("key_findings", []),
            "confidence": result["result"].get("confidence", {}),
            "caveats": result["result"].get("caveats", []),
            "next_steps": result["result"].get("next_steps", []),
            "stakeholder_ready_text": result["result"].get("stakeholder_ready_text", ""),
            "reasoning_trace": result["result"].get("reasoning_trace", result["reasoning_trace"]),
            "full_evidence_used": result["result"].get("full_evidence_used", []),
            "call_id": result["call_id"],
        }
    
    def generate_persuasion_guide(
        self,
        recommendation: str,
        evidence: List[Dict],
        objections: List[str],
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a guide for convincing a skeptical stakeholder.
        
        Args:
            recommendation: What the PM wants to recommend
            evidence: Supporting evidence
            objections: Likely stakeholder objections
            context: Additional context about the situation
            
        Returns:
            Objection responses and suggested framing
        """
        
        evidence_formatted = json.dumps(evidence, indent=2) if evidence else "No evidence provided."
        objections_formatted = "\n".join([f"- {obj}" for obj in objections]) if objections else "No objections specified."
        
        user_prompt = CONVINCE_STAKEHOLDER_PROMPT.format(
            recommendation=recommendation,
            evidence=evidence_formatted,
            objections=objections_formatted,
            context=context or "No additional context.",
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_STAKEHOLDER,
            user_prompt=user_prompt,
            action_type="persuasion_guide",
            context={
                "recommendation": recommendation[:100],
                "objection_count": len(objections) if objections else 0,
            },
        )
        
        return {
            "recommendation_summary": result["result"].get("recommendation_summary", ""),
            "objection_responses": result["result"].get("objection_responses", []),
            "areas_of_uncertainty": result["result"].get("areas_of_uncertainty", []),
            "suggested_framing": result["result"].get("suggested_framing", ""),
            "fallback_position": result["result"].get("fallback_position", ""),
            "suggested_script": result["result"].get("suggested_script", ""),
            "reasoning_trace": result["reasoning_trace"],
            "call_id": result["call_id"],
        }
    
    def identify_research_gaps(
        self,
        topic: str,
        evidence_chunks: List[Dict],
        decisions: str,
    ) -> Dict[str, Any]:
        """
        Identify what research is missing.
        
        Args:
            topic: The research topic/question
            evidence_chunks: What we have
            decisions: What decisions need to be made
            
        Returns:
            Prioritized gaps with suggestions
        """
        
        evidence_formatted = json.dumps(evidence_chunks, indent=2) if evidence_chunks else "No evidence provided."
        
        user_prompt = RESEARCH_GAPS_PROMPT.format(
            topic=topic,
            evidence_chunks=evidence_formatted,
            decisions=decisions,
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_STAKEHOLDER,
            user_prompt=user_prompt,
            action_type="gap_analysis",
            context={
                "topic": topic[:100],
                "evidence_count": len(evidence_chunks) if evidence_chunks else 0,
            },
        )
        
        return {
            "topic_evaluated": topic,
            "current_evidence_summary": result["result"].get("current_evidence_summary", ""),
            "critical_gaps": result["result"].get("critical_gaps", []),
            "important_gaps": result["result"].get("important_gaps", []),
            "nice_to_have_gaps": result["result"].get("nice_to_have_gaps", []),
            "sufficient_evidence_areas": result["result"].get("sufficient_evidence_areas", []),
            "recommendation": result["result"].get("recommendation", ""),
            "reasoning_trace": result["result"].get("reasoning_trace", result["reasoning_trace"]),
            "call_id": result["call_id"],
        }
    
    def find_counter_evidence(
        self,
        assumption: str,
        evidence_chunks: List[Dict],
    ) -> Dict[str, Any]:
        """
        Actively look for evidence against an assumption (debiasing).
        
        Args:
            assumption: The PM's assumption to challenge
            evidence_chunks: Available evidence
            
        Returns:
            Counter-evidence and alternative explanations
        """
        
        evidence_formatted = json.dumps(evidence_chunks, indent=2) if evidence_chunks else "No evidence provided."
        
        user_prompt = COUNTER_EVIDENCE_PROMPT.format(
            assumption=assumption,
            evidence_chunks=evidence_formatted,
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_STAKEHOLDER,
            user_prompt=user_prompt,
            action_type="counter_evidence",
            context={
                "assumption": assumption[:100],
                "evidence_count": len(evidence_chunks) if evidence_chunks else 0,
            },
        )
        
        return {
            "assumption_tested": assumption,
            "counter_evidence": result["result"].get("counter_evidence", []),
            "alternative_explanations": result["result"].get("alternative_explanations", []),
            "what_would_disprove": result["result"].get("what_would_disprove", []),
            "devil_advocate_summary": result["result"].get("devil_advocate_summary", ""),
            "honest_assessment": result["result"].get("honest_assessment", ""),
            "reasoning_trace": result["result"].get("reasoning_trace", result["reasoning_trace"]),
            "call_id": result["call_id"],
        }
    
    def format_for_export(
        self,
        content: Dict[str, Any],
        format_type: str = "markdown",
    ) -> str:
        """
        Format output for export.
        
        Args:
            content: The content to format
            format_type: 'markdown' or 'plain'
            
        Returns:
            Formatted string
        """
        
        if format_type == "markdown":
            return self._format_markdown(content)
        else:
            return self._format_plain(content)
    
    def _format_markdown(self, content: Dict[str, Any]) -> str:
        """Format content as Markdown."""
        lines = []
        
        if content.get("headline"):
            lines.append(f"# {content['headline']}\n")
        
        if content.get("evidence_base"):
            lines.append(f"**Evidence Base:** {content['evidence_base']}\n")
        
        if content.get("key_findings"):
            lines.append("## Key Findings\n")
            for finding in content["key_findings"]:
                if isinstance(finding, dict):
                    lines.append(f"- **{finding.get('finding', '')}**")
                    if finding.get("evidence_reference"):
                        lines.append(f"  - *Evidence:* {finding['evidence_reference']}")
                    if finding.get("implication"):
                        lines.append(f"  - *Implication:* {finding['implication']}")
                else:
                    lines.append(f"- {finding}")
            lines.append("")
        
        if content.get("confidence"):
            conf = content["confidence"]
            if isinstance(conf, dict):
                lines.append(f"**Confidence Level:** {conf.get('level', 'Unknown').upper()}")
                if conf.get("explanation"):
                    lines.append(f"> {conf['explanation']}\n")
        
        if content.get("caveats"):
            lines.append("## Caveats & Gaps\n")
            for caveat in content["caveats"]:
                lines.append(f"- ⚠️ {caveat}")
            lines.append("")
        
        if content.get("next_steps"):
            lines.append("## Recommended Next Steps\n")
            for step in content["next_steps"]:
                if isinstance(step, dict):
                    lines.append(f"- **{step.get('action', '')}**")
                    if step.get("rationale"):
                        lines.append(f"  - *Rationale:* {step['rationale']}")
                else:
                    lines.append(f"- {step}")
            lines.append("")
        
        if content.get("reasoning_trace"):
            lines.append("---\n")
            lines.append("## Reasoning Trace (Internal Reference)\n")
            for step in content["reasoning_trace"]:
                lines.append(f"- {step}")
        
        return "\n".join(lines)
    
    def _format_plain(self, content: Dict[str, Any]) -> str:
        """Format content as plain text."""
        lines = []
        
        if content.get("headline"):
            lines.append(content["headline"].upper())
            lines.append("=" * len(content["headline"]))
            lines.append("")
        
        if content.get("stakeholder_ready_text"):
            lines.append(content["stakeholder_ready_text"])
        
        return "\n".join(lines)


# Convenience function
def generate_summary(topic: str, evidence: str, patterns: List[Dict], api_key: str = None) -> Dict[str, Any]:
    """Quick summary generation."""
    generator = OutputGenerator(api_key)
    return generator.generate_stakeholder_summary(topic, evidence, patterns)
