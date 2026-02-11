"""
Example usage of the new two-table architecture.
Demonstrates how to interact with assist_data and chat_history tables.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.repository import PostgresRepository


def demo_assist_data(repo: PostgresRepository):
    """Demonstrate assist_data table usage."""
    print("\n" + "="*60)
    print("📚 EXAMPLE 1: assist_data (Static Knowledge)")
    print("="*60)
    
    # Example: Save transfer agreement data
    sample_agreement = {
        "categories": {
            "Computer Science (Required)": {
                "minimum_required": "all",
                "courses": [
                    {
                        "uc_course": "COMPSCI 61A",
                        "dvc_equivalents": ["COMSC-210"]
                    },
                    {
                        "uc_course": "COMPSCI 61B",
                        "dvc_equivalents": ["COMSC-260"]
                    }
                ]
            }
        }
    }
    
    print("\n💾 Saving transfer agreement...")
    saved = repo.save_assist_data(
        source_college="DVC",
        target_college="UCB",
        major="Computer Science",
        agreements_json=sample_agreement
    )
    print(f"✅ Saved: {saved}")
    
    print("\n🔍 Retrieving UCB agreements...")
    agreements = repo.get_assist_data(target_college="UCB")
    for agreement in agreements:
        print(f"   • {agreement.source_college} → {agreement.target_college}")
        print(f"     Major: {agreement.major}")
        print(f"     Updated: {agreement.updated_at}")


def demo_chat_history(repo: PostgresRepository):
    """Demonstrate chat_history table usage."""
    print("\n" + "="*60)
    print("💬 EXAMPLE 2: chat_history (Dynamic Memory)")
    print("="*60)
    
    session_id = "sess_demo_123"
    
    print(f"\n💾 Saving conversation for session: {session_id}")
    
    # User message
    repo.save_message(session_id, "user", "Show me CS courses for UCB")
    print("   ✅ Saved user message")
    
    # Assistant response
    repo.save_message(
        session_id, 
        "assistant", 
        "Here are the Computer Science courses for UC Berkeley..."
    )
    print("   ✅ Saved assistant response")
    
    # Another exchange
    repo.save_message(session_id, "user", "What about math courses?")
    print("   ✅ Saved user message")
    
    repo.save_message(
        session_id,
        "assistant",
        "Here are the Mathematics courses..."
    )
    print("   ✅ Saved assistant response")
    
    print(f"\n🔍 Retrieving chat history for session: {session_id}")
    history = repo.get_chat_history(session_id)
    
    for msg in history:
        role_icon = "👤" if msg.role == "user" else "🤖"
        print(f"\n   {role_icon} [{msg.timestamp}] {msg.role.upper()}")
        print(f"      {msg.content[:60]}...")
    
    print(f"\n📊 Total messages in session: {len(history)}")
    
    # Get recent sessions
    print("\n🔍 Recent sessions (last 7 days):")
    recent = repo.get_recent_sessions(days=7)
    for sess_id in recent:
        print(f"   • {sess_id}")


def main():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        sys.exit(1)
    
    print("🔗 Connecting to database...")
    repo = PostgresRepository(database_url)
    
    try:
        demo_assist_data(repo)
        demo_chat_history(repo)
        
        print("\n" + "="*60)
        print("✅ Demo complete! Tables are working correctly.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
