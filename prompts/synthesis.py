# Evidence Engine - Synthesis Prompts

SYSTEM_PROMPT_SYNTHESIS = """You are a research synthesis assistant for product managers. Your job is to find patterns, themes, and insights across evidence chunks WITHOUT introducing bias.

## Your Principles

1. **Let patterns emerge**: Don't force evidence into predetermined categories
2. **Count carefully**: "5 of 8 users" not "many users" 
3. **Distinguish signal from noise**: Not every mention is a pattern
4. **Note contradictions**: Conflicting evidence is valuable information
5. **Trace every claim**: Every pattern must cite specific evidence
6. **Acknowledge uncertainty**: Say "this might indicate" not "this proves"

## Pattern Thresholds

Be conservative about what counts as a pattern:
- **Strong pattern**: 60%+ of evidence points in same direction, multiple sources
- **Moderate pattern**: 40-60% consistency, or strong signal from fewer sources
- **Weak signal**: <40% or single source type—flag as needing validation

## What You Should Surface

1. **Themes**: Recurring topics or issues across evidence
2. **Contradictions**: Where evidence conflicts (this is valuable!)
3. **Segments**: Different user types showing different patterns
4. **Gaps**: What's notably ABSENT from the evidence
5. **Surprises**: Evidence that contradicts common assumptions
"""

PATTERN_SYNTHESIS_PROMPT = """## Task: Find patterns in this evidence

**Evidence to analyze:**
{evidence_chunks}

**Context (if provided):**
{context}

**Instructions:**

1. Read through ALL evidence first before identifying patterns

2. For each potential pattern:
   - How many evidence chunks support it?
   - What % of total relevant evidence?
   - Are there counter-examples?
   - What type of evidence (user quotes, analytics, etc.)?

3. Cluster related evidence into themes

4. Explicitly call out:
   - Contradictions (where evidence conflicts)
   - Surprises (unexpected findings)
   - Gaps (what you'd expect to see but don't)

5. For each pattern, provide a confidence level based on evidence strength

Format your response as JSON:
```json
{
  "patterns": [
    {
      "theme": "Short label for this pattern",
      "description": "What this pattern shows",
      "evidence_support": [
        {
          "evidence_id": "...",
          "how_it_supports": "..."
        }
      ],
      "counter_evidence": [...],
      "evidence_count": "X of Y relevant chunks",
      "confidence": "strong|moderate|weak",
      "confidence_reasoning": "Why this confidence level"
    }
  ],
  "contradictions": [
    {
      "description": "What's contradicting",
      "evidence_a": "...",
      "evidence_b": "...",
      "possible_explanations": ["..."]
    }
  ],
  "gaps": [
    {
      "description": "What's missing",
      "why_notable": "Why this gap matters",
      "how_to_fill": "Suggested research"
    }
  ],
  "surprises": [
    {
      "finding": "What was unexpected",
      "evidence": "...",
      "implications": "What this might mean"
    }
  ],
  "synthesis_summary": "3-5 sentence overview of key findings",
  "reasoning_trace": ["Step by step how you identified these patterns"]
}
```
"""

CLUSTER_EVIDENCE_PROMPT = """## Task: Cluster this evidence by theme

**Evidence to cluster:**
{evidence_chunks}

**Instructions:**

1. Group evidence chunks that relate to the same underlying topic or issue
2. Name each cluster with a clear, descriptive label
3. For each cluster, note:
   - What unifies these pieces of evidence
   - How strong/consistent the cluster is
   - Any outliers or edge cases within the cluster
4. Some evidence may fit multiple clusters—note this
5. Some evidence may not fit any cluster—that's okay, call it out

Format as JSON:
```json
{
  "clusters": [
    {
      "name": "Cluster label",
      "description": "What this cluster represents",
      "evidence_ids": ["..."],
      "unifying_theme": "What ties these together",
      "strength": "strong|moderate|weak",
      "internal_contradictions": ["Any conflicts within this cluster"],
      "outliers": ["Evidence that partially fits"]
    }
  ],
  "unclustered": [
    {
      "evidence_id": "...",
      "reason": "Why this didn't fit anywhere"
    }
  ],
  "cross_cluster_connections": [
    {
      "clusters": ["cluster1", "cluster2"],
      "relationship": "How these clusters relate"
    }
  ],
  "reasoning_trace": ["How you decided on these groupings"]
}
```
"""

CONFIDENCE_ASSESSMENT_PROMPT = """## Task: Assess evidence strength for a problem area

**Problem/Opportunity being evaluated:**
{problem_statement}

**Available evidence:**
{evidence_chunks}

**Instructions:**

1. Evaluate the OVERALL evidence strength for this problem area
2. Consider:
   - Quantity: How much evidence?
   - Diversity: How many source types?
   - Consistency: Does evidence point in same direction?
   - Quality: Direct vs inferred, strong vs weak sources
   - Recency: Is evidence current?
   - Gaps: What's missing?

3. Rate each dimension and explain why

4. Provide an overall confidence score with detailed reasoning

Format as JSON:
```json
{
  "problem_evaluated": "...",
  "dimensions": {
    "quantity": {
      "score": "high|medium|low",
      "evidence_count": X,
      "reasoning": "..."
    },
    "diversity": {
      "score": "high|medium|low",
      "source_types": ["..."],
      "reasoning": "..."
    },
    "consistency": {
      "score": "high|medium|low",
      "contradictions_found": X,
      "reasoning": "..."
    },
    "quality": {
      "score": "high|medium|low",
      "strong_evidence_count": X,
      "weak_evidence_count": Y,
      "reasoning": "..."
    },
    "gaps": {
      "severity": "critical|moderate|minor",
      "key_gaps": ["..."],
      "reasoning": "..."
    }
  },
  "overall_confidence": "high|medium|low|insufficient",
  "overall_reasoning": "...",
  "what_would_increase_confidence": ["..."],
  "what_would_decrease_confidence": ["..."],
  "recommendation": "Proceed|Gather more evidence|Pivot"
}
```
"""
