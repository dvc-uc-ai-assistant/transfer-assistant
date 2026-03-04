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
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

#STRUCTURED LOGGING
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

#Import AI agent directly 
from backend.ai_agent import get_response

#ENV & PATHS 
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_DIST = os.path.join(ROOT_DIR, "frontend", "dist")

#FLASK APP 
app = Flask(
    __name__,
    static_folder=REACT_DIST,
    static_url_path="/"
)

CORS(app, resources={
    r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}
})

#SWAGGER (API DOCS)
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

#Session storage for maintaining context
sessions = {}

#GUARDRAILS (INPUT)
MAX_PROMPT_CHARS = int(os.getenv("MAX_PROMPT_CHARS", "2000"))
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", "20000"))  # about 20KB JSON cap

#GUARDRAILS (RATE LIMIT)
RATE_LIMIT_WINDOW_SECS = int(os.getenv("RATE_LIMIT_WINDOW_SECS", "60"))
RATE_LIMIT_MAX_REQ = int(os.getenv("RATE_LIMIT_MAX_REQ", "20"))
_rate_hits = defaultdict(deque)  # in-memory per instance

#GUARDRAILS (TIMEOUT)
AI_TIMEOUT_SECS = int(os.getenv("AI_TIMEOUT_SECS", "20"))
_executor = ThreadPoolExecutor(max_workers=int(os.getenv("AI_MAX_WORKERS", "4")))

#HELPERS
def new_session_id() -> str:
    return "sess_" + os.urandom(6).hex()

def now_iso() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

def guardrail_log(event: str, session_id: str, meta: dict | None = None):
    payload = {"event": event, "session_id": session_id}
    if meta:
        payload.update(meta)
    logger.warning(json.dumps(payload))

def get_client_ip() -> str:
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"

def rate_limit_or_429(session_id: str):
    key = get_client_ip()
    now = time.time()
    q = _rate_hits[key]

    while q and q[0] < now - RATE_LIMIT_WINDOW_SECS:
        q.popleft()

    if len(q) >= RATE_LIMIT_MAX_REQ:
        guardrail_log("rate_limited", session_id, {
            "client_ip": key,
            "window_secs": RATE_LIMIT_WINDOW_SECS,
            "max_req": RATE_LIMIT_MAX_REQ
        })
        return jsonify({
            "error": "Rate limit exceeded. Please try again soon.",
            "session_id": session_id
        }), 429

    q.append(now)
    return None

def get_response_with_timeout(user_prompt: str, session_state: dict, session_id: str):
    future = _executor.submit(get_response, user_prompt, session_state, session_id)
    return future.result(timeout=AI_TIMEOUT_SECS)

#API ROUTES 
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

    #Size cap (cost/resource protection) 
    if request.content_length is not None and request.content_length > MAX_BODY_BYTES:
        session_id = (request.args.get("session_id") or "").strip() or new_session_id()
        guardrail_log("input_rejected_body_too_large", session_id, {"content_length": request.content_length})
        return jsonify({
            "error": f"Request too large. Max {MAX_BODY_BYTES} bytes.",
            "session_id": session_id
        }), 413

    #Strict JSON validation 
    req_data = request.get_json(silent=True)

    session_id = ""
    if isinstance(req_data, dict):
        session_id = (req_data.get("session_id") or "").strip()
    session_id = session_id or new_session_id()

    if req_data is None:
        guardrail_log("input_rejected_invalid_json", session_id, {})
        return jsonify({
            "error": "Invalid or missing JSON body. Expected application/json with {'prompt': '...'}",
            "session_id": session_id
        }), 400

    if not isinstance(req_data, dict):
        guardrail_log("input_rejected_bad_format", session_id, {"type": str(type(req_data))})
        return jsonify({
            "error": "Invalid request format. JSON body must be an object.",
            "session_id": session_id
        }), 400

    user_prompt = req_data.get("prompt")

    if not isinstance(user_prompt, str):
        guardrail_log("input_rejected_prompt_not_string", session_id, {"type": str(type(user_prompt))})
        return jsonify({
            "error": "Invalid prompt type. 'prompt' must be a string.",
            "session_id": session_id
        }), 400

    user_prompt = user_prompt.strip()

    #Safer structured info log
    logger.info(json.dumps({
        "event": "prompt_received",
        "session_id": session_id,
        "prompt_length": len(user_prompt)
    }))

    #Input guardrails 
    if not user_prompt:
        guardrail_log("input_rejected_empty_prompt", session_id, {})
        return jsonify({
            "error": "No prompt provided.",
            "session_id": session_id
        }), 400

    if len(user_prompt) > MAX_PROMPT_CHARS:
        guardrail_log("input_rejected_prompt_too_long", session_id, {"length": len(user_prompt)})
        return jsonify({
            "error": f"Prompt too long. Max {MAX_PROMPT_CHARS} characters.",
            "session_id": session_id
        }), 400

    rl = rate_limit_or_429(session_id)
    if rl is not None:
        return rl

    try:
        if session_id not in sessions:
            sessions[session_id] = {
            "campuses": [],
            "completed_courses": [],
            "completed_domains": [],
            "categories": []
        }
        
        session_state = sessions[session_id]
        
        try:
        formatted_response, updated_state = get_response_with_timeout(
            user_prompt,
            session_state,
            session_id
        )
    except FuturesTimeoutError:
        guardrail_log("ai_timeout", session_id, {"timeout_secs": AI_TIMEOUT_SECS})
        return jsonify({
            "error": "Upstream timeout. Please try again.",
            "session_id": session_id
        }), 504

    sessions[session_id] = updated_state

        logger.info(json.dumps({
            "event": "response_generated",
            "session_id": session_id
        }))

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


#SPA STATIC 
@app.get("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:path>")
def catch_all(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


#MAIN
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    host = "0.0.0.0" if os.getenv("FLASK_ENV") == "production" else "127.0.0.1"
    debug = os.getenv("FLASK_ENV") != "production"

    print(f"Flask running on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
