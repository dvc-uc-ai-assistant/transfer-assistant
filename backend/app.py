# app.py  — NEXA backend (Flask)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AI agent directly (no subprocess needed!)
from backend.ai_agent import get_response

# ---------- ENV & PATHS ----------
load_dotenv()

# Go up from backend/ to root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REACT_DIST = os.path.join(ROOT_DIR, "frontend", "dist")  # Vite build output

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

print("[OK] Flask app initialized")

# Session storage for maintaining context
sessions = {}

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
    """
    Handles AI prompt requests from the frontend using direct import (fast!)
    """
    req_data = request.get_json(silent=True) or {}
    user_prompt = (req_data.get("prompt") or "").strip()
    session_id = (req_data.get("session_id") or "").strip() or new_session_id()

    if not user_prompt:
        return jsonify({"error": "No prompt provided.", "session_id": session_id}), 400

    try:
        # Get or create session state
        if session_id not in sessions:
            sessions[session_id] = {
                "campuses": [],
                "completed_courses": [],
                "completed_domains": [],
                "categories": []
            }
        
        session_state = sessions[session_id]
        
        # Call AI agent (handles: READ from AssistData → Call AI → WRITE to ChatHistory)
        formatted_response, updated_state = get_response(user_prompt, session_state, session_id)
        
        # Update session with new state
        sessions[session_id] = updated_state

        # Return formatted response to chatbot
        return jsonify({
            "response": formatted_response,
            "session_id": session_id,
            "state": updated_state
        }), 200

    except ValueError as e:
        # Handle missing API key or database errors
        error_msg = str(e)
        print(f"ValueError in handle_prompt: {error_msg}")
        return jsonify({
            "error": f"Configuration error: {error_msg}",
            "session_id": session_id
        }), 500
    except Exception as e:
        print(f"Error in handle_prompt: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "session_id": session_id
        }), 500

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
    # Use PORT from environment (Cloud Run) or default to 8081 (local dev)
    port = int(os.getenv("PORT", 8081))
    host = "0.0.0.0" if os.getenv("FLASK_ENV") == "production" else "127.0.0.1"
    debug = os.getenv("FLASK_ENV") != "production"
    
    print(f"Flask running on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
