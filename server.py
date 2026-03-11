from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sys
import os
from datetime import datetime
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import get_agent_response, StateManager, Planner, parse_quick_replies, SYSTEM_PROMPT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'synchron-secret-key'
CORS(app, cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def requires_planning(message):
    scheduling_keywords = [
        'schedule', 'meeting', 'book', 'plan', 'reserve', 'appointment',
        'calendar', 'event', 'organize', 'arrange', 'set up', 'coordinate',
        'tomorrow', 'today', 'next week', 'next month', 'at', 'on', 'from'
    ]
    
    constraint_keywords = [
        'budget', 'cost', 'price', 'money', 'spend', 'limit',
        'weather', 'rain', 'sunny', 'outdoor', 'indoor',
        'time', 'duration', 'hours', 'minutes'
    ]
    
    message_lower = message.lower()
    
    # If message is very short, don't plan
    if len(message.split()) <= 3:
        return False
        
    # Check for scheduling specific intent
    has_scheduling_keywords = any(keyword in message_lower for keyword in scheduling_keywords)
    has_constraint_keywords = any(keyword in message_lower for keyword in constraint_keywords)
    
    # Only require planning if there's a scheduling keyword AND either explicit constraints or it's a longer complex request
    return has_scheduling_keywords and (has_constraint_keywords or len(message.split()) > 8)
# State storage for session history
session_histories = {}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('user_id', 'user_001')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
        state_manager = StateManager()
        state_manager.initialize_from_world(user_id, current_date)
        
        constraints = state_manager.parse_user_constraints(message)
        
        plan = None
        if requires_planning(message):
            planner = Planner()
            plan = planner.create_plan(message, constraints)
            
            if plan:
                messages.append({
                    "role": "system",
                    "content": f"PLAN: {plan}\nFollow this plan step by step."
                })
        
        messages, trace_log = get_agent_response(messages, debug_mode=False, state_manager=state_manager)
        
        tool_calls = []
        if trace_log:
            for log in trace_log:
                if log.get("action"):
                    tool_calls.append({
                        "id": str(log.get("timestamp", "")),
                        "name": log.get("action", ""),
                        "input": log.get("input", {}),
                        "output": log.get("result", {}),
                        "status": "success" if log.get("result", {}).get("status") == "success" else "error",
                        "timestamp": log.get("timestamp", datetime.now())
                    })
        
        plan_data = None
        if plan:
            progress = planner.get_progress_summary()
            total_steps = len(planner.plan)
            plan_data = {
                "steps": [
                    {
                        "step": step.get("step", 0),
                        "action": step.get("action", ""),
                        "priority": step.get("priority", "medium"),
                        "status": step.get("status", "pending")
                    }
                    for step in planner.plan
                ],
                "currentStep": progress.get("current_step", {}).get("step", 0) - 1 if progress.get("current_step") else total_steps,
                "completedSteps": progress.get("completed_steps", 0),
                "percentage": progress.get("percentage", 0)
            }
        
        assistant_content = messages[-1].get('content', '')
        clean_message, replies = parse_quick_replies(assistant_content)
        
        response = {
            'message': clean_message,
            'role': messages[-1].get('role', 'assistant'),
            'quickReplies': replies,
            'toolCalls': tool_calls,
            'plan': plan_data,
            'userState': {
                'name': 'User',
                'date': current_date,
                'budget': {
                    'current': 0,
                    'max': state_manager.constraints.get('max_budget', 50),
                    'remaining': state_manager.budget or 50
                },
                'schedule': state_manager.calendar.get(current_date, []),
                'violations': state_manager.violations
            }
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/user/<user_id>', methods=['GET'])
def get_user_state(user_id):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        state_manager = StateManager()
        state_manager.initialize_from_world(user_id, current_date)
        
        user_state = {
            'name': 'User',
            'date': current_date,
            'budget': {
                'current': 0,
                'max': state_manager.constraints.get('max_budget', 50),
                'remaining': state_manager.budget or 50
            },
            'schedule': state_manager.calendar.get(current_date, [])
        }
        
        return jsonify(user_state)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    from world import world
    world.reset()
    # Reset history for this session
    session_histories[request.sid] = []
    print(f'Client {request.sid} connected, world and history reset')

@socketio.on('disconnect')
def handle_disconnect():
    # Clean up history on disconnect
    if request.sid in session_histories:
        del session_histories[request.sid]
    print(f'Client {request.sid} disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    try:
        message = data.get('message', '')
        user_id = data.get('user_id', 'user_001')
        session_id = request.sid
        
        if not message:
            emit('error', {'error': 'Message is required'})
            return
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        emit('status', {'status': 'thinking', 'message': 'Analyzing your request...'})
        
        # Get or initialize history for this session
        if session_id not in session_histories:
            session_histories[session_id] = []
            
        history = session_histories[session_id]
        
        # Build the message list for this turn
        if not history:
            # First message in session
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        else:
            messages = history.copy()
            
        messages.append({"role": "user", "content": message})
        
        state_manager = StateManager()
        state_manager.initialize_from_world(user_id, current_date)
        
        constraints = state_manager.parse_user_constraints(message)
        
        plan = None
        planner = None
        
        # Only create a plan if we don't have one or if the message explicitly requires new planning
        # Check if conversation already has an active plan (very basic check)
        has_active_plan = any("PLAN:" in msg.get("content", "") for msg in messages if msg.get("role") == "system")
        
        if requires_planning(message) and not has_active_plan:
            planner = Planner()
            plan = planner.create_plan(message, constraints)
            
            if plan:
                emit('plan_created', {
                    'plan': plan,
                    'steps': [
                        {
                            'step': step.get('step', 0),
                            'action': step.get('action', ''),
                            'priority': step.get('priority', 'medium'),
                            'status': step.get('status', 'pending')
                        }
                        for step in plan
                    ],
                    'currentStep': 0,
                    'completedSteps': 0,
                    'percentage': 0
                })
                
                messages.append({
                    "role": "system",
                    "content": f"PLAN: {plan}\nFollow this plan step by step."
                })
        
        def on_tool_call_callback(name, args, result):
            emit('tool_call', {
                'id': f"tool-{datetime.now().timestamp()}",
                'name': name,
                'input': args,
                'output': result,
                'status': 'success' if result.get("status") == "success" else "error",
                'timestamp': str(datetime.now())
            })
            
            if planner:
                # Mark a step as complete (simple heuristic: one tool call = one step)
                # This could be improved if we knew which step corresponds to which tool
                completed_count = len(state_manager.attempts)
                if completed_count <= len(plan):
                    planner.mark_step_complete(completed_count)
                    progress = planner.get_progress_summary()
                    total_steps = len(planner.plan)
                    emit('progress_update', {
                        'currentStep': progress.get('current_step', {}).get('step', 0) - 1 if progress.get('current_step') else total_steps,
                        'completedSteps': progress.get('completed_steps', 0),
                        'percentage': progress.get('percentage', 0)
                    })

        emit('status', {'status': 'processing', 'message': 'Executing plan...'})
        
        messages, trace_log = get_agent_response(
            messages, 
            debug_mode=False, 
            state_manager=state_manager,
            on_tool_call=on_tool_call_callback
        )
        
        tool_calls = []
        if trace_log:
            for log in trace_log:
                if log.get("action"):
                    tool_calls.append({
                        "id": str(log.get("timestamp", "")),
                        "name": log.get("action", ""),
                        "input": log.get("input", {}),
                        "output": log.get("result", {}),
                        "status": "success" if log.get("result", {}).get("status") == "success" else "error",
                        "timestamp": log.get("timestamp", datetime.now())
                    })
        
        plan_data = None
        if plan:
            progress = planner.get_progress_summary()
            total_steps = len(planner.plan)
            plan_data = {
                "steps": [
                    {
                        "step": step.get("step", 0),
                        "action": step.get("action", ""),
                        "priority": step.get("priority", "medium"),
                        "status": step.get("status", "pending")
                    }
                    for step in planner.plan
                ],
                "currentStep": progress.get("current_step", {}).get("step", 0) - 1 if progress.get("current_step") else total_steps,
                "completedSteps": progress.get("completed_steps", 0),
                "percentage": progress.get("percentage", 0)
            }
        # Prepare final response
        assistant_content = messages[-1].get('content', '')
        clean_message, replies = parse_quick_replies(assistant_content)
        
        response_data = {
            'message': clean_message,
            'role': messages[-1].get('role', 'assistant'),
            'quickReplies': replies,
            'toolCalls': tool_calls,
            'plan': plan_data,
            'userState': {
                'name': 'User',
                'date': current_date,
                'budget': {
                    'current': 0,
                    'max': state_manager.constraints.get('max_budget', 50),
                    'remaining': state_manager.budget or 50
                },
                'schedule': state_manager.calendar.get(current_date, []),
                'violations': state_manager.violations
            }
        }
        
        emit('response', response_data)
        
        # Persist history for next turn
        session_histories[session_id] = messages
        
        emit('status', {'status': 'completed', 'message': 'Done!'})
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
