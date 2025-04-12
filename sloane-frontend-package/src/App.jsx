// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import HomePage from './pages/landing/HomePage';
import LoginPage from './pages/auth/LoginPage';
import SignupPage from './pages/auth/SignupPage';
import SignupRedirect from './components/redirects/SignupRedirect';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import OnboardingPage from './pages/onboarding/OnboardingPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import ErrorBoundary from './utils/ErrorHandling';
import NetworkStatusIndicator from './components/common/NetworkStatusIndicator';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ErrorBoundary>
          <React.Fragment>
            <NetworkStatusIndicator />
            <Routes>
              <Route path="/" element={<Layout />}>
                {/* Public routes */}
                <Route index element={<HomePage />} />
                <Route path="login" element={<LoginPage />} />
                <Route path="signup" element={<SignupRedirect />} />
                <Route path="forgot-password" element={<ForgotPasswordPage />} />
                <Route path="reset-password/:token" element={<ResetPasswordPage />} />
                
                {/* Make onboarding public for easier access */}
                <Route path="onboarding" element={<OnboardingPage />} />
                <Route 
                  path="dashboard/*" 
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Fallback route */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </React.Fragment>
        </ErrorBoundary>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
