import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import DestinationsPage from './pages/DestinationsPage';
import DestinationDetailPage from './pages/DestinationDetailPage';
import RecommendPage from './pages/RecommendPage';
import AdminPage from './pages/AdminPage';
import AdminDashboard from './pages/AdminDashboard';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import ChatbotWidget from './components/ChatbotWidget';
import ThemeSwitcher from './components/ThemeSwitcher';
import WorldMapPage from './pages/WorldMapPage';
import { RecommendationProvider } from './contexts/RecommendationContext';
import { AuthProvider } from './contexts/AuthContext';
import './App.css';

function App() {
  return (
    <HelmetProvider>
      <AuthProvider>
        <Router>
          <RecommendationProvider>
            <div className="App">
              <Navbar />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/destinations" element={<DestinationsPage />} />
                  <Route path="/destinations/:name" element={<DestinationDetailPage />} />
                  <Route path="/map" element={<WorldMapPage />} />
                  <Route path="/recommend" element={<RecommendPage />} />
                  <Route path="/admin" element={<AdminPage />} />
                  <Route path="/admin/dashboard" element={<AdminDashboard />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                  <Route path="/reset-password/:token" element={<ResetPasswordPage />} />
                  <Route path="/change-password" element={<ChangePasswordPage />} />
                </Routes>
              </main>
              <ChatbotWidget />
              <ThemeSwitcher />
            </div>
          </RecommendationProvider>
        </Router>
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
