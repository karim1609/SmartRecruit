import api from './axios'

export const matchCandidates = (jobId, topK = 5) =>
  api.get(`/matching/job/${jobId}`, { params: { top_k: topK } })

export const getMatchingHealth = () => api.get('/matching/health')

