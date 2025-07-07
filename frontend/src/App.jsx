import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './components/Login';
import VADashboard from './pages/VADashboard';
import AdminDashboard from './pages/AdminDashboard';
import TimeLog from './pages/TimeLog';
import EODReport from './pages/EODReport';
import Trainings from './pages/Trainings';
import SOPs from './pages/SOPs';
import LeaveRequests from './pages/LeaveRequests';
import Announcements from './pages/Announcements';
import ManageUsers from './pages/ManageUsersSimple';
import './App.css';

const AppContent = () => {
  const { user, logout, isAuthenticated, isAdmin } = useAuth();

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <Layout userRole={user?.role} onLogout={logout}>
      <Routes>
        {/* Redirect based on user role */}
        <Route 
          path="/" 
          element={
            <Navigate to={isAdmin ? "/dashboard" : "/dashboard"} replace />
          } 
        />
        
        {/* Common Routes for both VA and Admin */}
        <Route path="/dashboard" element={isAdmin ? <AdminDashboard /> : <VADashboard />} />
        <Route path="/time-logs" element={<TimeLog />} />
        <Route path="/eod-reports" element={<EODReport />} />
        <Route path="/trainings" element={<Trainings />} />
        <Route path="/sops" element={<SOPs />} />
        <Route path="/leave-requests" element={<LeaveRequests />} />
        <Route path="/announcements" element={<Announcements />} />
        
        {/* Admin-only Routes */}
        <Route 
          path="/users" 
          element={
            <ProtectedRoute adminOnly>
              <ManageUsers />
            </ProtectedRoute>
          } 
        />
        
        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;




