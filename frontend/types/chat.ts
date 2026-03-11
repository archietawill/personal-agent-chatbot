export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  quickReplies?: QuickReply[]
  toolCalls?: ToolCall[]
  plan?: Plan
}

export interface QuickReply {
  id: string
  label: string
  action?: string
}

export interface ToolCall {
  id: string
  name: string
  input: Record<string, any>
  output?: Record<string, any>
  status: 'pending' | 'success' | 'error'
  timestamp: Date
}

export interface Plan {
  steps: PlanStep[]
  currentStep: number
  completedSteps: number
  percentage: number
}

export interface PlanStep {
  step: number
  action: string
  priority: 'high' | 'medium' | 'low'
  status: 'pending' | 'in_progress' | 'completed'
}

export interface UserState {
  name: string
  date: Date
  budget: {
    current: number
    max: number
    remaining: number
  }
  schedule: ScheduleEvent[]
}

export interface ScheduleEvent {
  id: string
  time: string
  event: string
  type: string
  cost?: number
}

export interface ViolationAlert {
  id: string
  type: 'budget' | 'weather' | 'time' | 'other'
  severity: 'low' | 'medium' | 'high'
  message: string
  suggestion: string
  dismissed: boolean
}
