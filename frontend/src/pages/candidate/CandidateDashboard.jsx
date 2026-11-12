import { useEffect, useState } from 'react'
import { FileText, Clock, Eye, CheckCircle, XCircle } from 'lucide-react'
import { getDashboard } from '../../api/dashboard'
import StatCard from '../../components/common/StatCard'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS = ['#f59e0b', '#3b82f6', '#22c55e', '#ef4444']

export default function CandidateDashboard() {
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
    { name: 'Pending', value: stats.pending || 0 },
    { name: 'Reviewing', value: stats.reviewing || 0 },
    { name: 'Accepted', value: stats.accepted || 0 },
    { name: 'Rejected', value: stats.rejected || 0 },
  ].filter(d => d.value > 0)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">
          Welcome back{profile.full_name ? `, ${profile.full_name}` : ''}!
        </h1>
        <p className="text-slate-500 text-sm mt-1">Here's your application overview.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText} label="Total Applications" value={stats.total_applications} color="indigo" />
        <StatCard icon={Clock} label="Pending" value={stats.pending} color="amber" />
        <StatCard icon={Eye} label="Reviewing" value={stats.reviewing} color="blue" />
        <StatCard icon={CheckCircle} label="Accepted" value={stats.accepted} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {chartData.length > 0 && (
          <div className="card p-5">
            <h2 className="text-sm font-semibold text-slate-700 mb-4">Application Status Breakdown</h2>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={chartData} cx="50%" cy="50%" outerRadius={75} dataKey="value" label>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Recent Applications</h2>
          {data?.recent_applications?.length ? (
            <div className="space-y-3">
              {data.recent_applications.map((app) => (
                <div key={app.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                  <div>
                    <p className="text-sm text-slate-700 font-medium truncate">
                      Job ID: {app.job_offer_id?.slice(-8)}
                    </p>
                    <p className="text-xs text-slate-400">
                      {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : ''}
                    </p>
                  </div>
                  <StatusBadge status={app.status} />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-8">No applications yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}

