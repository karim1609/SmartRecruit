import { useState, useEffect } from 'react'
import { Menu, Bell, Search, Sparkles, ChevronDown } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import CommandPalette from './common/CommandPalette'

export default function Navbar({ onMenuClick }) {
  const { user } = useAuth()
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

  // Listen for Cmd+K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(prev => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <>
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-3.5 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 lg:hidden transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Global search button triggering command palette */}
          <button
            type="button"
            onClick={() => setCommandPaletteOpen(true)}
            className="hidden md:flex items-center gap-2 bg-slate-100/70 hover:bg-slate-100 text-slate-400 hover:text-slate-600 rounded-xl px-3.5 py-1.5 text-xs w-72 border border-slate-200/60 transition-colors text-left"
          >
            <Search className="w-3.5 h-3.5 text-slate-400" />
            <span>Search jobs, candidates, pages...</span>
            <kbd className="ml-auto bg-white px-1.5 py-0.5 rounded text-[10px] font-mono text-slate-400 border border-slate-200 shadow-2xs">⌘K</kbd>
          </button>
        </div>

      <div className="flex items-center gap-4">
        {/* Role badge */}
        <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-pulse" />
          {user?.role === 'candidate' ? 'Job Seeker' : user?.role === 'recruiter' ? 'Recruiter Pro' : 'Administrator'}
        </span>

        {/* Notifications Icon */}
        <button className="relative p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-600" />
        </button>

        {/* User avatar menu */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-600 flex items-center justify-center text-white shadow-sm shadow-indigo-200 font-semibold text-sm">
            {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-bold text-slate-900 leading-tight truncate max-w-[140px]">
              {user?.full_name || user?.email}
            </p>
            <p className="text-[11px] font-medium text-slate-400 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </header>

    {/* Global Quick Search Command Palette */}
    <CommandPalette
      isOpen={commandPaletteOpen}
      onClose={() => setCommandPaletteOpen(false)}
    />
  </>
  )
}
