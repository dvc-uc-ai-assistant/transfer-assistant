"""
PostgreSQL Repository for Transfer Assistant.
Queries the database for course data, equivalencies, and transfer mappings.
"""

from typing import List, Dict, Set, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.database.models import (
    University, Year, Category, UCCourse, DVCCourse, CourseEquivalency, Base
)


class PostgresRepository:
    """PostgreSQL-backed data repository for transfer course data."""

    def __init__(self, database_url: str):
        """Initialize repository with database connection."""
        self.engine = create_engine(database_url, echo=False)
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
        Retrieve course equivalencies filtered by campus, category, and other criteria.
        
        Returns:
            {
                "UCB": [
                    {
                        "dvc_code": "MATH-192",
                        "dvc_title": "Analytic Geometry and Calculus I",
                        "dvc_units": 5,
                        "category": "Mathematics (Required)",
                        "minimum_required": "all",
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
                # Get university by name mapping
                uni_name_map = {
                    "UCB": "UC Berkeley",
                    "UCD": "UC Davis",
                    "UCSD": "UC San Diego",
                }
                uni_name = uni_name_map.get(campus_key)
                if not uni_name:
                    continue

                # Query university
                uni = session.query(University).filter_by(name=uni_name).first()
                if not uni:
                    result[campus_key] = []
                    continue

                # Get latest year for this university
                year = session.query(Year).filter_by(university_id=uni.id).order_by(Year.year.desc()).first()
                if not year:
                    result[campus_key] = []
                    continue

                # Query equivalencies for this year
                courses = []
                equivalencies = (
                    session.query(CourseEquivalency)
                    .join(Category)
                    .join(Year)
                    .join(University)
                    .filter(University.id == uni.id, Year.id == year.id)
                    .all()
                )

                for equiv in equivalencies:
                    cat = equiv.category
                    dvc = equiv.dvc_course

                    # Skip if DVC course doesn't exist
                    if not dvc:
                        continue

                    # Filter by category
                    if categories and cat.name not in categories:
                        continue

                    # Filter by required_only
                    if required_only:
                        mr = str(cat.minimum_required or "").lower()
                        if mr != "all" and not (mr.isdigit() and int(mr) > 0):
                            continue

                    # Filter by completed courses
                    if dvc.course_code.upper() in {c.upper() for c in completed_courses}:
                        continue

                    # Filter by completed domains
                    if self._is_cs_course(dvc) and "cs" in completed_domains:
                        continue
                    if self._is_math_course(dvc) and "math" in completed_domains:
                        continue
                    if self._is_science_course(dvc) and "science" in completed_domains:
                        continue

                    # Filter by focus_only (if LLM specified)
                    if focus_only == "cs" and not self._is_cs_course(dvc):
                        continue
                    if focus_only == "math" and not self._is_math_course(dvc):
                        continue
                    if focus_only == "science" and not self._is_science_course(dvc):
                        continue

                    courses.append({
                        "dvc_code": dvc.course_code,
                        "dvc_title": dvc.title,
                        "dvc_units": dvc.units or 0,
                        "category": cat.name,
                        "minimum_required": cat.minimum_required or "None",
                    })

                result[campus_key] = courses

        return result

    def get_campuses(self) -> List[str]:
        """Get list of available campus codes."""
        with Session(self.engine) as session:
            unis = session.query(University).all()
            code_map = {
                "UC Berkeley": "UCB",
                "UC Davis": "UCD",
                "UC San Diego": "UCSD",
            }
            return [code_map[u.name] for u in unis if u.name in code_map]

    def get_categories(self, campus_key: str, year: str = "2025-2026") -> List[str]:
        """Get list of categories for a specific campus and year."""
        uni_name_map = {
            "UCB": "UC Berkeley",
            "UCD": "UC Davis",
            "UCSD": "UC San Diego",
        }
        uni_name = uni_name_map.get(campus_key)
        if not uni_name:
            return []

        with Session(self.engine) as session:
            cats = (
                session.query(Category.name)
                .join(Year)
                .join(University)
                .filter(University.name == uni_name, Year.year == year)
                .distinct()
                .all()
            )
            return [c[0] for c in cats]

    @staticmethod
    def _is_cs_course(dvc: DVCCourse) -> bool:
        """Check if course is computer science."""
        code = (dvc.course_code or "").upper()
        title = (dvc.title or "").lower()
        return (
            code.startswith(("COMSC-", "COMSCI-", "COMPSC-", "CS-"))
            or "programming" in title
            or "data structures" in title
            or "software" in title
        )

    @staticmethod
    def _is_math_course(dvc: DVCCourse) -> bool:
        """Check if course is mathematics."""
        code = (dvc.course_code or "").upper()
        title = (dvc.title or "").lower()
        return (
            code.startswith(("MATH-", "STAT-"))
            or "calculus" in title
            or "linear algebra" in title
            or "differential equations" in title
        )

    @staticmethod
    def _is_science_course(dvc: DVCCourse) -> bool:
        """Check if course is science."""
        code = (dvc.course_code or "").upper()
        return code.startswith(("PHYS-", "CHEM-", "BIOSC-", "BIOL-"))
