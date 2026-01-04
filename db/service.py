# Evidence Engine - Database Service Layer
# Handles all database operations for sessions, evidence, outputs, and messages

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from sqlalchemy.orm import Session as DBSession
from .models import Session, EvidenceChunk, Output, Message, init_db, get_session_maker


class DatabaseService:
    """
    Service layer for database operations.
    Handles all CRUD operations for sessions, evidence, outputs, messages.
    """

    def __init__(self, db_path: str = "db/database.db"):
        self.engine = init_db(db_path)
        self.SessionMaker = get_session_maker(self.engine)

    def get_session(self) -> DBSession:
        """Get a new database session"""
        return self.SessionMaker()

    # ============= SESSION OPERATIONS =============

    def create_session(self, title: str = None, opportunity_statement: str = None) -> Session:
        """Create a new research session"""
        db = self.get_session()
        try:
            session = Session(
                title=title or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                opportunity_statement=opportunity_statement or "",
                status="active",
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session
        finally:
            db.close()

    def get_session_by_id(self, session_id: int) -> Optional[Session]:
        """Get a session by ID"""
        db = self.get_session()
        try:
            return db.query(Session).filter(Session.id == session_id).first()
        finally:
            db.close()

    def list_sessions(self, status: str = None, limit: int = 50) -> List[Session]:
        """List all sessions, optionally filtered by status"""
        db = self.get_session()
        try:
            query = db.query(Session)
            if status:
                query = query.filter(Session.status == status)
            return query.order_by(Session.updated_at.desc()).limit(limit).all()
        finally:
            db.close()

    def update_session(self, session_id: int, **kwargs) -> Session:
        """Update session fields"""
        db = self.get_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                raise ValueError(f"Session {session_id} not found")

            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)

            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
            return session
        finally:
            db.close()

    def archive_session(self, session_id: int) -> Session:
        """Archive a session"""
        return self.update_session(session_id, status="archived")

    # ============= EVIDENCE CHUNK OPERATIONS =============

    def add_evidence_chunk(self, session_id: int, chunk_data: Dict[str, Any]) -> EvidenceChunk:
        """Add an evidence chunk to a session"""
        db = self.get_session()
        try:
            chunk = EvidenceChunk(
                session_id=session_id,
                content=chunk_data.get("content", ""),
                evidence_type=chunk_data.get("evidence_type", "unknown"),
                source=chunk_data.get("source", ""),
                source_raw=chunk_data.get("source_raw", ""),
                tags=chunk_data.get("tags", []),
                strength=chunk_data.get("strength", "unknown"),
                extraction_reasoning=chunk_data.get("extraction_reasoning", ""),
            )
            db.add(chunk)
            db.commit()
            db.refresh(chunk)

            # Update session timestamp
            self._touch_session(db, session_id)

            return chunk
        finally:
            db.close()

    def bulk_add_evidence_chunks(self, session_id: int, chunks: List[Dict[str, Any]]) -> List[EvidenceChunk]:
        """Add multiple evidence chunks at once"""
        db = self.get_session()
        try:
            chunk_objects = []
            for chunk_data in chunks:
                chunk = EvidenceChunk(
                    session_id=session_id,
                    content=chunk_data.get("content", ""),
                    evidence_type=chunk_data.get("evidence_type", "unknown"),
                    source=chunk_data.get("source", ""),
                    source_raw=chunk_data.get("source_raw", ""),
                    tags=chunk_data.get("tags", []),
                    strength=chunk_data.get("strength", "unknown"),
                    extraction_reasoning=chunk_data.get("extraction_reasoning", ""),
                )
                chunk_objects.append(chunk)

            db.bulk_save_objects(chunk_objects)
            db.commit()

            # Update session timestamp
            self._touch_session(db, session_id)

            return chunk_objects
        finally:
            db.close()

    def get_evidence_chunks(self, session_id: int) -> List[EvidenceChunk]:
        """Get all evidence chunks for a session"""
        db = self.get_session()
        try:
            return db.query(EvidenceChunk).filter(
                EvidenceChunk.session_id == session_id
            ).order_by(EvidenceChunk.created_at.asc()).all()
        finally:
            db.close()

    # ============= OUTPUT OPERATIONS =============

    def add_output(self, session_id: int, output_data: Dict[str, Any]) -> Output:
        """Add an output (hypothesis test, summary, etc.) to a session"""
        db = self.get_session()
        try:
            # Convert lists to JSON strings if needed
            reasoning_trace = output_data.get("reasoning_trace", "")
            if isinstance(reasoning_trace, list):
                reasoning_trace = json.dumps(reasoning_trace)

            output = Output(
                session_id=session_id,
                output_type=output_data.get("output_type", "unknown"),
                title=output_data.get("title", ""),
                content=output_data.get("content", ""),
                reasoning_trace=reasoning_trace,
                evidence_used=output_data.get("evidence_used", []),
                evidence_excluded=output_data.get("evidence_excluded", []),
                confidence_level=output_data.get("confidence_level", ""),
                confidence_reasoning=output_data.get("confidence_reasoning", ""),
                gaps_identified=output_data.get("gaps_identified", []),
                caveats=output_data.get("caveats", []),
                suggested_research=output_data.get("suggested_research", []),
            )
            db.add(output)
            db.commit()
            db.refresh(output)

            # Update session timestamp
            self._touch_session(db, session_id)

            return output
        finally:
            db.close()

    def get_outputs(self, session_id: int, output_type: str = None) -> List[Output]:
        """Get outputs for a session, optionally filtered by type"""
        db = self.get_session()
        try:
            query = db.query(Output).filter(Output.session_id == session_id)
            if output_type:
                query = query.filter(Output.output_type == output_type)
            return query.order_by(Output.created_at.asc()).all()
        finally:
            db.close()

    # ============= MESSAGE OPERATIONS =============

    def add_message(self, session_id: int, role: str, content: str,
                   action_type: str = None, reasoning: str = None) -> Message:
        """Add a message to the conversation history"""
        db = self.get_session()
        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                action_type=action_type,
                reasoning=reasoning,
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # Update session timestamp
            self._touch_session(db, session_id)

            return message
        finally:
            db.close()

    def get_messages(self, session_id: int) -> List[Message]:
        """Get all messages for a session"""
        db = self.get_session()
        try:
            return db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at.asc()).all()
        finally:
            db.close()

    # ============= HELPER METHODS =============

    def _touch_session(self, db: DBSession, session_id: int):
        """Update session's updated_at timestamp"""
        session = db.query(Session).filter(Session.id == session_id).first()
        if session:
            session.updated_at = datetime.utcnow()
            db.commit()

    def session_to_dict(self, session: Session) -> Dict[str, Any]:
        """Convert session and all related data to dict for st.session_state"""
        db = self.get_session()
        try:
            # Reload to ensure relationships are loaded
            session = db.query(Session).filter(Session.id == session.id).first()

            return {
                "id": session.id,
                "title": session.title,
                "opportunity_statement": session.opportunity_statement,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "evidence_chunks": [self._chunk_to_dict(c) for c in session.evidence_chunks],
                "outputs": [self._output_to_dict(o) for o in session.outputs],
                "messages": [self._message_to_dict(m) for m in session.messages],
            }
        finally:
            db.close()

    def _chunk_to_dict(self, chunk: EvidenceChunk) -> Dict[str, Any]:
        """Convert evidence chunk to dict"""
        return {
            "id": chunk.id,
            "content": chunk.content,
            "evidence_type": chunk.evidence_type,
            "source": chunk.source,
            "tags": chunk.tags,
            "strength": chunk.strength,
            "extraction_reasoning": chunk.extraction_reasoning,
        }

    def _output_to_dict(self, output: Output) -> Dict[str, Any]:
        """Convert output to dict"""
        return {
            "id": output.id,
            "type": output.output_type,
            "result": {
                "title": output.title,
                "content": output.content,
                "confidence_level": output.confidence_level,
                "caveats": output.caveats,
            }
        }

    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert message to dict"""
        reasoning_list = []
        if message.reasoning:
            # Try to parse as JSON array, fallback to single string
            try:
                reasoning_list = json.loads(message.reasoning)
            except (json.JSONDecodeError, TypeError):
                reasoning_list = [message.reasoning] if message.reasoning else []

        return {
            "role": message.role,
            "content": message.content,
            "reasoning": reasoning_list,
            "action_type": message.action_type,
            "timestamp": message.created_at.isoformat(),
        }
