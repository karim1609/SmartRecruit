import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './routes/ProtectedRoute'

// Layouts
import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'

// Auth pages
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'

// Candidate pages
import CandidateDashboard from './pages/candidate/CandidateDashboard'
import CandidateProfile from './pages/candidate/CandidateProfile'
import BrowseJobs from './pages/candidate/BrowseJobs'
import MyApplications from './pages/candidate/MyApplications'

// Recruiter pages
import RecruiterDashboard from './pages/recruiter/RecruiterDashboard'
import RecruiterProfile from './pages/recruiter/RecruiterProfile'
import RecruiterCompanies from './pages/recruiter/Companies'
import RecruiterJobOffers from './pages/recruiter/JobOffers'
import RecruiterApplications from './pages/recruiter/Applications'
import Matching from './pages/recruiter/Matching'

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminUsers from './pages/admin/Users'
import AdminCompanies from './pages/admin/Companies'
import AdminJobOffers from './pages/admin/JobOffers'
import AdminApplications from './pages/admin/Applications'

import NotFound from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: { fontSize: '14px' },
          }}
        />
        <Routes>
          {/* Public auth routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Candidate routes */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['candidate']}>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/candidate/dashboard" element={<CandidateDashboard />} />
            <Route path="/candidate/profile" element={<CandidateProfile />} />
            <Route path="/candidate/jobs" element={<BrowseJobs />} />
            <Route path="/candidate/applications" element={<MyApplications />} />
          </Route>

          {/* Recruiter routes */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['recruiter']}>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/recruiter/dashboard" element={<RecruiterDashboard />} />
            <Route path="/recruiter/profile" element={<RecruiterProfile />} />
            <Route path="/recruiter/companies" element={<RecruiterCompanies />} />
            <Route path="/recruiter/jobs" element={<RecruiterJobOffers />} />
            <Route path="/recruiter/applications" element={<RecruiterApplications />} />
            <Route path="/recruiter/matching" element={<Matching />} />
          </Route>

          {/* Admin routes */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/companies" element={<AdminCompanies />} />
            <Route path="/admin/jobs" element={<AdminJobOffers />} />
            <Route path="/admin/applications" element={<AdminApplications />} />
          </Route>

          {/* Root redirect */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
