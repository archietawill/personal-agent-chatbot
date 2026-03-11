from agent import Planner
import json

def test_planner_refinement():
    print("Testing Planner Refinement...")
    planner = Planner()
    
    # Simple query
    print("\nCase 1: Simple schedule lookup")
    plan = planner.create_plan("What's my schedule today?", {})
    print(f"Plan steps: {len(plan)}")
    for s in plan:
        print(f" - {s['action']}")
    
    if len(plan) <= 1:
        print("✅ Refinement verified: Simple query has 0-1 step plan.")
    else:
        print(f"❌ Refinement failed: Simple query still has {len(plan)} steps.")

    # Complex query
    print("\nCase 2: Complex scheduling")
    plan = planner.create_plan("Schedule a meeting with Sarah for 1 hour at a quiet cafe. Keep it under $20.", {"budget_limit": 20})
    print(f"Plan steps: {len(plan)}")
    for s in plan:
        print(f" - {s['action']}")
        
    if len(plan) > 1:
        print("✅ Refinement verified: Complex query still has multi-step plan.")
    else:
        print("❌ Refinement failed: Complex query should have multiple steps.")

if __name__ == "__main__":
    test_planner_refinement()
