"""
SQLAlchemy ORM models for Transfer Assistant database.

This module now includes a SQL-first transfer_rules table used for course
retrieval. Legacy assist_data is kept for staged migration.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index, Text, JSON, Boolean, Numeric
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


class TransferRule(Base):
    """
    Table 1 (SQL-first): Transfer rule rows used by the backend query layer.
    Each row represents one DVC <-> UC course mapping within a category.
    """
    __tablename__ = "transfer_rules"

    id = Column(Integer, primary_key=True, index=True)

    source_college = Column(String(20), nullable=False, index=True)   # e.g., DVC
    target_college = Column(String(20), nullable=False, index=True)   # e.g., UCB/UCD/UCSD
    academic_year = Column(String(20), nullable=False, index=True)    # e.g., 2025-2026
    major = Column(String(120), nullable=True, index=True)

    category_name = Column(String(200), nullable=False, index=True)
    minimum_required = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, nullable=False, default=False, index=True)
    domain = Column(String(20), nullable=False, default="other", index=True)

    dvc_course_code = Column(String(40), nullable=False, index=True)
    dvc_course_title = Column(Text, nullable=False)
    dvc_units = Column(Numeric(4, 1), nullable=True)

    uc_course_code = Column(String(40), nullable=True, index=True)
    uc_course_title = Column(Text, nullable=True)
    uc_units = Column(Numeric(4, 1), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        # Used by the primary assistant retrieval path.
        Index("idx_transfer_campus_year", "target_college", "academic_year"),
        Index("idx_transfer_campus_category", "target_college", "category_name"),
        Index("idx_transfer_campus_domain", "target_college", "domain"),
        Index("idx_transfer_required", "target_college", "is_required"),
        Index(
            "idx_transfer_dedupe",
            "source_college",
            "target_college",
            "academic_year",
            "major",
            "category_name",
            "dvc_course_code",
            "uc_course_code",
            unique=False,
        ),
    )

    def __repr__(self):
        return (
            f"<TransferRule(id={self.id}, source='{self.source_college}', "
            f"target='{self.target_college}', dvc='{self.dvc_course_code}', "
            f"uc='{self.uc_course_code}')>"
        )


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
