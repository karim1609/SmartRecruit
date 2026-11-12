import { useEffect, useState } from 'react'
import { getRecruiterProfile, updateRecruiterProfile } from '../../api/recruiters'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import toast from 'react-hot-toast'
import { Save } from 'lucide-react'

export default function RecruiterProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ full_name: '', phone: '', job_title: '' })

  const load = async () => {
    setLoading(true)
    try {
      const res = await getRecruiterProfile()
      setProfile(res.data)
      setForm({
        full_name: res.data.full_name || '',
        phone: res.data.phone || '',
        job_title: res.data.job_title || '',
      })
    } catch {
      setError('Failed to load profile.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {}
      if (form.full_name) payload.full_name = form.full_name
      if (form.phone !== undefined) payload.phone = form.phone || null
      if (form.job_title !== undefined) payload.job_title = form.job_title || null
      await updateRecruiterProfile(payload)
      toast.success('Profile updated!')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">My Profile</h1>
        <p className="text-slate-500 text-sm mt-1">Update your recruiter information.</p>
      </div>

      <form onSubmit={handleSubmit} className="card p-6 space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <input className="input-field" value={form.full_name}
              onChange={e => setForm({ ...form, full_name: e.target.value })} required minLength={2} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
            <input className="input-field" value={form.phone}
              onChange={e => setForm({ ...form, phone: e.target.value })} placeholder="+1234567890" />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1">Job Title</label>
            <input className="input-field" value={form.job_title}
              onChange={e => setForm({ ...form, job_title: e.target.value })} placeholder="e.g. Talent Acquisition Manager" />
          </div>
        </div>
        <div className="flex justify-end">
          <button type="submit" disabled={saving} className="btn-primary flex items-center gap-2">
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>

      <div className="card p-5 mt-5">
        <h2 className="text-sm font-semibold text-slate-700 mb-3">Account Info</h2>
        <div className="text-sm text-slate-600 space-y-1">
          <p>Member since: <span className="font-medium">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : '—'}</span></p>
          <p>Profile ID: <span className="font-mono text-xs text-slate-400">{profile?.id}</span></p>
        </div>
      </div>
    </div>
  )
}

