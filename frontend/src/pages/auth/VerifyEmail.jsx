import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function VerifyEmail() {
  const { verifyEmail, resendVerification, loading } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const [email, setEmail] = useState(location.state?.email || '')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [cooldown, setCooldown] = useState(0)
  const [isResending, setIsResending] = useState(false)

  useEffect(() => {
    let timer
    if (cooldown > 0) {
      timer = setInterval(() => {
        setCooldown((prev) => prev - 1)
      }, 1000)
    }
    return () => clearInterval(timer)
  }, [cooldown])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const cleanCode = code.trim()
    if (cleanCode.length !== 6 || !/^\d+$/.test(cleanCode)) {
      setError('Please enter a valid 6-digit verification code.')
      return
    }

    try {
      const res = await verifyEmail(email, cleanCode)
      toast.success(res.message || 'Email verified successfully!')
      
      const userData = res.user
      if (userData?.role === 'candidate') navigate('/candidate/dashboard')
      else if (userData?.role === 'recruiter') navigate('/recruiter/dashboard')
      else if (userData?.role === 'admin') navigate('/admin/dashboard')
      else navigate('/login')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Verification failed. Please check the code.'
      setError(msg)
    }
  }

  const handleResend = async () => {
    if (cooldown > 0 || isResending) return
    setError('')
    setIsResending(true)

    try {
      const res = await resendVerification(email)
      toast.success(res.message || 'New code sent to your email!')
      setCooldown(60)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to resend code.'
      setError(msg)
      if (err.response?.status === 429) {
        setCooldown(60)
      }
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div>
      <div className="w-12 h-12 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 mb-4 mx-auto">
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>

      <h2 className="text-xl font-semibold text-slate-800 mb-1 text-center">Verify your email</h2>
      <p className="text-sm text-slate-500 mb-6 text-center">
        We sent a 6-digit verification code to <br />
        <span className="font-semibold text-slate-700">{email || 'your email'}</span>
      </p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {!location.state?.email && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              required
              className="input-field"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">6-digit Code</label>
          <input
            type="text"
            required
            maxLength={6}
            className="input-field text-center font-mono tracking-widest text-2xl font-bold py-2"
            placeholder="000000"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
          />
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
          {loading ? 'Verifying...' : 'Verify Email'}
        </button>
      </form>

      <div className="mt-5 text-center">
        <p className="text-sm text-slate-500 mb-2">
          Didn't receive the code? Check spam or Mailpit inbox.
        </p>
        <button
          type="button"
          onClick={handleResend}
          disabled={cooldown > 0 || isResending}
          className="text-sm text-indigo-600 font-medium hover:underline disabled:text-slate-400 disabled:no-underline"
        >
          {cooldown > 0 ? `Resend code in ${cooldown}s` : isResending ? 'Sending...' : 'Resend verification code'}
        </button>
      </div>

      <p className="text-sm text-center text-slate-500 mt-6 border-t border-slate-100 pt-4">
        Back to{' '}
        <Link to="/login" className="text-indigo-600 font-medium hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  )
}
