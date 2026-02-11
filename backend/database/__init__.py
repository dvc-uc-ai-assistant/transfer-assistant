"""
Database module initialization.
Exports repository and models for use in the application.
"""

from backend.database.models import Base, AssistData, ChatHistory
from backend.database.repository import PostgresRepository

__all__ = [
    "Base",
    "AssistData",
    "ChatHistory",
    "PostgresRepository",
]
