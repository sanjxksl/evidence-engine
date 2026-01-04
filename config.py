# Evidence Engine - Configuration

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
# Set your Google Gemini API key in .env file, Streamlit secrets, or environment variable
# FREE - No credit card required! Get yours at: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Model to use (Gemini 1.5 Flash is FREE with generous limits!)
# Options:
# - "gemini-1.5-flash-latest" (FREE - 15 requests/min, 1M tokens/min, RECOMMENDED)
# - "gemini-1.5-pro-latest" (FREE - 2 requests/min, highest quality)
# - "gemini-2.0-flash-exp" (Experimental - very limited quotas, not recommended)
MODEL_NAME = "gemini-1.5-flash-latest"


def get_api_key():
    """
    Get API key from environment or Streamlit secrets.
    Supports multiple configuration sources for flexibility.
    """
    # Try environment variable first
    key = os.getenv("GOOGLE_API_KEY", "")
    if key:
        return key

    # Try Streamlit secrets (for deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            return st.secrets['GOOGLE_API_KEY']
    except (ImportError, FileNotFoundError, KeyError):
        pass

    return ""

# Database
DATABASE_URL = "sqlite:///db/database.db"

# App settings
APP_NAME = "Evidence Engine"
APP_DESCRIPTION = "Turn messy research into defensible decisions"

# Evidence types
EVIDENCE_TYPES = [
    "user_quote",           # Direct quote from user research
    "behavioral_observation", # What users did (not said)
    "support_ticket",       # From support/feedback channels
    "analytics_data",       # Quantitative metrics
    "stakeholder_input",    # Internal stakeholder requests/opinions
    "competitor_intel",     # What competitors are doing
    "market_research",      # External research/reports
]

# Output types available to users
OUTPUT_TYPES = {
    "hypothesis_test": "Test my hypothesis",
    "pattern_cluster": "Find patterns in evidence",
    "confidence_assessment": "Assess evidence strength",
    "stakeholder_summary": "Generate stakeholder summary",
    "research_gaps": "Identify what research is missing",
    "counter_evidence": "Find evidence against my assumption",
}

# Confidence levels
CONFIDENCE_LEVELS = {
    "high": {
        "label": "High",
        "description": "Multiple evidence types, quantitative validation, consistent pattern",
        "min_evidence_types": 3,
        "min_evidence_count": 8,
    },
    "medium": {
        "label": "Medium", 
        "description": "Qualitative pattern with some consistency, gaps exist",
        "min_evidence_types": 2,
        "min_evidence_count": 4,
    },
    "low": {
        "label": "Low",
        "description": "Limited evidence, single source type, or contradictory signals",
        "min_evidence_types": 1,
        "min_evidence_count": 1,
    },
}
