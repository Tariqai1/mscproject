/**
 * Result Card Component
 */

import React, { useState } from 'react';
import { submitFeedback } from '../utils/api';
import '../styles/ResultCard.css';

const ResultCard = ({ prediction, onCopyReview }) => {
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');

  if (!prediction) return null;

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'Negative':
        return '#FF6B6B'; // Red
      case 'Positive':
        return '#51CF66'; // Green
      default:
        return '#4ECDC4'; // Teal
    }
  };

  const getSarcasmColor = (sarcasm) => {
    return sarcasm === 'Sarcastic' ? '#FFD93D' : '#A8E6CF';
  };

  const handleFeedback = async (sentimentCorrect, sarcasmCorrect) => {
    try {
      await submitFeedback(prediction.id, {
        sentiment_correct: sentimentCorrect,
        sarcasm_correct: sarcasmCorrect,
        comments: feedbackText
      });
      setFeedbackSubmitted(true);
      setTimeout(() => setFeedbackSubmitted(false), 3000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <div className="result-card">
      <div className="result-header">
        <h2>📊 Analysis Result</h2>
        <button
          className="copy-btn"
          onClick={() => onCopyReview(prediction.text)}
          title="Copy original review"
        >
          📋 Copy
        </button>
      </div>

      <div className="original-text">
        <strong>Original Review:</strong>
        <p>{prediction.text}</p>
      </div>

      <div className="results-grid">
        {/* Sentiment Result */}
        <div className="result-item sentiment-result">
          <div className="result-label">Sentiment</div>
          <div className="result-value" style={{ borderColor: getSentimentColor(prediction.sentiment_label) }}>
            {prediction.sentiment_label}
          </div>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${prediction.sentiment_confidence * 100}%`,
                backgroundColor: getSentimentColor(prediction.sentiment_label)
              }}
            />
          </div>
          <div className="confidence-text">
            {(prediction.sentiment_confidence * 100).toFixed(1)}% confidence
          </div>
        </div>

        {/* Sarcasm Result */}
        <div className="result-item sarcasm-result">
          <div className="result-label">Sarcasm Detection</div>
          <div className="result-value" style={{ borderColor: getSarcasmColor(prediction.sarcasm_label) }}>
            {prediction.sarcasm_label}
          </div>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${prediction.sarcasm_confidence * 100}%`,
                backgroundColor: getSarcasmColor(prediction.sarcasm_label)
              }}
            />
          </div>
          <div className="confidence-text">
            {(prediction.sarcasm_confidence * 100).toFixed(1)}% confidence
          </div>
        </div>

        {/* Emotions Detection */}
        {prediction.emotions && (
          <div className="result-item full-width emotions-section">
            <div className="result-label">Detected Emotions</div>
            <div className="emotions-grid">
              {Object.entries(prediction.emotions).map(([emotion, score]) => (
                <div key={emotion} className="emotion-item">
                  <div className="emotion-name">{emotion.charAt(0).toUpperCase() + emotion.slice(1)}</div>
                  <div className="emotion-bar">
                    <div
                      className="emotion-fill"
                      style={{
                        width: `${Math.min(100, score * 100)}%`,
                        backgroundColor: `hsl(${Math.random() * 360}, 70%, 50%)`
                      }}
                    />
                  </div>
                  <div className="emotion-score">{(score * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Final Interpretation */}
        <div className="result-item full-width">
          <div className="result-label">Interpretation</div>
          <div className="interpretation">
            {prediction.interpretation || 'No interpretation available'}
          </div>
        </div>

        {/* Explanation */}
        <div className="result-item full-width">
          <div className="result-label">Explanation</div>
          <div className="explanation">
            {prediction.explanation}
          </div>
        </div>

        {/* Model Info */}
        <div className="result-item full-width">
          <div className="result-label">Model Used</div>
          <div className="model-info">
            {prediction.model || 'Hybrid-Ensemble'}
          </div>
          <div className="overall-confidence">
            Overall Confidence: {(prediction.overall_confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Feedback Section */}
      <div className="feedback-section">
        <h3>Was this analysis correct?</h3>
        <div className="feedback-buttons">
          <button
            className="feedback-btn positive"
            onClick={() => handleFeedback(true, true)}
          >
            ✅ Correct
          </button>
          <button
            className="feedback-btn negative"
            onClick={() => handleFeedback(false, false)}
          >
            ❌ Incorrect
          </button>
        </div>
        
        {feedbackSubmitted && (
          <div className="feedback-success">
            ✅ Thank you! Your feedback helps improve the model.
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultCard;
