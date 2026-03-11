interface ToolCall {
  name: string
  input: Record<string, any>
  output?: Record<string, any>
  status: 'pending' | 'success' | 'error'
  timestamp: Date
}

interface ToolCallDisplayProps {
  toolCalls: ToolCall[]
}

export default function ToolCallDisplay({ toolCalls }: ToolCallDisplayProps) {
  if (!toolCalls || toolCalls.length === 0) {
    return null
  }

  const getStatusText = (toolName: string, status: string) => {
    const messages: Record<string, string> = {
      'get_calendar': 'Checking your schedule...',
      'get_weather': 'Looking up weather forecast...',
      'search_venues': 'Searching for perfect venues...',
      'notify_contact': 'Sending notification...',
      'update_schedule': 'Updating your calendar...',
      'fetch_contact_info': 'Getting contact details...',
      'calculate_travel_time': 'Calculating travel time...'
    }
    
    const baseMessage = messages[toolName] || `Processing ${toolName}...`
    return status === 'pending' ? baseMessage : `${baseMessage} Done.`
  }

  return (
    <div className="bg-transparent p-1 mb-3 sm:mb-4">
      <h3 className="text-[10px] sm:text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">Activities</h3>
      <div className="space-y-1.5 sm:space-y-2">
        {toolCalls.map((tool, index) => (
          <div
            key={index}
            className="flex items-center gap-1.5 p-1 rounded transition-colors bg-gray-50/30"
          >
            <div
              className={`w-1 h-1 sm:w-1.5 sm:h-1.5 rounded-full ${
                tool.status === 'success'
                  ? 'bg-green-400'
                  : tool.status === 'error'
                  ? 'bg-red-400'
                  : 'bg-blue-400 animate-pulse'
              }`}
            />
            <span className="text-[10px] sm:text-xs font-medium text-gray-500">
              {getStatusText(tool.name, tool.status)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
