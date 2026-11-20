import api from './axios'

export const getCandidateProfile = () => api.get('/candidates/me')
export const updateCandidateProfile = (data) => api.patch('/candidates/me', data)

export const uploadCandidateCV = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/candidates/me/cv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const downloadCandidateCV = () =>
  api.get('/candidates/me/cv', { responseType: 'blob' })

export const deleteCandidateCV = () => api.delete('/candidates/me/cv')
