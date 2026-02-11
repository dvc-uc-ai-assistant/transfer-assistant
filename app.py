# app.py  — NEXA backend (Flask)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import datetime
import subprocess
import sys

# ---------- ENV & PATHS ----------
load_dotenv()

# Current directory is root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_DIST = os.path.join(ROOT_DIR, "frontend", "dist")  # Vite build output
AI_AGENT_PATH = os.path.join(ROOT_DIR, "backend", "ai_agent.py")

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
    Handles AI prompt requests from the frontend by directly running ai_agent.py
    """
    req_data = request.get_json(silent=True) or {}
    user_prompt = (req_data.get("prompt") or "").strip()
    session_id = (req_data.get("session_id") or "").strip() or new_session_id()

    if not user_prompt:
        return jsonify({"error": "No prompt provided.", "session_id": session_id}), 400

    try:
        # Run ai_agent.py as subprocess with the user prompt
        result = subprocess.run(
            [sys.executable, AI_AGENT_PATH, user_prompt],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ROOT_DIR
        )

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error from ai_agent.py"
            print(f"ai_agent.py error: {error_msg}")
            return jsonify({
                "error": f"AI Agent error: {error_msg}",
                "session_id": session_id
            }), 500

        # Get the output from ai_agent.py
        output = result.stdout.strip()
        
        # The output from ai_agent is the formatted response
        formatted_response = output if output else "No response from AI Agent"

        # Return formatted response to chatbot
        return jsonify({
            "response": formatted_response,
            "session_id": session_id
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "AI Agent timed out. Please try again.",
            "session_id": session_id
        }), 500
    except Exception as e:
        print(f"Error in handle_prompt: {e}")
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
