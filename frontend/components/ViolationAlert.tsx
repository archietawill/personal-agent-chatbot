interface ViolationAlertProps {
  type: 'budget' | 'weather' | 'time' | 'other'
  severity: 'low' | 'medium' | 'high'
  message: string
  suggestion: string
  onDismiss: () => void
}

export default function ViolationAlert({
  type,
  severity,
  message,
  suggestion,
  onDismiss,
}: ViolationAlertProps) {
  const severityColors = {
    low: 'bg-yellow-50 border-yellow-300 text-yellow-800',
    medium: 'bg-orange-50 border-orange-300 text-orange-800',
    high: 'bg-red-50 border-red-300 text-red-800',
  }

  const typeIcons = {
    budget: '💰',
    weather: '🌤',
    time: '⏰',
    other: '⚠️',
  }

  return (
    <div
      className={`rounded-lg border p-2.5 sm:p-4 mb-2 sm:mb-4 ${severityColors[severity]}`}
    >
      <div className="flex items-start gap-2 sm:gap-3">
        <div className="flex-shrink-0 text-xl sm:text-2xl">{typeIcons[type]}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1.5 sm:mb-2">
            <h4 className="text-xs sm:text-sm font-semibold capitalize">{type} Violation</h4>
            <button
              onClick={onDismiss}
              className="text-xs sm:text-sm hover:opacity-70 transition-opacity"
            >
              ✕
            </button>
          </div>
          <p className="text-[11px] sm:text-sm mb-1.5 sm:mb-2">{message}</p>
          <p className="text-[11px] sm:text-sm font-medium">
            <span className="font-bold">Suggestion:</span> {suggestion}
          </p>
        </div>
      </div>
    </div>
  )
}
