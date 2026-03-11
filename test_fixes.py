from agent import StateManager, extract_quick_replies

def test_budget_fix():
    print("Testing Budget Fix...")
    sm = StateManager()
    sm.budget = 100
    
    # Simulate a schedule update with a cost
    tool_args = {
        "event_details": {"cost": 10, "time": "16:00-17:00", "event": "Test", "type": "meeting"},
        "date": "2026-03-11"
    }
    result = {"status": "success", "event": {"time": "16:00-17:00", "event": "Test", "type": "meeting"}}
    
    sm._handle_schedule_update(tool_args, result)
    
    print(f"Remaining budget: {sm.budget}")
    if sm.budget == 90:
        print("✅ Budget fix verified: 100 - 10 = 90")
    else:
        print(f"❌ Budget fix failed: Expected 90, got {sm.budget}")

def test_quick_reply_parsing():
    print("\nTesting Quick Reply Parsing...")
    text = """
I found some great options for you.
QUICK_REPLIES:
- Yes, proceed
- No, show alternatives
- Cancel
    """
    replies = extract_quick_replies(text)
    print(f"Extracted: {replies}")
    expected = ["Yes, proceed", "No, show alternatives", "Cancel"]
    if replies == expected:
        print("✅ Quick reply parsing verified")
    else:
        print(f"❌ Quick reply parsing failed: Expected {expected}, got {replies}")

if __name__ == "__main__":
    test_budget_fix()
    test_quick_reply_parsing()
