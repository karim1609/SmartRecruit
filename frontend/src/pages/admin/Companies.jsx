import { useEffect, useState } from 'react'
import { getMyCompanies } from '../../api/companies'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import { Building2 } from 'lucide-react'

export default function AdminCompanies() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      // Admin uses same companies endpoint — in production there would be an admin-specific listing
      // For now, since there's no GET /companies/ admin endpoint, show info notice
      setCompanies([])
    } catch {
      setError('Failed to load companies.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Companies</h1>
        <p className="text-slate-500 text-sm mt-1">Platform company directory.</p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 text-sm text-blue-800">
        <Building2 className="w-5 h-5 text-blue-600 mb-2" />
        <p className="font-medium mb-1">Company directory</p>
        <p className="text-xs text-blue-700">
          A platform-wide company listing endpoint is not yet implemented in the backend.
          Companies can be accessed individually by their ID via <code className="font-mono bg-blue-100 px-1 rounded">GET /companies/&#123;id&#125;</code>.
        </p>
      </div>
    </div>
  )
}

