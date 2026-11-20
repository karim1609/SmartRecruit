import { useEffect, useState } from 'react'
import { getPublicJobOffers } from '../../api/jobOffers'
import { createApplication } from '../../api/applications'
import { getCandidateProfile } from '../../api/candidates'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import Modal from '../../components/common/Modal'
import StatusBadge from '../../components/common/StatusBadge'
import toast from 'react-hot-toast'
import { MapPin, Briefcase, ChevronRight, Search, FileText, Upload, CheckCircle2, AlertCircle } from 'lucide-react'

export default function BrowseJobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(null)
  const [applyModal, setApplyModal] = useState(null)
  const [coverLetter, setCoverLetter] = useState('')
  const [applying, setApplying] = useState(false)

  // Candidate CV selection state
  const [candidateProfile, setCandidateProfile] = useState(null)
  const [cvOption, setCvOption] = useState('profile') // 'profile' | 'custom'
  const [customFile, setCustomFile] = useState(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [jobsRes, profileRes] = await Promise.allSettled([
        getPublicJobOffers(0, 50),
        getCandidateProfile(),
      ])

      if (jobsRes.status === 'fulfilled') {
        setJobs(jobsRes.value.data)
      } else {
        setError('Failed to load job offers.')
      }

      if (profileRes.status === 'fulfilled') {
        setCandidateProfile(profileRes.value.data)
        if (!profileRes.value.data?.cv_filename) {
          setCvOption('custom')
        }
      }
    } catch {
      setError('Failed to load job offers.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openApplyModal = (job) => {
    setApplyModal(job)
    setCoverLetter('')
    setCustomFile(null)
    if (candidateProfile?.cv_filename) {
      setCvOption('profile')
    } else {
      setCvOption('custom')
    }
  }

  const filtered = jobs.filter(j =>
    j.title?.toLowerCase().includes(search.toLowerCase()) ||
    j.location?.toLowerCase().includes(search.toLowerCase())
  )

  const handleApply = async () => {
    if (!applyModal?.id) {
      toast.error('Invalid job offer.')
      return
    }

    if (cvOption === 'profile' && !candidateProfile?.cv_filename) {
      toast.error('No CV in your profile. Please upload a custom CV or update your profile.')
      return
    }

    if (cvOption === 'custom' && !customFile) {
      toast.error('Please select a custom CV file to upload.')
      return
    }

    setApplying(true)
    try {
      let payload
      if (cvOption === 'custom' && customFile) {
        payload = new FormData()
        payload.append('job_offer_id', applyModal.id)
        if (coverLetter) payload.append('cover_letter', coverLetter)
        payload.append('cv_option', 'custom')
        payload.append('cv_file', customFile)
      } else {
        payload = {
          job_offer_id: applyModal.id,
          cover_letter: coverLetter || null,
          cv_option: 'profile',
        }
      }

      await createApplication(payload)
      toast.success('Application submitted successfully!')
      setApplyModal(null)
      setCoverLetter('')
      setCustomFile(null)
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
        <p className="text-slate-500 text-sm mt-1">Explore open positions and apply with your profile CV or a tailored CV.</p>
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
                onClick={e => { e.stopPropagation(); openApplyModal(job) }}
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
              <button className="btn-primary" onClick={() => { const j = selected; setSelected(null); openApplyModal(j) }}>
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
            {/* CV Selection Section */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Choose Curriculum Vitae (CV)</label>
              <div className="space-y-2.5">
                {/* Option 1: Profile CV */}
                <label className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                  cvOption === 'profile'
                    ? 'border-indigo-600 bg-indigo-50/40 ring-1 ring-indigo-600'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}>
                  <input
                    type="radio"
                    name="cv_option"
                    value="profile"
                    checked={cvOption === 'profile'}
                    onChange={() => setCvOption('profile')}
                    className="mt-1 text-indigo-600 focus:ring-indigo-500"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-medium text-slate-800">Use Profile CV</span>
                      {candidateProfile?.cv_filename && (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      )}
                    </div>
                    {candidateProfile?.cv_filename ? (
                      <div className="flex items-center gap-1.5 text-xs text-slate-600 mt-1 bg-white border border-slate-200 px-2.5 py-1.5 rounded-lg">
                        <FileText className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                        <span className="truncate font-mono">{candidateProfile.cv_filename}</span>
                      </div>
                    ) : (
                      <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                        No CV in profile yet. Upload a custom CV below or add one in My Profile.
                      </p>
                    )}
                  </div>
                </label>

                {/* Option 2: Custom CV */}
                <label className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                  cvOption === 'custom'
                    ? 'border-indigo-600 bg-indigo-50/40 ring-1 ring-indigo-600'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}>
                  <input
                    type="radio"
                    name="cv_option"
                    value="custom"
                    checked={cvOption === 'custom'}
                    onChange={() => setCvOption('custom')}
                    className="mt-1 text-indigo-600 focus:ring-indigo-500"
                  />
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-medium text-slate-800">Upload a Custom CV for this offer</span>
                    <p className="text-xs text-slate-500 mt-0.5">Attach a tailored resume specifically for this position</p>

                    {cvOption === 'custom' && (
                      <div className="mt-2.5 pt-2 border-t border-slate-100">
                        <input
                          type="file"
                          accept=".pdf,.doc,.docx,.txt"
                          onChange={e => setCustomFile(e.target.files[0] || null)}
                          className="block w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                        />
                        {customFile && (
                          <div className="flex items-center gap-1 text-xs text-emerald-700 mt-1.5 font-medium">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            Selected: {customFile.name}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Cover Letter <span className="text-slate-400 font-normal">(optional)</span></label>
              <textarea
                className="input-field min-h-[110px] resize-y"
                placeholder="Tell us why you're a great fit for this position..."
                value={coverLetter}
                onChange={e => setCoverLetter(e.target.value)}
              />
            </div>

            <div className="flex justify-end gap-3 pt-1">
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
