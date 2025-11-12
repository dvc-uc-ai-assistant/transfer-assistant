import sys
import os

# Ensure repo root is on sys.path so we can import app when this script is executed from scripts/
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from app import app

print('Using app from:', app.import_name)

with app.test_client() as c:
    print('\n--- GET / ---')
    r = c.get('/')
    print('status:', r.status_code)
    body = r.get_data(as_text=True)
    print('body (first 800 chars):\n')
    print(body[:800])

    # Parse index for asset references and request them to detect 404s
    import re
    scripts = re.findall(r'<script[^>]+src="([^"]+)"', body)
    links = re.findall(r'<link[^>]+href="([^"]+)"', body)
    assets = [a for a in (scripts + links) if a and not a.startswith('http')]
    if assets:
        print('\n--- Asset check ---')
        for a in assets:
            path = a if a.startswith('/') else '/' + a
            rr = c.get(path)
            print(f"{path} -> {rr.status_code} ({len(rr.get_data())} bytes)")

    print('\n--- GET /health ---')
    r2 = c.get('/health')
    print('status:', r2.status_code)
    try:
        print('json:', r2.get_json())
    except Exception:
        print('body:', r2.get_data(as_text=True))

    print('\n--- POST /prompt (test) ---')
    r3 = c.post('/prompt', json={'prompt': 'Hello, I want to test the backend.'})
    print('status:', r3.status_code)
    try:
        print('json:', r3.get_json())
    except Exception:
        print('body:', r3.get_data(as_text=True))

print('\nDone.')
