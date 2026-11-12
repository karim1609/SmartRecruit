import { useEffect, useState } from 'react'
import { getUsers, updateUserStatus } from '../../api/users'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import StatusBadge from '../../components/common/StatusBadge'
import toast from 'react-hot-toast'
import { Users, ChevronLeft, ChevronRight, ToggleLeft, ToggleRight } from 'lucide-react'

export default function AdminUsers() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const limit = 20

  const load = async (p = 0) => {
    setLoading(true)
    setError('')
    try {
      const res = await getUsers(p * limit, limit)
      setUsers(res.data)
    } catch {
      setError('Failed to load users.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(page) }, [page])

  const toggleStatus = async (user) => {
    const newStatus = !user.is_active
    try {
      await updateUserStatus(user.id, newStatus)
      toast.success(`User ${newStatus ? 'activated' : 'deactivated'}.`)
      load(page)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed.')
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={() => load(page)} />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Users</h1>
        <p className="text-slate-500 text-sm mt-1">Manage registered users.</p>
      </div>

      {users.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <Users className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No users found.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Email</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Role</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Joined</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-800 font-medium">{u.email}</td>
                  <td className="px-4 py-3"><StatusBadge status={u.role} /></td>
                  <td className="px-4 py-3">
                    <StatusBadge status={u.is_active ? 'active' : 'inactive'} />
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggleStatus(u)}
                      className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-lg transition-colors ${
                        u.is_active
                          ? 'bg-red-50 text-red-600 hover:bg-red-100'
                          : 'bg-green-50 text-green-600 hover:bg-green-100'
                      }`}
                    >
                      {u.is_active ? (
                        <><ToggleRight className="w-3.5 h-3.5" /> Deactivate</>
                      ) : (
                        <><ToggleLeft className="w-3.5 h-3.5" /> Activate</>
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 bg-slate-50">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              className="flex items-center gap-1 text-sm text-slate-600 disabled:opacity-40 hover:text-indigo-600"
            >
              <ChevronLeft className="w-4 h-4" /> Previous
            </button>
            <span className="text-xs text-slate-400">Page {page + 1}</span>
            <button
              disabled={users.length < limit}
              onClick={() => setPage(p => p + 1)}
              className="flex items-center gap-1 text-sm text-slate-600 disabled:opacity-40 hover:text-indigo-600"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

