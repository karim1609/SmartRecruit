import api from './axios'

export const getCandidateProfile = () => api.get('/candidates/me')
export const updateCandidateProfile = (data) => api.patch('/candidates/me', data)

