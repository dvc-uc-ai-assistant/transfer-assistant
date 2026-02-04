#!/usr/bin/env python3
"""
Test script to verify session persistence and follow-up question handling.
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8081"

def test_session_flow():
    """Test complete session flow: first query -> follow-up query"""
    
    print("=" * 60)
    print("TEST 1: First Query (detect campus)")
    print("=" * 60)
    
    first_query = "What Science courses are required for Computer Science at UC Davis?"
    payload = {"prompt": first_query}
    
    try:
        response = requests.post(f"{BASE_URL}/prompt", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            state = data.get("state", {})
            response_text = data.get("response", "")
            
            print(f"\nSession ID: {session_id}")
            print(f"State: {json.dumps(state, indent=2)}")
            print(f"\nResponse preview (first 300 chars):")
            print(response_text[:300])
            
            if state.get("campuses"):
                print(f"\n✓ Campus detected and saved: {state['campuses']}")
            else:
                print("\n✗ No campus in saved state!")
                return False
            
            print("\n" + "=" * 60)
            print("TEST 2: Follow-up Query (use saved session state)")
            print("=" * 60)
            
            time.sleep(1)  # Small delay
            
            second_query = "show me only physics"
            payload2 = {
                "prompt": second_query,
                "session_id": session_id
            }
            
            response2 = requests.post(f"{BASE_URL}/prompt", json=payload2, timeout=30)
            print(f"Status: {response2.status_code}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                state2 = data2.get("state", {})
                response_text2 = data2.get("response", "")
                
                print(f"\nUpdated State: {json.dumps(state2, indent=2)}")
                print(f"\nResponse preview (first 300 chars):")
                print(response_text2[:300])
                
                # Check if campus is still there
                if state2.get("campuses") == state.get("campuses"):
                    print(f"\n✓ Campus retained from session: {state2['campuses']}")
                else:
                    print(f"\n✗ Campus lost! Expected {state['campuses']}, got {state2.get('campuses')}")
                    return False
                
                # Check if response contains physics-related content
                if "physics" in response_text2.lower() or "phys" in response_text2.lower():
                    print("✓ Response appears to be physics-filtered")
                else:
                    print("? Response might not be filtered (check content manually)")
                
                print("\n" + "=" * 60)
                print("✓ SESSION PERSISTENCE TEST PASSED")
                print("=" * 60)
                return True
            else:
                print(f"✗ Second request failed: {response2.text}")
                return False
        else:
            print(f"✗ First request failed: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Flask server at http://127.0.0.1:8081")
        print("  Make sure Flask is running: python -m backend.app")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_session_flow()
    exit(0 if success else 1)
