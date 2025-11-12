
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Import necessary functions from ai_agent
from backend.ai_agent import (
    llm_parse_user_message,
    load_all_data,
    collect_course_rows,
    filter_rows,
    llm_format_response_multi,
    parse_preferences_seed,
    detect_campuses_from_query
)

load_dotenv()

# --- Flask App Setup ---
# Serve the built frontend files from the 'frontend/dist' directory.
app = Flask(__name__, static_folder=os.path.join('frontend', 'dist'), static_url_path='')
CORS(app)


# --- AI Agent and Data Loading ---
raw_api_key = os.getenv("OPENAI_API_KEY")
# Normalize common accidental formatting: strip surrounding whitespace and quotes
api_key = None
if raw_api_key:
    api_key = raw_api_key.strip()
    if (api_key.startswith('"') and api_key.endswith('"')) or (api_key.startswith("'") and api_key.endswith("'")):
        api_key = api_key[1:-1].strip()

OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() in ("1", "true", "yes")
print(f"OFFLINE_MODE={OFFLINE_MODE}")

if not api_key:
    print("WARNING: OPENAI_API_KEY is missing or malformed. Server will run in limited mode.")
    client = None
else:
    # Print a masked confirmation (don't leak the key)
    print(f"Loaded OPENAI_API_KEY (masked): {'*' * (6) }... (len={len(api_key)})")
    client = OpenAI(api_key=api_key)

# --- Lazy Loading Data Cache ---
_data_cache = None

def get_data():
    """Lazily loads and caches the campus data."""
    global _data_cache
    if _data_cache is None:
        print("Loading campus data...")
        _data_cache = load_all_data([
            os.path.join("agreements_25-26", "*.json"),
        ])
        print("✅ Loaded campuses:", sorted(list(_data_cache.keys())))
        if not _data_cache:
            print("⚠️ No campus files loaded. Check the 'agreements_25-26/' directory.")
    return _data_cache

# --- API and Frontend Routes ---

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # For any other path, serve the index.html file for the React app to handle routing.
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/health', methods=['GET'])
def health():
    data = get_data()
    loaded = list(data.keys()) if isinstance(data, dict) else []
    ok = bool(loaded)
    return (jsonify({'ok': ok, 'has_api_key': bool(api_key), 'loaded_campuses': loaded}), 200 if ok else 503)

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    """Handles the AI prompt requests from the frontend."""
    data = get_data()
    req_data = request.get_json() or {}
    user_prompt = req_data.get('prompt')
    if not user_prompt:
        return jsonify({'ok': False, 'error': {'code': 'MISSING_PROMPT', 'message': 'No prompt provided.'}}), 400

    # Offline/demo mode
    if OFFLINE_MODE or client is None:
        # Return a canned response useful for frontend development.
        canned = "Demo response (offline mode). The backend is running without an OpenAI key."
        return jsonify({
            'ok': True,
            'response': canned,
            'data': {'text': canned, 'provenance': [], 'meta': {'offline': True}}
        })

    # 1. Parse the user's message.
    try:
        parsed = llm_parse_user_message(client, user_prompt)
    except Exception as e:
        app.logger.exception('Failed to parse user message')
        return jsonify({'ok': False, 'error': {'code': 'PARSE_ERROR', 'message': 'Failed to parse user message.'}}), 500

    # 2. Determine campuses.
    campus_keys = parsed.get("parameters", {}).get("campuses") or detect_campuses_from_query(user_prompt)
    campus_keys = [ck for ck in campus_keys if ck in data]

    if not campus_keys:
        msg = "Sorry, I couldn't detect a specific campus. I cover UCB, UCD, and UCSD."
        return jsonify({'ok': True, 'response': msg, 'data': {'text': msg}})

    # 3. Extract filters.
    filters = parsed.get("filters", {})
    completed_courses = set(filters.get("completed_courses", []))
    completed_domains = set(filters.get("domains_completed", []))
    focus_only = filters.get("focus_only")
    required_only = filters.get("required_only", False)
    categories_only = filters.get("categories", [])
    seed_prefs = parse_preferences_seed(user_prompt)

    # 4. Filter course data.
    campus_to_remaining = {}
    for ck in campus_keys:
        all_rows = collect_course_rows(data.get(ck, {}))
        filtered_rows = filter_rows(
            all_rows, seed_prefs, completed_courses, completed_domains,
            focus_only, required_only, categories_only=categories_only
        )
        campus_to_remaining[ck] = filtered_rows

    # 5. Format the final response.
    try:
        formatted_response = llm_format_response_multi(
            client, campus_keys, campus_to_remaining, parsed,
            completed_courses, completed_domains, plain=False
        )
    except Exception:
        app.logger.exception('LLM formatting failed')
        return jsonify({'ok': False, 'error': {'code': 'LLM_ERROR', 'message': 'Failed to generate response.'}}), 500

    # 6. Send the response back to the frontend (include both legacy 'response' and structured 'data')
    return jsonify({
        'ok': True,
        'response': formatted_response,
        'data': {
            'text': formatted_response,
            'provenance': parsed.get('matched_texts', []),
            'confidence': parsed.get('confidence'),
            'meta': {'campuses': campus_keys}
        }
    })

if __name__ == '__main__':
    if not api_key and not OFFLINE_MODE:
        print("WARNING: OPENAI_API_KEY is not set. The server will still start but LLM features will be disabled.")
    print("\nFlask server is running. Open your browser to:")
    print(f"http://127.0.0.1:8080\n")
    app.run(host='0.0.0.0', port=8080, debug=True)
