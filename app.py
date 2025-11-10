
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
# The static_folder is set to 'public' so Flask can serve your index.html, CSS, and JS files.
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Prefer serving a built frontend if it exists. This makes it simple to serve the
# React/Vite `frontend/dist` output without copying files into `public/`.
frontend_dist_index = os.path.join('frontend', 'dist', 'index.html')
if os.path.exists(frontend_dist_index):
    # Use absolute path for the static folder to avoid confusion when running from scripts/
    app.static_folder = os.path.abspath(os.path.join('frontend', 'dist'))
    print(f"Serving static files from: {app.static_folder}")
else:
    app.static_folder = os.path.abspath('public')
    print(f"Serving static files from: {app.static_folder}")

# --- AI Agent and Data Loading ---
api_key = os.getenv("OPENAI_API_KEY")
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() in ("1", "true", "yes")
if not api_key:
    print("WARNING: OPENAI_API_KEY is missing. Server will run in limited mode.")
    client = None
else:
    client = OpenAI(api_key=api_key)

# Load all campus data once at startup.
data = load_all_data([
    os.path.join("agreements_25-26", "*.json"),
])
print("✅ Loaded campuses:", sorted(list(data.keys())))
if not data:
    print("⚠️ No campus files loaded. Check the 'agreements_25-26/' directory.")

# --- API and Frontend Routes ---

@app.route('/')
def serve_index():
    """Serves the main index.html file from the 'public' directory."""
    # Prefer a demo public/ index, then a built frontend, otherwise show a helpful page.
    public_index = os.path.join(app.static_folder, 'index.html')
    frontend_dist_index = os.path.join('frontend', 'dist', 'index.html')
    frontend_src_index = os.path.join('frontend', 'index.html')

    if os.path.exists(public_index):
        return send_from_directory(app.static_folder, 'index.html')
    if os.path.exists(frontend_dist_index):
        # Serve built React app files from frontend/dist
        return send_from_directory(os.path.dirname(frontend_dist_index), os.path.basename(frontend_dist_index))
    if os.path.exists(frontend_src_index):
        # The React app is present but not built. Serve a small helper page that tells the developer
        # to run the Vite dev server or build the frontend.
        helper_html = f"""
        <!doctype html>
        <html>
          <head><meta charset='utf-8'><title>Frontend not built</title></head>
          <body>
            <h2>Frontend not built</h2>
            <p>The repository contains a frontend development project but the built assets were not found.</p>
            <p>To use the development server (recommended):</p>
            <pre>cd frontend
npm install
npm run dev</pre>
            <p>Then open <a href='http://localhost:5173' target='_blank'>http://localhost:5173</a></p>
            <p>Or build the frontend and place the output in <code>frontend/dist/</code> or copy into <code>public/</code>.</p>
          </body>
        </html>
        """
        return helper_html

    return (
        jsonify({
            'error': 'No index.html found',
            'checked': [public_index, frontend_dist_index, frontend_src_index],
            'hint': 'Build the frontend (cd frontend && npm run build) or place a demo index.html in public/'
        }),
        404,
    )


@app.route('/health', methods=['GET'])
def health():
    loaded = list(data.keys()) if isinstance(data, dict) else []
    ok = bool(loaded)
    return (jsonify({'ok': ok, 'has_api_key': bool(api_key), 'loaded_campuses': loaded}), 200 if ok else 503)

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    """Handles the AI prompt requests from the frontend."""
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
