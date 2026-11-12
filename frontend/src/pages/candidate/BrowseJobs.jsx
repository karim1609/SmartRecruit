import { useEffect, useState } from 'react'
import { getPublicJobOffers } from '../../api/jobOffers'
import { createApplication } from '../../api/applications'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import Modal from '../../components/common/Modal'
import StatusBadge from '../../components/common/StatusBadge'
import toast from 'react-hot-toast'
import { MapPin, Briefcase, ChevronRight, Search } from 'lucide-react'

export default function BrowseJobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(null)
  const [applyModal, setApplyModal] = useState(null)
  const [coverLetter, setCoverLetter] = useState('')
  const [applying, setApplying] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getPublicJobOffers(0, 50)
      setJobs(res.data)
    } catch {
      setError('Failed to load job offers.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const filtered = jobs.filter(j =>
    j.title?.toLowerCase().includes(search.toLowerCase()) ||
    j.location?.toLowerCase().includes(search.toLowerCase())
  )

  const handleApply = async () => {
    if (!applyModal?.id) {
      toast.error('Invalid job offer.')
      return
    }
    setApplying(true)
    try {
      await createApplication({ job_offer_id: applyModal.id, cover_letter: coverLetter || null })
      toast.success('Application submitted!')
      setApplyModal(null)
      setCoverLetter('')
    } catch (err) {
      const detail = err.response?.data?.detail
      let msg = 'Failed to submit application.'
      if (typeof detail === 'string') msg = detail
      else if (Array.isArray(detail)) msg = detail.map(d => d.msg || d.message || JSON.stringify(d)).join(', ')
      else if (detail) msg = JSON.stringify(detail)
      toast.error(msg)
    } finally {
      setApplying(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Browse Jobs</h1>
        <p className="text-slate-500 text-sm mt-1">Explore open positions and apply.</p>
      </div>

      <div className="relative mb-5">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          className="input-field pl-9"
          placeholder="Search by title or location..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No open job offers found.</p>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
          {filtered.map(job => (
            <div key={job.id} className="card p-5 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelected(job)}>
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-slate-800 text-sm leading-tight pr-2">{job.title}</h3>
                <StatusBadge status={job.status} />
              </div>
              {job.location && (
                <div className="flex items-center gap-1 text-xs text-slate-500 mb-2">
                  <MapPin className="w-3 h-3" />
                  {job.location}
                </div>
              )}
              {job.required_skills?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {job.required_skills.slice(0, 3).map(s => (
                    <span key={s} className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs">{s}</span>
                  ))}
                  {job.required_skills.length > 3 && (
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-xs">+{job.required_skills.length - 3}</span>
                  )}
                </div>
              )}
              <button
                className="mt-4 flex items-center gap-1 text-indigo-600 text-xs font-medium hover:underline"
                onClick={e => { e.stopPropagation(); setApplyModal(job); setCoverLetter('') }}
              >
                Apply now <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selected && (
        <Modal title={selected.title} onClose={() => setSelected(null)} size="lg">
          <div className="space-y-4">
            <div className="flex items-center gap-4 text-sm text-slate-500">
              {selected.location && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{selected.location}</span>}
              {selected.min_experience !== undefined && <span>Min {selected.min_experience}y exp</span>}
            </div>
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-1">Description</h3>
              <p className="text-sm text-slate-700 leading-relaxed">{selected.description}</p>
            </div>
            {selected.required_skills?.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-slate-500 uppercase mb-2">Required Skills</h3>
                <div className="flex flex-wrap gap-1.5">
                  {selected.required_skills.map(s => (
                    <span key={s} className="px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-medium">{s}</span>
                  ))}
                </div>
              </div>
            )}
            <div className="flex justify-end gap-3 pt-2">
              <button className="btn-secondary" onClick={() => setSelected(null)}>Close</button>
              <button className="btn-primary" onClick={() => { setApplyModal(selected); setSelected(null); setCoverLetter('') }}>
                Apply
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Apply Modal */}
      {applyModal && (
        <Modal title={`Apply for ${applyModal.title}`} onClose={() => setApplyModal(null)}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Cover Letter <span className="text-slate-400 font-normal">(optional)</span></label>
              <textarea
                className="input-field min-h-[120px] resize-y"
                placeholder="Tell us why you're a great fit..."
                value={coverLetter}
                onChange={e => setCoverLetter(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-3">
              <button className="btn-secondary" onClick={() => setApplyModal(null)}>Cancel</button>
              <button className="btn-primary" onClick={handleApply} disabled={applying}>
                {applying ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

