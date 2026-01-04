# Evidence Engine - Main Streamlit App
# A conversational tool for PM evidence synthesis

import streamlit as st
import json
from datetime import datetime
from typing import List, Dict, Any

from config import APP_NAME, APP_DESCRIPTION, OUTPUT_TYPES
from core.extractor import EvidenceExtractor
from core.synthesizer import Synthesizer
from core.output_generator import OutputGenerator
from core.reasoning import get_engine
from core.intent_classifier import IntentClassifier
from db.service import DatabaseService

# Page config
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Initialize database service
if "db_service" not in st.session_state:
    st.session_state.db_service = DatabaseService()

# Initialize or load current session
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "session_data" not in st.session_state:
    st.session_state.session_data = None

# Create new session if none exists
if st.session_state.current_session_id is None:
    db_session = st.session_state.db_service.create_session()
    st.session_state.current_session_id = db_session.id
    st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)


def add_message(role: str, content: str, reasoning: str = None, action_type: str = None):
    """Add a message to the conversation and save to database."""
    # Save to database
    st.session_state.db_service.add_message(
        session_id=st.session_state.current_session_id,
        role=role,
        content=content,
        action_type=action_type,
        reasoning=json.dumps(reasoning) if reasoning else None,
    )

    # Reload session data to update UI
    db_session = st.session_state.db_service.get_session_by_id(st.session_state.current_session_id)
    st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)


def display_reasoning_trace(reasoning: List[str], title: str = "Reasoning"):
    """Display reasoning in an expandable box."""
    if reasoning:
        with st.expander(f"🧠 {title} (click to expand)"):
            for step in reasoning:
                st.markdown(f"- {step}")


def display_evidence_chunk(chunk: Dict, index: int):
    """Display a single evidence chunk."""
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**[{index}]** {chunk.get('content', '')[:200]}...")
        with col2:
            st.caption(f"Type: {chunk.get('evidence_type', 'unknown')}")
            st.caption(f"Strength: {chunk.get('strength', 'unknown')}")


# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Key input
    api_key = st.text_input(
        "Google Gemini API Key (FREE!)",
        type="password",
        value=st.session_state.api_key,
        help="Get a FREE API key at aistudio.google.com/app/apikey - no credit card required!"
    )
    if api_key:
        st.session_state.api_key = api_key
    
    st.divider()
    
    # Evidence summary
    st.subheader("📊 Evidence Summary")
    if st.session_state.session_data:
        evidence_chunks = st.session_state.session_data.get("evidence_chunks", [])
        if evidence_chunks:
            st.metric("Total Chunks", len(evidence_chunks))

            # Count by type
            types = {}
            for chunk in evidence_chunks:
                t = chunk.get("evidence_type", "unknown")
                types[t] = types.get(t, 0) + 1

            for t, count in types.items():
                st.caption(f"• {t}: {count}")
        else:
            st.caption("No evidence yet. Paste your research to get started.")
    else:
        st.caption("No evidence yet. Paste your research to get started.")
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    if st.button("🗑️ Clear All", use_container_width=True):
        # Archive current session
        st.session_state.db_service.archive_session(st.session_state.current_session_id)

        # Create new session
        db_session = st.session_state.db_service.create_session()
        st.session_state.current_session_id = db_session.id
        st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)
        st.rerun()

    if st.session_state.session_data and st.session_state.session_data.get("evidence_chunks"):
        if st.button("📥 Export Evidence (JSON)", use_container_width=True):
            st.download_button(
                label="Download",
                data=json.dumps(st.session_state.session_data["evidence_chunks"], indent=2),
                file_name="evidence_export.json",
                mime="application/json",
            )


# Main content
st.title(f"🔍 {APP_NAME}")
st.caption(APP_DESCRIPTION)

# Check for API key
if not st.session_state.api_key:
    st.warning("👈 Please enter your FREE Google Gemini API key in the sidebar to get started.")
    st.info("""
    **What is this tool?**
    
    Evidence Engine helps Product Managers:
    - Extract structured evidence from messy research notes
    - Test hypotheses against actual evidence
    - Find patterns and contradictions
    - Generate stakeholder-ready summaries
    - See exactly HOW conclusions are reached (full transparency)
    
    **Get started:**
    1. Get a FREE API key at https://aistudio.google.com/app/apikey (no credit card!)
    2. Enter your Google Gemini API key in the sidebar
    2. Paste your research notes (from Google Docs, interviews, etc.)
    3. Tell the tool what you want to learn
    """)
    st.stop()

