import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, User, Briefcase, FileText, Building2,
  Users, Sparkles, Settings, LogOut, BrainCircuit
} from 'lucide-react'

const candidateNav = [
  { to: '/candidate/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/candidate/profile', icon: User, label: 'My Profile' },
  { to: '/candidate/jobs', icon: Briefcase, label: 'Browse Jobs' },
  { to: '/candidate/applications', icon: FileText, label: 'My Applications' },
]

const recruiterNav = [
  { to: '/recruiter/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/recruiter/profile', icon: User, label: 'My Profile' },
  { to: '/recruiter/companies', icon: Building2, label: 'Companies' },
  { to: '/recruiter/jobs', icon: Briefcase, label: 'Job Offers' },
  { to: '/recruiter/applications', icon: FileText, label: 'Applications' },
  { to: '/recruiter/matching', icon: BrainCircuit, label: 'AI Matching' },
]

const adminNav = [
  { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/admin/users', icon: Users, label: 'Users' },
  { to: '/admin/companies', icon: Building2, label: 'Companies' },
  { to: '/admin/jobs', icon: Briefcase, label: 'Job Offers' },
  { to: '/admin/applications', icon: FileText, label: 'Applications' },
]

const navByRole = {
  candidate: candidateNav,
  recruiter: recruiterNav,
  admin: adminNav,
}

export default function Sidebar({ onClose }) {
  const { user, logout } = useAuth()
  const navItems = navByRole[user?.role] || []

  return (
    <aside className="flex flex-col w-64 bg-white border-r border-slate-200 h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-200">
        <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <span className="text-lg font-bold text-slate-800">SmartRecruit</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-3 py-4 border-t border-slate-200 space-y-1">
        <div className="px-3 py-2 mb-1">
          <p className="text-xs font-semibold text-slate-800 truncate">{user?.full_name || user?.email}</p>
          <p className="text-xs text-slate-400 capitalize">{user?.role}</p>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>
    </aside>
  )
}

