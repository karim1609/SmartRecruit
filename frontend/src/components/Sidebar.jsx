import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, User, Briefcase, FileText, Building2,
  Users, Sparkles, LogOut, BrainCircuit, ChevronRight
} from 'lucide-react'

const candidateNav = [
  { to: '/candidate/dashboard', icon: LayoutDashboard, label: 'Overview' },
  { to: '/candidate/profile', icon: User, label: 'CV & Profile' },
  { to: '/candidate/jobs', icon: Briefcase, label: 'Explore Jobs' },
  { to: '/candidate/applications', icon: FileText, label: 'My Applications' },
]

const recruiterNav = [
  { to: '/recruiter/dashboard', icon: LayoutDashboard, label: 'Overview' },
  { to: '/recruiter/profile', icon: User, label: 'Recruiter Profile' },
  { to: '/recruiter/companies', icon: Building2, label: 'Companies' },
  { to: '/recruiter/jobs', icon: Briefcase, label: 'Job Listings' },
  { to: '/recruiter/applications', icon: FileText, label: 'Candidate Pipeline' },
  { to: '/recruiter/matching', icon: BrainCircuit, label: 'AI Match Engine' },
]

const adminNav = [
  { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Analytics' },
  { to: '/admin/users', icon: Users, label: 'User Directory' },
  { to: '/admin/companies', icon: Building2, label: 'Organizations' },
  { to: '/admin/jobs', icon: Briefcase, label: 'All Job Offers' },
  { to: '/admin/applications', icon: FileText, label: 'All Applications' },
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
    <aside className="flex flex-col w-64 bg-slate-900 border-r border-slate-800 text-slate-300 h-full select-none shadow-xl">
      {/* Brand Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800/80">
        <img
          src="/logo.png"
          alt="SmartRecruit Logo"
          className="w-10 h-10 rounded-xl shadow-lg shadow-indigo-500/30 object-cover"
        />
        <div>
          <span className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
            SmartRecruit
            <span className="text-[10px] bg-indigo-500/20 text-indigo-400 font-semibold px-1.5 py-0.5 rounded border border-indigo-500/30">PRO</span>
          </span>
          <p className="text-[11px] text-slate-400 leading-none mt-0.5">Talent Engine</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 px-3 py-6 space-y-6 overflow-y-auto">
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Main Navigation</p>
          <nav className="space-y-1">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 group ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:bg-slate-800/70 hover:text-slate-200'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`} />
                      <span>{label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-indigo-200" />}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* User profile & Logout */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center gap-3 px-2 py-2 mb-2 rounded-xl bg-slate-800/40 border border-slate-700/50">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center font-bold text-xs text-indigo-400">
            {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
          </div>
          <div className="overflow-hidden flex-1">
            <p className="text-xs font-semibold text-white truncate">{user?.full_name || user?.email}</p>
            <p className="text-[10px] text-slate-400 capitalize">{user?.role} account</p>
          </div>
        </div>

        <button
          onClick={logout}
          className="flex items-center justify-center gap-2 w-full py-2 px-3 rounded-xl text-xs font-semibold text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 border border-transparent hover:border-rose-500/20 transition-all duration-200"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
