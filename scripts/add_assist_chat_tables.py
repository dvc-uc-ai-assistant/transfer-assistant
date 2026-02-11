"""
Migration script to add assist_data and chat_history tables.
Run this to upgrade your database with the new two-table architecture.

Usage:
    python scripts/add_assist_chat_tables.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.models import Base, AssistData, ChatHistory
from backend.database.repository import PostgresRepository


def migrate():
    """Create the new assist_data and chat_history tables."""
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment")
        print("   Please ensure .env file contains DATABASE_URL")
        sys.exit(1)
    
    print("🔧 Connecting to database...")
    print(f"   URL: {database_url.split('@')[0]}@...")  # Hide password
    
    try:
        repo = PostgresRepository(database_url)
        
        # Create tables (Base.metadata.create_all creates only missing tables)
        print("\n📦 Creating new tables...")
        Base.metadata.create_all(repo.engine, tables=[
            AssistData.__table__,
            ChatHistory.__table__
        ])
        
        print("✅ Migration complete!")
        print("\n📋 New tables created:")
        print("   • assist_data (Static transfer agreement knowledge)")
        print("   • chat_history (Dynamic conversation memory)")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(repo.engine)
        tables = inspector.get_table_names()
        
        if "assist_data" in tables and "chat_history" in tables:
            print("\n✅ Verification: Both tables exist in database")
            
            # Show table details
            print("\n📊 assist_data columns:")
            for col in inspector.get_columns("assist_data"):
                print(f"   • {col['name']} ({col['type']})")
            
            print("\n📊 chat_history columns:")
            for col in inspector.get_columns("chat_history"):
                print(f"   • {col['name']} ({col['type']})")
        else:
            print("\n⚠️  Warning: Tables may not have been created properly")
            print(f"   Found tables: {tables}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("  DATABASE MIGRATION: Two-Table Architecture")
    print("=" * 60)
    migrate()
    print("\n" + "=" * 60)
    print("  🎉 Ready to use assist_data and chat_history!")
    print("=" * 60)
