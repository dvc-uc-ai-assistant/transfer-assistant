"""
Database module initialization.
Exports repository and models for use in the application.
"""

from backend.database.models import Base, University, Year, Category, UCCourse, DVCCourse, CourseEquivalency
from backend.database.repository import PostgresRepository

__all__ = [
    "Base",
    "University",
    "Year",
    "Category",
    "UCCourse",
    "DVCCourse",
    "CourseEquivalency",
    "PostgresRepository",
]
