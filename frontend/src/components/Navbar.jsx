import { Menu } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar({ onMenuClick }) {
  const { user } = useAuth()

  return (
    <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center gap-3">
      <button
        onClick={onMenuClick}
        className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 lg:hidden"
      >
        <Menu className="w-5 h-5" />
      </button>
      <div className="flex-1" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
          <span className="text-sm font-semibold text-indigo-700">
            {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
          </span>
        </div>
        <div className="hidden sm:block">
          <p className="text-sm font-medium text-slate-800">{user?.full_name || user?.email}</p>
          <p className="text-xs text-slate-400 capitalize">{user?.role}</p>
        </div>
      </div>
    </header>
  )
}

