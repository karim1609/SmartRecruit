import { useEffect, useState } from 'react'
import { getDashboard } from '../../api/dashboard'
import StatCard from '../../components/common/StatCard'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import { Users, Building2, Briefcase, FileText, UserCheck, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function AdminDashboard() {
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

  const appChart = [
    { name: 'Pending', value: stats.pending_applications || 0 },
    { name: 'Accepted', value: stats.accepted_applications || 0 },
    { name: 'Rejected', value: stats.rejected_applications || 0 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Admin Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Platform-wide overview.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Users" value={stats.total_users} color="indigo" />
        <StatCard icon={UserCheck} label="Active Users" value={stats.active_users} color="green" />
        <StatCard icon={Building2} label="Companies" value={stats.total_companies} color="violet" />
        <StatCard icon={Briefcase} label="Job Offers" value={stats.total_jobs} color="blue" />
        <StatCard icon={TrendingUp} label="Open Jobs" value={stats.open_jobs} color="green" />
        <StatCard icon={FileText} label="Applications" value={stats.total_applications} color="indigo" />
        <StatCard icon={Users} label="Candidates" value={stats.total_candidates} color="blue" />
        <StatCard icon={Users} label="Recruiters" value={stats.total_recruiters} color="violet" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Application Status</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={appChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Recent Users</h2>
          {data?.recent_users?.length ? (
            <div className="space-y-2">
              {data.recent_users.map(u => (
                <div key={u.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                  <div>
                    <p className="text-sm text-slate-700 font-medium">{u.email}</p>
                    <p className="text-xs text-slate-400">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</p>
                  </div>
                  <StatusBadge status={u.role} />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-8">No users yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}

