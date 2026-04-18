import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import BatchPredictPage from './pages/BatchPredictPage';
import ModelComparisonPage from './pages/ModelComparisonPage';
import TimeSeriesAnalyticsPage from './pages/TimeSeriesAnalyticsPage';
import EmotionBreakdownPage from './pages/EmotionBreakdownPage';
import BusinessDashboardPage from './pages/BusinessDashboardPage';
import AutoMLPage from './pages/AutoMLPage';
import SocialMediaPage from './pages/SocialMediaPage';
import ExplainableAIPage from './pages/ExplainableAIPage';
import './App.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Load theme preference from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.setAttribute('data-theme', 'dark');
    } else if (savedTheme === 'light') {
      setIsDarkMode(false);
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      // Use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
  }, []);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
  };

  return (
    <Router>
      <div className="App">
        <Header isDarkMode={isDarkMode} toggleTheme={toggleTheme} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/timeline" element={<TimeSeriesAnalyticsPage />} />
            <Route path="/batch" element={<BatchPredictPage />} />
            <Route path="/compare" element={<ModelComparisonPage />} />
            <Route path="/emotions" element={<EmotionBreakdownPage />} />
            <Route path="/business" element={<BusinessDashboardPage />} />
            <Route path="/automl" element={<AutoMLPage />} />
            <Route path="/social" element={<SocialMediaPage />} />
            <Route path="/explain" element={<ExplainableAIPage />} />
          </Routes>
        </main>
        <footer className="app-footer">
          <p>© 2026 Sarcasm-Aware Sentiment Analysis System | MSc IT Project</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
