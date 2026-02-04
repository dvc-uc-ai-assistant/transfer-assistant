
# Transfer Assistant — DVC → UC (LLM-assisted transfer helper)

This repository contains an AI-powered assistant that helps Diablo Valley College (DVC) students plan UC transfer preparation for multiple UC campuses (UCB, UCD, UCSD).
The project includes a Python/Flask backend with PostgreSQL database (LLM parsing, course filtering and formatting) and a React/Vite frontend for exploration and testing.

**🎉 NEW: PostgreSQL Migration Complete!** All course data now stored in PostgreSQL for better scalability and performance. See [POSTGRES_MIGRATION.md](POSTGRES_MIGRATION.md) for details.

## High-level structure
- `app.py` — Flask server that exposes the UI and the `/prompt` endpoint.
- `backend/` — Backend code (AI agent, database models, repository layer).
  - `backend/ai_agent.py` — LLM parsing and course filtering logic.
  - `backend/database/` — SQLAlchemy models and PostgreSQL repository.
- `agreements_25-26/` — Source JSON files containing campus transfer agreements (used for initial data import).
- `data/` — Runtime logs (conversation_log.csv, user_log.jsonl) and local data artifacts.
- `public/` — Static demo UI files served by Flask (index.html, home/how-to/chatbot partials).
- `frontend/` — React + Vite application (development source, `frontend/src/*`).

## What endpoints exist today
- `GET /` — serves the static `public/index.html` (if you use Flask to serve the UI).
- `POST /prompt` — accepts JSON `{ "prompt": "..." }` and returns the assistant's response as JSON (current shape: `{ "response": "..." }`).

Planned improvements (recommended): `/health`, `/meta`, structured `{ok,data,error}` responses for `/prompt`, streaming or async prompt endpoints, and admin endpoints for reload and offline toggling.

## Quick start (recommended dev workflow)

### Prerequisites
- Python 3.10+ (python on PATH)
- Node.js + npm (for the React frontend)
- PostgreSQL 17 (or compatible version)

### Step 1: PostgreSQL Database Setup

1. **Install PostgreSQL 17** (Windows):

```powershell
winget install -e --id PostgreSQL.PostgreSQL.17
```

2. **Set PostgreSQL superuser password** (required for database creation):

```powershell
# Temporarily allow trust authentication
# Edit: C:\Program Files\PostgreSQL\17\data\pg_hba.conf
# Change: host all all 127.0.0.1/32 scram-sha-256
# To: host all all 127.0.0.1/32 trust
# Then restart PostgreSQL service

Restart-Service postgresql-x64-17

# Connect and set password
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'your_postgres_password';"

# Restore scram-sha-256 authentication in pg_hba.conf and restart again
```

3. **Create database and user using the provided script**:

```powershell
# Set environment variable for automation
$env:PGPASSWORD = "your_postgres_password"

# Run the setup script
.\setup_postgresql.ps1
```

The script creates:
- Database: `transfer_assistant_db`
- User: `transfer_user` with password `hello`
- Grants all necessary privileges

### Step 2: Backend (Flask + PostgreSQL)

