'use client'

import { useSidebarStore } from '@/store/useSidebarStore'
import ViolationAlert from '@/components/ViolationAlert'

export default function Sidebar() {
  const { isOpen, toggle, userState, violations, dismissViolation } = useSidebarStore()

  return (
    <div 
      className={`fixed inset-0 z-50 flex transition-all duration-300 ease-in-out ${
        isOpen ? 'visible pointer-events-auto' : 'invisible pointer-events-none'
      }`}
    >
      {/* Backdrop */}
      <div
        className={`fixed inset-0 bg-black/40 backdrop-blur-[2px] transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={toggle}
      />
      
      {/* Sidebar Content */}
      <div 
        className={`relative ml-auto w-full sm:w-[380px] h-full bg-white/95 backdrop-blur-md border-l border-gray-100 shadow-2xl overflow-y-auto transform transition-transform duration-300 ease-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-6 sm:p-8">
          <button
            onClick={toggle}
            className="absolute top-6 right-6 p-2 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all active:scale-95"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-200">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 tracking-tight">Focus State</h2>
              <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest leading-none mt-1">User Environment</p>
            </div>
          </div>

          {userState ? (
            <div className="space-y-8">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50/50 p-4 rounded-2xl border border-gray-100">
                  <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1">Date</div>
                  <div className="text-sm font-bold text-gray-800">
                    {userState.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </div>
                </div>
                <div className="bg-gray-50/50 p-4 rounded-2xl border border-gray-100">
                  <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1">Budget</div>
                  <div className="text-sm font-bold text-gray-800">
                    ${userState.budget.remaining} <span className="text-gray-400 font-medium">/ ${userState.budget.max}</span>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-[11px] font-black text-gray-900 uppercase tracking-widest">Schedule</h3>
                  <span className="bg-blue-50 text-blue-600 text-[10px] font-bold px-2 py-0.5 rounded-full">
                    {userState.schedule.length} Events
                  </span>
                </div>
                {userState.schedule.length > 0 ? (
                  <div className="space-y-3">
                    {userState.schedule.map((event, idx) => (
                      <div
                        key={`${event.time}-${event.event}-${idx}`}
                        className="group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:border-blue-200 hover:shadow-md transition-all duration-200"
                      >
                        <div className="flex items-start justify-between gap-3 mb-1">
                          <span className="text-[10px] font-black text-blue-500 bg-blue-50/50 px-2 py-0.5 rounded-lg whitespace-nowrap">
                            {event.time}
                          </span>
                          {event.cost && (
                            <span className="text-[10px] font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-lg">
                              -${event.cost}
                            </span>
                          )}
                        </div>
                        <div className="text-sm font-semibold text-gray-800 line-clamp-2 leading-tight">
                          {event.event}
                        </div>
                        <div className="mt-2 text-[10px] text-gray-400 font-medium uppercase tracking-tighter">
                          {event.type || 'Activity'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-10 bg-gray-50/50 rounded-3xl border border-dashed border-gray-200">
                    <p className="text-xs text-gray-400 font-medium whitespace-nowrap">No events scheduled today</p>
                  </div>
                )}
              </div>

              {violations.length > 0 && (
                <div className="pt-6 border-t border-gray-100">
                  <h3 className="text-[11px] font-black text-red-500 uppercase tracking-widest mb-4">Constraints</h3>
                  <div className="space-y-3">
                    {violations.map((violation) => (
                      <ViolationAlert
                        key={violation.id}
                        type={violation.type}
                        severity={violation.severity}
                        message={violation.message}
                        suggestion={violation.suggestion}
                        onDismiss={() => dismissViolation(violation.id)}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 opacity-50">
              <div className="w-12 h-12 bg-gray-100 rounded-2xl mb-4 animate-pulse" />
              <p className="text-xs text-gray-400 font-medium tracking-tight">Initializing state...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
