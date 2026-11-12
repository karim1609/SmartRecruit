import api from './axios'

export const getRecruiterProfile = () => api.get('/recruiters/me')
export const updateRecruiterProfile = (data) => api.patch('/recruiters/me', data)

