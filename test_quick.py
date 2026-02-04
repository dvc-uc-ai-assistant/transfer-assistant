import requests
import json

BASE = "http://127.0.0.1:8081"

# First query
print("Sending first query...")
r1 = requests.post(f"{BASE}/prompt", json={"prompt": "What Science courses for CS at UC Davis?"}, timeout=30)
print(f"Status: {r1.status_code}")

if r1.status_code == 200:
    data1 = r1.json()
    sid = data1.get("session_id")
    state1 = data1.get("state", {})
    resp1 = data1.get("response", "")
    
    print(f"Session ID: {sid}")
    print(f"Campuses in state: {state1.get('campuses', [])}")
    print(f"Response length: {len(resp1)}")
    print(f"Response preview: {resp1[:200]}")
    
    # Follow-up query with session_id
    print("\n\nSending follow-up query with session...")
    r2 = requests.post(f"{BASE}/prompt", json={"prompt": "show me only physics", "session_id": sid}, timeout=30)
    print(f"Status: {r2.status_code}")
    
    if r2.status_code == 200:
        data2 = r2.json()
        state2 = data2.get("state", {})
        resp2 = data2.get("response", "")
        
        print(f"Campuses in follow-up state: {state2.get('campuses', [])}")
        print(f"Response length: {len(resp2)}")
        print(f"Response preview: {resp2[:200]}")
        
        if state2.get('campuses') == state1.get('campuses'):
            print("\n✓ Campus preserved in follow-up!")
        else:
            print(f"\n✗ Campus changed! Was {state1.get('campuses')}, now {state2.get('campuses')}")
    else:
        print(f"Follow-up failed: {r2.text[:300]}")
else:
    print(f"First request failed: {r1.text[:300]}")
