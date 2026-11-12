import { useEffect, useState } from 'react'
import { getMyCompanies, createCompany, updateCompany } from '../../api/companies'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import Modal from '../../components/common/Modal'
import toast from 'react-hot-toast'
import { Building2, Plus, Pencil, Globe, MapPin } from 'lucide-react'

const emptyForm = { name: '', description: '', industry: '', website: '', location: '', size: '' }

export default function RecruiterCompanies() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modal, setModal] = useState(null) // 'create' | { editing: company }
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getMyCompanies()
      setCompanies(res.data)
    } catch {
      setError('Failed to load companies.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => { setForm(emptyForm); setModal('create') }
  const openEdit = (c) => {
    setForm({ name: c.name || '', description: c.description || '', industry: c.industry || '', website: c.website || '', location: c.location || '', size: c.size || '' })
    setModal({ editing: c })
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      if (modal === 'create') {
        await createCompany(form)
        toast.success('Company created!')
      } else {
        await updateCompany(modal.editing.id, form)
        toast.success('Company updated!')
      }
      setModal(null)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={load} />

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Companies</h1>
          <p className="text-slate-500 text-sm mt-1">Manage your companies.</p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Company
        </button>
      </div>

      {companies.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <Building2 className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No companies yet. Create your first one!</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {companies.map(c => (
            <div key={c.id} className="card p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                    <Building2 className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800 text-sm">{c.name}</h3>
                    <p className="text-xs text-slate-400">{c.industry}</p>
                  </div>
                </div>
                <button onClick={() => openEdit(c)} className="p-1.5 rounded hover:bg-slate-100 text-slate-500">
                  <Pencil className="w-3.5 h-3.5" />
                </button>
              </div>
              <p className="text-xs text-slate-500 line-clamp-2 mb-3">{c.description}</p>
              <div className="flex flex-wrap gap-3 text-xs text-slate-400">
                {c.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{c.location}</span>}
                {c.website && <span className="flex items-center gap-1"><Globe className="w-3 h-3" />{c.website}</span>}
              </div>
            </div>
          ))}
        </div>
      )}

      {modal && (
        <Modal
          title={modal === 'create' ? 'Create Company' : 'Edit Company'}
          onClose={() => setModal(null)}
          size="lg"
        >
          <div className="space-y-4">
            {['name', 'description', 'industry', 'website', 'location', 'size'].map(field => (
              <div key={field}>
                <label className="block text-sm font-medium text-slate-700 mb-1 capitalize">{field.replace('_', ' ')}
                  {['name', 'description', 'industry', 'location'].includes(field) && <span className="text-red-500 ml-0.5">*</span>}
                </label>
                {field === 'description' ? (
                  <textarea
                    className="input-field min-h-[80px] resize-y"
                    value={form[field]}
                    onChange={e => setForm({ ...form, [field]: e.target.value })}
                    required
                  />
                ) : (
                  <input
                    className="input-field"
                    value={form[field]}
                    onChange={e => setForm({ ...form, [field]: e.target.value })}
                    required={['name', 'industry', 'location'].includes(field)}
                  />
                )}
              </div>
            ))}
            <div className="flex justify-end gap-3 pt-2">
              <button className="btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

