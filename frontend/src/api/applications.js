import api from './axios'

export const createApplication = (data) => {
  if (data instanceof FormData) {
    return api.post('/applications/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  }
  return api.post('/applications/', data)
}

export const getMyApplications = (skip = 0, limit = 20) =>
  api.get('/applications/my', { params: { skip, limit } })

export const getReceivedApplications = (skip = 0, limit = 20) =>
  api.get('/applications/received', { params: { skip, limit } })

export const getApplication = (id) => api.get(`/applications/${id}`)

export const updateApplication = (id, data) => api.patch(`/applications/${id}`, data)

export const withdrawApplication = (id) => api.delete(`/applications/${id}`)

export const downloadApplicationCV = (id) =>
  api.get(`/applications/${id}/cv`, { responseType: 'blob' })
