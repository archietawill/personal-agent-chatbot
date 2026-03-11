import { create } from 'zustand'
import { ChatMessage, QuickReply, ToolCall, Plan } from '@/types/chat'

interface ChatState {
  messages: ChatMessage[]
  addMessage: (message: ChatMessage) => void
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map((msg) =>
      msg.id === id ? { ...msg, ...updates } : msg
    ),
  })),
  clearMessages: () => set({ messages: [] }),
}))
