/**
 * Model Comparison Page - Compare model predictions
 */

import React, { useState } from 'react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import '../styles/pages/ModelComparisonPage.css';

const ModelComparisonPage = () => {
  const [text, setText] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCompare = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please enter a review text');
      return;
    }
    
    if (text.length > 5000) {
      setError('Text is too long (max 5000 characters)');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(
        'http://localhost:8000/api/compare-models',
        { text }
      );
      setComparison(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to compare models');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Comparing models..." />;
  }

  return (
    <div className="model-comparison-page">
      <div className="container">
        <h1>🔬 Model Comparison Tool</h1>
        <p className="subtitle">Compare predictions from different ML models side-by-side</p>

        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError('')}
          />
        )}

        {/* Input Form */}
        <div className="comparison-form">
          <textarea
            placeholder="Enter a review to compare model predictions..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={loading}
            rows={4}
            maxLength={5000}
            className="comparison-input"
          />
          
          <div className="form-actions">
            <button
              onClick={handleCompare}
              className="compare-btn"
              disabled={loading || !text.trim()}
            >
              {loading ? '⏳ Comparing...' : '🔄 Compare Models'}
            </button>
            <span className="char-count">{text.length}/5000</span>
          </div>
        </div>

        {/* Comparison Results */}
        {comparison && (
          <div className="comparison-results">
            {/* Analysis Summary */}
            <div className="analysis-summary">
              <div className="summary-card">
                <h3>📊 Agreement</h3>
                <p className="summary-value">{comparison.analysis?.agreement || 'N/A'}</p>
              </div>
              <div className="summary-card">
                <h3>📈 Confidence</h3>
                <p className="summary-value">{comparison.analysis?.confidence_level || 'N/A'}</p>
              </div>
              <div className="summary-card">
                <h3>🎭 Sarcasm</h3>
                <p className="summary-value">{comparison.analysis?.sarcasm_indicator || 'N/A'}</p>
              </div>
              <div className="summary-card">
                <h3>🏆 Recommended</h3>
                <p className="summary-value">{comparison.recommended || 'N/A'}</p>
              </div>
            </div>

            {/* Models Comparison Table */}
            <div className="models-comparison">
              <h2>Model Predictions</h2>
              <div className="comparison-grid">
                {Object.entries(comparison.models || {}).map(([key, model], idx) => (
                  <div key={idx} className="model-card">
                    <div className="model-header">
                      <h3>{key.replace(/_/g, ' ').toUpperCase()}</h3>
                      <span className="model-type">{model.model_type || 'Model'}</span>
                    </div>

                    <div className="model-predictioncomparison-grid">
                      <div className="prediction-row">
                        <label>Sentiment:</label>
                        <div className="sentiment-value">
                          <strong>{model.sentiment}</strong>
                          <div className="score-bar">
                            <div 
                              className="score-fill"
                              style={{
                                width: `${(model.sentiment_score || 0) * 100}%`,
                                backgroundColor: model.sentiment === 'Positive' ? '#51CF66' : 
                                               model.sentiment === 'Negative' ? '#FF6B6B' : '#4ECDC4'
                              }}
                            />
                          </div>
                          <span className="score-text">{((model.sentiment_score || 0) * 100).toFixed(1)}%</span>
                        </div>
                      </div>

                      <div className="prediction-row">
                        <label>Sarcasm:</label>
                        <div className="sarcasm-value">
                          <strong>{model.sarcasm}</strong>
                          <div className="score-bar">
                            <div 
                              className="score-fill"
                              style={{
                                width: `${(model.sarcasm_score || 0) * 100}%`,
                                backgroundColor: model.sarcasm === 'Sarcastic' ? '#FFD93D' : '#A8E6CF'
                              }}
                            />
                          </div>
                          <span className="score-text">{((model.sarcasm_score || 0) * 100).toFixed(1)}%</span>
                        </div>
                      </div>

                      <div className="prediction-row overall">
                        <label>Overall Confidence:</label>
                        <strong>{(((model.sentiment_score || 0) + (model.sarcasm_score || 0)) / 2 * 100).toFixed(1)}%</strong>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Input Review Display */}
            <div className="input-review">
              <h3>📝 Input Review</h3>
              <p>{comparison.text}</p>
            </div>
          </div>
        )}

        {!comparison && !loading && (
          <div className="empty-state">
            <p>👆 Enter a review above to compare model predictions</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelComparisonPage;
