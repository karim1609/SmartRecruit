import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import { LogIn, ArrowRight, Lock, Mail } from 'lucide-react'

export default function Login() {
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const user = await login(form.email, form.password)
      toast.success(`Welcome back, ${user.full_name || 'User'}!`)
      if (user.role === 'candidate') navigate('/candidate/dashboard')
      else if (user.role === 'recruiter') navigate('/recruiter/dashboard')
      else if (user.role === 'admin') navigate('/admin/dashboard')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Check your credentials.'
      setError(msg)
      if (err.response?.status === 403 && msg.toLowerCase().includes('verification')) {
        toast.error('Email verification required. Redirecting...')
        setTimeout(() => {
          navigate('/verify-email', { state: { email: form.email } })
        }, 1500)
      }
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Welcome back</h2>
        <p className="text-sm text-slate-500 mt-1.5">Sign in to manage your talent pipeline or applications.</p>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200/80 text-rose-700 text-sm rounded-xl px-4 py-3 mb-5 flex items-start gap-2.5 animate-fadeIn">
          <span className="font-semibold text-rose-800 text-xs uppercase tracking-wider mt-0.5">Error:</span>
          <span className="flex-1">{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Work or Personal Email
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="email"
              required
              className="input-field pl-10"
              placeholder="name@company.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Password
            </label>
          </div>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="password"
              required
              className="input-field pl-10"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full mt-3 py-3 gap-2 group">
          <span>{loading ? 'Authenticating...' : 'Sign in to Account'}</span>
          {!loading && <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />}
        </button>
      </form>

      <div className="mt-8 pt-6 border-t border-slate-100 text-center">
        <p className="text-sm text-slate-500">
          New to SmartRecruit?{' '}
          <Link to="/register" className="text-indigo-600 font-semibold hover:text-indigo-700 transition-colors">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  )
}
