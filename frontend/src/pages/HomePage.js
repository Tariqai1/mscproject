/**
 * Home Page - Main prediction interface
 */

import React, { useState } from 'react';
import PredictionForm from '../components/PredictionForm';
import ResultCard from '../components/ResultCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { predictSentiment } from '../utils/api';
import '../styles/pages/HomePage.css';

const HomePage = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePrediction = async (text) => {
    setLoading(true);
    setError('');
    setPrediction(null);

    try {
      const result = await predictSentiment(text);
      setPrediction(result);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Error connecting to the server. Make sure the backend is running on http://localhost:8000'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCopyReview = (text) => {
    navigator.clipboard.writeText(text);
    alert('Review copied to clipboard!');
  };

  return (
    <div className="home-page">
      <div className="container">
        <div className="intro-section">
          <h1>🎭 Advanced Sarcasm-Aware Sentiment Analysis</h1>
          <p>Detect sentiment and sarcasm in e-commerce reviews using AI</p>
        </div>

        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError('')}
          />
        )}

        {loading ? (
          <LoadingSpinner message="🤖 Analyzing review..." />
        ) : (
          <>
            <PredictionForm
              onSubmit={handlePrediction}
              isLoading={loading}
            />

            {prediction && (
              <ResultCard
                prediction={prediction}
                onCopyReview={handleCopyReview}
              />
            )}
          </>
        )}

        <div className="info-section">
          <h2>ℹ️ How it Works</h2>
          <div className="info-grid">
            <div className="info-card">
              <h3>🔍 Sentiment Detection</h3>
              <p>Classifies reviews as Positive, Negative, or Neutral</p>
            </div>
            <div className="info-card">
              <h3>😏 Sarcasm Detection</h3>
              <p>Identifies sarcastic remarks and ironic statements</p>
            </div>
            <div className="info-card">
              <h3>🤖 AI-Powered</h3>
              <p>Uses advanced transformer models (BERT, RoBERTa, LSTM)</p>
            </div>
            <div className="info-card">
              <h3>⚡ Real-Time</h3>
              <p>Instant analysis with confidence scores for each prediction</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
