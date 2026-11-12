import { useEffect, useState } from 'react'
import { getMyApplications, withdrawApplication, updateApplication } from '../../api/applications'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import Modal from '../../components/common/Modal'
import toast from 'react-hot-toast'
import { FileText, Trash2, Edit2 } from 'lucide-react'

export default function MyApplications() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editModal, setEditModal] = useState(null)
  const [coverLetter, setCoverLetter] = useState('')
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getMyApplications(0, 50)
      setApps(res.data)
    } catch {
      setError('Failed to load applications.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleWithdraw = async (id) => {
    if (!confirm('Withdraw this application?')) return
    try {
      await withdrawApplication(id)
      toast.success('Application withdrawn.')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to withdraw.')
    }
  }

  const handleEdit = async () => {
    setSaving(true)
    try {
      await updateApplication(editModal.id, { cover_letter: coverLetter })
      toast.success('Cover letter updated.')
      setEditModal(null)
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
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">My Applications</h1>
        <p className="text-slate-500 text-sm mt-1">Track and manage your job applications.</p>
      </div>

      {apps.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <FileText className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No applications yet. Start by browsing jobs!</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Job ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Applied</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {apps.map(app => (
                <tr key={app.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">{app.job_offer_id?.slice(-12)}</td>
                  <td className="px-4 py-3"><StatusBadge status={app.status} /></td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {app.status === 'pending' && (
                        <button
                          onClick={() => { setEditModal(app); setCoverLetter(app.cover_letter || '') }}
                          className="p-1.5 rounded hover:bg-indigo-50 text-indigo-600"
                          title="Edit cover letter"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => handleWithdraw(app.id)}
                        className="p-1.5 rounded hover:bg-red-50 text-red-500"
                        title="Withdraw"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editModal && (
        <Modal title="Edit Cover Letter" onClose={() => setEditModal(null)}>
          <div className="space-y-4">
            <textarea
              className="input-field min-h-[140px] resize-y"
              value={coverLetter}
              onChange={e => setCoverLetter(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button className="btn-secondary" onClick={() => setEditModal(null)}>Cancel</button>
              <button className="btn-primary" onClick={handleEdit} disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

