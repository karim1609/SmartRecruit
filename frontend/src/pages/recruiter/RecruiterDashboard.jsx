import { useEffect, useState } from 'react'
import { getDashboard } from '../../api/dashboard'
import StatCard from '../../components/common/StatCard'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import { Briefcase, FileText, CheckCircle, Clock, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function RecruiterDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getDashboard()
      setData(res.data)
    } catch {
      setError('Failed to load dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  const stats = data?.statistics || {}
  const profile = data?.profile || {}

  const chartData = [
    { name: 'Total', value: stats.total_jobs || 0 },
    { name: 'Open', value: stats.open_jobs || 0 },
    { name: 'Closed', value: stats.closed_jobs || 0 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">
          Welcome{profile.full_name ? `, ${profile.full_name}` : ''}!
        </h1>
        <p className="text-slate-500 text-sm mt-1">Your recruitment activity overview.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard icon={Briefcase} label="Total Jobs" value={stats.total_jobs} color="indigo" />
        <StatCard icon={TrendingUp} label="Open Jobs" value={stats.open_jobs} color="green" />
        <StatCard icon={FileText} label="Total Applications" value={stats.total_applications} color="blue" />
        <StatCard icon={Clock} label="Pending Apps" value={stats.pending_applications} color="amber" />
        <StatCard icon={CheckCircle} label="Accepted" value={stats.accepted_applications} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Job Status Overview</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Recent Job Offers</h2>
          {data?.recent_jobs?.length ? (
            <div className="space-y-3">
              {data.recent_jobs.map(job => (
                <div key={job.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-slate-700">{job.title}</p>
                    <p className="text-xs text-slate-400">{job.location}</p>
                  </div>
                  <StatusBadge status={job.status} />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-8">No job offers yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}

