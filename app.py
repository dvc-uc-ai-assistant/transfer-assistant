# app.py  — NEXA backend (Flask)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
from log_writer import log_event   # <-- JSON logging helper (logs/...)
import datetime

# ---------- ENV & PATHS ----------
load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
REACT_DIST = os.path.join(HERE, "frontend", "dist")  # Vite build output

# ---------- FLASK APP ----------
# (We keep static config so Flask can serve the built SPA in prod.)
app = Flask(
    __name__,
    static_folder=REACT_DIST,
    static_url_path="/"      # '/' resolves to index.html
)

# Allow Vite dev server (localhost:5173) to call Flask (localhost:8081)
CORS(app, resources={
    r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}
})

# ---------- OPENAI ----------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY is missing. Please set it in your .env file.")
client = OpenAI(api_key=api_key)

# ---------- DATA LOAD ----------
from src.ai_agent import (
    llm_parse_user_message,
    load_all_data,
    collect_course_rows,
    filter_rows,
    llm_format_response_multi,
    parse_preferences_seed,
    detect_campuses_from_query
)

data = load_all_data([os.path.join("agreements_25-26", "*.json")])
print("✅ Loaded campuses:", sorted(list(data.keys())))
if not data:
    print("⚠️ No campus files loaded. Check the 'agreements_25-26/' directory.")

# ---------- HELPERS ----------
def new_session_id() -> str:
    return "sess_" + os.urandom(6).hex()

def now_iso() -> str:
    # millisecond ISO + Z suffix
    return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

# ---------- API ROUTES ----------
@app.get("/health")
def health():
    return "OK", 200

@app.post("/prompt")
def handle_prompt():
    """Handles the AI prompt requests from the frontend, with session logging."""
    if not api_key:
        return jsonify({"error": "OPENAI_API_KEY is not configured on the server."}), 500

    req_data = request.get_json(silent=True) or {}
    user_prompt = (req_data.get("prompt") or "").strip()
    session_id = (req_data.get("session_id") or "").strip() or new_session_id()

    if not user_prompt:
        return jsonify({"error": "No prompt provided.", "session_id": session_id}), 400

    # 1) Parse the user's message.
    parsed = llm_parse_user_message(client, user_prompt)

    # 2) Determine campuses (fall back to detection if not parsed)
    campus_keys = parsed.get("parameters", {}).get("campuses") or detect_campuses_from_query(user_prompt)
    campus_keys = [ck for ck in (campus_keys or []) if ck in data]

    if not campus_keys:
        resp_text = "Sorry, I couldn't detect a specific campus. I cover UCB, UCD, and UCSD."

        # Log this turn (no campus detected)
        log_event({
            "timestamp": now_iso(),
            "session_id": session_id,
            "user_prompt": user_prompt,
            "campuses": [],
            "response_preview": resp_text[:150]
        })

        return jsonify({"response": resp_text, "session_id": session_id}), 200

    # 3) Extract filters.
    filters = parsed.get("filters", {}) or {}
    completed_courses = set(filters.get("completed_courses", []))
    completed_domains = set(filters.get("domains_completed", []))
    focus_only = filters.get("focus_only")
    required_only = filters.get("required_only", False)
    categories_only = filters.get("categories", [])
    seed_prefs = parse_preferences_seed(user_prompt)

    # 4) Filter course data.
    campus_to_remaining = {}
    for ck in campus_keys:
        all_rows = collect_course_rows(data.get(ck, {}))
        filtered_rows = filter_rows(
            all_rows, seed_prefs, completed_courses, completed_domains,
            focus_only, required_only, categories_only=categories_only
        )
        campus_to_remaining[ck] = filtered_rows

    # 5) Format the final response.
    formatted_response = llm_format_response_multi(
        client, campus_keys, campus_to_remaining, parsed,
        completed_courses, completed_domains, plain=False
    )

    # 6) Log this turn (append to logs/nexa_log_YYYY-MM-DD.json)
    log_event({
        "timestamp": now_iso(),
        "session_id": session_id,
        "user_prompt": user_prompt,
        "campuses": campus_keys,
        "response_preview": str(formatted_response)[:150]
    })

    # 7) Send the response back to the frontend (include session_id)
    return jsonify({"response": formatted_response, "session_id": session_id}), 200

# ---------- SPA STATIC (when serving build via Flask) ----------
@app.get("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/<path:path>")
def catch_all(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# ---------- MAIN ----------
if __name__ == "__main__":
    # Run on 8081 to match your working setup
    print("Flask running on http://127.0.0.1:8081")
    app.run(host="127.0.0.1", port=8081, debug=True)
