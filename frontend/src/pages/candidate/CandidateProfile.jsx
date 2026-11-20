import { useEffect, useState, useRef } from 'react'
import {
  getCandidateProfile,
  updateCandidateProfile,
  uploadCandidateCV,
  downloadCandidateCV,
  deleteCandidateCV,
} from '../../api/candidates'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import toast from 'react-hot-toast'
import { Plus, X, Save, FileText, Upload, Download, Trash2, CheckCircle2 } from 'lucide-react'
import { downloadBlob } from '../../utils/download'

export default function CandidateProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [uploadingCV, setUploadingCV] = useState(false)
  const [downloadingCV, setDownloadingCV] = useState(false)
  const [selectedCVFile, setSelectedCVFile] = useState(null)
  const fileInputRef = useRef(null)
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

  const handleCVUpload = async () => {
    if (!selectedCVFile) {
      toast.error('Please select a file first.')
      return
    }
    setUploadingCV(true)
    try {
      const res = await uploadCandidateCV(selectedCVFile)
      toast.success(res.data?.message || 'CV uploaded successfully!')
      setSelectedCVFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to upload CV.')
    } finally {
      setUploadingCV(false)
    }
  }

  const handleCVDownload = async () => {
    setDownloadingCV(true)
    try {
      const res = await downloadCandidateCV()
      downloadBlob(res.data, profile?.cv_filename || 'my_cv.pdf')
      toast.success('CV downloaded.')
    } catch {
      toast.error('Failed to download CV.')
    } finally {
      setDownloadingCV(false)
    }
  }

  const handleCVDelete = async () => {
    if (!confirm('Are you sure you want to delete your current CV?')) return
    try {
      await deleteCandidateCV()
      toast.success('CV removed from profile.')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete CV.')
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">My Profile</h1>
        <p className="text-slate-500 text-sm mt-1">Update your professional information and curriculum vitae (CV).</p>
      </div>

      {/* CV Upload & Management Section */}
      <div className="card p-6 border-indigo-100 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-800">Curriculum Vitae (CV)</h2>
              <p className="text-xs text-slate-500">Stored in your profile and used for 1-click job applications</p>
            </div>
          </div>
          {profile?.cv_filename && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5" />
              CV Available
            </span>
          )}
        </div>

        {profile?.cv_filename ? (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="p-2.5 bg-white border border-slate-200 rounded-lg shadow-2xs text-indigo-600">
                <FileText className="w-6 h-6" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-slate-800 truncate" title={profile.cv_filename}>
                  {profile.cv_filename}
                </p>
                <p className="text-xs text-slate-400">Attached to your candidate profile</p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={handleCVDownload}
                disabled={downloadingCV}
                className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3"
              >
                <Download className="w-3.5 h-3.5 text-slate-600" />
                {downloadingCV ? 'Downloading...' : 'Download'}
              </button>
              <button
                type="button"
                onClick={handleCVDelete}
                className="p-1.5 rounded-lg border border-slate-200 text-red-500 hover:bg-red-50 transition-colors"
                title="Delete CV"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="border border-dashed border-slate-300 rounded-xl p-5 text-center mb-4 bg-slate-50/50">
            <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2 opacity-60" />
            <p className="text-sm font-medium text-slate-700">No CV uploaded yet</p>
            <p className="text-xs text-slate-400 mt-0.5">Upload your CV to apply to jobs quickly without re-uploading each time.</p>
          </div>
        )}

        <div className="pt-2 border-t border-slate-100">
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            {profile?.cv_filename ? 'Replace Current CV' : 'Upload New CV'}
          </label>
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={(e) => setSelectedCVFile(e.target.files[0] || null)}
              className="block w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
            />
            <button
              type="button"
              onClick={handleCVUpload}
              disabled={!selectedCVFile || uploadingCV}
              className="btn-primary text-xs flex items-center justify-center gap-1.5 py-2 px-4 shrink-0 disabled:opacity-50"
            >
              <Upload className="w-3.5 h-3.5" />
              {uploadingCV ? 'Uploading...' : 'Save CV'}
            </button>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">Accepted formats: PDF, DOC, DOCX, TXT (Max 10MB)</p>
        </div>
      </div>

      {/* Main Profile Form */}
      <form onSubmit={handleSubmit} className="card p-6 space-y-5">
        <h2 className="text-base font-semibold text-slate-800">Basic Information</h2>
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
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>

      {/* Read-only info */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-slate-700 mb-3">Account Info</h2>
        <div className="text-sm text-slate-600 space-y-1">
          <p>Member since: <span className="font-medium">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : '—'}</span></p>
          <p>Profile ID: <span className="font-mono text-xs text-slate-400">{profile?.id}</span></p>
        </div>
      </div>
    </div>
  )
}
