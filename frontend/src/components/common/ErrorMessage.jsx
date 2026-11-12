import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message = 'Something went wrong.', onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] text-center p-6">
      <AlertCircle className="w-10 h-10 text-red-500 mb-3" />
      <p className="text-slate-700 font-medium mb-2">Error</p>
      <p className="text-sm text-slate-500 mb-4">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-primary text-sm">
          Try Again
        </button>
      )}
    </div>
  )
}

