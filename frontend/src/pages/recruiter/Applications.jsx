import { useEffect, useState } from 'react'
import { getReceivedApplications, updateApplication, downloadApplicationCV } from '../../api/applications'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import Modal from '../../components/common/Modal'
import CVPreviewModal from '../../components/common/CVPreviewModal'
import toast from 'react-hot-toast'
import { FileText, Download, Eye } from 'lucide-react'
import { downloadBlob } from '../../utils/download'

export default function RecruiterApplications() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)
  const [updating, setUpdating] = useState(false)
  const [downloadingCV, setDownloadingCV] = useState(false)
  const [previewApp, setPreviewApp] = useState(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getReceivedApplications(0, 50)
      setApps(res.data)
    } catch {
      setError('Failed to load applications.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleStatusChange = async (appId, newStatus) => {
    setUpdating(true)
    try {
      await updateApplication(appId, { status: newStatus })
      toast.success('Status updated.')
      setSelected(null)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed.')
    } finally {
      setUpdating(false)
    }
  }

  const handleDownloadCV = async (app) => {
    setDownloadingCV(true)
    try {
      const res = await downloadApplicationCV(app.id)
      downloadBlob(res.data, app.cv_filename || `candidate_cv_${app.id.slice(-6)}.pdf`)
      toast.success('Candidate CV downloaded.')
    } catch {
      toast.error('Failed to download CV file.')
    } finally {
      setDownloadingCV(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Received Applications</h1>
        <p className="text-slate-500 text-sm mt-1">Review and manage candidate applications and CVs for your job offers.</p>
      </div>

      {apps.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <FileText className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No applications received yet.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Application ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Job ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Candidate CV</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Applied</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {apps.map(app => (
                <tr key={app.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">{app.id?.slice(-10)}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{app.job_offer_id?.slice(-10)}</td>
                  <td className="px-4 py-3">
                    {app.cv_filename ? (
                      <button
                        onClick={() => setPreviewApp(app)}
                        className="inline-flex items-center gap-1.5 text-xs text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-lg font-mono truncate max-w-[170px] transition-colors"
                        title="Quick Preview CV"
                      >
                        <Eye className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                        <span className="truncate">{app.cv_filename}</span>
                      </button>
                    ) : (
                      <span className="text-xs text-slate-400 italic">None</span>
                    )}
                  </td>
                  <td className="px-4 py-3"><StatusBadge status={app.status} /></td>
                  <td className="px-4 py-3 text-xs text-slate-400">{app.applied_at ? new Date(app.applied_at).toLocaleDateString() : '—'}</td>
                  <td className="px-4 py-3">
                    <button onClick={() => setSelected(app)} className="text-indigo-600 text-xs font-medium hover:underline">
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <Modal title="Review Application" onClose={() => setSelected(null)} size="lg">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-xs text-slate-400 uppercase font-semibold mb-0.5">Application ID</p>
                <p className="font-mono text-xs text-slate-700">{selected.id}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase font-semibold mb-0.5">Candidate ID</p>
                <p className="font-mono text-xs text-slate-700">{selected.candidate_id}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase font-semibold mb-0.5">Status</p>
                <StatusBadge status={selected.status} />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase font-semibold mb-0.5">Applied</p>
                <p className="text-slate-700 text-xs">{selected.applied_at ? new Date(selected.applied_at).toLocaleString() : '—'}</p>
              </div>
            </div>

            {/* Candidate CV section */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5">
              <p className="text-xs text-slate-500 uppercase font-semibold mb-2">Candidate Curriculum Vitae (CV)</p>
              {selected.cv_filename ? (
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                      <FileText className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-medium text-slate-800 truncate font-mono">
                      {selected.cv_filename}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPreviewApp(selected)}
                      className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3 shrink-0"
                    >
                      <Eye className="w-3.5 h-3.5 text-indigo-600" />
                      Preview CV
                    </button>
                    <button
                      onClick={() => handleDownloadCV(selected)}
                      disabled={downloadingCV}
                      className="btn-primary text-xs flex items-center gap-1.5 py-1.5 px-3 shrink-0"
                    >
                      <Download className="w-3.5 h-3.5" />
                      {downloadingCV ? 'Downloading...' : 'Download'}
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No CV attached with this application.</p>
              )}
            </div>

            {selected.cover_letter && (
              <div>
                <p className="text-xs text-slate-400 uppercase font-semibold mb-1">Cover Letter</p>
                <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-700 leading-relaxed max-h-40 overflow-y-auto">
                  {selected.cover_letter}
                </div>
              </div>
            )}

            <div>
              <p className="text-xs text-slate-400 uppercase font-semibold mb-2">Update Status</p>
              <div className="flex flex-wrap gap-2">
                {['pending', 'reviewing', 'accepted', 'rejected'].map(s => (
                  <button
                    key={s}
                    disabled={selected.status === s || updating}
                    onClick={() => handleStatusChange(selected.id, s)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-40 disabled:cursor-not-allowed
                      ${selected.status === s
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                      }`}
                  >
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* In-Browser PDF CV Preview */}
      {previewApp && (
        <CVPreviewModal
          application={previewApp}
          onClose={() => setPreviewApp(null)}
        />
      )}
    </div>
  )
}
