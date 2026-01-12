# Evidence Engine

Transform unstructured product research into defensible, evidence-based decisions.

Evidence Engine is a conversational AI tool designed to help Product Managers:
- Extract structured evidence from raw research inputs (user interviews, feedback, analytics)
- Test hypotheses against empirical evidence rather than intuition
- Identify patterns, contradictions, and gaps in research data
- Generate stakeholder-ready summaries with complete reasoning transparency

The tool addresses cognitive bias in product prioritization through systematic evidence synthesis.

## Problem Statement

Product prioritization frameworks like RICE and ICE promise objectivity through scoring, but in practice they often become post-hoc rationalization tools. Through a combination of literature review, hands-on framework testing, and interviews with practicing Product Managers and stakeholders, I found that prioritization decisions are consistently distorted by cognitive biases (e.g., HiPPO bias, confirmation bias, anchoring) and by data scarcity rather than lack of framework knowledge.

This project emerged from the insight that the core problem is not calculating better scores, but generating better inputs and reasoning. PMs need structured ways to gather evidence, surface counter-evidence, and articulate defensible narratives—especially in environments where stakeholder pressure and uncertainty dominate. Evidence Engine was designed as a decision-support system that augments PM judgment by making assumptions explicit, evidence traceable, and gaps visible, rather than attempting to automate prioritization itself.

Research indicates significant challenges in product decision-making:
- Only 6.4% of features drive 80% of product usage (Pendo 2024)
- 92% of high-confidence A/B tests fail to achieve predicted outcomes (Kohavi)
- Product management frameworks such as RICE often become rationalization tools rather than decision aids

The underlying issue is that cognitive bias enters during evidence synthesis, prior to the prioritization phase.

Evidence Engine addresses this by structuring the synthesis process with full transparency. Users can see exactly how conclusions are derived, making decisions defensible and bias observable.

## Installation and Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/sanjxksl/evidence-engine.git
cd evidence-engine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

This application uses Google Gemini API, which is available at no cost with no credit card required.

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google Gemini API key
# Obtain a key at: https://aistudio.google.com/app/apikey
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will be available at http://localhost:8501.

## Usage Guide

### Step 1: Input Research Data

Input raw research data into the application interface:
- User interview notes
- Customer feedback from support channels
- Survey responses
- Stakeholder requests and requirements

The system extracts structured evidence chunks and displays the extraction reasoning.

### Step 2: Perform Analysis

The application supports multiple analysis modes:

**Hypothesis Testing:**
```
Test my hypothesis that users are churning because onboarding is confusing
```

**Pattern Identification:**
```
What patterns do you see in this evidence?
```

**Confidence Assessment:**
```
How strong is our evidence that users want dark mode?
```

**Stakeholder Reporting:**
```
Generate a summary I can present to my VP
```

**Assumption Validation:**
```
Find evidence against my belief that pricing is the main churn driver
```

### Step 3: Iterate and Refine

The application supports conversational interaction:
- Challenge conclusions with follow-up questions
- Request clarification on specific verdicts
- Add supplementary evidence to existing sessions
- Generate alternative output formats

## Key Features

### Transparent Reasoning
All conclusions include complete reasoning traces with no hidden logic.

```
┌─ REASONING TRACE ───────────────────────────────────────┐
│ • Found 4 supporting evidence chunks                    │
│ • Found 2 counter-evidence chunks                       │
│ • Counter-evidence from technical users suggests        │
│   segment-specific problem, not universal               │
│ • Verdict: PARTIALLY_SUPPORTED due to mixed signals     │
└─────────────────────────────────────────────────────────┘
```

### Evidence Classification
Evidence is automatically categorized by type:
- `user_quote`: Direct user statements
- `behavioral_observation`: Observed user actions
- `support_ticket`: Customer support feedback
- `analytics_data`: Quantitative metrics
- `stakeholder_input`: Internal requirements
- `competitor_intel`: Competitive intelligence

### Bias Mitigation Features
- Hypothesis testing actively searches for counter-evidence
- Confidence assessment evaluates evidence quality rather than quantity alone
- Assumption challenge mode identifies contradictory evidence
- Gap identification highlights missing information

### Stakeholder Reports
Generated summaries include:
- Executive summary and evidence base
- Key findings with business implications
- Confidence assessment with supporting reasoning
- Acknowledged caveats and research gaps
- Recommended next steps

## Project Structure

```
evidence-engine/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
│
├── core/                     # Core processing logic
│   ├── reasoning.py          # Transparent LLM wrapper
│   ├── extractor.py          # Evidence extraction
│   ├── synthesizer.py        # Pattern finding and hypothesis testing
│   ├── intent_classifier.py  # LLM-based intent classification
│   └── output_generator.py   # Stakeholder output generation
│
├── prompts/                  # LLM prompt templates
│   ├── extraction.py         # Evidence extraction prompts
│   ├── hypothesis.py         # Hypothesis testing prompts
│   ├── synthesis.py          # Pattern finding prompts
│   └── stakeholder.py        # Output generation prompts
│
└── db/                       # Database layer
    ├── models.py             # SQLAlchemy data models
    └── service.py            # Database service layer
```

## Configuration and Customization

### Model Selection

Modify the model in `config.py`:
```python
MODEL_NAME = "gemini-2.0-flash-exp"  # Default (recommended)
# MODEL_NAME = "gemini-1.5-flash"    # 15 requests/min, optimized for speed
# MODEL_NAME = "gemini-1.5-pro"      # 2 requests/min, highest quality
```

All Google Gemini models are available at no cost with generous rate limits.

### Prompt Customization

All prompts are located in the `prompts/` directory:
- `extraction.py`: Evidence parsing from raw text
- `hypothesis.py`: Hypothesis evaluation logic
- `synthesis.py`: Pattern identification algorithms
- `stakeholder.py`: Output formatting templates

### Extending Functionality

To add new output types:
1. Create a new prompt template in `prompts/`
2. Implement a handler method in `core/output_generator.py`
3. Update intent detection in `app.py`

## Deployment

### Streamlit Cloud

Streamlit Cloud provides free hosting for Streamlit applications.

1. Push repository to GitHub
2. Navigate to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Configure secrets: Add `GOOGLE_API_KEY` with your API key from https://aistudio.google.com/app/apikey
5. Deploy the application

### Docker Deployment

For containerized deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

## Validation Metrics

Recommended metrics for evaluating the tool with product teams:

| Metric | Target |
|--------|--------|
| Time to useful output | < 15 minutes |
| User retention ("Would use again") | > 70% |
| Real stakeholder usage | At least 2/5 testers |
| Reasoning trace utility | > 80% |

## Future Development

Current areas identified for enhancement:

1. Advanced intent detection using additional context
2. Enhanced evidence persistence with session management
3. Direct integrations with tools such as Notion, Intercom, and Jira
4. Outcome tracking to compare predictions against actual results
5. Historical calibration to improve accuracy over time

## Research Foundation

This tool is based on research in cognitive bias and product decision-making:

- Kahneman & Tversky (1974): Heuristics and biases
- Morewedge et al. (2015): Debiasing interventions
- Pendo (2024): Feature adoption benchmarks
- Kohavi (2020): A/B testing success rates

## License

MIT

## About

Evidence Engine was developed to address systematic bias in product prioritization decisions through transparent, evidence-based synthesis.
