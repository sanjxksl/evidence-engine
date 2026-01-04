# 🔍 Evidence Engine

**Turn messy PM research into defensible decisions.**

Evidence Engine is a conversational tool that helps Product Managers:
- Extract structured evidence from raw research (interviews, feedback, analytics)
- Test hypotheses against actual evidence (not gut feeling)
- Find patterns, contradictions, and gaps
- Generate stakeholder-ready summaries with full reasoning transparency

Built to combat cognitive bias in product prioritization.

---

## 🎯 The Problem It Solves

Research shows:
- **6.4%** of features drive 80% of product usage (Pendo 2024)
- **92%** of "high confidence" A/B tests fail (Kohavi)
- PM frameworks like RICE become **rationalization tools**, not decision aids

The root cause: bias enters during evidence synthesis, before prioritization even begins.

Evidence Engine structures that messy synthesis step with full transparency—you see exactly how conclusions are reached, making decisions defensible and bias visible.

---

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo>
cd evidence-engine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key (100% FREE!)

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your FREE Google Gemini API key
# Get one at: https://aistudio.google.com/app/apikey
# NO CREDIT CARD REQUIRED!
```

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 📖 How to Use

### Step 1: Paste Your Research

Copy-paste your raw research into the chat:
- Interview notes from Google Docs
- User feedback from Zendesk/Intercom
- Survey responses
- Stakeholder requests

The engine will extract structured evidence chunks, showing you exactly what it found and why.

### Step 2: Tell It What You Need

**Test a hypothesis:**
```
Test my hypothesis that users are churning because onboarding is confusing
```

**Find patterns:**
```
What patterns do you see in this evidence?
```

**Assess confidence:**
```
How strong is our evidence that users want dark mode?
```

**Prepare for stakeholders:**
```
Generate a summary I can present to my VP
```

**Challenge your assumptions:**
```
Find evidence against my belief that pricing is the main churn driver
```

### Step 3: Iterate

The engine is conversational. You can:
- Challenge its conclusions ("What about the enterprise users?")
- Ask follow-up questions ("What would change this verdict?")
- Add more evidence ("Here's another interview...")
- Request different outputs ("Now give me the stakeholder version")

---

## 🔍 Key Features

### Full Transparency
Every conclusion shows its reasoning trace. No black boxes.

```
┌─ REASONING TRACE ───────────────────────────────────────┐
│ • Found 4 supporting evidence chunks                    │
│ • Found 2 counter-evidence chunks                       │
│ • Counter-evidence from technical users suggests        │
│   segment-specific problem, not universal               │
│ • Verdict: PARTIALLY_SUPPORTED due to mixed signals     │
└─────────────────────────────────────────────────────────┘
```

### Evidence Typing
Each chunk is categorized:
- `user_quote` - Direct user statements
- `behavioral_observation` - What users did (not said)
- `support_ticket` - Feedback from support channels
- `analytics_data` - Quantitative metrics
- `stakeholder_input` - Internal requests
- `competitor_intel` - Competitive information

### Bias Mitigation
- **Hypothesis testing** actively searches for counter-evidence
- **Confidence assessment** rates evidence quality, not just quantity
- **Devil's advocate mode** challenges your assumptions
- **Gap identification** shows what you don't know

### Stakeholder-Ready Output
Generate summaries with:
- Clear headline and evidence base
- Key findings with implications
- Confidence level with reasoning
- Caveats and gaps acknowledged
- Recommended next steps

---

## 📁 Project Structure

```
evidence-engine/
├── app.py                    # Main Streamlit app
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
│
├── core/                     # Core processing logic
│   ├── reasoning.py          # Transparent LLM wrapper
│   ├── extractor.py          # Evidence extraction
│   ├── synthesizer.py        # Pattern finding, hypothesis testing
│   └── output_generator.py   # Stakeholder outputs
│
├── prompts/                  # All LLM prompts (the secret sauce)
│   ├── extraction.py         # Evidence extraction prompts
│   ├── hypothesis.py         # Hypothesis testing prompts
│   ├── synthesis.py          # Pattern finding prompts
│   └── stakeholder.py        # Output generation prompts
│
└── db/                       # Database (SQLite)
    └── models.py             # Data models
```

---

## 🔧 Customization

### Change the LLM Model

In `config.py`:
```python
MODEL_NAME = "gemini-2.0-flash-exp"  # Default: FREE, fast and smart (recommended!)
# MODEL_NAME = "gemini-1.5-flash"    # FREE - 15 requests/min, very fast
# MODEL_NAME = "gemini-1.5-pro"      # FREE - 2 requests/min, highest quality
```

**All models are 100% FREE** with generous rate limits!

### Modify Prompts

All prompts are in `prompts/`. The key ones:
- `extraction.py` - How evidence is parsed from raw text
- `hypothesis.py` - How hypotheses are evaluated
- `synthesis.py` - How patterns are found
- `stakeholder.py` - How outputs are formatted

### Add New Output Types

1. Add a new prompt template in `prompts/`
2. Add a handler method in `core/output_generator.py`
3. Add the intent detection in `app.py`

---

## 🚢 Deployment

### Streamlit Cloud (Free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Add `GOOGLE_API_KEY` to secrets (get FREE key at https://aistudio.google.com/app/apikey)
5. Deploy

### Local Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 📊 Validation Metrics

When testing with PM friends, track:

| Metric | Target |
|--------|--------|
| Time to useful output | < 15 min |
| "Would use again" | > 70% |
| Used output in real stakeholder convo | At least 2/5 testers |
| Reasoning trace was helpful | > 80% |

---

## 🤝 Contributing

This is an MVP. Key areas for improvement:

1. **Better intent detection** - Current keyword matching is brittle
2. **Evidence persistence** - Save sessions across browser refreshes
3. **Integrations** - Pull from Notion, Intercom, Jira directly
4. **Outcome tracking** - Compare predictions to actual outcomes
5. **Historical calibration** - Learn from past accuracy

---

## 📚 Research Background

This tool is based on research into cognitive bias in PM prioritization:

- Kahneman & Tversky (1974) - Heuristics and biases
- Morewedge et al. (2015) - Debiasing interventions
- Pendo (2024) - Feature adoption benchmarks
- Kohavi (2020) - A/B testing success rates

See the full research report for methodology and findings.

---

## License

MIT

---

**Built with frustration, research, and hope that PMs can make better decisions.**
