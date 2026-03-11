# SYNCHRON - AI Scheduling Assistant

An intelligent constraint-satisfaction agent for scheduling and planning with real-time updates.

## Features

- Real-time WebSocket communication
- Progress tracking with live updates
- Tool call visualization
- Constraint violation alerts
- Mobile-responsive design
- Markdown support for rich text
- Quick reply suggestions

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Zustand (state management)
- Socket.IO Client
- React Markdown

### Backend
- Python Flask
- Flask-SocketIO
- OpenRouter API
- OpenAI SDK

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- OpenRouter API key

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd agent
```

2. Install frontend dependencies
```bash
cd frontend
npm install
```

3. Install backend dependencies
```bash
cd ..
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Create .env file in the agent directory
OPENROUTER_API_KEY=your_openrouter_api_key
```

### Running the Application

1. Start the backend server
```bash
cd agent
python server.py
```

2. Start the frontend development server
```bash
cd frontend
npm run dev
```

3. Open your browser
```
http://localhost:3000
```

## API Endpoints

### HTTP Endpoints

- `POST /chat` - Send a chat message (HTTP fallback)
- `GET /user/<user_id>` - Get user state

### WebSocket Events

#### Client → Server
- `connect` - Connection established
- `disconnect` - Connection closed
- `chat_message` - Send chat message
  ```json
  {
    "message": "Schedule a meeting with Sarah",
    "user_id": "user_001"
  }
  ```

#### Server → Client
- `connect` - Connection confirmed
- `disconnect` - Disconnection confirmed
- `plan_created` - Plan created
- `progress_update` - Progress updated
- `tool_call` - Tool executed
- `status` - Status update
- `response` - Final response
- `error` - Error occurred

## Project Structure

```
agent/
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── route.ts
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── Sidebar.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── TodoChecklist.tsx
│   │   ├── ToolCallDisplay.tsx
│   │   └── ViolationAlert.tsx
│   ├── hooks/
│   │   └── useWebSocket.ts
│   ├── store/
│   │   ├── useChatStore.ts
│   │   └── useSidebarStore.ts
│   ├── types/
│   │   └── chat.ts
│   ├── package.json
│   └── tailwind.config.ts
├── agent.py
├── world.py
└── server.py
```

## Deployment

### Frontend (Vercel)

1. Install Vercel CLI
```bash
npm install -g vercel
```

2. Deploy
```bash
cd frontend
vercel
```

### Backend (Render/Railway/Heroku)

1. Create `requirements.txt`
```bash
flask
flask-cors
flask-socketio
python-socketio
openai
python-dotenv
```

2. Deploy to your preferred platform

## Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes |
| `PYTHON_AGENT_URL` | Backend URL (for frontend) | No (default: http://localhost:5001) |

## Development

### Running Tests
```bash
cd frontend
npm test
```

### Building for Production
```bash
cd frontend
npm run build
```

## License

MIT
