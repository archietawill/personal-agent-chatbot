'use client'

import ReactMarkdown from 'react-markdown'
import { ChatMessage } from '@/types/chat'

interface MessageBubbleProps {
  message: ChatMessage
  isLatest?: boolean
}

export default function MessageBubble({ message, isLatest }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  if (isSystem) {
    return null
  }

  return (
    <div
      className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} mb-3 sm:mb-4`}
    >
      <div
        className={`max-w-[90%] sm:max-w-[85%] md:max-w-[70%] rounded-2xl px-4 sm:px-5 py-2.5 sm:py-3 ${
          isUser ? 'bg-blue-600 text-white shadow-sm' : 'bg-gray-100 text-gray-800 shadow-sm'
        }`}
      >
        <div className="text-[13px] sm:text-[15px] leading-relaxed prose prose-sm max-w-none">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-1.5 sm:mb-2 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-inside mb-1.5 sm:mb-2">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside mb-1.5 sm:mb-2">{children}</ol>,
              li: ({ children }) => <li className="mb-0.5 sm:mb-1">{children}</li>,
              strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
              em: ({ children }) => <em className="italic">{children}</em>,
              code: ({ children }) => (
                <code className="bg-black/10 px-1 py-0.5 rounded text-xs sm:text-sm font-mono">
                  {children}
                </code>
              ),
              a: ({ children, href }) => (
                <a href={href} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
      {isLatest && message.quickReplies && message.quickReplies.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5 sm:gap-2 ml-1">
          {message.quickReplies.map((reply) => (
            <button
              key={reply.id}
              className="px-3 py-1.5 text-[11px] sm:text-xs font-semibold rounded-full border border-blue-200 bg-blue-50/30 text-blue-600 hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-all duration-200 active:scale-95 shadow-sm"
              onClick={() => {
                const event = new CustomEvent('quickReply', { detail: reply.label })
                window.dispatchEvent(event)
              }}
            >
              {reply.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
