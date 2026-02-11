"""
View chat history from the database.
Useful for debugging and verifying conversations are saved.
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.repository import PostgresRepository


def show_chat_history(repo, session_id=None, days=1):
    """Display chat history."""
    
    if session_id:
        # Show specific session
        print(f"\n{'='*60}")
        print(f"  Chat History for Session: {session_id}")
        print(f"{'='*60}")
        
        messages = repo.get_chat_history(session_id)
        
        if not messages:
            print(f"❌ No messages found for session: {session_id}")
            return
        
        print(f"\n📊 Total messages: {len(messages)}\n")
        
        for msg in messages:
            icon = "👤" if msg.role == "user" else "🤖"
            color = "\033[96m" if msg.role == "user" else "\033[92m"
            reset = "\033[0m"
            
            print(f"{icon} {color}[{msg.timestamp:%Y-%m-%d %H:%M:%S}] {msg.role.upper()}{reset}")
            print(f"   {msg.content[:200]}{'...' if len(msg.content) > 200 else ''}")
            print()
    
    else:
        # Show recent sessions
        print(f"\n{'='*60}")
        print(f"  Recent Sessions (Last {days} day(s))")
        print(f"{'='*60}\n")
        
        sessions = repo.get_recent_sessions(days=days)
        
        if not sessions:
            print(f"❌ No sessions found in the last {days} day(s)")
            return
        
        print(f"📊 Found {len(sessions)} active session(s):\n")
        
        for sess_id in sessions:
            messages = repo.get_chat_history(sess_id)
            first_msg = messages[0] if messages else None
            last_msg = messages[-1] if messages else None
            
            print(f"  🆔 {sess_id}")
            print(f"     Messages: {len(messages)}")
            if first_msg:
                print(f"     Started: {first_msg.timestamp:%Y-%m-%d %H:%M:%S}")
                print(f"     First message: {first_msg.content[:60]}...")
            if last_msg and len(messages) > 1:
                print(f"     Last: {last_msg.timestamp:%Y-%m-%d %H:%M:%S}")
            print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="View chatbot conversation history")
    parser.add_argument("--session", "-s", help="View specific session ID")
    parser.add_argument("--days", "-d", type=int, default=1, help="Look back N days (default: 1)")
    args = parser.parse_args()
    
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env")
        sys.exit(1)
    
    repo = PostgresRepository(database_url)
    
    try:
        show_chat_history(repo, session_id=args.session, days=args.days)
        
        if not args.session:
            print("\n💡 Tip: Use --session SESSION_ID to view full conversation")
            print("   Example: python scripts/view_chat_history.py --session sess_abc123\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
