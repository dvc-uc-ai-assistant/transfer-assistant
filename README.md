
# Transfer Assistant — DVC → UC (LLM-assisted transfer helper)

This repository contains a small assistant that helps Diablo Valley College (DVC) students plan UC transfer preparation for a subset of UC campuses (UCB, UCD, UCSD).
The project includes a Python/Flask backend (LLM parsing, course filtering and formatting) and a React/Vite frontend for exploration and testing.

## High-level structure
- `app.py` — Flask server that exposes the UI and the `/prompt` endpoint.
- `backend/` (previously `src/` or `src/ai_agent.py`) — backend code (parsing/filtering/formatting). NOTE: repo may contain `src/` as the backend folder; both are acceptable but consider renaming to `backend/` for clarity.
- `agreements_25-26/` — campus mapping JSON files used as the data source.
- `data/` — runtime logs (conversation_log.csv, user_log.jsonl) and local data artifacts.
- `public/` — static demo UI files served by Flask (index.html, home/how-to/chatbot partials).
- `frontend/` — React + Vite application (development source, `frontend/src/*`).

## What endpoints exist today
- `GET /` — serves the static `public/index.html` (if you use Flask to serve the UI).
- `POST /prompt` — accepts JSON `{ "prompt": "..." }` and returns the assistant's response as JSON (current shape: `{ "response": "..." }`).

Planned improvements (recommended): `/health`, `/meta`, structured `{ok,data,error}` responses for `/prompt`, streaming or async prompt endpoints, and admin endpoints for reload and offline toggling.

## Quick start (recommended dev workflow)

Prerequisites
- Python 3.10+ (python on PATH)
- Node.js + npm (for the React frontend)

Backend (Flask)

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the repository root with your OpenAI key (do NOT commit it):

```
OPENAI_API_KEY=sk-...your-key...
```

4. Run the Flask server:

```powershell
python app.py
# server binds to 0.0.0.0:8080 by default
```

Frontend (React + Vite) — development mode

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

- `frontend/.vite/` — Vite dev/build cache files. These are generated artifacts and should be ignored by git. Add `frontend/.vite/` to `.gitignore` and remove from tracking if present:

```powershell
git rm -r --cached frontend/.vite
echo "frontend/.vite/" >> .gitignore
git add .gitignore
git commit -m "Ignore Vite cache"
```

- `frontend/node_modules/` — should be ignored (generated)
- `.env` — should never be committed. Use `.env.example` to show required variables.
- Python venv folders (`.venv/`, `venv/`) and `__pycache__` — ignore these too.

## Recommended repository organization

- Keep backend code in `backend/` (or `src/` if you prefer). Keep frontend code under `frontend/`.
- Keep `public/` for small demo static pages (or as the target for built frontend assets). Avoid keeping two independent canonical UIs unless you intentionally support both.

## Development tips & troubleshooting

- If `python app.py` exits immediately, check `app_start.log` or console output — the server prints a helpful message when `OPENAI_API_KEY` is missing.
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

