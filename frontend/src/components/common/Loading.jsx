export default function Loading({ text = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="text-center">
        <div className="inline-block w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-3" />
        <p className="text-sm text-slate-500">{text}</p>
      </div>
    </div>
  )
}

