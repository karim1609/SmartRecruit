import { useEffect, useState } from 'react'
import { getMyApplications, withdrawApplication, updateApplication, downloadApplicationCV } from '../../api/applications'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import ApplicationTimeline from '../../components/common/ApplicationTimeline'
import CVPreviewModal from '../../components/common/CVPreviewModal'
import Modal from '../../components/common/Modal'
import toast from 'react-hot-toast'
import { FileText, Trash2, Edit2, Download, Eye, ChevronDown, ChevronUp } from 'lucide-react'
import { downloadBlob } from '../../utils/download'

export default function MyApplications() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editModal, setEditModal] = useState(null)
  const [coverLetter, setCoverLetter] = useState('')
  const [saving, setSaving] = useState(false)
  const [downloadingId, setDownloadingId] = useState(null)
  const [previewApp, setPreviewApp] = useState(null)
  const [expandedId, setExpandedId] = useState(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getMyApplications(0, 50)
      setApps(res.data)
      if (res.data?.length > 0) {
        setExpandedId(res.data[0].id) // expand first by default
      }
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

  const handleDownloadCV = async (app) => {
    setDownloadingId(app.id)
    try {
      const res = await downloadApplicationCV(app.id)
      downloadBlob(res.data, app.cv_filename || `application_${app.id.slice(-6)}_cv.pdf`)
      toast.success('CV downloaded.')
    } catch {
      toast.error('Failed to download CV file.')
    } finally {
      setDownloadingId(null)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Applications</h1>
          <p className="text-slate-500 text-sm mt-1">
            Track real-time hiring progress, view attached CVs, and manage your submissions.
          </p>
        </div>
      </div>

      {apps.length === 0 ? (
        <div className="card text-center py-16 px-4">
          <FileText className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <h3 className="text-sm font-bold text-slate-800">No applications submitted yet</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Discover opportunities matching your skills and experience on the job board.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {apps.map((app) => {
            const isExpanded = expandedId === app.id
            return (
              <div key={app.id} className="card p-5 transition-all duration-200 hover:shadow-md">
                {/* Application top bar */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-xs font-mono">
                      #{app.job_offer_id?.slice(-4)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-slate-800">Job Reference: {app.job_offer_id?.slice(-10)}</span>
                        <StatusBadge status={app.status} />
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Submitted on {app.applied_at ? new Date(app.applied_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {app.cv_filename && (
                      <button
                        onClick={() => setPreviewApp(app)}
                        className="btn-secondary py-1.5 px-3 text-xs gap-1.5"
                        title="Quick Preview CV"
                      >
                        <Eye className="w-3.5 h-3.5 text-indigo-600" />
                        Preview CV
                      </button>
                    )}

                    {app.status === 'pending' && (
                      <button
                        onClick={() => { setEditModal(app); setCoverLetter(app.cover_letter || '') }}
                        className="p-2 rounded-xl text-slate-500 hover:text-indigo-600 hover:bg-slate-100 transition-colors"
                        title="Edit cover letter"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    )}

                    <button
                      onClick={() => handleWithdraw(app.id)}
                      className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                      title="Withdraw Application"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => setExpandedId(isExpanded ? null : app.id)}
                      className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                      title={isExpanded ? "Collapse Timeline" : "Expand Timeline"}
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Stepper Timeline */}
                {isExpanded && (
                  <div className="pt-5 mt-2 bg-slate-50/60 rounded-xl p-4 border border-slate-100">
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">
                      Hiring Pipeline Progression
                    </p>
                    <ApplicationTimeline
                      status={app.status}
                      appliedAt={app.applied_at}
                      updatedAt={app.updated_at}
                    />

                    {app.cover_letter && (
                      <div className="mt-5 pt-4 border-t border-slate-200/80">
                        <p className="text-xs font-semibold text-slate-600 mb-1">Your Submitted Cover Letter:</p>
                        <p className="text-xs text-slate-500 bg-white p-3 rounded-lg border border-slate-200/60 whitespace-pre-wrap leading-relaxed">
                          {app.cover_letter}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Edit Cover Letter Modal */}
      {editModal && (
        <Modal title="Edit Cover Letter" onClose={() => setEditModal(null)}>
          <div className="space-y-4">
            <textarea
              className="input-field min-h-[140px] resize-y"
              value={coverLetter}
              onChange={e => setCoverLetter(e.target.value)}
              placeholder="Introduce yourself to the hiring manager..."
            />
            <div className="flex justify-end gap-3">
              <button className="btn-secondary" onClick={() => setEditModal(null)}>Cancel</button>
              <button className="btn-primary" onClick={handleEdit} disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* In-Browser PDF Preview Modal */}
      {previewApp && (
        <CVPreviewModal
          application={previewApp}
          onClose={() => setPreviewApp(null)}
        />
      )}
    </div>
  )
}
