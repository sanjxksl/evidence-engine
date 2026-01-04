# Evidence Engine - Intent Classification
# LLM-based intent classification to replace brittle keyword matching

from typing import Dict, Any
from core.reasoning import get_engine


INTENT_SYSTEM_PROMPT = """You are an intent classification system for a PM research tool.

Your job is to classify user input into ONE of these intents:

1. **extraction** - User is providing raw research to extract evidence from
   - Indicators: Long text, interview notes, quotes, feedback, "here are my notes"

2. **hypothesis_test** - User wants to test a hypothesis against evidence
   - Indicators: "test my hypothesis", "is it true that", "validate", "assumption"

3. **find_patterns** - User wants to find patterns/themes in evidence
   - Indicators: "what patterns", "themes", "what do you see", "cluster"

4. **stakeholder_summary** - User wants a stakeholder-ready summary
   - Indicators: "summary", "stakeholder", "present", "prepare", "convince"

5. **counter_evidence** - User wants evidence against their assumption (debiasing)
   - Indicators: "challenge", "counter", "wrong", "what if I'm wrong", "devil's advocate"

6. **confidence_assessment** - User wants to assess evidence strength
   - Indicators: "confidence", "how strong", "enough evidence", "assess"

7. **general_question** - General question or clarification
   - Indicators: Doesn't match above, questions about the tool, follow-ups

Respond with JSON:
{
  "intent": "<one of the above>",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation of why you chose this intent",
  "extracted_parameters": {
    "hypothesis": "...",  // For hypothesis_test
    "assumption": "...",  // For counter_evidence
    "problem_statement": "..."  // For confidence_assessment
  }
}"""


INTENT_USER_PROMPT = """Classify this user input:

"{user_input}"

Context:
- Has evidence chunks: {has_evidence}
- Previous action: {previous_action}

Classify the intent and extract any relevant parameters."""


class IntentClassifier:
    """
    LLM-based intent classification for Evidence Engine.
    Replaces brittle keyword matching with robust classification.
    """

    def __init__(self, api_key: str = None):
        self.engine = get_engine(api_key)

    def classify(
        self,
        user_input: str,
        has_evidence: bool = False,
        previous_action: str = None,
    ) -> Dict[str, Any]:
        """
        Classify user input into an intent category.

        Args:
            user_input: The user's message
            has_evidence: Whether evidence chunks exist
            previous_action: The previous action taken (for context)

        Returns:
            Dict with intent, confidence, reasoning, and extracted parameters
        """

        user_prompt = INTENT_USER_PROMPT.format(
            user_input=user_input[:1000],  # Limit to avoid huge prompts
            has_evidence="yes" if has_evidence else "no",
            previous_action=previous_action or "none",
        )

        result = self.engine.call(
            system_prompt=INTENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            action_type="intent_classification",
            context={
                "input_length": len(user_input),
                "has_evidence": has_evidence,
            },
            temperature=0.1,  # Low temperature for consistent classification
            expect_json=True,
        )

        classification = result["result"]

        return {
            "intent": classification.get("intent", "general_question"),
            "confidence": classification.get("confidence", "medium"),
            "reasoning": classification.get("reasoning", ""),
            "parameters": classification.get("extracted_parameters", {}),
            "call_id": result["call_id"],
        }


# Convenience function
def classify_intent(user_input: str, has_evidence: bool = False, api_key: str = None) -> Dict[str, Any]:
    """Quick intent classification."""
    classifier = IntentClassifier(api_key)
    return classifier.classify(user_input, has_evidence)
