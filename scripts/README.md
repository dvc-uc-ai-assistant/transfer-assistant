# Scripts Directory

Essential utility scripts for the Transfer Assistant application.

## Available Scripts

### 📦 `load_json_to_assist_data.py`
**Purpose:** Load transfer agreement JSON files into the database  
**When to use:** Initial setup or when updating course data  
**Usage:**
```powershell
python scripts/load_json_to_assist_data.py
```
Reads JSON files from `data/archived/` and populates the `assist_data` table.

---

### 🗄️ `setup_postgresql.ps1`
**Purpose:** Initialize PostgreSQL database and user  
**When to use:** First-time database setup  
**Usage:**
```powershell
.\scripts\setup_postgresql.ps1
```
Creates the `transfer_assistant_db` database and `transfer_user` with proper permissions.

---

### 🧪 `test_chatbot.ps1`
**Purpose:** Interactive chatbot testing via API  
**When to use:** Testing conversational flows and session management  
**Usage:**
```powershell
.\scripts\test_chatbot.ps1
```
Sends test prompts to the `/prompt` endpoint and displays responses.

---

### 💬 `view_chat_history.py`
**Purpose:** View stored conversation history from database  
**When to use:** Debugging, analytics, or verifying chat persistence  
**Usage:**
```powershell
# View recent sessions (last 24 hours)
python scripts/view_chat_history.py

# View specific session
python scripts/view_chat_history.py --session sess_abc123

# Look back 7 days
python scripts/view_chat_history.py --days 7
```

---

## Quick Setup Workflow

1. **Setup database:** `.\scripts\setup_postgresql.ps1`
2. **Load data:** `python scripts/load_json_to_assist_data.py`
3. **Test chatbot:** `.\scripts\test_chatbot.ps1`
4. **View history:** `python scripts/view_chat_history.py`
