"""
SQLAlchemy ORM models for Transfer Assistant database.
Simplified two-table architecture using JSON storage.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AssistData(Base):
    """
    Table 1: Static Knowledge Storage
    Stores parsed transfer agreements from the Scraper.
    This is the source of truth for transfer equivalencies.
    """
    __tablename__ = "assist_data"

    id = Column(Integer, primary_key=True, index=True)
    source_college = Column(String(100), nullable=False, index=True)  # e.g., "DVC"
    target_college = Column(String(100), nullable=False, index=True)  # e.g., "UCB", "UCD", "UCSD"
    major = Column(String(255), nullable=True, index=True)  # e.g., "Computer Science", "Mathematics"
    agreements_json = Column(JSON, nullable=False)  # Full JSON of parsed transfer data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes for fast lookups
    __table_args__ = (
        Index("idx_assist_source_target", "source_college", "target_college"),
        Index("idx_assist_target_major", "target_college", "major"),
    )

    def __repr__(self):
        return f"<AssistData(id={self.id}, source='{self.source_college}', target='{self.target_college}', major='{self.major}')>"


class ChatHistory(Base):
    """
    Table 2: Dynamic Memory Storage
    Remembers conversation context for each user session.
    Enables persistent, context-aware conversations.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)  # e.g., "sess_a3f2e1"
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)  # The actual message
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Indexes for efficient session retrieval
    __table_args__ = (
        Index("idx_chat_session_time", "session_id", "timestamp"),
    )

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, session_id='{self.session_id}', role='{self.role}', timestamp={self.timestamp})>"
