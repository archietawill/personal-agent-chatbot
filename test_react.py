from agent import get_agent_response, SYSTEM_PROMPT

test_scenarios = [
    {
        "name": "Complex Constraint Satisfaction (Original Project Scenario)",
        "prompt": """I need to meet Sarah for an hour this afternoon to discuss the project. It needs to be a quiet place with Wi-Fi. I also need to finish my 45-minute daily run before the meeting. My total budget for the afternoon is $20.""",
        "expected_steps": [
            "Check calendar for availability",
            "Check Sarah's contact info",
            "Check weather for run timing",
            "Search venues with budget constraint",
            "Update schedule"
        ]
    },
    {
        "name": "Impossible Constraint Test",
        "prompt": """I need to meet Sarah for an hour this afternoon at 5 PM.
I need to do a 1-hour outdoor run at 4 PM.
The weather at 5 PM shows 100% rain.
My budget is only $5.
Find a solution that satisfies all constraints.""",
        "expected_behavior": "Agent should detect impossible constraints and suggest alternatives"
    },
    {
        "name": "Multi-Step Venue Selection",
        "prompt": """I want to find a quiet cafe with Wi-Fi in University Town under $20.
After finding options, check the weather at 3 PM to see if I can walk there.
Also calculate travel time from SIGS Campus to the venue.""",
        "expected_steps": [
            "Search venues",
            "Check weather",
            "Calculate travel time"
        ]
    },
    {
        "name": "Budget-Constrained Planning",
        "prompt": """I have $15 remaining in my budget.
I want to meet Mark for coffee and also grab lunch.
Find venues that fit within this budget for both activities.""",
        "expected_steps": [
            "Check finances",
            "Search venues",
            "Calculate total costs"
        ]
    }
]

def run_test(scenario):
    print(f"\n{'='*70}")
    print(f"TEST: {scenario['name']}")
    print(f"{'='*70}")
    print(f"Prompt: {scenario['prompt']}\n")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": scenario['prompt']}
    ]
    
    messages, trace_log = get_agent_response(messages)
    
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")
    print(f"Total steps: {len(trace_log)}")
    print(f"Tools called: {[step['action'] for step in trace_log if step['action']]}")
    
    if 'expected_steps' in scenario:
        print(f"\nExpected steps:")
        for i, step in enumerate(scenario['expected_steps'], 1):
            print(f"  {i}. {step}")
    
    print(f"\nActual reasoning trace:")
    for step in trace_log:
        print(f"\nStep {step['step']}:")
        print(f"  Thought: {step['thought'][:100]}...")
        if step['action']:
            print(f"  Action: {step['action']}")
            print(f"  Observation: {str(step['observation'])[:100]}...")
    
    return trace_log

if __name__ == "__main__":
    print("="*70)
    print("REACT LOOP ROBUSTNESS TEST SUITE")
    print("="*70)
    
    for i, scenario in enumerate(test_scenarios, 1):
        trace_log = run_test(scenario)
        
        if i < len(test_scenarios):
            print(f"\n{'='*70}")
            print(f"Running test {i+1}/{len(test_scenarios)} in 2 seconds...")
            print(f"{'='*70}")
            import time
            time.sleep(2)
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETED")
    print("="*70)
