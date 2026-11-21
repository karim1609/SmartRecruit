export default function StatCard({ icon: Icon, label, value, color = 'indigo', sub }) {
  const styles = {
    indigo: {
      bg: 'bg-indigo-50 border-indigo-100 text-indigo-600',
      glow: 'group-hover:border-indigo-200',
    },
    green: {
      bg: 'bg-emerald-50 border-emerald-100 text-emerald-600',
      glow: 'group-hover:border-emerald-200',
    },
    amber: {
      bg: 'bg-amber-50 border-amber-100 text-amber-600',
      glow: 'group-hover:border-amber-200',
    },
    red: {
      bg: 'bg-rose-50 border-rose-100 text-rose-600',
      glow: 'group-hover:border-rose-200',
    },
    blue: {
      bg: 'bg-blue-50 border-blue-100 text-blue-600',
      glow: 'group-hover:border-blue-200',
    },
    violet: {
      bg: 'bg-violet-50 border-violet-100 text-violet-600',
      glow: 'group-hover:border-violet-200',
    },
  }

  const theme = styles[color] || styles.indigo

  return (
    <div className={`card p-5 group relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5 ${theme.glow}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</p>
          <p className="text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
            {value ?? '0'}
          </p>
          {sub && <p className="text-xs text-slate-500 mt-1 font-medium">{sub}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl border ${theme.bg} shadow-2xs group-hover:scale-110 transition-transform duration-200`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  )
}
