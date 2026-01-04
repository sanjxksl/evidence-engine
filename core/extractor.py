# Evidence Engine - Evidence Extractor
# Parses raw research inputs into structured evidence chunks

from typing import List, Dict, Any, Optional
import logging
from core.reasoning import get_engine

# Import prompts with error handling
try:
    from prompts.extraction import (
        SYSTEM_PROMPT_EXTRACTOR,
        EXTRACTION_USER_PROMPT,
        EXTRACTION_FOLLOW_UP,
    )
except ImportError as e:
    logging.warning(f"Failed to import extraction prompts: {e}. Using fallback prompts.")

    # Fallback prompts
    SYSTEM_PROMPT_EXTRACTOR = """You are an evidence extraction assistant for product managers.
Extract structured evidence chunks from raw research notes.
Return JSON with: chunks (array), summary (string), concerns (array), skipped (array).
Each chunk must have: content, evidence_type, source, tags, strength, extraction_reasoning."""

    EXTRACTION_USER_PROMPT = """Extract evidence from this research:

{raw_input}

Context: {context}

Respond with JSON containing chunks, summary, concerns, and skipped items."""

    EXTRACTION_FOLLOW_UP = """Refine extraction based on feedback:

{feedback}

Original input: {raw_input}

Previous extraction: {previous_extraction}"""


class EvidenceExtractor:
    """
    Extracts structured evidence chunks from messy research inputs.
    """
    
    def __init__(self, api_key: str = None):
        self.engine = get_engine(api_key)
    
    def extract(
        self,
        raw_input: str,
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Extract evidence chunks from raw research input.
        
        Args:
            raw_input: The raw text (interview notes, feedback, etc.)
            context: Optional context about the research
            
        Returns:
            Dict with 'chunks', 'summary', 'concerns', 'skipped', and reasoning
        """
        
        user_prompt = EXTRACTION_USER_PROMPT.format(
            raw_input=raw_input,
            context=context or "No additional context provided.",
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_EXTRACTOR,
            user_prompt=user_prompt,
            action_type="extraction",
            context={"input_length": len(raw_input), "has_context": bool(context)},
        )
        
        return {
            "chunks": result["result"].get("chunks", []),
            "summary": result["result"].get("summary", ""),
            "concerns": result["result"].get("concerns", []),
            "skipped": result["result"].get("skipped", []),
            "reasoning_trace": result["reasoning_trace"],
            "call_id": result["call_id"],
        }
    
    def refine_extraction(
        self,
        raw_input: str,
        previous_extraction: Dict[str, Any],
        feedback: str,
    ) -> Dict[str, Any]:
        """
        Refine extraction based on PM feedback.
        
        Args:
            raw_input: Original raw text
            previous_extraction: The previous extraction result
            feedback: PM's feedback on what to change
            
        Returns:
            Updated extraction result
        """
        
        user_prompt = EXTRACTION_FOLLOW_UP.format(
            feedback=feedback,
            raw_input=raw_input,
            previous_extraction=str(previous_extraction),
        )
        
        result = self.engine.call(
            system_prompt=SYSTEM_PROMPT_EXTRACTOR,
            user_prompt=user_prompt,
            action_type="extraction_refinement",
            context={"feedback": feedback[:200]},
        )
        
        return {
            "chunks": result["result"].get("chunks", []),
            "summary": result["result"].get("summary", ""),
            "concerns": result["result"].get("concerns", []),
            "skipped": result["result"].get("skipped", []),
            "changes_made": result["result"].get("changes_made", []),
            "reasoning_trace": result["reasoning_trace"],
            "call_id": result["call_id"],
        }
    
    def validate_chunks(self, chunks: List[Dict]) -> Dict[str, Any]:
        """
        Validate extracted chunks for quality and completeness.
        
        Returns:
            Dict with validation results and suggestions
        """
        
        validation = {
            "total_chunks": len(chunks),
            "by_type": {},
            "by_strength": {"strong": 0, "moderate": 0, "weak": 0},
            "issues": [],
            "suggestions": [],
        }
        
        for chunk in chunks:
            # Count by type
            etype = chunk.get("evidence_type", "unknown")
            validation["by_type"][etype] = validation["by_type"].get(etype, 0) + 1
            
            # Count by strength
            strength = chunk.get("strength", "unknown")
            if strength in validation["by_strength"]:
                validation["by_strength"][strength] += 1
            
            # Check for issues
            if not chunk.get("content"):
                validation["issues"].append("Chunk missing content")
            if not chunk.get("source"):
                validation["issues"].append("Chunk missing source attribution")
            if not chunk.get("extraction_reasoning"):
                validation["issues"].append("Chunk missing extraction reasoning")
        
        # Generate suggestions
        if len(validation["by_type"]) == 1:
            validation["suggestions"].append(
                f"All evidence is type '{list(validation['by_type'].keys())[0]}'. "
                "Consider gathering other evidence types for stronger validation."
            )
        
        if validation["by_strength"]["weak"] > validation["by_strength"]["strong"]:
            validation["suggestions"].append(
                "More weak evidence than strong. Consider gathering more direct evidence."
            )
        
        if validation["total_chunks"] < 5:
            validation["suggestions"].append(
                "Small evidence base. Conclusions may not be well-supported."
            )
        
        return validation


# Convenience function
def extract_evidence(raw_input: str, context: str = "", api_key: str = None) -> Dict[str, Any]:
    """Quick extraction without instantiating class."""
    extractor = EvidenceExtractor(api_key)
    return extractor.extract(raw_input, context)