1. **Create and activate a virtual environment** (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. **Install Python dependencies**:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. **Create a `.env` file** in the repository root (do NOT commit it):

```env
OPENAI_API_KEY=sk-...your-key...
DATABASE_URL=postgresql://transfer_user:hello@localhost:5432/transfer_assistant_db
DATA_BACKEND=postgres
FLASK_ENV=development
LOG_FOLDER=logs
```

See `.env.example` for a complete template.

4. **Initialize the database schema**:

```powershell
python init_db.py
```

This creates all necessary tables (universities, years, categories, courses, equivalencies).

5. **Populate the database with course data**:

```powershell
# Migrate JSON data to PostgreSQL (one-time migration)
python migrate_json_to_db.py
```

This loads all UC campus articulation agreements from `agreements_25-26/*.json` into PostgreSQL.

**Result:**
- 3 universities (UC Berkeley, UC Davis, UC San Diego)
- 9 categories (CS, Math, Science requirements)
- 39 UC courses, 27 DVC courses, 45 course equivalencies

6. **Run the Flask server**:

```powershell
python app.py
# server binds to 0.0.0.0:8081 by default
```

7. **Test the PostgreSQL integration** (optional):

```powershell
python test_postgres_integration.py
```

Frontend (React + Vite) — development mode

### Step 3: Frontend (React + Vite)

Open a separate terminal and run:

```powershell
cd frontend
npm install
npm run dev
# Vite dev server typically runs at http://localhost:5173
```

Notes:
- During development you can run both the Vite dev server and the Flask server. Flask has `CORS(app)` enabled so cross-origin requests from the frontend dev server should work.
- To serve the frontend from Flask (local production test): build the React app (`npm run build`) and copy `frontend/dist/*` into `public/` or configure Flask's `static_folder` to point to the build output.

## Files you may want to clean / avoid committing

- `.env` — **NEVER commit this file**. Contains secrets (API keys, database passwords). Use `.env.example` to show required variables.
- `frontend/.vite/` — Vite dev/build cache files. These are generated artifacts and should be ignored by git. Add `frontend/.vite/` to `.gitignore` and remove from tracking if present:

```powershell
git rm -r --cached frontend/.vite
echo "frontend/.vite/" >> .gitignore
git add .gitignore
git commit -m "Ignore Vite cache"
```

- `frontend/node_modules/` — should be ignored (generated)
- Python venv folders (`.venv/`, `venv/`) and `__pycache__` — ignore these too.
- `data/*.csv`, `data/*.jsonl`, `logs/*.json` — runtime logs (consider ignoring or using `.gitkeep` for empty folders)

## Recommended repository organization

- Keep backend code in `backend/` with subdirectories for logical separation:
  - `backend/ai_agent.py` — Core LLM logic
  - `backend/database/` — Database models and repository pattern
- Keep frontend code under `frontend/`.
- Keep `public/` for small demo static pages (or as the target for built frontend assets).
- Store configuration templates in root (`.env.example`, `setup_postgresql.ps1`, `init_db.py`).

## Architecture Notes

### Database Layer
The application uses SQLAlchemy ORM with PostgreSQL for data persistence:
- **Models**: `University`, `Year`, `Category`, `UCCourse`, `DVCCourse`, `CourseEquivalency`
- **Repository Pattern**: `PostgresRepository` class abstracts database queries
- **Relationships**: Properly defined foreign keys with cascade deletes
- **Indexes**: Performance-optimized for common query patterns

### Data Flow
1. User submits prompt → Flask `/prompt` endpoint
2. LLM parses intent (campus, categories, filters)
3. Repository queries PostgreSQL for matching courses
4. AI agent formats response with filtered results
5. Frontend displays formatted course recommendations

## Development tips & troubleshooting

### Database Connection Issues

- **Can't connect to PostgreSQL**: Verify the service is running:
  ```powershell
  Get-Service postgresql-x64-17
  ```
  If stopped, start it:
  ```powershell
  Start-Service postgresql-x64-17
  ```

- **Authentication failed**: Check that `DATABASE_URL` in `.env` matches the credentials created during setup (default: `transfer_user` / `hello`).

- **Tables don't exist**: Run `python init_db.py` to create the schema.

### Application Troubleshooting

- If `python app.py` exits immediately, check `app_start.log` or console output — the server prints a helpful message when `OPENAI_API_KEY` is missing or database connection fails.

- To confirm endpoints from PowerShell:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8080/health  # if implemented
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8080/prompt -Body '{"prompt":"hi"}' -ContentType 'application/json'
```

- If the frontend shows stale or duplicate content, ensure you're loading the correct UI (Vite dev server vs Flask-served `public/`) and clear caches.

## Security and secrets

- Rotate any API keys that were accidentally committed. Keep `.env` out of git and use `.env.example` to show variables.
- Protect admin endpoints with tokens and only expose metrics/docs on private networks in production.

## Tests

- There are unit tests for some backend helpers (e.g., fuzzy matching) under `tests/`. Run them with:

```powershell
python -m pytest -q
```

If your environment can't find `pytest`, ensure it is installed into the active virtual environment.

## Contributing / next steps

- Consider adding the following low-risk improvements first:
	- `GET /health` and `GET /meta` endpoints for monitoring and UI readiness checks.
	- Standardize `POST /prompt` responses to a structured `{ok,data,error}` schema (makes frontend parsing simpler).
	- Add `OFFLINE_MODE` to allow UI testing without a real OpenAI key.

If you'd like, I can make any of the above changes (ignore rules, README edits, health/meta endpoints, or offline mode). Tell me which you'd like me to implement and I'll apply the patch and run a quick smoke test.

---

## License

See `LICENSE` in the repository root.

