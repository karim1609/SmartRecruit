import { useEffect, useState } from 'react'
import { getPublicJobOffers } from '../../api/jobOffers'
import { deleteJobOffer } from '../../api/jobOffers'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import toast from 'react-hot-toast'
import { Briefcase, Trash2 } from 'lucide-react'

export default function AdminJobOffers() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getPublicJobOffers(0, 100)
      setJobs(res.data)
    } catch {
      setError('Failed to load job offers.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id) => {
    if (!confirm('Delete this job offer and its applications?')) return
    try {
      await deleteJobOffer(id)
      toast.success('Deleted.')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Delete failed.')
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Job Offers</h1>
        <p className="text-slate-500 text-sm mt-1">View and manage all open job offers.</p>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No open job offers.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Title</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Location</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Created</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {jobs.map(job => (
                <tr key={job.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">{job.title}</td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{job.location || '—'}</td>
                  <td className="px-4 py-3"><StatusBadge status={job.status} /></td>
                  <td className="px-4 py-3 text-xs text-slate-400">{job.created_at ? new Date(job.created_at).toLocaleDateString() : '—'}</td>
                  <td className="px-4 py-3">
                    <button onClick={() => handleDelete(job.id)} className="p-1.5 rounded hover:bg-red-50 text-red-500">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

