import api from './axios'

export const login = (data) => api.post('/auth/login', data)
export const register = (data) => api.post('/auth/register', data)
export const verifyEmail = (data) => api.post('/auth/verify-email', data)
export const resendVerification = (data) => api.post('/auth/resend-verification', data)
export const getMe = () => api.get('/auth/me')


