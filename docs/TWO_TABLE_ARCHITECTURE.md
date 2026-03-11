# 🏗️ Two-Table Architecture Documentation

## Overview
This document describes the professional two-table architecture for managing static knowledge and dynamic conversation history in the Transfer Assistant application.

---

## 📊 Table 1: `assist_data` (Static Knowledge)

### Purpose
Stores parsed transfer agreements from your web scraper. This is your **source of truth** for transfer equivalencies between community colleges and UC campuses.

### Schema
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `source_college` | VARCHAR(100) | Source institution (e.g., "DVC") |
| `target_college` | VARCHAR(100) | Target UC campus (e.g., "UCB", "UCD", "UCSD") |
| `major` | VARCHAR(255) | Major name (e.g., "Computer Science", NULL for general ed) |
| `agreements_json` | JSON | Full parsed transfer agreement data |
| `created_at` | TIMESTAMP | When the record was first created |
| `updated_at` | TIMESTAMP | When the record was last updated |

### Indexes
- `idx_assist_source_target`: Fast lookups by source and target colleges
- `idx_assist_target_major`: Fast lookups by target college and major

### Usage Example

```python
from backend.database.repository import PostgresRepository

repo = PostgresRepository(database_url)

# Save transfer agreement data
agreement_data = {
    "categories": {
        "Computer Science (Required)": {
            "minimum_required": "all",
            "courses": [
                {
                    "uc_course": "COMPSCI 61A",
                    "dvc_equivalents": ["COMSC-210"]
                }
            ]
        }
    }
}

repo.save_assist_data(
    source_college="DVC",
    target_college="UCB",
    major="Computer Science",
    agreements_json=agreement_data
)

# Retrieve agreements
ucb_agreements = repo.get_assist_data(target_college="UCB")
cs_agreements = repo.get_assist_data(target_college="UCB", major="Computer Science")
```

---

## 💬 Table 2: `chat_history` (Dynamic Memory)

### Purpose
Remembers conversation context for each user session. Enables persistent, context-aware conversations across multiple requests.

### Schema
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `session_id` | VARCHAR(64) | Unique session identifier (e.g., "sess_a3f2e1") |
| `role` | VARCHAR(20) | Message sender: "user" or "assistant" |
| `content` | TEXT | The actual message content |
| `timestamp` | TIMESTAMP | When the message was sent |

### Indexes
- `idx_chat_session_time`: Fast retrieval of messages by session and time order

### Usage Example

```python
# Save user message
repo.save_message("sess_abc123", "user", "Show me CS courses for UCB")

# Save assistant response
repo.save_message("sess_abc123", "assistant", "Here are the CS courses...")

# Retrieve full conversation history
history = repo.get_chat_history("sess_abc123")
for msg in history:
    print(f"{msg.role}: {msg.content}")

# Get last 5 messages only
recent = repo.get_chat_history("sess_abc123", limit=5)

# Delete conversation history
deleted_count = repo.delete_chat_history("sess_abc123")

# Find active sessions
recent_sessions = repo.get_recent_sessions(days=7)
```

---

## 🔄 Integration with Flask App

Both [app.py](../app.py) and [backend/entrypoint_wrapper.py](../backend/entrypoint_wrapper.py) now automatically save chat messages to the database:

```python
from backend.ai_agent import get_response, get_repository

@app.post("/prompt")
def handle_prompt():
    repo = get_repository()
    
    # Save user message
    repo.save_message(session_id, "user", user_prompt)
    
    # Get AI response
    formatted_response, updated_state = get_response(user_prompt, session_state)
    
    # Save assistant response
    repo.save_message(session_id, "assistant", formatted_response)
    
    return jsonify({"response": formatted_response, "session_id": session_id})
```

Every conversation is now **automatically persisted to PostgreSQL**!

---

## 🚀 Setup Instructions

### 1. Run Migration Script
```powershell
conda activate sklearn-env
python scripts/add_assist_chat_tables.py
```

This creates both tables in your existing database.

### 2. Test the Tables
```powershell
python scripts/test_two_tables.py
```

This runs sample operations on both tables to verify they work correctly.

### 3. Use in Your Application
The tables are now integrated! Just run your Flask app:

```powershell
# Development
python backend/entrypoint_wrapper.py

# Production (Docker)
docker build -t my-app .
docker run -p 8080:8080 -e DATABASE_URL="..." my-app
```

---

## 📈 Benefits of Two-Table Architecture

### ✅ `assist_data` Benefits
- **Centralized Knowledge**: Single source of truth for transfer agreements
- **Version Control**: Track when agreements were updated
- **Fast Queries**: Indexed by college and major for quick lookups
- **JSON Flexibility**: Store complex nested data structures
- **Scraper-Ready**: Perfect for automated data ingestion

### ✅ `chat_history` Benefits
- **Persistent Conversations**: Users can resume conversations later
- **Analytics Ready**: Track user questions and interaction patterns
- **Debugging**: Audit trail of all conversations
- **Context Awareness**: AI can reference previous messages
- **Session Management**: Track active vs. abandoned conversations

---

## 🔧 Repository API Reference

### AssistData Methods
```python
# Save or update transfer agreement
save_assist_data(source_college, target_college, major, agreements_json) -> AssistData

# Retrieve agreements with optional filters
get_assist_data(target_college=None, major=None) -> List[AssistData]
```

### ChatHistory Methods
```python
# Save a single message
save_message(session_id, role, content) -> ChatHistory

# Get conversation history (ordered by time)
get_chat_history(session_id, limit=None) -> List[ChatHistory]

# Delete all messages for a session
delete_chat_history(session_id) -> int

# Find active sessions in last N days
get_recent_sessions(days=7) -> List[str]
```

---

## 📝 Next Steps

1. **Data Population**: Use your scraper to populate `assist_data` with real transfer agreements
2. **Chat UI Enhancement**: Display conversation history from database on page load
3. **Analytics Dashboard**: Query `chat_history` to understand user behavior
4. **Backup Strategy**: Set up regular PostgreSQL backups
5. **Cloud Migration**: Deploy to Cloud SQL for production scalability

---

## 🎯 Database Schema Visualization

```
assist_data (Static Knowledge)
├── id (PK)
├── source_college → "DVC"
├── target_college → "UCB", "UCD", "UCSD"
├── major → "Computer Science"
└── agreements_json → {...full data...}

chat_history (Dynamic Memory)
├── id (PK)
├── session_id → "sess_abc123"
├── role → "user" or "assistant"
├── content → "Show me CS courses"
└── timestamp → 2026-02-11 08:56:47
```

---

## ✨ Status: Ready for Production

Both tables are:
- ✅ Created and verified
- ✅ Indexed for performance
- ✅ Integrated with Flask app
- ✅ Tested with sample data
- ✅ Docker-compatible
- ✅ Cloud-ready

**Your two-table architecture is live and operational!** 🚀
