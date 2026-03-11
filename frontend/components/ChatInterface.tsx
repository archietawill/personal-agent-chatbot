'use client'

import { useState, useEffect, useRef } from 'react'
import { useChatStore } from '@/store/useChatStore'
import { useSidebarStore } from '@/store/useSidebarStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import MessageBubble from '@/components/MessageBubble'
import Sidebar from '@/components/Sidebar'
import ProgressBar from '@/components/ProgressBar'
import TodoChecklist from '@/components/TodoChecklist'
import ToolCallDisplay from '@/components/ToolCallDisplay'
import { ChatMessage } from '@/types/chat'

export default function ChatInterface() {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPlanDetails, setShowPlanDetails] = useState(false)
  const { messages, addMessage, clearMessages } = useChatStore()
  const { isOpen, toggle, setUserState } = useSidebarStore()
  const { isConnected, sendMessage, currentPlan, currentProgress, toolCalls, status } = useWebSocket()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading, currentPlan, toolCalls, status, showPlanDetails])

  useEffect(() => {
    // Clear chat history on every reload/mount
    clearMessages()
  }, [])

  useEffect(() => {
    const handleQuickReply = (event: Event) => {
      const customEvent = event as CustomEvent<string>
      const text = customEvent.detail
      
      if (isLoading) return

      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: text,
        timestamp: new Date(),
      }

      addMessage(userMessage)
      setIsLoading(true)
      sendMessage(text, 'user_001')
    }

    window.addEventListener('quickReply', handleQuickReply)
    return () => window.removeEventListener('quickReply', handleQuickReply)
  }, [addMessage, sendMessage, isLoading])

  const handleSend = () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInput('')
    setIsLoading(true)

    sendMessage(input, 'user_001')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  useEffect(() => {
    if (status === 'Done!' || status === '') {
      setIsLoading(false)
    }
  }, [status])

  return (
    <div className="flex h-screen bg-[#F9FAFB] font-sans">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-hidden flex flex-col items-center">
          <div className="w-full h-full flex flex-col">
            <div className="flex-shrink-0 px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <h1
                  className="text-xl sm:text-2xl font-bold text-gray-900 cursor-pointer hover:text-blue-600 transition-colors"
                  onClick={toggle}
                >
                  SYNCHRON
                </h1>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-xs sm:text-sm text-gray-600 hidden sm:inline">
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto px-3 sm:px-6 py-3 sm:py-4">
              {messages.length === 0 ? (
                <div className="text-center mt-12 sm:mt-20">
                  <p className="text-gray-500 text-base sm:text-lg">
                    Start a conversation with SYNCHRON
                  </p>
                </div>
              ) : (
                messages.map((message, index) => {
                  const isLatest = index === messages.length - 1
                  return (
                    <div key={message.id}>
                      {message.toolCalls && message.toolCalls.length > 0 && (
                        <ToolCallDisplay toolCalls={message.toolCalls} />
                      )}
                      <MessageBubble message={message} isLatest={isLatest && !isLoading} />
                    </div>
                  )
                })
              )}

              {/* Render planning UI for the current/most recent plan at the bottom */}
              {(() => {
                const latestMessage = messages[messages.length - 1];
                const lastMessageWithPlan = [...messages].reverse().find(m => m.plan && m.plan.steps.length > 1);
                
                // Show plan ONLY if the latest message IS the one with the plan, 
                // OR if we are currently loading a plan.
                // This ensures it auto-hides when a new topic starts.
                const shouldShowPlan = (isLoading && currentPlan) || 
                                     (!isLoading && latestMessage && latestMessage.plan && latestMessage.plan.steps.length > 1);

                if (!shouldShowPlan) return null;

                const activePlan = (isLoading && currentPlan) ? currentPlan : ((!isLoading && latestMessage?.plan) ? latestMessage.plan : null);
                if (!activePlan) return null;

                const activeProgress = isLoading ? currentProgress : { 
                  percentage: latestMessage?.plan?.percentage || 0, 
                  currentStep: latestMessage?.plan?.currentStep || 0 
                };

                return (
                  <div className="mt-4 mb-6 max-w-[75%] sm:max-w-[60%] md:max-w-[40%] bg-white/50 backdrop-blur-sm rounded-xl p-3 border border-gray-100 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <ProgressBar
                      percentage={activeProgress?.percentage || 0}
                      label={isLoading ? "Executing Plan" : "Plan Summary"}
                    />
                    
                    <button 
                      onClick={() => setShowPlanDetails(!showPlanDetails)}
                      className="mt-2 text-[10px] sm:text-xs font-semibold text-blue-500 hover:text-blue-700 flex items-center gap-1 transition-colors"
                    >
                      <span>{showPlanDetails ? 'Hide Steps' : 'View Details'}</span>
                      <svg 
                        className={`w-3 h-3 transition-transform ${showPlanDetails ? 'rotate-180' : ''}`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {showPlanDetails && (
                      <div className="mt-2 animate-in fade-in duration-300">
                        <TodoChecklist
                          steps={activePlan.steps}
                          currentStep={activeProgress?.currentStep || 0}
                        />
                      </div>
                    )}
                  </div>
                );
              })()}

              {isLoading && toolCalls.length > 0 && (
                <div className="opacity-70">
                  <ToolCallDisplay toolCalls={toolCalls} />
                </div>
              )}

              {isLoading && status && status !== 'Done!' && (
                <div className="flex justify-start mb-3 sm:mb-4">
                  <div className="bg-transparent text-gray-500 rounded-lg px-2 py-1 flex items-center gap-2">
                    <div className="flex gap-1 scale-75">
                      <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" />
                      <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                      <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                    </div>
                    <span className="text-[10px] sm:text-xs font-medium uppercase tracking-wider">{status}</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>

        <div className="flex-shrink-0 border-t border-gray-200 bg-white/80 backdrop-blur-sm">
          <div className="w-full p-3 sm:p-4">
            <div className="flex gap-2 sm:gap-3 items-end max-w-4xl mx-auto">
              <div className="flex-1 relative min-w-0">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your scheduling request..."
                  disabled={isLoading}
                  className="w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm sm:text-base text-gray-800 placeholder-gray-400 disabled:opacity-50"
                />
              </div>

              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="px-4 sm:px-5 py-2.5 sm:py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium text-sm sm:text-base whitespace-nowrap"
              >
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
