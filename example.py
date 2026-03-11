import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import search_flights, search_hotels, search_places
import datetime

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-3-flash-preview"

if not OPENROUTER_API_KEY:
    print("\n[!] Error: OPENROUTER_API_KEY not found.")
    print("Please ensure you have a '.env' file with your OpenRouter key.")
    print("Example: OPENROUTER_API_KEY=sk-or-v1-...\n")
    exit(1)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Tool Definitions for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for real-time flight offers and prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "IATA city code (e.g. JFK)"},
                    "destination": {"type": "string", "description": "IATA city code (e.g. LAX)"},
                    "departure_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"}
                },
                "required": ["origin", "destination", "departure_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Search for hotels in a specific location with real-time prices and ratings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city or destination name"},
                    "check_in": {"type": "string", "description": "Check-in date in YYYY-MM-DD format"},
                    "check_out": {"type": "string", "description": "Check-out date in YYYY-MM-DD format"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_places",
            "description": "Search for attractions, restaurants, and local businesses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g. 'best pizza in Rome')"}
                },
                "required": ["query"]
            }
        }
    }
]

# Get current date dynamically
today = datetime.date.today() # e.g., 2026-03-05

SYSTEM_PROMPT = f"""You are 'VibeCheck', an elite, detail-oriented travel concierge.
Your goal is to provide stunningly detailed, accurate, and COMPLETE travel guides.

IMPORTANT CONTEXT: 
- Today's date is {today.strftime('%B %d, %Y')}.
- All user queries are relative to this date.

Rules for Excellence:
1. Tool-Augmented: You MUST use tools for all real-time data. NEVER hallucinate names, prices, or links.
2. The "No Summary" Rule: When users ask for flights or hotels, do NOT just say "I found some options." You must list the specific details for at least 3-4 top options.
3. MANDATORY Fields for Tool Results:
    - FLIGHTS: Airline name, Flight numbers (if available), Departure/Arrival times, and PRICE.
    - HOTELS: Exact Price per night, 3-5 key facilities (Gym, Pool, Breakfast, etc.), Neighborhood Vibe, and a BOOKING/WEBSITE LINK.
    - PLACES/ITINERARY: Specific names of attractions, estimated time to spend, and why it's a "must-see" based on the user's preferences.
4. Iterative Research: If search_hotels doesn't give you a link or facilities, you MUST call search_places for that specific hotel to find the missing details.
5. Structured Formatting: Use Markdown headers (###), bold text, and bullet points to make the information scannable and premium-looking.
6. Comprehensive Itineraries: If a user asks for a trip plan, provide a Day-by-Day breakdown.

Final Output Tone: Professional, enthusiastic, and extremely thorough. Your response should feel like a high-end travel magazine feature, not a quick text message.
"""

def chat():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("--- VibeCheck Travel Agent (CLI) ---")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})

def get_agent_response(messages):
    """
    Process a list of messages and return the updated conversation.
    Handles multi-turn tool calling internally.
    """
    try:
        max_turns = 5
        turns = 0
        
        while turns < max_turns:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            
            # If there are no tool calls, this is the final answer
            if not response_message.tool_calls:
                messages.append(response_message)
                return messages

            # Add the assistant's request to the conversation
            messages.append(response_message)

            # Handle Tool Calls
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"[*] Calling {function_name} with {function_args}...")
                
                if function_name == "search_flights":
                    result = search_flights(**function_args)
                elif function_name == "search_hotels":
                    result = search_hotels(**function_args)
                elif function_name == "search_places":
                    result = search_places(**function_args)
                else:
                    result = "Error: Tool not found."

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result)
                })
            
            turns += 1
            if turns == max_turns:
                print("[!] Warning: Maximum tool iterations reached.")
                final_response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages
                )
                messages.append(final_response.choices[0].message)
                return messages
    except Exception as e:
        print(f"Error in agent processing: {e}")
        messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {e}"})
        return messages

def chat():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("--- VibeCheck Travel Agent (CLI) ---")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})
        messages = get_agent_response(messages)
        print(f"VibeCheck: {messages[-1].content}")

if __name__ == "__main__":
    chat()
