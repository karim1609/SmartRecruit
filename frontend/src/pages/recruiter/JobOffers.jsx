import { useEffect, useState } from 'react'
import { getMyJobOffers, createJobOffer, updateJobOffer, deleteJobOffer } from '../../api/jobOffers'
import { getMyCompanies } from '../../api/companies'
import Loading from '../../components/common/Loading'
import ErrorMessage from '../../components/common/ErrorMessage'
import Modal from '../../components/common/Modal'
import StatusBadge from '../../components/common/StatusBadge'
import toast from 'react-hot-toast'
import { Briefcase, Plus, Pencil, Trash2, X } from 'lucide-react'

const emptyForm = { title: '', company_id: '', description: '', required_skills: [], min_experience: 0, location: '', status: 'open' }

export default function RecruiterJobOffers() {
  const [jobs, setJobs] = useState([])
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [skillInput, setSkillInput] = useState('')
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [jobsRes, compRes] = await Promise.all([getMyJobOffers(), getMyCompanies()])
      setJobs(jobsRes.data)
      setCompanies(compRes.data)
    } catch {
      setError('Failed to load job offers.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setForm({ ...emptyForm, company_id: companies[0]?.id || '' })
    setSkillInput('')
    setModal('create')
  }

  const openEdit = (j) => {
    setForm({
      title: j.title || '',
      company_id: j.company_id || '',
      description: j.description || '',
      required_skills: j.required_skills || [],
      min_experience: j.min_experience ?? 0,
      location: j.location || '',
      status: j.status || 'open',
    })
    setSkillInput('')
    setModal({ editing: j })
  }

  const addSkill = () => {
    const s = skillInput.trim()
    if (s && !form.required_skills.includes(s)) {
      setForm({ ...form, required_skills: [...form.required_skills, s] })
      setSkillInput('')
    }
  }

  const handleSave = async () => {
    if (!form.company_id) { toast.error('Select a company first.'); return }
    setSaving(true)
    try {
      const payload = { ...form, min_experience: parseInt(form.min_experience) || 0 }
      if (modal === 'create') {
        await createJobOffer(payload)
        toast.success('Job offer created!')
      } else {
        const { company_id, ...updatePayload } = payload
        await updateJobOffer(modal.editing.id, updatePayload)
        toast.success('Job offer updated!')
      }
      setModal(null)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this job offer?')) return
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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Job Offers</h1>
          <p className="text-slate-500 text-sm mt-1">Manage your job postings.</p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2" disabled={companies.length === 0}>
          <Plus className="w-4 h-4" /> New Job Offer
        </button>
      </div>

      {companies.length === 0 && !loading && (
        <div className="bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded-lg px-4 py-3 mb-4">
          You need to create a company before posting job offers.
        </div>
      )}

      {jobs.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-40" />
          <p>No job offers yet.</p>
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
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {jobs.map(job => (
                <tr key={job.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">{job.title}</td>
                  <td className="px-4 py-3 text-slate-500">{job.location || '—'}</td>
                  <td className="px-4 py-3"><StatusBadge status={job.status} /></td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{job.created_at ? new Date(job.created_at).toLocaleDateString() : '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(job)} className="p-1.5 rounded hover:bg-indigo-50 text-indigo-600">
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => handleDelete(job.id)} className="p-1.5 rounded hover:bg-red-50 text-red-500">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <Modal title={modal === 'create' ? 'Create Job Offer' : 'Edit Job Offer'} onClose={() => setModal(null)} size="xl">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Title <span className="text-red-500">*</span></label>
                <input className="input-field" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required />
              </div>
              {modal === 'create' && (
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Company <span className="text-red-500">*</span></label>
                  <select className="input-field" value={form.company_id} onChange={e => setForm({ ...form, company_id: e.target.value })}>
                    {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
              )}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Description <span className="text-red-500">*</span></label>
                <textarea className="input-field min-h-[100px] resize-y" value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Location <span className="text-red-500">*</span></label>
                <input className="input-field" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Min Experience (years)</label>
                <input type="number" min={0} className="input-field" value={form.min_experience}
                  onChange={e => setForm({ ...form, min_experience: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
                <select className="input-field" value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                  <option value="open">Open</option>
                  <option value="draft">Draft</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Required Skills</label>
                <div className="flex flex-wrap gap-1 mb-1.5">
                  {form.required_skills.map(s => (
                    <span key={s} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-xs">
                      {s}
                      <button type="button" onClick={() => setForm({ ...form, required_skills: form.required_skills.filter(x => x !== s) })}>
                        <X className="w-2.5 h-2.5" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input className="input-field flex-1 text-xs" placeholder="Add skill" value={skillInput}
                    onChange={e => setSkillInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addSkill())} />
                  <button type="button" onClick={addSkill} className="btn-secondary px-2 text-xs">Add</button>
                </div>
              </div>
            </div>
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

