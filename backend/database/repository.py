"""
PostgreSQL Repository for Transfer Assistant.
Queries the database for course data, equivalencies, and transfer mappings.
"""

from typing import List, Dict, Set, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.database.models import AssistData, ChatHistory, Base


class PostgresRepository:
    """PostgreSQL-backed data repository for transfer course data."""

    def __init__(self, database_url: str):
        """Initialize repository with database connection."""
        
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
        """
        Retrieve course equivalencies from JSON data, filtered by campus, category, and criteria.
        
        Returns:
            {
                "UCB": [
                    {
                        "dvc_code": "MATH-192",
                        "dvc_title": "Analytic Geometry and Calculus I",
                        "dvc_units": 5,
                        "uc_code": "MATH-51",
                        "uc_title": "Calculus 1",
                        "uc_units": 4,
                        "category": "Mathematics Requirements",
                        "minimum_required": "3",
                    },
                    ...
                ],
                "UCD": [...],
                ...
            }
        """
        completed_courses = completed_courses or set()
        completed_domains = completed_domains or set()
        
        result = {}

        with Session(self.engine) as session:
            for campus_key in campus_keys:
                courses = []
                
                # Get assist_data for this campus
                records = session.query(AssistData).filter_by(
                    source_college="DVC",
                    target_college=campus_key
                ).all()
                
                if not records:
                    result[campus_key] = []
                    continue
                
                # Use the most recent record
                record = max(records, key=lambda r: r.updated_at)
                json_data = record.agreements_json
                
                # Parse the JSON structure
                category_list = json_data.get("categories", [])
                
                for item in category_list:
                    if not isinstance(item, dict):
                        continue
                    
                    # Skip the Year entry
                    if "Year" in item:
                        continue
                    
                    # This is a category
                    category_name = item.get("Category", "")
                    minimum_required = item.get("Minimum_Required", 0)
                    course_list = item.get("Courses", [])
                    
                    # Filter by category name
                    if categories and category_name not in categories:
                        continue
                    
                    # Filter by required_only
                    if required_only and minimum_required == 0:
                        continue
                    
                    # Process each course in this category
                    for course_item in course_list:
                        if not isinstance(course_item, dict):
                            continue
                        
                        uc_info = course_item.get("UC_Berkeley", course_item.get("UC_Davis", course_item.get("UC_San_Diego", {})))
                        dvc_info = course_item.get("DVC", {})
                        
                        # Handle DVC as array (multiple equivalencies)
                        if isinstance(dvc_info, list):
                            dvc_courses = dvc_info
                        else:
                            dvc_courses = [dvc_info]
                        
                        for dvc in dvc_courses:
                            if not isinstance(dvc, dict):
                                continue
                            
                            dvc_code = dvc.get("Course_Code", "")
                            dvc_title = dvc.get("Title", "")
                            dvc_units = dvc.get("Units", 0)
                            
                            if not dvc_code:
                                continue
                            
                            # Filter by completed courses
                            if dvc_code.upper() in {c.upper() for c in completed_courses}:
                                continue
                            
                            # Filter by completed domains
                            if self._is_cs_course(dvc_code, dvc_title) and "cs" in completed_domains:
                                continue
                            if self._is_math_course(dvc_code, dvc_title) and "math" in completed_domains:
                                continue
                            if self._is_science_course(dvc_code, dvc_title) and "science" in completed_domains:
                                continue
                            
                            # Filter by focus_only
                            if focus_only == "cs" and not self._is_cs_course(dvc_code, dvc_title):
                                continue
                            if focus_only == "math" and not self._is_math_course(dvc_code, dvc_title):
                                continue
                            if focus_only == "science" and not self._is_science_course(dvc_code, dvc_title):
                                continue
                            
                            courses.append({
                                "dvc_code": dvc_code,
                                "dvc_title": dvc_title,
                                "dvc_units": dvc_units,
                                "uc_code": uc_info.get("Course_Code", ""),
                                "uc_title": uc_info.get("Title", ""),
                                "uc_units": uc_info.get("Units", 0),
                                "category": category_name,
                                "minimum_required": str(minimum_required),
                            })
                
                result[campus_key] = courses

        return result

    def get_campuses(self) -> List[str]:
        """Get list of available campus codes."""
        with Session(self.engine) as session:
            records = session.query(AssistData.target_college).distinct().all()
            return [r[0] for r in records]

    def get_categories(self, campus_key: str, year: str = "2025-2026") -> List[str]:
        """Get list of categories for a specific campus."""
        with Session(self.engine) as session:
            records = session.query(AssistData).filter_by(target_college=campus_key).all()
            
            if not records:
                return []
            
            # Use most recent record
            record = max(records, key=lambda r: r.updated_at)
            json_data = record.agreements_json
            category_list = json_data.get("categories", [])
            
            categories = []
            for item in category_list:
                if isinstance(item, dict) and "Category" in item:
                    categories.append(item["Category"])
            
            return categories

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
                existing.updated_at = existing.__table__.c.updated_at.server_default
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
            query = query.order_by(ChatHistory.timestamp.asc())
            
            if limit:
                # Get last N messages
                query = query.limit(limit)
            
            return query.all()

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
