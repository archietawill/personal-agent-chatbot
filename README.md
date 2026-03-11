# SYNCHRON: Autonomous Adaptive Scheduling Agent

SYNCHRON is a sophisticated autonomous agent designed to bridge the gap between LLM reasoning and real-world execution. Unlike traditional chatbots, SYNCHRON operates within a simulated "World State," allowing it to plan, reason about constraints, and execute complex workflows involving time, budget, and weather.

## 🧠 The Intelligence Loop: ReAct + Hierarchical Planning

SYNCHRON doesn't just respond; it thinks and acts. At its core, it utilizes a sophisticated **ReAct (Reason + Act)** pattern combined with a **Hierarchical Planner**:

1.  **Decomposition**: Upon receiving a complex request, SYNCHRON breaks it down into a granular "Todo Checklist."
2.  **Reasoning**: For every step, the agent generates a "Thought" to evaluate its current state.
3.  **Action**: It selects and executes one of its 8 specialized tools.
4.  **Observation**: It processes the tool's output, updates its internal world state, and revises its plan if constraints are violated.

---

## 🛠 Core Agent Capabilities (The 8-Tool Arsenal)

SYNCHRON is empowered with a specialized toolkit that allows it to interact with its environment with precision:

*   **📅 Time Management (`get_calendar`, `update_schedule`)**: Seamlessly coordinates and books events while avoiding time conflicts.
*   **💰 Financial Intelligence (`check_finances`)**: Real-time budget tracking to ensure every scheduled activity is financially viable.
*   **📍 Venue Discovery (`search_venues`, `get_venue_details`)**: Finds the perfect locations based on specific needs like Wi-Fi availability, "vibe" (quiet vs. casual), and cost.
*   **📱 Social Connectivity (`get_contacts`, `notify_contact`)**: Automatically reaches out to stakeholders (e.g., notifying a friend via WeChat once a meeting is booked).
*   **🌦 Environmental Awareness (`get_weather`)**: Checks real-time weather forecasts to validate activity types (e.g., suggesting indoor alternatives if rain is predicted for an outdoor run).

---

## 🖥 Progressive Interface & Visualization

The frontend is designed dedicatedly for Agentic AI, making the agent's internal reasoning visible and interactive:

*   **Planning Visualization**: A dynamic progress bar and a toggleable "Todo Checklist" follow the conversation flow, showing exactly what phase of the plan the agent is executing.
*   **Action Transparency**: Real-time logs for every tool call and background calculation, ensuring the agent's invisible work is fully transparent to the user.
*   **Smart Quick Replies**: Contextually aware button options appear after agent responses, allowing for seamless confirmation without manual typing.
*   **Live Focus State**: A dedicated dashboard (Sidebar) that displays your current "World State"—budget, today's schedule, and any active constraint violations in real-time.

---

## 🛡 Robust State & Constraint Management

*   **The StateManager Engine**: Prevents redundant actions by tracking every attempt and error internally.
*   **Constraint Safeguards**: SYNCHRON will automatically detect and warn you about budget overlaps, time conflicts, or weather issues before you commit to a plan.
*   **Session Persistence**: Utilizes server-side history to maintain context across multi-turn conversations (e.g., remembering which venue you picked two messages ago).
*   **The Sandbox Reset**: Every page reload triggers a full "World Reset," restoring the world to its original state for a fresh, clean testing experience.

---

## 🚀 Try It Out: Showcase the Agent's Intelligence

To see SYNCHRON's reasoning and tool-calling in action, try these targeted scenarios:

### 1. The Multi-Step ReAct Master (Complex Reasoning)
**Prompt**: *"I want to meet Mark for coffee this afternoon. Find a casual place, check if I have enough budget (I only want to spend max $30), and make sure the weather is good because I'd like to walk there. If everything is good, schedule it for 15:30 and tell him."*
*   **What to watch for**: The agent will chain 5+ tools: `get_contacts` (availablity) → `search_venues` (casual) → `check_finances` (budget) → `get_weather` (walking) → `update_schedule` → `notify_contact`.

### 2. State Management & Environment Modification
**Prompt**: *"Check my schedule for today. Then, find a time to meet Sarah for a 1-hour study session at the Library and book it. Afterwards, check my schedule again to confirm it was added."*
*   **What to watch for**: The agent will read the initial state, perform an "environmental write" (booking the meeting), and then verify its own work by re-checking the calendar.

### 3. Constraint Checking (Backtracking & Recovery)
**Prompt**: *"I want to go for a 2-hour outdoor run starting at 10:00 AM today. Check my schedule and the weather first."*
*   **What to watch for**: The agent will detect a **time conflict** (with your 10:45 lecture) or a **weather violation** (if rain is forecast). It should explain *why* it can't execute the plan and suggest a better time or an indoor alternative.

### 4. Financial "Stress Test"
**Prompt**: *"Schedule a fancy dinner for 2 guests tonight at the most expensive venue you can find."*
*   **What to watch for**: The agent checking the `discretionary_budget` versus its `search_venues` results, potentially alerting you if the remaining $85 isn't enough for a premium 5-star experience.

---

## ⚙️ Installation & Configuration

### 1. Backend Setup
```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

### 2. Frontend Setup
```bash
cd agent/frontend
npm install
npm run dev
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_key_here
```
