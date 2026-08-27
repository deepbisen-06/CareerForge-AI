import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './lib/auth';
import { ThemeProvider } from './lib/theme';
import { DashboardLayout } from './layouts/DashboardLayout';

import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { AgentWorkspace } from './pages/AgentWorkspace';
import { AgentRunsHistory } from './pages/AgentRunsHistory';
import { ProfileWizard } from './pages/ProfileWizard';
import { ResumeStudio } from './pages/ResumeStudio';
import { InternshipExplorer } from './pages/InternshipExplorer';
import { InternshipDetail } from './pages/InternshipDetail';
import { SavedJobs } from './pages/SavedJobs';
import { SkillGapRoadmap } from './pages/SkillGapRoadmap';
import { TailoredDocuments } from './pages/TailoredDocuments';
import { InterviewPrep } from './pages/InterviewPrep';
import { MockInterview } from './pages/MockInterview';
import { ApplicationTracker } from './pages/ApplicationTracker';
import { CareerChat } from './pages/CareerChat';
import { AdminDashboard } from './pages/AdminDashboard';

const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({
  children,
  adminOnly = false
}) => {
  const { token, user, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/workspace" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Landing Page */}
            <Route path="/" element={<Landing />} />

            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Dashboard Routes */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              {/* Primary Autonomous Agent Routes */}
              <Route path="/dashboard" element={<AgentWorkspace />} />
              <Route path="/workspace" element={<AgentWorkspace />} />
              <Route path="/agent-runs" element={<AgentRunsHistory />} />
              <Route path="/classic-dashboard" element={<Dashboard />} />

              {/* Opportunities & Applications */}
              <Route path="/internships" element={<InternshipExplorer />} />
              <Route path="/internships/:id" element={<InternshipDetail />} />
              <Route path="/saved-jobs" element={<SavedJobs />} />
              <Route path="/applications" element={<ApplicationTracker />} />

              {/* Secondary Career Intelligence Tools */}
              <Route path="/profile-wizard" element={<ProfileWizard />} />
              <Route path="/resume-studio" element={<ResumeStudio />} />
              <Route path="/skill-gaps" element={<SkillGapRoadmap />} />
              <Route path="/documents" element={<TailoredDocuments />} />
              <Route path="/interview-prep" element={<InterviewPrep />} />
              <Route path="/mock-interview" element={<MockInterview />} />
              <Route path="/chat" element={<CareerChat />} />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute adminOnly>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
