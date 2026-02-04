"""
Initialize the PostgreSQL database with tables from SQLAlchemy models.
Run this once to set up the schema.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from backend.database.models import Base

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not set in .env file")

print(f"Connecting to: {database_url}")

# Create engine
engine = create_engine(database_url, echo=True)

# Create all tables
print("\nCreating tables...")
Base.metadata.create_all(engine)

print("\n✓ All tables created successfully!")
print("\nTables created:")
print("  - universities")
print("  - years")
print("  - categories")
print("  - uc_courses")
print("  - dvc_courses")
print("  - course_equivalencies")
