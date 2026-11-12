import { useEffect, useState } from 'react'
import { getCandidateProfile, updateCandidateProfile } from '../../api/candidates'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import toast from 'react-hot-toast'
import { Plus, X, Save } from 'lucide-react'

export default function CandidateProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    full_name: '',
    phone: '',
    location: '',
    skills: [],
  })
  const [newSkill, setNewSkill] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const res = await getCandidateProfile()
      setProfile(res.data)
      setForm({
        full_name: res.data.full_name || '',
        phone: res.data.phone || '',
        location: res.data.location || '',
        skills: res.data.skills || [],
      })
    } catch {
      setError('Failed to load profile.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const addSkill = () => {
    const s = newSkill.trim()
    if (s && !form.skills.includes(s)) {
      setForm({ ...form, skills: [...form.skills, s] })
      setNewSkill('')
    }
  }

  const removeSkill = (s) => {
    setForm({ ...form, skills: form.skills.filter(sk => sk !== s) })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {}
      if (form.full_name) payload.full_name = form.full_name
      if (form.phone !== undefined) payload.phone = form.phone || null
      if (form.location !== undefined) payload.location = form.location || null
      payload.skills = form.skills
      await updateCandidateProfile(payload)
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
        <p className="text-slate-500 text-sm mt-1">Update your professional information.</p>
      </div>

      <form onSubmit={handleSubmit} className="card p-6 space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <input
              className="input-field"
              value={form.full_name}
              onChange={e => setForm({ ...form, full_name: e.target.value })}
              minLength={2}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
            <input
              className="input-field"
              value={form.phone}
              onChange={e => setForm({ ...form, phone: e.target.value })}
              placeholder="+1234567890"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
            <input
              className="input-field"
              value={form.location}
              onChange={e => setForm({ ...form, location: e.target.value })}
              placeholder="City, Country"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Skills</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {form.skills.map(sk => (
              <span key={sk} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-medium">
                {sk}
                <button type="button" onClick={() => removeSkill(sk)}>
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              className="input-field flex-1"
              placeholder="Add a skill..."
              value={newSkill}
              onChange={e => setNewSkill(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addSkill())}
            />
            <button type="button" onClick={addSkill} className="btn-secondary px-3">
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button type="submit" disabled={saving} className="btn-primary flex items-center gap-2">
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>

      {/* Read-only info */}
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

