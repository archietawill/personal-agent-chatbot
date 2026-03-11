import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from world import world
from datetime import datetime
import inspect

load_dotenv()

current_date = datetime.now().strftime("%Y-%m-%d")
current_datetime = datetime.now()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


class StateManager:
    def __init__(self):
        self.budget = None
        self.calendar = {}
        self.constraints = {
            "max_budget": None,
            "user_budget_limit": None,
            "weather_constraints": [],
            "time_conflicts": [],
            "outdoor_activity_required": False,
            "outdoor_activity_time": None
        }
        self.violations = []
        self.state_history = []
        self.user_constraints = {}
    
    def initialize_from_world(self, user_id="user_001", date=None):
        if date is None:
            date = current_date
        
        finances = world.check_finances(user_id)
        if finances["status"] == "success":
            self.budget = finances["remaining"]
            self.constraints["max_budget"] = finances["weekly_discretionary"]
        
        calendar = world.get_calendar(user_id, date)
        if calendar["status"] == "success":
            self.calendar[date] = calendar["events"]
        
        self._log_state("initialization")
    
    def update_after_tool_call(self, tool_name, tool_args, result):
        if result.get("status") != "success":
            return
        
        if tool_name == "update_schedule":
            self._handle_schedule_update(tool_args, result)
        elif tool_name == "check_finances":
            self._handle_finances_check(result)
        elif tool_name == "get_calendar":
            self._handle_calendar_get(tool_args, result)
        elif tool_name == "get_weather":
            self._handle_weather_check(tool_args, result)
        
        self._log_state(f"after_{tool_name}")
    
    def _handle_schedule_update(self, tool_args, result):
        if "event_details" in tool_args:
            event = tool_args["event_details"]
            if "cost" in event:
                if self.budget is not None:
                    self.budget -= event["cost"]
                    self._check_budget_violation(event["cost"])
        
        if "date" in tool_args:
            date = tool_args["date"]
            if date not in self.calendar:
                self.calendar[date] = []
            
            new_event = result.get("event", {})
            if new_event:
                # Local de-duplication in state manager
                is_duplicate = any(e.get("time") == new_event.get("time") and 
                                 e.get("event") == new_event.get("event") 
                                 for e in self.calendar[date])
                if not is_duplicate:
                    self.calendar[date].append(new_event)
    
    def _handle_finances_check(self, result):
        if "remaining" in result:
            self.budget = result["remaining"]
        if "weekly_discretionary" in result:
            self.constraints["max_budget"] = result["weekly_discretionary"]
    
    def _handle_calendar_get(self, tool_args, result):
        if "date" in tool_args:
            date = tool_args["date"]
            if result.get("status") == "success":
                self.calendar[date] = result.get("events", [])
    
    def _handle_weather_check(self, tool_args, result):
        if "rain_prob" in result:
            rain_prob = result["rain_prob"]
            hour = tool_args.get("hour")
            if rain_prob > 80:
                self.constraints["weather_constraints"].append({
                    "hour": hour,
                    "rain_prob": rain_prob,
                    "severity": "high"
                })
            elif rain_prob > 50:
                self.constraints["weather_constraints"].append({
                    "hour": hour,
                    "rain_prob": rain_prob,
                    "severity": "moderate"
                })
    
    def _check_budget_violation(self, cost):
        if self.constraints["max_budget"] and self.budget < 0:
            self.violations.append({
                "type": "budget",
                "severity": "critical",
                "message": f"Budget exceeded by ${abs(self.budget)}",
                "current_budget": self.budget,
                "cost_attempted": cost
            })
    
    def check_time_conflicts(self, new_event_time, date=None):
        if date is None:
            date = current_date
        
        if date not in self.calendar:
            return False
        
        new_start, new_end = self._parse_time_range(new_event_time)
        
        for event in self.calendar[date]:
            event_time = event.get("time", "")
            existing_start, existing_end = self._parse_time_range(event_time)
            
            if self._times_overlap(new_start, new_end, existing_start, existing_end):
                self.violations.append({
                    "type": "time_conflict",
                    "severity": "high",
                    "message": f"Time conflict: {new_event_time} overlaps with {event_time}",
                    "new_event": new_event_time,
                    "existing_event": event_time
                })
                return True
        
        return False
    
    def _parse_time_range(self, time_str):
        try:
            parts = time_str.split("-")
            start_time = int(parts[0].replace(":", ""))
            end_time = int(parts[1].replace(":", ""))
            return start_time, end_time
        except:
            return 0, 0
    
    def _times_overlap(self, start1, end1, start2, end2):
        return not (end1 <= start2 or end2 <= start1)
    
    def get_state_summary(self):
        return {
            "budget": self.budget,
            "max_budget": self.constraints["max_budget"],
            "calendar_events": len(self.calendar.get(current_date, [])),
            "violations": self.violations,
            "weather_constraints": self.constraints["weather_constraints"]
        }
    
    def _log_state(self, context):
        self.state_history.append({
            "context": context,
            "budget": self.budget,
            "calendar_keys": list(self.calendar.keys()),
            "violations_count": len(self.violations)
        })
    
    def has_critical_violations(self):
        return any(v.get("severity") == "critical" for v in self.violations)
    
    def parse_user_constraints(self, user_message):
        constraints = self._extract_constraints_with_llm(user_message)
        
        self.user_constraints = constraints
        
        if "budget_limit" in constraints:
            self.constraints["user_budget_limit"] = constraints["budget_limit"]
        
        if "outdoor_activity_required" in constraints:
            self.constraints["outdoor_activity_required"] = constraints["outdoor_activity_required"]
        
        if "outdoor_activity_time" in constraints:
            self.constraints["outdoor_activity_time"] = constraints["outdoor_activity_time"]
        
        if "meeting_time" in constraints:
            self.constraints["meeting_time"] = constraints["meeting_time"]
        
        return constraints
    
    def _extract_constraints_with_llm(self, user_message):
        try:
            response = client.chat.completions.create(
                model="google/gemini-3.1-flash-lite-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a constraint extraction system. Extract constraints from user messages about scheduling and logistics.

Extract ONLY these types of constraints:
1. budget_limit: Maximum amount user wants to spend (number, no $ symbol)
2. outdoor_activity_required: True if user mentions outdoor run, exercise, or activity
3. outdoor_activity_time: Hour (0-23) when outdoor activity should happen
4. meeting_time: Hour (0-23) when meeting should happen

Rules:
- Convert PM times to 24-hour format (4 PM = 16, 5 PM = 17)
- Convert AM times to 24-hour format (9 AM = 9, 12 AM = 0)
- Look for phrases like "spend more than X", "budget is X", "only X dollars", "cost less than X"
- Look for phrases like "run at X", "outdoor activity at X", "exercise at X"
- Look for phrases like "meet at X", "meeting at X"

Return ONLY valid JSON, no explanations. Example:
{"budget_limit": 50, "outdoor_activity_required": true, "outdoor_activity_time": 16, "meeting_time": 17}

If a constraint is not mentioned, omit it from JSON."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            import json
            try:
                constraints = json.loads(content)
                
                cleaned_constraints = {}
                for key, value in constraints.items():
                    if value is not None and value != "":
                        cleaned_constraints[key] = value
                
                return cleaned_constraints
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            return {}
    
    def check_constraint_before_action(self, tool_name, tool_args):
        if tool_name == "update_schedule":
            return self._check_schedule_constraint(tool_args)
        return True, None
    
    def _check_schedule_constraint(self, tool_args):
        if "event_details" not in tool_args:
            return True, None
        
        event = tool_args["event_details"]
        
        if "cost" in event and self.constraints["user_budget_limit"]:
            if self.budget - event["cost"] < 0:
                return False, {
                    "type": "budget",
                    "severity": "critical",
                    "message": f"Cannot schedule: Event cost ${event['cost']} would exceed your budget limit of ${self.constraints['user_budget_limit']}. Current budget: ${self.budget}",
                    "suggestion": f"Consider finding a cheaper venue or increasing your budget. You need at least ${event['cost'] - self.budget} more."
                }
        
        if "time" in event:
            event_time = event["time"]
            if self._check_time_conflict_prevention(event_time, tool_args.get("date", current_date)):
                return False, {
                    "type": "time_conflict",
                    "severity": "high",
                    "message": f"Time conflict: {event_time} overlaps with existing event",
                    "suggestion": "Choose a different time slot"
                }
        
        return True, None
    
    def _check_time_conflict_prevention(self, new_event_time, date):
        if date not in self.calendar:
            return False
        
        new_start, new_end = self._parse_time_range(new_event_time)
        
        for event in self.calendar[date]:
            event_time = event.get("time", "")
            existing_start, existing_end = self._parse_time_range(event_time)
            
            if self._times_overlap(new_start, new_end, existing_start, existing_end):
                return True
        
        return False
    
    def check_weather_constraint_for_outdoor_activity(self):
        if not self.constraints["outdoor_activity_required"]:
            return True, None
        
        if not self.constraints["outdoor_activity_time"]:
            return True, None
        
        for weather_constraint in self.constraints["weather_constraints"]:
            if weather_constraint["hour"] == self.constraints["outdoor_activity_time"]:
                if weather_constraint["severity"] == "high":
                    return False, {
                        "type": "weather",
                        "severity": "critical",
                        "message": f"Cannot schedule outdoor run at {self.constraints['outdoor_activity_time']}:00 - {weather_constraint['rain_prob']}% chance of rain",
                        "suggestion": "Consider moving the run to a different time or doing an indoor workout instead"
                    }
        
        return True, None
    
    def get_constraint_violation_summary(self):
        summary = {
            "violations": [],
            "impossible_constraints": []
        }
        
        if self.constraints["user_budget_limit"]:
            if self.budget < 0:
                summary["violations"].append({
                    "type": "budget",
                    "message": f"Budget exceeded by ${abs(self.budget)}",
                    "limit": self.constraints["user_budget_limit"]
                })
        
        if self.constraints["outdoor_activity_required"]:
            weather_ok, weather_msg = self.check_weather_constraint_for_outdoor_activity()
            if not weather_ok:
                summary["impossible_constraints"].append(weather_msg)
        
        return summary
    
    def record_attempt(self, action, params, result):
        if not hasattr(self, 'attempts'):
            self.attempts = []
        
        self.attempts.append({
            "action": action,
            "params": params,
            "result": result,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    def has_tried(self, action, params):
        if not hasattr(self, 'attempts'):
            return False
        
        for attempt in self.attempts:
            if attempt["action"] == action and attempt["params"] == params:
                return True
        return False
    
    def get_alternative_suggestions(self, failed_action, failed_params, constraint_msg):
        suggestions = []
        
        if failed_action == "update_schedule":
            if "budget" in constraint_msg.lower():
                suggestions.extend([
                    "Try searching for venues with max_price=0 (free venues)",
                    "Try searching for venues with max_price=5 (cheaper venues)",
                    "Consider meeting on campus instead of off-campus",
                    "Ask user if they can increase budget limit"
                ])
            elif "time" in constraint_msg.lower() or "conflict" in constraint_msg.lower():
                suggestions.extend([
                    "Try a different time slot",
                    "Check calendar for available times",
                    "Ask user for flexible meeting times"
                ])
        
        elif failed_action == "search_venues":
            if failed_params.get("result", {}).get("count", 0) == 0:
                suggestions.extend([
                    "Try a different venue type (cafe, study, restaurant)",
                    "Try searching without location constraint",
                    "Try searching with higher max_price"
                ])
        
        elif failed_action == "get_weather":
            if "rain" in constraint_msg.lower():
                suggestions.extend([
                    "Move outdoor activity to different time",
                    "Suggest indoor alternatives",
                    "Check weather for other times today"
                ])
        
        return suggestions
    
    def get_attempt_summary(self):
        if not hasattr(self, 'attempts'):
            return []
        
        summary = []
        for attempt in self.attempts:
            status = "success" if attempt["result"].get("status") == "success" else "failed"
            summary.append({
                "action": attempt["action"],
                "params": attempt["params"],
                "status": status,
                "timestamp": attempt["timestamp"]
            })
        return summary


class Planner:
    def __init__(self):
        self.plan = []
        self.completed_steps = []
        self.current_step = 0
    
    def create_plan(self, user_request, constraints):
        try:
            response = client.chat.completions.create(
                model="google/gemini-3.1-flash-lite-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a task decomposition planner. Break down complex scheduling requests into a step-by-step plan.

Your job is to create a checklist of sub-goals that the agent should accomplish.

Rules:
1. Break down complex requests into logical steps
2. Each step should be a specific, achievable action
3. Order steps logically (e.g., check calendar before scheduling)
4. Consider constraints (budget, time, weather) in the plan
5. Keep steps concise and actionable
6. IMPORTANT: For simple requests that only require a single tool call (e.g., "What's my schedule?", "What's the weather?"), do NOT create a multi-step plan. Just create a single-step plan or no plan at all if it's trivial.

Common patterns:
- For meetings: Check calendar → Check availability → Find/Suggest venues → Confirm choice with user → Schedule → Notify
- For activities: Check weather → Check schedule → Present options → Confirm with user → Schedule → Update
- For simple lookups: Single-step lookup

Return ONLY valid JSON with this format:
{
  "plan": [
    {"step": 1, "action": "Check user's calendar for today", "priority": "high"},
    {"step": 2, "action": "Check weather conditions for outdoor activities", "priority": "high"},
    {"step": 3, "action": "Search for suitable venues within budget", "priority": "medium"},
    {"step": 4, "action": "Schedule meeting with Sarah", "priority": "high"},
    {"step": 5, "action": "Notify contact about the meeting", "priority": "low"}
  ]
}

Priority levels: high, medium, low"""
                    },
                    {
                        "role": "user",
                        "content": f"User request: {user_request}\n\nConstraints: {constraints}\n\nCreate a step-by-step plan to accomplish this request."
                    }
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            import json
            try:
                plan_data = json.loads(content)
                self.plan = plan_data.get("plan", [])
                return self.plan
            except json.JSONDecodeError:
                return []
        except Exception as e:
            return []
    
    def mark_step_complete(self, step_number):
        for step in self.plan:
            if step.get("step") == step_number:
                step["status"] = "completed"
                self.completed_steps.append(step_number)
                return True
        return False
    
    def get_current_step(self):
        if not self.plan:
            return None
        
        for step in self.plan:
            if step.get("status") != "completed":
                return step
        return None
    
    def get_progress_summary(self):
        total = len(self.plan)
        completed = len(self.completed_steps)
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        return {
            "total_steps": total,
            "completed_steps": completed,
            "percentage": percentage,
            "current_step": self.get_current_step()
        }
    
    def display_plan(self, debug_mode=True):
        if not self.plan:
            return
        
        if debug_mode:
            print("\n" + "="*60)
            print("PLANNER: Task Decomposition")
            print("="*60)
            for step in self.plan:
                status_icon = "✓" if step.get("status") == "completed" else "○"
                priority = step.get("priority", "medium")
                print(f"  [{status_icon}] Step {step.get('step')}: {step.get('action')} (Priority: {priority})")
            print("="*60 + "\n")


tools = [  {
        "type": "function",
        "function": {
            "name": "get_calendar",
            "description": "Get user's schedule for a specific date",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (default: 'user_001')"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (default: today)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_contact_info",
            "description": "Get contact's availability, location, and preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Contact name (e.g., 'Sarah', 'Mark')"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_venues",
            "description": "Search for venues by location, type, and price",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location filter (e.g., 'University Town', 'SIGS Campus', 'any')"
                    },
                    "venue_type": {
                        "type": "string",
                        "description": "Venue type (e.g., 'cafe', 'study', 'restaurant', 'any')"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum average cost filter"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather forecast for a specific hour",
            "parameters": {
                "type": "object",
                "properties": {
                    "hour": {
                        "type": "integer",
                        "description": "Hour of the day (0-23)"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (default: today)"
                    }
                },
                "required": ["hour"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_travel_time",
            "description": "Calculate travel time between two locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "Starting location"
                    },
                    "end": {
                        "type": "string",
                        "description": "Destination location"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Travel mode: 'walking', 'cycling', 'taxi', 'metro' (default: 'walking')"
                    }
                },
                "required": ["start", "end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_finances",
            "description": "Check user's current budget status",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (default: 'user_001')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_schedule",
            "description": "Add a new event to the user's calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (default: 'user_001')"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (default: today)"
                    },
                    "event_details": {
                        "type": "object",
                        "properties": {
                            "time": {
                                "type": "string",
                                "description": "Time slot (e.g., '16:00-17:00')"
                            },
                            "event": {
                                "type": "string",
                                "description": "Event description"
                            },
                            "type": {
                                "type": "string",
                                "description": "Event type (e.g., 'meeting', 'lecture')"
                            },
                            "cost": {
                                "type": "number",
                                "description": "Event cost (deducts from budget)"
                            }
                        },
                        "required": ["time", "event", "type"]
                    }
                },
                "required": ["event_details"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "notify_contact",
            "description": "Send a message to a contact",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Contact name to notify"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content"
                    }
                },
                "required": ["name", "message"]
            }
        }
        }
    ]


SYSTEM_PROMPT = f"""You are a helpful assistant with access to tools to help manage daily schedules and logistics.

Your role is to help users plan their day by:
- Checking their calendar availability
- Finding suitable venues for meetings
- Checking weather conditions
- Managing their budget
- Coordinating with contacts

INTERNAL REASONING (Do NOT show this to user):
Use the ReAct pattern internally for your decision-making:
1. **Thought**: Explain what you're thinking and why
2. **Action**: Choose a tool to call (or respond directly)
3. **Observation**: Review the tool result
4. **Revision**: Decide what to do next based on the observation

IMPORTANT: Your internal reasoning is for your own decision-making process. 
When you respond to the user, provide a natural, conversational response.
Do NOT show "Thought:", "Action:", or "Input:" in your final responses to users.

QUICK REPLIES / SUGGESTED OPTIONS:
When presenting options to the user (venues, times, activities, etc.), you MUST include a structured list of suggested replies.

Format your response like this:

[Your conversational message to the user]

QUICK_REPLIES:
- Option 1: [Brief description]
- Option 2: [Brief description]
- Option 3: [Brief description]

Examples:
1. Presenting venue options:
   "I found two great venues for your meeting:"
   QUICK_REPLIES:
   - The Lab Coffee ($12)
   - Meet You Tea House ($18)

2. Presenting time options:
   "You're free at these times:"
   QUICK_REPLIES:
   - 4:00 PM
   - 5:00 PM
   - 6:00 PM

3. Asking for confirmation:
   "Would you like me to proceed?"
   QUICK_REPLIES:
   - Yes, proceed
   - No, show alternatives
   - Cancel

CONTEXT PRESERVATION & GOAL STABILITY:
- ALWAYS prioritize the user's original goal (e.g., "meet Sarah") when selecting venues or suggesting times.
- DO NOT drift from the original purpose based on venue types (e.g., if a library is chosen for a meeting, it remains a meeting, NOT a study session).
- Maintain multi-turn context by referencing previous decisions and constraints.
- When presenting options, ensure they align with ALL established constraints (budget, weather, time, purpose).

SMART WEATHER-BASED SUGGESTIONS:
When checking weather for outdoor activities:
1. Check weather at the requested time
2. If weather is unfavorable (high rain, extreme temps), check weather at alternative times within the same day
3. Prioritize same-day time changes before suggesting different days or indoor options
4. Present options in this order:
   - First: Better time today (if available)
   - Second: Indoor alternatives
   - Third: Different day

Example:
- User: "I need to do an outdoor run at 4 PM."
- Agent: [Checks weather: 90% rain at 4 PM]
- Agent: [Checks weather at 5 PM: 100% rain, 6 PM: 80% rain, 7 PM: 40% rain]
- Agent: "4 PM has 90% rain. However, 7 PM has only 40% rain. Would you like to reschedule to 7 PM?"
  QUICK_REPLIES:
  - Reschedule to 7:00 PM (40% rain)
  - Look for indoor exercise options
  - Reschedule for another day

CRITICAL: Before taking any action that modifies the user's schedule or notifies contacts, you MUST:

1. **Gather all necessary information first**:
   - Check calendar availability
   - Find suitable venues
   - Check weather conditions (at multiple times if needed)
   - Check budget constraints
   - Get contact information

2. **Present a clear plan to the user**:
   - Show the proposed meeting/activity details
   - Explain the venue choice and why it fits constraints
   - Mention any relevant conditions (weather, budget, time conflicts)
   - Show the total cost if applicable
   - Include QUICK_REPLIES for user selection

3. **Ask for explicit permission**:
   - "Would you like me to proceed with this plan?"
   - "Should I schedule this meeting for you?"
   - "Do you approve this arrangement?"

4. **Only take action after user confirms**:
    - Wait for user to say "yes", "go ahead", "proceed", or select a specific option from your suggestions.
    - If the user selects a venue from your QUICK_REPLIES, that counts as confirmation to proceed with that venue at the proposed time.
    - NEVER call update_schedule or notify_contact until the user has explicitly agreed to a specific time and location.
    - Confirm the action was completed after calling the tool.

Example workflow:
- User: "I need to meet Sarah for an hour this afternoon. Find a quiet place with Wi-Fi."
- Agent: [Internally: Checks calendar, finds venues, checks weather]
- Agent: "I found two venues for your meeting:
         QUICK_REPLIES:
         - The Lab Coffee ($12)
         - Meet You Tea House ($18)"
- User: [Selects] "The Lab Coffee ($12)"
- Agent: [Internally: Calls update_schedule, then send_notification]
- Agent: "Meeting scheduled! I've also notified Sarah."

Important:
- Default user_id is "user_001"
- Today's date is {current_datetime.strftime('%B %d, %Y')}.
- When scheduling events, consider budget constraints
- When suggesting venues, check weather if relevant
- Always explain your reasoning when making recommendations
- NEVER schedule or notify without asking first
- Your final responses should be natural and conversational, not showing internal reasoning
- ALWAYS include QUICK_REPLIES when presenting options
- For outdoor activities, ALWAYS check weather at multiple times and suggest better same-day times before suggesting different days or indoor options"""

import inspect

def execute_tool_call(tool_name, tool_args):
    try:
        tool_func = getattr(world, tool_name)
        # Inject user_id if needed and supported by the tool
        sig = inspect.signature(tool_func)
        if "user_id" in sig.parameters and "user_id" not in tool_args:
            tool_args["user_id"] = "user_001"
            
        result = tool_func(**tool_args)
        return result
    except AttributeError:
        return {"error": f"Tool '{tool_name}' not found"}
    except Exception as e:
        return {"error": str(e)}



def extract_quick_replies(text):
    """
    Extract quick replies from a text block formatted like:
    QUICK_REPLIES:
    - Option 1
    - Option 2
    """
    import re
    quick_replies = []
    
    # Use regex to find the QUICK_REPLIES section
    match = re.search(r"QUICK_REPLIES:\s*((?:- .*(?:\n|$))*)", text, re.IGNORECASE)
    if match:
        replies_text = match.group(1)
        # Extract items starting with '- '
        lines = replies_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                quick_replies.append(line[2:].strip())
    
    return quick_replies


def get_agent_response(messages, debug_mode=True, state_manager=None, on_tool_call=None):
    if state_manager is None:
        state_manager = StateManager()
        state_manager.initialize_from_world()
    
    max_turns = 10
    turns = 0
    trace_log = []
    
    if debug_mode:
        print("\n" + "="*60)
        print("REACT LOOP STARTED")
        print("="*60 + "\n")
        print(f"[STATE] Budget: ${state_manager.budget}, Max: ${state_manager.constraints['max_budget']}")
        print(f"[STATE] Calendar events: {len(state_manager.calendar.get(current_date, []))}")
        print()
    
    while turns < max_turns:
        response = client.chat.completions.create(
            model="google/gemini-3.1-flash-lite-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if response_message.content:
            if debug_mode:
                print(f"[THOUGHT] {response_message.content}")
            trace_log.append({
                "step": turns + 1,
                "thought": response_message.content,
                "action": None,
                "observation": None
            })
        
        if not response_message.tool_calls:
            if debug_mode:
                print(f"\n[FINAL ANSWER] {response_message.content}")
            trace_log[-1]["final_answer"] = response_message.content
            messages.append({
                "role": "assistant",
                "content": response_message.content
            })
            if debug_mode:
                print("\n" + "="*60)
                print("REACT LOOP COMPLETED")
                print("="*60 + "\n")
            return messages, trace_log
        
        messages.append({
            "role": "assistant",
            "content": response_message.content or "",
            "tool_calls": response_message.tool_calls
        })
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Normalize arguments before checking has_tried
            # Inject user_id if needed and supported by the tool
            try:
                tool_func = getattr(world, function_name)
                sig = inspect.signature(tool_func)
                if "user_id" in sig.parameters and "user_id" not in function_args:
                    function_args["user_id"] = "user_001"
            except (AttributeError, ValueError):
                pass

            if debug_mode:
                print(f"[ACTION] {function_name}")
                print(f"[INPUT] {json.dumps(function_args, indent=2)}")
            
            if state_manager.has_tried(function_name, function_args):
                if debug_mode:
                    print(f"[BACKTRACKING] Already tried {function_name} with these params, skipping...")
                    print()
                
                result = {
                    "status": "already_tried",
                    "error": f"This action was already attempted",
                    "message": "Try a different approach or different parameters"
                }
            else:
                constraint_ok, constraint_msg = state_manager.check_constraint_before_action(function_name, function_args)
                
                if not constraint_ok:
                    if debug_mode:
                        print(f"[CONSTRAINT VIOLATION] {constraint_msg['message']}")
                        print(f"[SUGGESTION] {constraint_msg['suggestion']}")
                        print()
                    
                    suggestions = state_manager.get_alternative_suggestions(function_name, function_args, constraint_msg['message'])
                    
                    result = {
                        "status": "constraint_violation",
                        "error": constraint_msg['message'],
                        "suggestion": constraint_msg['suggestion'],
                        "type": constraint_msg['type'],
                        "alternative_suggestions": suggestions
                    }
                else:
                    # Execute tool call (arguments already normalized)
                    try:
                        tool_func = getattr(world, function_name)
                        result = tool_func(**function_args)
                    except AttributeError:
                        result = {"error": f"Tool '{function_name}' not found"}
                    except Exception as e:
                        result = {"error": str(e)}
            
            state_manager.record_attempt(function_name, function_args, result)
            state_manager.update_after_tool_call(function_name, function_args, result)
            
            if debug_mode:
                print(f"[OBSERVATION] {json.dumps(result, indent=2)}")
                if state_manager.violations:
                    print(f"[VIOLATION] Latest: {state_manager.violations[-1]}")
                print(f"[STATE] Budget: ${state_manager.budget}")
                attempt_summary = state_manager.get_attempt_summary()
                if attempt_summary:
                    print(f"[ATTEMPTS] {len(attempt_summary)} actions attempted")
                print()
            
            if trace_log:
                trace_log[-1]["action"] = function_name
                trace_log[-1]["observation"] = result
                trace_log[-1]["state"] = state_manager.get_state_summary()
            
            if on_tool_call:
                on_tool_call(function_name, function_args, result)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result)
            })
        
        turns += 1
    
    if debug_mode:
        print("\n" + "="*60)
        print("REACT LOOP COMPLETED (max turns reached)")
        print("="*60 + "\n")
    return messages, trace_log


def parse_quick_replies(response_text):
    quick_replies = []
    message = response_text
    
    if "QUICK_REPLIES:" in response_text:
        parts = response_text.split("QUICK_REPLIES:")
        message = parts[0].strip()
        replies_section = parts[1].strip()
        
        for line in replies_section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                quick_replies.append(line[2:].strip())
            elif line and not line.startswith('-'):
                quick_replies.append(line)
    
    return message, quick_replies


def display_quick_replies(quick_replies):
    if not quick_replies:
        return
    
    print("\n" + "="*60)
    print("QUICK REPLIES (select by number or type your response):")
    print("="*60)
    for i, reply in enumerate(quick_replies, 1):
        print(f"  [{i}] {reply}")
    print("="*60 + "\n")


def chat(debug_mode=False):
    state_manager = StateManager()
    state_manager.initialize_from_world()
    planner = Planner()
    current_quick_replies = []
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("=== SYNCHRON Agent ===")
    print("Type 'exit' or 'quit' to stop.\n")
    
    if debug_mode:
        print(f"[INITIAL STATE] Budget: ${state_manager.budget}, Max: ${state_manager.constraints['max_budget']}")
        print(f"[INITIAL STATE] Calendar events: {len(state_manager.calendar.get(current_date, []))}")
        print()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        if current_quick_replies:
            try:
                selection = int(user_input.strip())
                if 1 <= selection <= len(current_quick_replies):
                    user_input = current_quick_replies[selection - 1]
                    current_quick_replies = []
            except ValueError:
                pass
        
        constraints = state_manager.parse_user_constraints(user_input)
        
        if debug_mode and constraints:
            print(f"[CONSTRAINTS PARSED] {constraints}")
        
        plan = planner.create_plan(user_input, constraints)
        
        if plan and debug_mode:
            planner.display_plan(debug_mode=True)
        
        messages.append({"role": "user", "content": user_input})
        
        if plan:
            messages.append({
                "role": "system",
                "content": f"PLAN: {json.dumps(plan)}\nFollow this plan step by step."
            })
        
        messages, trace_log = get_agent_response(messages, debug_mode=debug_mode, state_manager=state_manager)
        
        if plan and trace_log:
            last_action = trace_log[-1].get("action", "") if trace_log else ""
            if last_action and ("schedule" in last_action or "notify" in last_action):
                planner.mark_step_complete(planner.current_step + 1)
            
            if debug_mode:
                progress = planner.get_progress_summary()
                print(f"[PROGRESS] {progress['completed_steps']}/{progress['total_steps']} steps completed ({progress['percentage']}%)")
                print()
        
        final_message = messages[-1]
        if isinstance(final_message, dict) and final_message.get("role") == "assistant":
            response_content = final_message.get('content', '')
            message, quick_replies = parse_quick_replies(response_content)
            
            print(f"Agent: {message}\n")
            
            if quick_replies:
                current_quick_replies = quick_replies
                display_quick_replies(quick_replies)
            
            if debug_mode:
                violation_summary = state_manager.get_constraint_violation_summary()
                if violation_summary["violations"] or violation_summary["impossible_constraints"]:
                    print(f"\n[CONSTRAINT VIOLATION SUMMARY]")
                    for v in violation_summary["violations"]:
                        print(f"  - {v['type']}: {v['message']}")
                    for v in violation_summary["impossible_constraints"]:
                        print(f"  - {v['type']}: {v['message']}")
                        print(f"    Suggestion: {v['suggestion']}")


if __name__ == "__main__":
    import sys
    
    debug_mode = "--debug" in sys.argv or "-d" in sys.argv
    chat(debug_mode=debug_mode)
