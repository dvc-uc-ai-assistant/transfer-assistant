# Scripts Directory

Essential utility scripts for the Transfer Assistant application.

## Available Scripts

### 🔄 `migrate_assist_to_transfer_rules.py`
**Purpose:** One-time migration from legacy `assist_data` JSON rows to SQL-first `transfer_rules` rows  
**When to use:** During SQL conversion (no local JSON file reads required)  
**Usage:**
```powershell
# Preview row counts only
python scripts/migrate_assist_to_transfer_rules.py --dry-run

# Execute migration
python scripts/migrate_assist_to_transfer_rules.py
```
Reads existing `assist_data` records from PostgreSQL and writes flattened SQL rows into `transfer_rules`.

---

### 📦 `load_json_to_assist_data.py` (Legacy)
**Purpose:** Load transfer agreement JSON files from disk into legacy `assist_data`  
**When to use:** Legacy bootstrap only  
**Usage:**
```powershell
python scripts/load_json_to_assist_data.py
```

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
2. **Migrate to SQL rules:** `python scripts/migrate_assist_to_transfer_rules.py`
3. **Test chatbot:** `.\scripts\test_chatbot.ps1`
4. **View history:** `python scripts/view_chat_history.py`
