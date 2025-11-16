"""
Quick Terminal Test for Feedback Agent
Run this to verify feedback collection is working
"""
import requests
import json

API_URL = "http://localhost:8000/api/chat"

def test(message, session_id, test_name):
    """Send message and print response"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"User: {message}")
    print(f"Session: {session_id}")
    
    payload = {"message": message, "session_id": session_id}
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✓ Response received:")
        for msg in data["messages"]:
            print(f"  {msg}")
        
        # Check for HITL marker
        all_text = " ".join(data["messages"])
        if "NEEDS_HUMAN_REVIEW" in all_text:
            print(f"\n🚨 HITL FLAG DETECTED! 🚨")
            print(f"   Human review required")
        
        return data
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

# Test 1: Trigger feedback
print("\n" + "="*70)
print(" FEEDBACK AGENT TERMINAL TESTS")
print("="*70)

test("I want to give feedback", "term-test-1", "Trigger Feedback Agent")

# Test 2: Positive feedback
test("rate this", "term-test-2", "Rate Trigger")
test("Rating 5/5! Very helpful!", "term-test-2", "Positive Feedback")

# Test 3: Safety concern
test("feedback", "term-test-3", "Feedback Trigger")
test("Rating 1/5. This advice was dangerous and hurt me!", "term-test-3", "Safety Concern - SHOULD TRIGGER HITL")

print("\n" + "="*70)
print(" Tests Complete!")
print("="*70)
