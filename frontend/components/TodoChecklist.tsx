interface PlanStep {
  step: number
  action: string
  status: 'pending' | 'in_progress' | 'completed'
}

interface TodoChecklistProps {
  steps: PlanStep[]
  currentStep: number
}

export default function TodoChecklist({ steps, currentStep }: TodoChecklistProps) {
  return (
    <div className="bg-transparent p-1">
      <h3 className="text-[10px] sm:text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">Plan</h3>
      <div className="space-y-1">
        {steps.map((step, index) => {
          const isCompleted = step.status === 'completed'
          const isCurrent = index === currentStep
          const isPending = step.status === 'pending'

          return (
            <div
              key={step.step}
              className={`flex items-start gap-2 p-1 rounded transition-colors ${
                isCurrent ? 'bg-blue-50/20' : ''
              } ${isCompleted ? 'opacity-90' : 'opacity-100'}`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {isCompleted ? (
                  <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-green-500 flex items-center justify-center">
                    <svg
                      className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={3}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                ) : isCurrent ? (
                  <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 border-blue-500 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-blue-500 rounded-full animate-pulse" />
                  </div>
                ) : (
                  <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 border-gray-300" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className={`text-[11px] sm:text-xs font-medium ${
                  isCompleted ? 'text-gray-400 line-through' : isCurrent ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {step.action}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