# Initialize components
try:
    extractor = EvidenceExtractor(st.session_state.api_key)
    synthesizer = Synthesizer(st.session_state.api_key)
    output_gen = OutputGenerator(st.session_state.api_key)
    intent_classifier = IntentClassifier(st.session_state.api_key)
except Exception as e:
    st.error(f"Error initializing: {e}")
    st.stop()

# Display conversation history
if st.session_state.session_data:
    for msg in st.session_state.session_data.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("reasoning"):
                display_reasoning_trace(msg["reasoning"], "How I reached this")

# Initial prompt if no messages
if not st.session_state.session_data or not st.session_state.session_data.get("messages"):
    with st.chat_message("assistant"):
        st.markdown("""
**Hi! I'm your Evidence Engine.** 👋

I help you turn messy research into defensible decisions. Here's how:

1. **Paste your research** - Interview notes, feedback, analytics... anything
2. **Tell me what you want** - Test a hypothesis, find patterns, prepare for a stakeholder
3. **I'll analyze with full transparency** - You'll see exactly how I reach every conclusion

**What would you like to do?**

- 📝 **"Here are my interview notes..."** - Paste research to extract evidence
- 🔬 **"Test my hypothesis that..."** - I'll find supporting AND contradicting evidence  
- 🔍 **"What patterns do you see?"** - I'll cluster and synthesize
- 📊 **"Prepare a summary for my VP"** - I'll generate stakeholder-ready output

Just type or paste below to get started.
        """)

# Chat input
user_input = st.chat_input("Paste research, ask a question, or tell me what you need...")

