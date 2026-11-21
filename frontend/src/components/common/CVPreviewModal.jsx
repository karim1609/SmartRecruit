import { useEffect, useState } from 'react'
import { X, Download, FileText, ExternalLink, Loader2 } from 'lucide-react'
import { downloadApplicationCV } from '../../api/applications'
import { downloadBlob } from '../../utils/download'
import toast from 'react-hot-toast'

export default function CVPreviewModal({ application, onClose }) {
  const [pdfUrl, setPdfUrl] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!application?.id) return

    let objectUrl = null
    const loadCV = async () => {
      setLoading(true)
      setError('')
      try {
        const res = await downloadApplicationCV(application.id)
        const blob = new Blob([res.data], { type: 'application/pdf' })
        objectUrl = URL.createObjectURL(blob)
        setPdfUrl(objectUrl)
      } catch (err) {
        setError('Could not load CV preview. Please download the file instead.')
      } finally {
        setLoading(false)
      }
    }

    loadCV()

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [application?.id])

  if (!application) return null

  const handleDownload = async () => {
    try {
      const res = await downloadApplicationCV(application.id)
      downloadBlob(res.data, application.cv_filename || `cv_${application.id.slice(-6)}.pdf`)
      toast.success('CV downloaded.')
    } catch {
      toast.error('Failed to download CV file.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col w-full max-w-5xl h-[88vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800 truncate max-w-md">
                {application.cv_filename || 'Candidate Resume'}
              </h3>
              <p className="text-xs text-slate-400">
                Application #{application.id?.slice(-8)} • Applied: {application.applied_at ? new Date(application.applied_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="btn-secondary py-1.5 px-3 text-xs gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              Download
            </button>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* PDF viewer frame */}
        <div className="flex-1 bg-slate-100 relative">
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/80 z-10">
              <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-2" />
              <p className="text-xs font-semibold text-slate-600">Rendering document preview...</p>
            </div>
          )}

          {error ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <FileText className="w-12 h-12 text-slate-300 mb-3" />
              <p className="text-sm font-semibold text-slate-700">{error}</p>
              <button onClick={handleDownload} className="btn-primary mt-4 text-xs py-2 px-4 gap-1.5">
                <Download className="w-3.5 h-3.5" /> Download File Directly
              </button>
            </div>
          ) : (
            pdfUrl && (
              <iframe
                src={`${pdfUrl}#toolbar=0`}
                title="CV Preview"
                className="w-full h-full border-0"
              />
            )
          )}
        </div>
      </div>
    </div>
  )
}
