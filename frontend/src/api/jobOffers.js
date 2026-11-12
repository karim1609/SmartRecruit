import api from './axios'

export const getPublicJobOffers = (skip = 0, limit = 20) =>
  api.get('/job-offers/', { params: { skip, limit } })

export const getMyJobOffers = () => api.get('/job-offers/my')

export const getJobOffer = (id) => api.get(`/job-offers/${id}`)

export const createJobOffer = (data) => api.post('/job-offers/', data)

export const updateJobOffer = (id, data) => api.patch(`/job-offers/${id}`, data)

export const deleteJobOffer = (id) => api.delete(`/job-offers/${id}`)

