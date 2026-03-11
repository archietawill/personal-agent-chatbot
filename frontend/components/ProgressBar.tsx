interface ProgressBarProps {
  percentage: number
  label?: string
}

export default function ProgressBar({ percentage, label }: ProgressBarProps) {
  const clampedPercentage = Math.min(100, Math.max(0, percentage))
  const isComplete = clampedPercentage === 100

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-1">
          <div className="flex items-center gap-1.5">
            <span className={`text-[10px] sm:text-xs font-semibold uppercase tracking-tight transition-colors ${isComplete ? 'text-green-600' : 'text-gray-500'}`}>
              {isComplete ? 'Task Complete' : label}
            </span>
            {isComplete && (
              <svg className="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
          <span className={`text-[10px] sm:text-xs font-medium transition-colors ${isComplete ? 'text-green-500' : 'text-gray-400'}`}>
            {clampedPercentage}%
          </span>
        </div>
      )}
      <div className="w-full bg-gray-200/50 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-in-out ${
            isComplete ? 'bg-green-500' : 'bg-blue-400'
          }`}
          style={{ width: `${clampedPercentage}%` }}
        />
      </div>
    </div>
  )
}
