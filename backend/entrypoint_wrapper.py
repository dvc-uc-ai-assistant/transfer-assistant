"""Compatibility wrapper for legacy backend entrypoint.

Canonical Flask app lives in the repository root at app.py.
This module re-exports it so legacy commands can still run from backend/.
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app  # noqa: E402


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    host = "0.0.0.0" if os.getenv("FLASK_ENV") == "production" else "127.0.0.1"
    debug = os.getenv("FLASK_ENV") != "production"
    app.run(host=host, port=port, debug=debug)
