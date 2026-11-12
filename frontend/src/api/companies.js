import api from './axios'

export const createCompany = (data) => api.post('/companies/', data)
export const getMyCompanies = () => api.get('/companies/me')
export const getCompany = (id) => api.get(`/companies/${id}`)
export const updateCompany = (id, data) => api.patch(`/companies/${id}`, data)

