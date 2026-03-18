"""
PostgreSQL Repository for Transfer Assistant.
Queries the database for course data, equivalencies, and transfer mappings.
"""

from datetime import datetime
from typing import List, Dict, Set, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.database.models import AssistData, ChatHistory, TransferRule, Base


class PostgresRepository:
    """PostgreSQL-backed data repository for transfer course data."""

    def __init__(self, database_url: str):
        """Initialize repository with database connection."""
        if not database_url or not isinstance(database_url, str):
            raise ValueError(
                "DATABASE_URL is missing. Set it in your environment or load it from .env before creating PostgresRepository."
            )
        
        # Cloud SQL connection pool settings for production
        connect_args = {}
        engine_kwargs = {
            "echo": False,
            "pool_pre_ping": True,     # Verify connections before using
            "pool_recycle": 3600,      # Recycle connections after 1 hour
        }
        
        # If using Cloud SQL Unix socket, add special handling
        if "/cloudsql/" in database_url:
            engine_kwargs.update({
                "pool_size": 5,        # Keep 5 connections in pool
                "max_overflow": 2,     # Allow 2 extra during traffic spikes
            })
        
        self.engine = create_engine(database_url, connect_args=connect_args, **engine_kwargs)
        # Verify tables exist
        Base.metadata.create_all(self.engine)

    def get_courses(
        self,
        campus_keys: List[str],
        categories: Optional[List[str]] = None,
        required_only: bool = False,
        focus_only: Optional[str] = None,
        completed_courses: Optional[Set[str]] = None,
        completed_domains: Optional[Set[str]] = None,
    ) -> Dict[str, List[Dict]]:
        """Retrieve SQL transfer rule rows, filtered by campus and user criteria."""
        completed_courses = completed_courses or set()
        completed_domains = completed_domains or set()
        completed_courses_upper = {c.upper() for c in completed_courses}
        categories_lower = {c.strip().lower() for c in (categories or []) if c and c.strip()}
        focus_only = (focus_only or "").strip().lower() or None

        result: Dict[str, List[Dict]] = {}

        with Session(self.engine) as session:
            for campus_key in campus_keys:
                rules = (
                    session.query(TransferRule)
                    .filter_by(source_college="DVC", target_college=campus_key)
                    .order_by(TransferRule.category_name.asc(), TransferRule.dvc_course_code.asc())
                    .all()
                )

                courses: List[Dict] = []
                for rule in rules:
                    dvc_code = (rule.dvc_course_code or "").strip()
                    dvc_title = rule.dvc_course_title or ""
                    category_name = rule.category_name or ""
                    if not dvc_code:
                        continue

                    if categories_lower and category_name.strip().lower() not in categories_lower:
                        continue

                    if required_only and not rule.is_required:
                        continue

                    if dvc_code.upper() in completed_courses_upper:
                        continue

                    domain = self._course_domain(dvc_code, dvc_title, rule.domain)

                    if domain in completed_domains:
                        continue

                    if focus_only in {"cs", "math", "science"} and domain != focus_only:
                        continue

                    courses.append({
                        "dvc_code": dvc_code,
                        "dvc_title": dvc_title,
                        "dvc_units": float(rule.dvc_units) if rule.dvc_units is not None else 0,
                        "uc_code": rule.uc_course_code or "",
                        "uc_title": rule.uc_course_title or "",
                        "uc_units": float(rule.uc_units) if rule.uc_units is not None else 0,
                        "category": category_name,
                        "minimum_required": str(rule.minimum_required or 0),
                    })

                result[campus_key] = courses

        return result

    def get_campuses(self) -> List[str]:
        """Get list of available campus codes."""
        with Session(self.engine) as session:
            records = session.query(TransferRule.target_college).distinct().all()
            return sorted([r[0] for r in records if r[0]])

    def get_categories(self, campus_key: str, year: str = "2025-2026") -> List[str]:
        """Get list of categories for a specific campus."""
        with Session(self.engine) as session:
            query = session.query(TransferRule.category_name).filter_by(target_college=campus_key)
            if year:
                query = query.filter_by(academic_year=year)

            records = query.distinct().all()
            return sorted([r[0] for r in records if r[0]])

    @staticmethod
    def _course_domain(code: str, title: str = "", domain_hint: Optional[str] = None) -> str:
        """Resolve domain using stored hint first, then fallback heuristics."""
        if domain_hint in {"cs", "math", "science", "other"}:
            return domain_hint
        if PostgresRepository._is_cs_course(code, title):
            return "cs"
        if PostgresRepository._is_math_course(code, title):
            return "math"
        if PostgresRepository._is_science_course(code, title):
            return "science"
        return "other"

    @staticmethod
    def _is_cs_course(code: str, title: str = "") -> bool:
        """Check if course is computer science."""
        code = code.upper()
        title = title.lower()
        return (
            code.startswith(("COMSC-", "COMPSC-", "CS-"))
            or "programming" in title
            or "data structures" in title
            or "software" in title
        )

    @staticmethod
    def _is_math_course(code: str, title: str = "") -> bool:
        """Check if course is mathematics."""
        code = code.upper()
        title = title.lower()
        return (
            code.startswith(("MATH-", "STAT-"))
            or "calculus" in title
            or "linear algebra" in title
            or "differential equations" in title
        )

    @staticmethod
    def _is_science_course(code: str, title: str = "") -> bool:
        """Check if course is science."""
        code = code.upper()
        return code.startswith(("PHYS-", "CHEM-", "BIOSC-", "BIOL-"))

    # ==================== TRANSFER_RULES METHODS ====================

    def replace_transfer_rules_for_campus(
        self,
        target_college: str,
        academic_year: str,
        rows: List[Dict],
        source_college: str = "DVC",
    ) -> int:
        """
        Replace all transfer rows for a campus/year with the provided row list.
        This is the SQL-first ingestion path.
        """
        with Session(self.engine) as session:
            session.query(TransferRule).filter_by(
                source_college=source_college,
                target_college=target_college,
                academic_year=academic_year,
            ).delete()

            for row in rows:
                rule = TransferRule(
                    source_college=source_college,
                    target_college=target_college,
                    academic_year=academic_year,
                    major=row.get("major"),
                    category_name=row.get("category_name", ""),
                    minimum_required=int(row.get("minimum_required") or 0),
                    is_required=bool(row.get("is_required", False)),
                    domain=(row.get("domain") or "other").lower(),
                    dvc_course_code=row.get("dvc_course_code", ""),
                    dvc_course_title=row.get("dvc_course_title", ""),
                    dvc_units=row.get("dvc_units"),
                    uc_course_code=row.get("uc_course_code"),
                    uc_course_title=row.get("uc_course_title"),
                    uc_units=row.get("uc_units"),
                    updated_at=datetime.utcnow(),
                )
                session.add(rule)

            session.commit()
            return len(rows)

    # ==================== ASSIST_DATA METHODS ====================

    def save_assist_data(
        self, 
        source_college: str, 
        target_college: str, 
        major: Optional[str], 
        agreements_json: dict
    ) -> AssistData:
        """
        Save or update transfer agreement data from scraper.
        
        Args:
            source_college: Source institution (e.g., "DVC")
            target_college: Target UC campus (e.g., "UCB", "UCD", "UCSD")
            major: Major name (e.g., "Computer Science") or None for general ed
            agreements_json: Full JSON structure of transfer agreements
            
        Returns:
            AssistData: The saved record
        """
        with Session(self.engine) as session:
            # Check if record already exists
            existing = session.query(AssistData).filter_by(
                source_college=source_college,
                target_college=target_college,
                major=major
            ).first()
            
            if existing:
                # Update existing record
                existing.agreements_json = agreements_json
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                return existing
            else:
                # Create new record
                new_data = AssistData(
                    source_college=source_college,
                    target_college=target_college,
                    major=major,
                    agreements_json=agreements_json
                )
                session.add(new_data)
                session.commit()
                session.refresh(new_data)
                return new_data

    def get_assist_data(
        self,
        target_college: Optional[str] = None,
        major: Optional[str] = None
    ) -> List[AssistData]:
        """
        Retrieve transfer agreement data with optional filters.
        
        Args:
            target_college: Filter by target UC campus (e.g., "UCB")
            major: Filter by major name
            
        Returns:
            List of AssistData records
        """
        with Session(self.engine) as session:
            query = session.query(AssistData)
            
            if target_college:
                query = query.filter_by(target_college=target_college)
            if major:
                query = query.filter_by(major=major)
            
            return query.order_by(AssistData.updated_at.desc()).all()

    # ==================== CHAT_HISTORY METHODS ====================

    def save_message(self, session_id: str, role: str, content: str) -> ChatHistory:
        """
        Save a single chat message to history.
        
        Args:
            session_id: Unique session identifier
            role: Either "user" or "assistant"
            content: The message text
            
        Returns:
            ChatHistory: The saved message record
        """
        with Session(self.engine) as session:
            message = ChatHistory(
                session_id=session_id,
                role=role,
                content=content
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    def get_chat_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ChatHistory]:
        """
        Retrieve chat history for a session, ordered by timestamp.
        
        Args:
            session_id: Session to retrieve history for
            limit: Maximum number of messages to return (most recent)
            
        Returns:
            List of ChatHistory records, oldest first
        """
        with Session(self.engine) as session:
            query = session.query(ChatHistory).filter_by(session_id=session_id)

            if limit:
                # Fetch most recent N first, then reverse to keep oldest->newest order.
                rows = query.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
                return list(reversed(rows))

            return query.order_by(ChatHistory.timestamp.asc()).all()

    def delete_chat_history(self, session_id: str) -> int:
        """
        Delete all chat history for a session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            Number of messages deleted
        """
        with Session(self.engine) as session:
            count = session.query(ChatHistory).filter_by(session_id=session_id).delete()
            session.commit()
            return count

    def get_recent_sessions(self, days: int = 7) -> List[str]:
        """
        Get list of session IDs with activity in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of unique session IDs
        """
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with Session(self.engine) as session:
            sessions = (
                session.query(ChatHistory.session_id)
                .filter(ChatHistory.timestamp >= cutoff)
                .distinct()
                .all()
            )
            return [s[0] for s in sessions]
