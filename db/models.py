# Evidence Engine - Database Models

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class Session(Base):
    """A research session - one opportunity/problem being explored"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # What the PM is exploring
    title = Column(String(500))  # e.g., "Onboarding churn investigation"
    opportunity_statement = Column(Text)  # The problem framing
    
    # Session state
    status = Column(String(50), default="active")  # active, completed, archived
    
    # Relationships
    evidence_chunks = relationship("EvidenceChunk", back_populates="session")
    outputs = relationship("Output", back_populates="session")
    messages = relationship("Message", back_populates="session")


class EvidenceChunk(Base):
    """A single piece of evidence extracted from raw input"""
    __tablename__ = "evidence_chunks"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # The evidence itself
    content = Column(Text, nullable=False)  # The actual quote/observation/data
    evidence_type = Column(String(50))  # user_quote, analytics_data, etc.
    
    # Source tracking
    source = Column(String(500))  # e.g., "User Interview - Sarah, Jan 15"
    source_raw = Column(Text)  # The original raw text this was extracted from
    
    # Metadata
    tags = Column(JSON, default=list)  # Themes, keywords
    strength = Column(String(20))  # strong, moderate, weak
    
    # For hypothesis testing
    supports_hypothesis = Column(Boolean, nullable=True)  # True, False, or None (neutral)
    hypothesis_relevance = Column(Text)  # Why this is relevant/irrelevant
    
    # Extraction reasoning (transparency)
    extraction_reasoning = Column(Text)  # Why this was extracted, how it was interpreted
    
    # Relationship
    session = relationship("Session", back_populates="evidence_chunks")


class Output(Base):
    """Generated outputs (summaries, hypothesis tests, etc.)"""
    __tablename__ = "outputs"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Output type
    output_type = Column(String(50))  # hypothesis_test, stakeholder_summary, etc.
    
    # The output content
    title = Column(String(500))
    content = Column(Text)  # The main output
    
    # Transparency - this is crucial
    reasoning_trace = Column(Text)  # Full chain of thought
    evidence_used = Column(JSON, default=list)  # IDs of evidence chunks used
    evidence_excluded = Column(JSON, default=list)  # IDs excluded and why
    confidence_level = Column(String(20))
    confidence_reasoning = Column(Text)
    
    # Gaps and caveats
    gaps_identified = Column(JSON, default=list)
    caveats = Column(JSON, default=list)
    
    # Suggested next steps
    suggested_research = Column(JSON, default=list)
    
    # Relationship
    session = relationship("Session", back_populates="outputs")


class Message(Base):
    """Conversation history for the session"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    role = Column(String(20))  # user, assistant, system
    content = Column(Text)
    
    # For assistant messages, track what was happening
    action_type = Column(String(50), nullable=True)  # extraction, synthesis, output, question
    reasoning = Column(Text, nullable=True)  # Why the assistant said this
    
    # Relationship
    session = relationship("Session", back_populates="messages")


# Database initialization
def init_db(db_path="db/database.db"):
    """Initialize the database"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def get_session_maker(engine):
    """Get a session maker for the database"""
    return sessionmaker(bind=engine)


# Convenience function
def get_db():
    """Get a database session"""
    engine = init_db()
    SessionMaker = get_session_maker(engine)
    return SessionMaker()
