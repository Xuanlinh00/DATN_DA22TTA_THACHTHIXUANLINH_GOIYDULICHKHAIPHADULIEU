import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import DestinationsPage from './pages/DestinationsPage';
import DestinationDetailPage from './pages/DestinationDetailPage';
import RecommendPage from './pages/RecommendPage';
import AdminPage from './pages/AdminPage';
import ChatbotWidget from './components/ChatbotWidget';
import ThemeSwitcher from './components/ThemeSwitcher';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/destinations" element={<DestinationsPage />} />
            <Route path="/destinations/:name" element={<DestinationDetailPage />} />
            <Route path="/recommend" element={<RecommendPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </main>
        <ChatbotWidget />
        <ThemeSwitcher />
      </div>
    </Router>
  );
}

export default App;
