import api from './axios'

export const getUsers = (skip = 0, limit = 20) =>
  api.get('/users/', { params: { skip, limit } })

export const getUserById = (userId) => api.get(`/users/${userId}`)

export const updateUserStatus = (userId, isActive) =>
  api.patch(`/users/${userId}/status`, { is_active: isActive })

