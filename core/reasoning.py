# Evidence Engine - Reasoning Engine
# Wraps all LLM calls with transparency and logging
# Now using Google Gemini (FREE!)

import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, get_api_key


class ReasoningEngine:
    """
    Wraps LLM calls with full transparency.
    Every call is logged with inputs, outputs, and reasoning.
    Now powered by Google Gemini 2.0 Flash (FREE!).
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Set GOOGLE_API_KEY in .env file "
                "or Streamlit secrets. Get a FREE key at: https://aistudio.google.com/app/apikey"
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.call_log: List[Dict[str, Any]] = []

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        action_type: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3,
        expect_json: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an LLM call with full logging and transparency.

        Args:
            system_prompt: The system prompt defining behavior
            user_prompt: The user prompt with the specific task
            action_type: What kind of action this is (extraction, synthesis, etc.)
            context: Additional context for logging
            temperature: LLM temperature (lower = more deterministic)
            expect_json: Whether to parse response as JSON

        Returns:
            Dict with 'result', 'raw_response', 'reasoning_trace', and metadata
        """

        call_id = f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Log the call inputs
        call_record = {
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "system_prompt_preview": system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt,
            "user_prompt_preview": user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt,
            "context": context,
            "temperature": temperature,
        }

        try:
            # Configure generation settings
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }

            # Add JSON mode if expected
            if expect_json:
                generation_config["response_mime_type"] = "application/json"

            # Create model instance
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                generation_config=generation_config,
                system_instruction=system_prompt,
            )

            # Make the API call
            # Combine system and user prompts for Gemini
            response = model.generate_content(user_prompt)

            # Extract response text
            raw_response = response.text

            # Parse JSON if expected
            if expect_json:
                try:
                    result = json.loads(raw_response)
                except json.JSONDecodeError as e:
                    # Fallback: Try to extract JSON from markdown code blocks
                    result = self._extract_json_from_response(raw_response, e)
            else:
                result = {"text": raw_response}

            # Extract reasoning trace if present
            reasoning_trace = result.get("reasoning_trace", [])
            if not reasoning_trace and isinstance(result, dict):
                # Try to construct reasoning from result structure
                reasoning_trace = self._construct_reasoning_trace(action_type, result)

            # Token counting for Gemini
            # Gemini provides usage metadata
            tokens_used = {
                "prompt": getattr(response.usage_metadata, 'prompt_token_count', 0),
                "completion": getattr(response.usage_metadata, 'candidates_token_count', 0),
                "total": getattr(response.usage_metadata, 'total_token_count', 0),
            }

            # Complete the call record
            call_record.update({
                "status": "success",
                "raw_response_preview": raw_response[:500] + "..." if len(raw_response) > 500 else raw_response,
                "result_keys": list(result.keys()) if isinstance(result, dict) else None,
                "reasoning_trace": reasoning_trace,
                "tokens_used": tokens_used,
            })

            self.call_log.append(call_record)

            return {
                "result": result,
                "raw_response": raw_response,
                "reasoning_trace": reasoning_trace,
                "call_id": call_id,
                "tokens_used": tokens_used,
            }

        except Exception as e:
            call_record.update({
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            })
            self.call_log.append(call_record)

            # Re-raise with context
            raise RuntimeError(
                f"LLM call failed for action '{action_type}': {str(e)}"
            ) from e

    def _extract_json_from_response(self, raw_response: str, original_error: Exception) -> Dict[str, Any]:
        """
        Fallback JSON extraction from markdown code blocks.
        Gemini sometimes wraps JSON in ```json...``` blocks.
        """
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find any JSON object in the response
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Complete failure - return error dict with raw response
        return {
            "error": "Failed to parse JSON response",
            "raw_response": raw_response,
            "parse_error": str(original_error),
            "fallback_attempted": True,
        }

    def _construct_reasoning_trace(self, action_type: str, result: Dict) -> List[str]:
        """Construct a reasoning trace from result structure if not provided."""
        trace = []

        if action_type == "extraction":
            chunks = result.get("chunks", [])
            trace.append(f"Extracted {len(chunks)} evidence chunks")
            if result.get("concerns"):
                trace.append(f"Noted concerns: {', '.join(result['concerns'][:3])}")
            if result.get("skipped"):
                trace.append(f"Skipped items: {len(result['skipped'])}")

        elif action_type == "hypothesis_test":
            supporting = len(result.get("supporting_evidence", []))
            counter = len(result.get("counter_evidence", []))
            trace.append(f"Found {supporting} supporting and {counter} counter evidence chunks")
            trace.append(f"Verdict: {result.get('verdict', 'unknown')}")
            trace.append(f"Confidence: {result.get('confidence', 'unknown')}")

        elif action_type == "pattern_synthesis":
            patterns = len(result.get("patterns", []))
            trace.append(f"Identified {patterns} patterns")
            contradictions = len(result.get("contradictions", []))
            if contradictions:
                trace.append(f"Found {contradictions} contradictions")
            gaps = len(result.get("gaps", []))
            if gaps:
                trace.append(f"Identified {gaps} evidence gaps")

        return trace

    def get_call_log(self) -> List[Dict[str, Any]]:
        """Return the full call log for transparency."""
        return self.call_log

    def get_reasoning_summary(self) -> str:
        """Get a human-readable summary of all reasoning steps."""
        if not self.call_log:
            return "No calls made yet."

        summary = []
        for call in self.call_log:
            summary.append(f"\n## {call['action_type'].upper()} ({call['timestamp']})")
            if call.get('status') == 'success':
                if call.get('reasoning_trace'):
                    for step in call['reasoning_trace']:
                        summary.append(f"  - {step}")
            else:
                summary.append(f"  ERROR: {call.get('error', 'Unknown error')}")

        return "\n".join(summary)

    def clear_log(self):
        """Clear the call log."""
        self.call_log = []


# Singleton instance for convenience
_engine: Optional[ReasoningEngine] = None

def get_engine(api_key: str = None) -> ReasoningEngine:
    """Get or create the reasoning engine singleton."""
    global _engine
    if _engine is None:
        _engine = ReasoningEngine(api_key)
    return _engine
