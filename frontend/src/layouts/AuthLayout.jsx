import { Outlet, Link } from 'react-router-dom'
import { Sparkles, ShieldCheck, Zap, Users, ArrowUpRight } from 'lucide-react'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center relative overflow-hidden">
      {/* Decorative gradient blur background */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-tr from-indigo-200/40 via-blue-100/30 to-purple-100/40 blur-3xl -z-10 pointer-events-none" />

      {/* Header bar */}
      <header className="absolute top-0 left-0 right-0 py-6 px-6 sm:px-12 flex items-center justify-between z-10">
        <Link to="/" className="flex items-center gap-3 group">
          <img
            src="/logo.png"
            alt="SmartRecruit Logo"
            className="w-11 h-11 rounded-2xl shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform duration-200 object-cover"
          />
          <span className="text-xl font-bold bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-800 bg-clip-text text-transparent">
            SmartRecruit
          </span>
        </Link>
        <div className="hidden sm:flex items-center gap-6 text-sm text-slate-500 font-medium">
          <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-emerald-500" /> Enterprise Grade</span>
          <span className="flex items-center gap-1.5"><Zap className="w-4 h-4 text-indigo-500" /> AI Matched</span>
        </div>
      </header>

      {/* Main card */}
      <div className="w-full max-w-md mx-auto px-4 py-20 relative z-10">
        <div className="bg-white/90 backdrop-blur-xl rounded-3xl border border-slate-200/90 shadow-[0_20px_50px_rgba(8,_112,_184,_0.07)] p-8 sm:p-10">
          <Outlet />
        </div>

        {/* Footer info */}
        <p className="text-center text-xs text-slate-400 mt-6">
          &copy; {new Date().getFullYear()} SmartRecruit Inc. Secure talent intelligence platform.
        </p>
      </div>
    </div>
  )
}