if user_input:
    # Add user message
    add_message("user", user_input)
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            # Get current evidence chunks and previous action
            evidence_chunks = st.session_state.session_data.get("evidence_chunks", []) if st.session_state.session_data else []
            has_evidence = len(evidence_chunks) > 0

            messages = st.session_state.session_data.get("messages", []) if st.session_state.session_data else []
            previous_action = messages[-1].get("action_type") if messages else None

            # Classify intent using LLM
            try:
                classification = intent_classifier.classify(
                    user_input=user_input,
                    has_evidence=has_evidence,
                    previous_action=previous_action,
                )

                intent = classification["intent"]
                parameters = classification["parameters"]

            except Exception as e:
                st.warning(f"Intent classification failed: {e}. Using fallback logic.")
                # Fallback to simple heuristic
                if len(user_input) > 500 and not has_evidence:
                    intent = "extraction"
                else:
                    intent = "general_question"
                parameters = {}

            try:
                # Route to appropriate handler

                if intent == "extraction":
                    # Extract evidence from raw input
                    st.markdown("📝 **Extracting evidence from your research...**")

                    result = extractor.extract(user_input)

                    chunks = result.get("chunks", [])
                    # Save chunks to database
                    st.session_state.db_service.bulk_add_evidence_chunks(
                        session_id=st.session_state.current_session_id,
                        chunks=chunks
                    )
                    # Reload session data
                    db_session = st.session_state.db_service.get_session_by_id(st.session_state.current_session_id)
                    st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)
                    
                    # Display results
                    response = f"""
**Extracted {len(chunks)} evidence chunks** from your input.

**Summary:** {result.get('summary', 'No summary generated.')}
"""
                    
                    if result.get("concerns"):
                        response += "\n\n**⚠️ Concerns:**\n"
                        for concern in result["concerns"]:
                            response += f"- {concern}\n"
                    
                    if result.get("skipped"):
                        response += f"\n\n*Skipped {len(result['skipped'])} items (not evidence)*"
                    
                    response += """

**What would you like to do next?**
- "Test my hypothesis that [X]" - I'll evaluate evidence for/against
- "What patterns do you see?" - I'll cluster and find themes
- "Assess confidence for [problem]" - I'll evaluate evidence strength
- "Prepare a stakeholder summary" - I'll generate a defensible narrative
"""
                    
                    st.markdown(response)
                    display_reasoning_trace(result.get("reasoning_trace", []))
                    
                    add_message("assistant", response, result.get("reasoning_trace"), "extraction")
                
                elif intent == "hypothesis_test":
                    if not has_evidence:
                        response = "I don't have any evidence yet. Please paste your research first, and then I can test hypotheses against it."
                        st.markdown(response)
                        add_message("assistant", response)
                    else:
                        # Use extracted hypothesis from parameters if available
                        hypothesis = parameters.get("hypothesis", user_input)

                        st.markdown(f"🔬 **Testing hypothesis:** *{hypothesis}*")

                        result = synthesizer.test_hypothesis(hypothesis, evidence_chunks)
                        
                        verdict_emoji = {
                            "SUPPORTED": "✅",
                            "PARTIALLY_SUPPORTED": "🟡",
                            "INCONCLUSIVE": "❓",
                            "NOT_SUPPORTED": "🟠",
                            "REFUTED": "❌",
                        }.get(result.get("verdict", ""), "❓")
                        
                        response = f"""
## {verdict_emoji} Verdict: {result.get('verdict', 'Unknown')}

**Confidence:** {result.get('confidence', 'unknown').upper()}

{result.get('verdict_summary', '')}

### Supporting Evidence ({len(result.get('supporting_evidence', []))} pieces)
"""
                        for ev in result.get("supporting_evidence", [])[:3]:
                            response += f"\n- {ev.get('content_summary', '')} *(Relevance: {ev.get('relevance', 'unknown')})*"
                        
                        if result.get("counter_evidence"):
                            response += f"\n\n### Counter Evidence ({len(result.get('counter_evidence', []))} pieces)"
                            for ev in result.get("counter_evidence", [])[:3]:
                                response += f"\n- {ev.get('content_summary', '')} *(Severity: {ev.get('severity', 'unknown')})*"
                        
                        if result.get("evidence_gaps"):
                            response += "\n\n### Evidence Gaps"
                            for gap in result.get("evidence_gaps", [])[:3]:
                                response += f"\n- {gap.get('gap', '')} *(Importance: {gap.get('importance', 'unknown')})*"
                        
                        response += """

---
**What next?**
- "Challenge this" - Tell me what I'm missing
- "Generate stakeholder summary" - I'll write it up
- "What would change this verdict?" - I'll explain
"""
                        
                        st.markdown(response)
                        display_reasoning_trace(result.get("reasoning_trace", []))

                        # Save output to database
                        st.session_state.db_service.add_output(
                            session_id=st.session_state.current_session_id,
                            output_data={
                                "output_type": "hypothesis_test",
                                "title": f"Hypothesis: {hypothesis[:100]}",
                                "content": json.dumps(result),
                                "reasoning_trace": result.get("reasoning_trace", []),
                                "confidence_level": result.get("confidence", "unknown"),
                                "confidence_reasoning": result.get("confidence_reasoning", ""),
                                "caveats": [str(gap) for gap in result.get("evidence_gaps", [])],
                            }
                        )
                        # Reload session data
                        db_session = st.session_state.db_service.get_session_by_id(st.session_state.current_session_id)
                        st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)

                        add_message("assistant", response, result.get("reasoning_trace"), "hypothesis_test")
                
                elif intent == "find_patterns":
                    if not has_evidence:
                        response = "I don't have any evidence yet. Please paste your research first."
                        st.markdown(response)
                        add_message("assistant", response)
                    else:
                        st.markdown("🔍 **Finding patterns in your evidence...**")

                        result = synthesizer.find_patterns(evidence_chunks)
                        
                        response = f"""
## Patterns Found

{result.get('synthesis_summary', 'No summary generated.')}

### Key Patterns ({len(result.get('patterns', []))})
"""
                        for pattern in result.get("patterns", []):
                            confidence_emoji = {"strong": "🟢", "moderate": "🟡", "weak": "🔴"}.get(pattern.get("confidence", ""), "⚪")
                            response += f"\n**{pattern.get('theme', 'Unknown')}** {confidence_emoji}\n"
                            response += f"{pattern.get('description', '')}\n"
                            response += f"*Evidence: {pattern.get('evidence_count', 'unknown')} | Confidence: {pattern.get('confidence', 'unknown')}*\n"
                        
                        if result.get("contradictions"):
                            response += f"\n\n### ⚠️ Contradictions ({len(result.get('contradictions', []))})"
                            for contradiction in result.get("contradictions", []):
                                response += f"\n- {contradiction.get('description', '')}"
                        
                        if result.get("gaps"):
                            response += f"\n\n### 🕳️ Evidence Gaps ({len(result.get('gaps', []))})"
                            for gap in result.get("gaps", []):
                                response += f"\n- {gap.get('description', '')}"
                        
                        st.markdown(response)
                        display_reasoning_trace(result.get("reasoning_trace", []))

                        # Save output to database
                        st.session_state.db_service.add_output(
                            session_id=st.session_state.current_session_id,
                            output_data={
                                "output_type": "pattern_synthesis",
                                "title": "Pattern Analysis",
                                "content": json.dumps(result),
                                "reasoning_trace": result.get("reasoning_trace", []),
                                "gaps_identified": [str(gap) for gap in result.get("gaps", [])],
                            }
                        )
                        # Reload session data
                        db_session = st.session_state.db_service.get_session_by_id(st.session_state.current_session_id)
                        st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)

                        add_message("assistant", response, result.get("reasoning_trace"), "pattern_synthesis")

                elif intent == "stakeholder_summary":
                    if not has_evidence:
                        response = "I don't have any evidence yet. Please paste your research first."
                        st.markdown(response)
                        add_message("assistant", response)
                    else:
                        st.markdown("📊 **Generating stakeholder summary...**")

                        # First find patterns if we haven't
                        patterns_result = synthesizer.find_patterns(evidence_chunks)

                        # Generate summary
                        evidence_summary = f"{len(evidence_chunks)} evidence chunks analyzed"
                        result = output_gen.generate_stakeholder_summary(
                            topic="Research findings",  # Could be smarter about this
                            evidence_summary=evidence_summary,
                            patterns=patterns_result.get("patterns", []),
                        )
                        
                        response = f"""
## 📋 Stakeholder Summary

### {result.get('headline', 'Research Findings')}

**Evidence Base:** {result.get('evidence_base', evidence_summary)}

### Key Findings
"""
                        for finding in result.get("key_findings", []):
                            if isinstance(finding, dict):
                                response += f"\n- **{finding.get('finding', '')}**"
                                if finding.get("implication"):
                                    response += f"\n  - *So what:* {finding['implication']}"
                            else:
                                response += f"\n- {finding}"
                        
                        conf = result.get("confidence", {})
                        response += f"\n\n**Confidence:** {conf.get('level', 'Unknown').upper()}"
                        if conf.get("explanation"):
                            response += f"\n> {conf['explanation']}"
                        
                        if result.get("caveats"):
                            response += "\n\n### ⚠️ Caveats"
                            for caveat in result["caveats"]:
                                response += f"\n- {caveat}"
                        
                        if result.get("next_steps"):
                            response += "\n\n### Recommended Next Steps"
                            for step in result["next_steps"]:
                                if isinstance(step, dict):
                                    response += f"\n- {step.get('action', '')}"
                                else:
                                    response += f"\n- {step}"
                        
                        response += "\n\n---\n*Copy the above for your stakeholder conversation.*"
                        
                        st.markdown(response)
                        display_reasoning_trace(result.get("reasoning_trace", []))

                        # Save output to database
                        st.session_state.db_service.add_output(
                            session_id=st.session_state.current_session_id,
                            output_data={
                                "output_type": "stakeholder_summary",
                                "title": result.get("headline", "Stakeholder Summary"),
                                "content": json.dumps(result),
                                "reasoning_trace": result.get("reasoning_trace", []),
                                "confidence_level": result.get("confidence", {}).get("level", "unknown"),
                                "confidence_reasoning": result.get("confidence", {}).get("explanation", ""),
                                "caveats": result.get("caveats", []),
                                "suggested_research": result.get("next_steps", []),
                            }
                        )
                        # Reload session data
                        db_session = st.session_state.db_service.get_session_by_id(st.session_state.current_session_id)
                        st.session_state.session_data = st.session_state.db_service.session_to_dict(db_session)

                        add_message("assistant", response, result.get("reasoning_trace"), "stakeholder_summary")

                elif intent == "counter_evidence":
                    if not has_evidence:
                        response = "I don't have any evidence yet. Please paste your research first."
                        st.markdown(response)
                        add_message("assistant", response)
                    else:
                        # Use extracted assumption from parameters if available
                        assumption = parameters.get("assumption", user_input)

                        st.markdown(f"😈 **Playing devil's advocate on:** *{assumption}*")

                        result = output_gen.find_counter_evidence(assumption, evidence_chunks)
                        
                        response = f"""
## 😈 Counter-Evidence Analysis

**Assumption tested:** {result.get('assumption_tested', assumption)}

### Evidence Against Your Assumption
"""
                        for ev in result.get("counter_evidence", []):
                            strength_emoji = {"strong": "🔴", "moderate": "🟠", "weak": "🟡"}.get(ev.get("strength_of_contradiction", ""), "⚪")
                            response += f"\n{strength_emoji} {ev.get('content', '')}"
                            response += f"\n   *Why this contradicts:* {ev.get('how_it_contradicts', '')}\n"
                        
                        if result.get("alternative_explanations"):
                            response += "\n### Alternative Explanations"
                            for alt in result.get("alternative_explanations", []):
                                response += f"\n- Your evidence: *{alt.get('for_evidence', '')}*"
                                response += f"\n  Alternative view: {alt.get('alternative', '')}\n"
                        
                        response += f"\n### 🎯 Devil's Advocate Summary\n{result.get('devil_advocate_summary', '')}"
                        
                        response += f"\n\n### 🤔 Honest Assessment\n{result.get('honest_assessment', '')}"
                        
                        st.markdown(response)
                        display_reasoning_trace(result.get("reasoning_trace", []))
                        
                        add_message("assistant", response, result.get("reasoning_trace"), "counter_evidence")
                
                elif intent == "confidence_assessment":
                    if not has_evidence:
                        response = "I don't have any evidence yet. Please paste your research first."
                        st.markdown(response)
                        add_message("assistant", response)
                    else:
                        # Use extracted problem statement from parameters if available
                        problem = parameters.get("problem_statement", user_input)

                        st.markdown(f"📊 **Assessing evidence strength for:** *{problem}*")

                        result = synthesizer.assess_confidence(problem, evidence_chunks)
                        
                        response = f"""
## 📊 Confidence Assessment

**Problem evaluated:** {result.get('problem_evaluated', problem)}

### Overall Confidence: {result.get('overall_confidence', 'Unknown').upper()}

{result.get('overall_reasoning', '')}

### Dimension Breakdown
"""
                        dims = result.get("dimensions", {})
                        for dim_name, dim_data in dims.items():
                            if isinstance(dim_data, dict):
                                score_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(dim_data.get("score", ""), "⚪")
                                response += f"\n**{dim_name.title()}:** {score_emoji} {dim_data.get('score', 'unknown')}"
                                response += f"\n   {dim_data.get('reasoning', '')}\n"
                        
                        if result.get("what_would_increase_confidence"):
                            response += "\n### To Increase Confidence"
                            for item in result["what_would_increase_confidence"]:
                                response += f"\n- {item}"
                        
                        response += f"\n\n### Recommendation\n{result.get('recommendation', 'No recommendation generated.')}"
                        
                        st.markdown(response)
                        display_reasoning_trace(result.get("reasoning_trace", []))
                        
                        add_message("assistant", response, result.get("reasoning_trace"), "confidence_assessment")
                
                else:
                    # General response - guide the user
                    if has_evidence:
                        response = f"""
I have **{len(evidence_chunks)} evidence chunks** loaded. What would you like to do?

- **"Test my hypothesis that [X]"** - I'll find evidence for and against
- **"What patterns do you see?"** - I'll cluster themes and contradictions
- **"Assess confidence for [problem]"** - I'll evaluate evidence strength
- **"Prepare a stakeholder summary"** - I'll generate a defensible narrative
- **"Challenge my assumption that [X]"** - I'll play devil's advocate

Or paste more research to add to the evidence base.
"""
                    else:
                        response = """
I'm not sure what you're asking for. To get started:

1. **Paste your research** - Interview notes, feedback, survey responses, etc.
2. **Tell me what you want** - Test a hypothesis, find patterns, prepare for stakeholders

Just paste your raw research and I'll help you make sense of it.
"""
                    st.markdown(response)
                    add_message("assistant", response)
            
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}\n\nPlease check your API key and try again."
                st.error(error_msg)
                add_message("assistant", error_msg)


# Footer
st.divider()
st.caption("Evidence Engine v0.1 | Built for PMs who want defensible decisions")
