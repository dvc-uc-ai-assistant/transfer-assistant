from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Import necessary functions from ai_agent
from src.ai_agent import (
    llm_parse_user_message,
    load_all_data,
    collect_course_rows,
    filter_rows,
    llm_format_response_multi,
    parse_preferences_seed,
    detect_campuses_from_query
)

load_dotenv()
app = Flask(__name__)
# Enable CORS for all routes, allowing your frontend to communicate with this server.
CORS(app)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # This will be printed at startup if the key is missing
    print("ERROR: OPENAI_API_KEY is missing. Please set it in your .env file.")
client = OpenAI(api_key=api_key)

# Load all campus data once when the server starts up.
data = load_all_data([
    os.path.join("agreements_25-26", "*.json"),
])
print("✅ Loaded campuses:", sorted(list(data.keys())))
if not data:
    print("⚠️ No campus files loaded. Check the 'agreements_25-26/' directory.")

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    """
    Handles POST requests to /prompt.
    It takes a JSON object with a "prompt" key, processes it with the AI agent,
    and returns a JSON object with a "response" key.
    """
    if not api_key:
        return jsonify({'error': 'OPENAI_API_KEY is not configured on the server.'}), 500

    req_data = request.get_json()
    user_prompt = req_data.get('prompt')
    if not user_prompt:
        return jsonify({'error': 'No prompt provided in the request body.'}), 400

    # 1. Parse the user's message to understand their intent, filters, and requested campuses.
    parsed = llm_parse_user_message(client, user_prompt)

    # 2. Determine which campuses the user is asking about.
    campus_keys = parsed.get("parameters", {}).get("campuses") or detect_campuses_from_query(user_prompt)
    campus_keys = [ck for ck in campus_keys if ck in data]

    if not campus_keys:
        return jsonify({'response': "Sorry, I couldn't detect a specific campus in your request. I can help with UC Berkeley (UCB), UC Davis (UCD), and UC San Diego (UCSD)."})

    # 3. Extract filters and other state from the parsed message.
    filters = parsed.get("filters", {})
    completed_courses = set(filters.get("completed_courses", []))
    completed_domains = set(filters.get("domains_completed", []))
    focus_only = filters.get("focus_only")
    required_only = filters.get("required_only", False)
    categories_only = filters.get("categories", [])
    
    # Use seed preferences for additional context if needed (e.g., for exclusive domains).
    seed_prefs = parse_preferences_seed(user_prompt)

    # 4. For each relevant campus, collect all course data and then filter it down.
    campus_to_remaining = {}
    for ck in campus_keys:
        all_rows = collect_course_rows(data.get(ck, {}))
        filtered_rows = filter_rows(
            all_rows,
            seed_prefs,
            completed_courses,
            completed_domains,
            focus_only,
            required_only,
            categories_only=categories_only
        )
        campus_to_remaining[ck] = filtered_rows

    # 5. Use the LLM to format a user-friendly, natural language response.
    formatted_response = llm_format_response_multi(
        client,
        campus_keys,
        campus_to_remaining,
        parsed,
        completed_courses,
        completed_domains,
        plain=False  # Use rich LLM-based formatting for the best user experience.
    )

    # 6. Send the final formatted response back to the frontend.
    return jsonify({'response': formatted_response})

if __name__ == '__main__':
    # Check for the essential OpenAI API key before starting the server.
    if not api_key:
        print("FATAL ERROR: The OPENAI_API_KEY environment variable is not set.")
    else:
        print("Starting Flask server...")
        # Run the app on host 0.0.0.0 to make it accessible from your local network.
        # The port is set to 8080, which the frontend expects.
        app.run(host='0.0.0.0', port=8080, debug=True)