const statusConfig = {
  pending: { label: 'Pending', cls: 'bg-amber-100 text-amber-700' },
  reviewing: { label: 'Reviewing', cls: 'bg-blue-100 text-blue-700' },
  accepted: { label: 'Accepted', cls: 'bg-green-100 text-green-700' },
  rejected: { label: 'Rejected', cls: 'bg-red-100 text-red-700' },
  open: { label: 'Open', cls: 'bg-green-100 text-green-700' },
  closed: { label: 'Closed', cls: 'bg-slate-100 text-slate-600' },
  draft: { label: 'Draft', cls: 'bg-amber-100 text-amber-700' },
  candidate: { label: 'Candidate', cls: 'bg-blue-100 text-blue-700' },
  recruiter: { label: 'Recruiter', cls: 'bg-violet-100 text-violet-700' },
  admin: { label: 'Admin', cls: 'bg-rose-100 text-rose-700' },
  active: { label: 'Active', cls: 'bg-green-100 text-green-700' },
  inactive: { label: 'Inactive', cls: 'bg-red-100 text-red-700' },
}

export default function StatusBadge({ status }) {
  const cfg = statusConfig[status] || { label: status, cls: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
  )
}

