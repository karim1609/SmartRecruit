import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to their role-appropriate dashboard
    if (user.role === 'candidate') return <Navigate to="/candidate/dashboard" replace />
    if (user.role === 'recruiter') return <Navigate to="/recruiter/dashboard" replace />
    if (user.role === 'admin') return <Navigate to="/admin/dashboard" replace />
  }

  return children
}

