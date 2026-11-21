import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Briefcase, User, FileText, Building2, Sparkles, X, ArrowRight } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { getPublicJobOffers } from '../../api/jobOffers'

export default function CommandPalette({ isOpen, onClose }) {
  const [query, setQuery] = useState('')
  const [jobs, setJobs] = useState([])
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isOpen) {
      setQuery('')
      // Pre-load jobs for fuzzy quick search
      getPublicJobOffers(0, 30)
        .then(res => setJobs(res.data || []))
        .catch(() => {})
    }
  }, [isOpen])

  // Handle keyboard shortcut Esc
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown)
    }
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  // Fast navigation shortcuts
  const navigationItems = [
    { label: 'Browse Jobs', path: '/candidate/jobs', role: ['candidate'], icon: Briefcase },
    { label: 'My Applications', path: '/candidate/applications', role: ['candidate'], icon: FileText },
    { label: 'Profile & CV', path: '/candidate/profile', role: ['candidate'], icon: User },
    { label: 'Job Offers', path: '/recruiter/jobs', role: ['recruiter'], icon: Briefcase },
    { label: 'Candidate Pipeline', path: '/recruiter/applications', role: ['recruiter'], icon: FileText },
    { label: 'AI Match Engine', path: '/recruiter/matching', role: ['recruiter'], icon: Sparkles },
    { label: 'Companies Directory', path: '/recruiter/companies', role: ['recruiter', 'admin'], icon: Building2 },
    { label: 'User Directory', path: '/admin/users', role: ['admin'], icon: User },
  ].filter(item => !item.role || item.role.includes(user?.role))

  // Filter jobs based on query
  const filteredJobs = query.trim()
    ? jobs.filter(j =>
        j.title?.toLowerCase().includes(query.toLowerCase()) ||
        j.location?.toLowerCase().includes(query.toLowerCase()) ||
        j.required_skills?.some(s => s.toLowerCase().includes(query.toLowerCase()))
      )
    : jobs.slice(0, 5)

  const handleSelect = (path) => {
    onClose()
    navigate(path)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200/90 w-full max-w-xl overflow-hidden animate-scaleUp">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-100">
          <Search className="w-5 h-5 text-indigo-600 mr-3" />
          <input
            type="text"
            autoFocus
            className="w-full text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none"
            placeholder="Type a command, job title, location, or skill..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results Area */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-3">
          {/* Quick Page Actions */}
          <div>
            <p className="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Quick Actions</p>
            <div className="space-y-0.5">
              {navigationItems
                .filter(item => !query || item.label.toLowerCase().includes(query.toLowerCase()))
                .map((item) => {
                  const Icon = item.icon
                  return (
                    <button
                      key={item.path}
                      onClick={() => handleSelect(item.path)}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors group"
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
                        <span>{item.label}</span>
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-indigo-600" />
                    </button>
                  )
                })}
            </div>
          </div>

          {/* Job Offers Search */}
          {filteredJobs.length > 0 && (
            <div className="border-t border-slate-100 pt-2">
              <p className="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Job Matches</p>
              <div className="space-y-1">
                {filteredJobs.map((job) => (
                  <button
                    key={job.id}
                    onClick={() => handleSelect(user?.role === 'candidate' ? '/candidate/jobs' : '/recruiter/jobs')}
                    className="w-full text-left px-3 py-2 rounded-xl text-xs hover:bg-slate-50 transition-colors flex items-center justify-between"
                  >
                    <div>
                      <p className="font-semibold text-slate-800">{job.title}</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">{job.location} • {job.required_skills?.slice(0, 3).join(', ')}</p>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">View</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
          <span>Press <kbd className="px-1.5 py-0.5 bg-white border rounded text-[10px] font-mono">Esc</kbd> to close</span>
          <span>SmartRecruit Instant Search</span>
        </div>
      </div>
    </div>
  )
}
