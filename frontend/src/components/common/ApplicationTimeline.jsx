import { Check, Clock, Eye, CheckCircle2, XCircle } from 'lucide-react'

export default function ApplicationTimeline({ status, appliedAt, updatedAt }) {
  const steps = [
    {
      id: 'submitted',
      label: 'Application Submitted',
      description: 'Received by SmartRecruit',
      date: appliedAt,
      completed: true,
      current: status === 'pending',
    },
    {
      id: 'reviewing',
      label: 'Hiring Team Review',
      description: 'Profile & CV assessment',
      date: status !== 'pending' ? updatedAt : null,
      completed: ['reviewing', 'accepted', 'rejected'].includes(status),
      current: status === 'reviewing',
    },
    {
      id: 'decision',
      label: status === 'rejected' ? 'Application Closed' : 'Final Selection & Offer',
      description: status === 'rejected' ? 'Not moving forward at this time' : 'Interview or job offer',
      date: ['accepted', 'rejected'].includes(status) ? updatedAt : null,
      completed: ['accepted', 'rejected'].includes(status),
      current: ['accepted', 'rejected'].includes(status),
      isRejected: status === 'rejected',
    },
  ]

  return (
    <div className="py-3 px-1">
      <div className="relative flex items-center justify-between">
        {/* Connecting line */}
        <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-0.5 bg-slate-200 -z-0" />

        {steps.map((step, idx) => {
          const isDone = step.completed
          const isCurrent = step.current
          const isRejected = step.isRejected

          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center group text-center max-w-[130px]">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 shadow-sm ${
                  isRejected
                    ? 'bg-rose-50 text-rose-600 border-2 border-rose-500'
                    : isDone
                    ? 'bg-indigo-600 text-white shadow-indigo-200'
                    : 'bg-white text-slate-400 border-2 border-slate-200'
                } ${isCurrent && !isRejected ? 'ring-4 ring-indigo-100 scale-110' : ''}`}
              >
                {isRejected ? (
                  <XCircle className="w-5 h-5 text-rose-600" />
                ) : isDone ? (
                  <Check className="w-4 h-4 stroke-[2.5]" />
                ) : (
                  <span>{idx + 1}</span>
                )}
              </div>

              <div className="mt-2">
                <p className={`text-xs font-semibold leading-tight ${isCurrent ? 'text-indigo-600 font-bold' : isRejected ? 'text-rose-600' : 'text-slate-700'}`}>
                  {step.label}
                </p>
                <p className="text-[10px] text-slate-400 mt-0.5 hidden sm:block">
                  {step.description}
                </p>
                {step.date && (
                  <span className="text-[10px] font-mono text-slate-400 mt-0.5 block">
                    {new Date(step.date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
