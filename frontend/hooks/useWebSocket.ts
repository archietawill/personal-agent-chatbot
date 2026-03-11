'use client'

import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { useChatStore } from '@/store/useChatStore'
import { useSidebarStore } from '@/store/useSidebarStore'
import { ChatMessage } from '@/types/chat'

interface UseWebSocketReturn {
  socket: Socket | null
  isConnected: boolean
  sendMessage: (message: string, userId?: string) => void
  currentPlan: any
  currentProgress: any
  toolCalls: any[]
  status: string
}

export function useWebSocket(): UseWebSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [currentPlan, setCurrentPlan] = useState<any>(null)
  const [currentProgress, setCurrentProgress] = useState<any>(null)
  const [toolCalls, setToolCalls] = useState<any[]>([])
  const [status, setStatus] = useState<string>('')
  
  const { addMessage } = useChatStore()
  const { setUserState } = useSidebarStore()
  const socketRef = useRef<Socket | null>(null)

  useEffect(() => {
    const socketInstance = io('http://localhost:5001', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    socketRef.current = socketInstance

    socketInstance.on('connect', () => {
      console.log('Connected to WebSocket server')
      setIsConnected(true)
    })

    socketInstance.on('disconnect', () => {
      console.log('Disconnected from WebSocket server')
      setIsConnected(false)
    })

    socketInstance.on('plan_created', (data) => {
      console.log('Plan created:', data)
      setCurrentPlan(data)
    })

    socketInstance.on('progress_update', (data) => {
      console.log('Progress update:', data)
      setCurrentProgress(data)
    })

    socketInstance.on('tool_call', (data) => {
      console.log('Tool call:', data)
      setToolCalls((prev) => [...prev, data])
    })

    socketInstance.on('status', (data) => {
      console.log('Status:', data)
      setStatus(data.message)
    })

    socketInstance.on('response', (data) => {
      console.log('Response received:', data)
      
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.message || 'Sorry, I could not process your request.',
        timestamp: new Date(),
        quickReplies: data.quickReplies?.map((reply: string, index: number) => ({
          id: `quick-reply-${index}`,
          label: reply,
        })),
        toolCalls: data.toolCalls,
        plan: data.plan,
      }

      addMessage(assistantMessage)

      if (data.userState) {
        setUserState({
          name: data.userState.name,
          date: new Date(data.userState.date),
          budget: data.userState.budget,
          schedule: data.userState.schedule,
        })
      }

      // Clear live states after adding to store
      setTimeout(() => {
        setCurrentPlan(null)
        setCurrentProgress(null)
        setToolCalls([])
        setStatus('')
      }, 50)
    })

    socketInstance.on('error', (data) => {
      console.error('WebSocket error:', data)
    })

    setSocket(socketInstance)

    return () => {
      socketInstance.disconnect()
    }
  }, [addMessage, setUserState])

  const sendMessage = (message: string, userId: string = 'user_001') => {
    if (socket && isConnected) {
      setCurrentPlan(null)
      setCurrentProgress(null)
      setToolCalls([])
      setStatus('')
      
      socket.emit('chat_message', {
        message,
        user_id: userId,
      })
    }
  }

  return {
    socket,
    isConnected,
    sendMessage,
    currentPlan,
    currentProgress,
    toolCalls,
    status,
  }
}
