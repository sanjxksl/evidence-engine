# Evidence Engine - Stakeholder Output Prompts

SYSTEM_PROMPT_STAKEHOLDER = """You are a communication assistant helping product managers create clear, defensible summaries of their research for stakeholders.

## Your Principles

1. **Lead with insight, not process**: Stakeholders want conclusions, not methodology
2. **Make it defensible**: Every claim traceable to evidence
3. **Acknowledge uncertainty**: Don't oversell weak evidence
4. **Be concise**: Respect stakeholder time
5. **Anticipate questions**: Address likely pushback proactively
6. **Separate findings from recommendations**: Let stakeholders see the evidence before your interpretation

## Stakeholder Psychology

Remember that stakeholders often:
- Have limited time (get to the point fast)
- Want to know "so what?" (implications, not just findings)
- Will challenge conclusions (prepare for this)
- Have their own hypotheses (address these if known)
- Need to justify decisions to THEIR stakeholders (give them ammunition)

## Honesty Requirements

- NEVER overstate evidence strength
- ALWAYS note significant gaps or caveats
- If confidence is low, say so clearly
- If evidence is mixed, show both sides
"""

STAKEHOLDER_SUMMARY_PROMPT = """## Task: Generate a stakeholder-ready summary

**Research topic:**
{topic}

**Evidence analyzed:**
{evidence_summary}

**Key patterns/findings:**
{patterns}

**Target stakeholder (if specified):**
{stakeholder_context}

**Instructions:**

Generate a summary with these sections:

1. **HEADLINE** (1 sentence)
   - The key finding in plain language

2. **EVIDENCE BASE** (2-3 sentences)
   - What research this is based on
   - Quantity and type of evidence

3. **KEY FINDINGS** (3-5 bullets)
   - Most important patterns
   - Each bullet should be traceable to evidence
   - Include the "so what" for each

4. **CONFIDENCE LEVEL** (1 sentence + brief explanation)
   - High/Medium/Low + why

5. **CAVEATS & GAPS** (2-3 bullets)
   - What we don't know
   - Where evidence is weak
   - What could change this conclusion

6. **RECOMMENDED NEXT STEPS** (2-3 bullets)
   - What should happen based on this
   - Or what research is needed

7. **REASONING TRACE** (for PM reference, not for stakeholder)
   - How conclusions were reached
   - Which evidence was weighted most heavily and why

Format as JSON:
```json
{
  "headline": "...",
  "evidence_base": "...",
  "key_findings": [
    {
      "finding": "...",
      "evidence_reference": "Based on X interviews / Y data points / etc.",
      "implication": "This means..."
    }
  ],
  "confidence": {
    "level": "high|medium|low",
    "explanation": "..."
  },
  "caveats": ["..."],
  "next_steps": [
    {
      "action": "...",
      "rationale": "..."
    }
  ],
  "reasoning_trace": ["..."],
  "full_evidence_used": ["evidence_ids"],
  "stakeholder_ready_text": "Formatted text version ready to paste"
}
```
"""

CONVINCE_STAKEHOLDER_PROMPT = """## Task: Help the PM convince a skeptical stakeholder

**The PM's recommendation:**
{recommendation}

**Evidence supporting this:**
{evidence}

**The stakeholder's likely objections:**
{objections}

**Additional context:**
{context}

**Instructions:**

1. Acknowledge the stakeholder's perspective—don't be dismissive
2. Address each objection with specific evidence
3. Be honest about where objections have merit
4. Provide alternative framings if direct evidence is weak
5. Suggest what would change if the stakeholder's view is correct
6. Keep it professional—this isn't about "winning"

Format as JSON:
```json
{
  "recommendation_summary": "...",
  "objection_responses": [
    {
      "objection": "...",
      "response": "...",
      "evidence_cited": ["..."],
      "merit_acknowledged": "Where this objection has a point (if applicable)",
      "confidence_in_response": "high|medium|low"
    }
  ],
  "areas_of_uncertainty": ["Where the stakeholder might be right"],
  "suggested_framing": "How to position this conversation",
  "fallback_position": "If they don't agree, what's a reasonable middle ground?",
  "suggested_script": "How the PM might actually say this"
}
```
"""

RESEARCH_GAPS_PROMPT = """## Task: Identify what research is missing

**Current research topic/question:**
{topic}

**Evidence we have:**
{evidence_chunks}

**Decisions this research needs to inform:**
{decisions}

**Instructions:**

1. Evaluate what questions remain unanswered
2. Prioritize gaps by:
   - Impact on decision quality
   - Feasibility to fill
   - Risk of proceeding without this knowledge

3. For each gap, suggest how to fill it

Format as JSON:
```json
{
  "topic_evaluated": "...",
  "current_evidence_summary": "...",
  "critical_gaps": [
    {
      "gap": "What we don't know",
      "why_critical": "Why this matters for the decision",
      "risk_if_unfilled": "What could go wrong",
      "how_to_fill": "Suggested research method",
      "effort_estimate": "low|medium|high",
      "suggested_timeline": "..."
    }
  ],
  "important_gaps": [...],
  "nice_to_have_gaps": [...],
  "sufficient_evidence_areas": ["Where we have enough info"],
  "recommendation": "Can we proceed or should we research more first?",
  "reasoning_trace": ["..."]
}
```
"""

COUNTER_EVIDENCE_PROMPT = """## Task: Find evidence against the PM's assumption

**The PM's assumption/belief:**
{assumption}

**Available evidence:**
{evidence_chunks}

**Instructions:**

This is a DEBIASING exercise. The PM wants you to actively look for reasons they might be wrong.

1. Assume the PM has confirmation bias about their assumption
2. Actively search for evidence that CONTRADICTS their assumption
3. Consider alternative explanations for supporting evidence
4. Identify what would DISPROVE the assumption
5. Be thorough—this is about intellectual honesty

Format as JSON:
```json
{
  "assumption_tested": "...",
  "counter_evidence": [
    {
      "evidence_id": "...",
      "content": "...",
      "how_it_contradicts": "...",
      "strength_of_contradiction": "strong|moderate|weak"
    }
  ],
  "alternative_explanations": [
    {
      "for_evidence": "Evidence that seems to support the assumption",
      "alternative": "Another way to interpret this"
    }
  ],
  "what_would_disprove": [
    "Evidence that would definitively show the assumption is wrong"
  ],
  "devil_advocate_summary": "The strongest case AGAINST the assumption",
  "honest_assessment": "After considering counter-evidence, how confident should the PM be?",
  "reasoning_trace": ["..."]
}
```
"""
