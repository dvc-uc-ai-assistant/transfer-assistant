# app.py  — NEXA backend (Flask)

from flasgger import Swagger
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import datetime
import logging
import sys
import json

# ---------- STRUCTURED LOGGING ----------
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record)
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Import AI agent directly (no subprocess needed!)
from backend.ai_agent import get_response

# ---------- ENV & PATHS ----------
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_DIST = os.path.join(ROOT_DIR, "frontend", "dist")

# ---------- FLASK APP ----------
app = Flask(
    __name__,
    static_folder=REACT_DIST,
    static_url_path="/"
)

CORS(app, resources={
    r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}
})

# ---------- SWAGGER (API DOCS) ----------
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

Swagger(app, config=swagger_config)

print("[OK] Flask app initialized")

# Session storage for maintaining context
sessions = {}

# ---------- HELPERS ----------
def new_session_id() -> str:
    return "sess_" + os.urandom(6).hex()

def now_iso() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

# ---------- API ROUTES ----------
@app.get("/health")
def health():
    return "OK", 200


@app.post("/prompt")
def handle_prompt():
    """
    Get an AI response to a transfer question.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - prompt
          properties:
            prompt:
              type: string
              example: "How do I transfer to UC Berkeley for Computer Science?"
            session_id:
              type: string
              example: "abc123"
    responses:
      200:
        description: AI-generated response
        schema:
          type: object
          properties:
            response:
              type: string
            session_id:
              type: string
    """
    req_data = request.get_json(silent=True) or {}
    user_prompt = (req_data.get("prompt") or "").strip()
    session_id = (req_data.get("session_id") or "").strip() or new_session_id()

    logger.info(f"Received prompt from session {session_id}")

    if not user_prompt:
        return jsonify({
            "error": "No prompt provided.",
            "session_id": session_id
        }), 400

    try:
        if session_id not in sessions:
            sessions[session_id] = {
                "campuses": [],
                "completed_courses": [],
                "completed_domains": [],
                "categories": []
            }

        session_state = sessions[session_id]

        formatted_response, updated_state = get_response(
            user_prompt,
            session_state,
            session_id
        )

        sessions[session_id] = updated_state

        logger.info(f"Response generated for session {session_id}")

        return jsonify({
            "response": formatted_response,
            "session_id": session_id,
            "state": updated_state
        }), 200

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"ValueError in handle_prompt: {error_msg}")
        return jsonify({
            "error": f"Configuration error: {error_msg}",
            "session_id": session_id
        }), 500

    except Exception as e:
        logger.exception("Unhandled exception in handle_prompt")
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "session_id": session_id
        }), 500


# ---------- SPA STATIC ----------
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
    port = int(os.getenv("PORT", 8081))
    host = "0.0.0.0" if os.getenv("FLASK_ENV") == "production" else "127.0.0.1"
    debug = os.getenv("FLASK_ENV") != "production"

    print(f"Flask running on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
