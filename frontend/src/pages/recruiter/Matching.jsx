import { useEffect, useState } from 'react'
import { getMyJobOffers } from '../../api/jobOffers'
import { matchCandidates, getMatchingHealth } from '../../api/matching'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import toast from 'react-hot-toast'
import { BrainCircuit, AlertCircle, Zap } from 'lucide-react'

export default function Matching() {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [jobsLoading, setJobsLoading] = useState(true)
  const [serviceStatus, setServiceStatus] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const init = async () => {
      setJobsLoading(true)
      try {
        const [jobsRes, healthRes] = await Promise.allSettled([
          getMyJobOffers(),
          getMatchingHealth()
        ])
        if (jobsRes.status === 'fulfilled') setJobs(jobsRes.value.data)
        if (healthRes.status === 'fulfilled') setServiceStatus(healthRes.value.data)
      } catch {}
      setJobsLoading(false)
    }
    init()
  }, [])

  const handleMatch = async () => {
    if (!selectedJob) { toast.error('Select a job offer.'); return }
    setLoading(true)
    setError('')
    setResults(null)
    try {
      const res = await matchCandidates(selectedJob, topK)
      setResults(res.data)
    } catch (err) {
      const msg = err.response?.data?.detail || 'AI matching service is unavailable.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  if (jobsLoading) return <Loading />

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <BrainCircuit className="w-6 h-6 text-indigo-600" />
          <h1 className="text-2xl font-bold text-slate-800">AI Candidate Matching</h1>
        </div>
        <p className="text-slate-500 text-sm">Find the most relevant candidates for your job offer using semantic AI matching.</p>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-amber-800">AI Matching — Beta</p>
          <p className="text-xs text-amber-700 mt-0.5">
            The semantic matching service requires Sentence Transformers and Qdrant to be fully operational.
            This feature is under active development.
          </p>
        </div>
      </div>

      <div className="card p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Select Job Offer</label>
          <select
            className="input-field"
            value={selectedJob}
            onChange={e => setSelectedJob(e.target.value)}
          >
            <option value="">— Choose a job offer —</option>
            {jobs.map(j => (
              <option key={j.id} value={j.id}>{j.title} ({j.status})</option>
            ))}
          </select>
          {jobs.length === 0 && (
            <p className="text-xs text-slate-400 mt-1">No job offers found. Create one first.</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Top K Candidates</label>
          <input
            type="number"
            min={1}
            max={20}
            className="input-field w-32"
            value={topK}
            onChange={e => setTopK(parseInt(e.target.value) || 5)}
          />
        </div>

        <button
          onClick={handleMatch}
          disabled={loading || !selectedJob}
          className="btn-primary flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          {loading ? 'Matching...' : 'Find Matching Candidates'}
        </button>
      </div>

      {loading && <Loading text="Running AI matching..." />}

      {error && (
        <div className="mt-5 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-700">Service Unavailable</p>
            <p className="text-xs text-red-600 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {results && !error && (
        <div className="mt-5 card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-1">
            Results for: <span className="text-indigo-600">{results.job_title}</span>
          </h2>
          <p className="text-xs text-slate-400 mb-4">{results.total_matches} candidates matched</p>

          {results.matches?.length > 0 ? (
            <div className="space-y-3">
              {results.matches.map((match, i) => (
                <div key={i} className="border border-slate-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-slate-800 text-sm">{match.candidate_name || `Candidate ${i + 1}`}</p>
                    {match.score !== undefined && (
                      <span className="text-xs text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full">
                        Score: {(match.score * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  {match.matched_skills?.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {match.matched_skills.map(s => (
                        <span key={s} className="px-2 py-0.5 rounded-full bg-green-50 text-green-700 text-xs">{s}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-6">No matches found.</p>
          )}
        </div>
      )}
    </div>
  )
}

