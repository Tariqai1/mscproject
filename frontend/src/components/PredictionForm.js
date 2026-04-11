/**
 * Prediction Form Component
 */

import React, { useState, useEffect, useRef } from 'react';
import { predictSentiment } from '../utils/api';
import '../styles/PredictionForm.css';

const PredictionForm = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [livePrediction, setLivePrediction] = useState(null);
  const [liveLoading, setLiveLoading] = useState(false);
  const [showLivePreview, setShowLivePreview] = useState(false);
  const debounceTimeoutRef = useRef(null);

  // Real-time prediction with debouncing
  useEffect(() => {
    // Clear previous timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    if (text.length >= 10 && text.length <= 5000) {
      setLiveLoading(true);
      
      // Debounce: wait 800ms after user stops typing
      debounceTimeoutRef.current = setTimeout(async () => {
        try {
          const result = await predictSentiment(text);
          setLivePrediction(result);
          setShowLivePreview(true);
        } catch (err) {
          // Silently fail - don't interrupt user
          setLivePrediction(null);
        } finally {
          setLiveLoading(false);
        }
      }, 800);
    } else {
      setShowLivePreview(false);
      setLivePrediction(null);
    }

    // Cleanup on unmount
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [text]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate input
    if (!text.trim()) {
      setError('Please enter a review text');
      return;
    }
    
    if (text.length > 5000) {
      setError('Text is too long (max 5000 characters)');
      return;
    }
    
    setError('');
    onSubmit(text);
  };

  return (
    <div className="prediction-form-container">
      <div className="form-card">
        <h2>📝 Enter Your Review</h2>
        <p className="description">
          Paste an e-commerce review and our AI will detect sentiment and sarcasm
        </p>
        
        <form onSubmit={handleSubmit}>
          <textarea
            className="review-input"
            placeholder="Enter your review here... e.g., 'This product is amazing... for a doorstop!'"
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={isLoading}
            rows={6}
            maxLength={5000}
          />
          
          <div className="form-footer">
            <span className="char-count">
              {text.length}/5000
            </span>
            
            <button
              type="submit"
              className="submit-btn"
              disabled={isLoading || !text.trim()}
            >
              {isLoading ? '⏳ Analyzing...' : '🚀 Analyze'}
            </button>
          </div>
        </form>
        
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* Live Preview */}
        {showLivePreview && livePrediction && !isLoading && (
          <div className="live-preview">
            <div className="live-preview-header">
              💡 Live Preview
              {liveLoading && <span className="live-loading">Updating...</span>}
            </div>
            <div className="live-preview-content">
              <div className="live-item">
                <span className="label">Sentiment:</span>
                <span className={`badge sentiment-${livePrediction.sentiment_label.toLowerCase()}`}>
                  {livePrediction.sentiment_label}
                </span>
              </div>
              <div className="live-item">
                <span className="label">Sarcasm:</span>
                <span className={`badge sarcasm-${livePrediction.sarcasm_label.toLowerCase()}`}>
                  {livePrediction.sarcasm_label}
                </span>
              </div>
              <div className="live-item">
                <span className="label">Confidence:</span>
                <span className="confidence">{(livePrediction.overall_confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="examples">
        <h3>💡 Example Reviews:</h3>
        <ul>
          <li>"Amazing quality and fast delivery!" (Positive)</li>
          <li>"Terrible product, broke immediately" (Negative)</li>
          <li>"Yeah, this is great... for a doorstop!" (Sarcastic)</li>
          <li>"It's okay, nothing special" (Neutral)</li>
        </ul>
      </div>
    </div>
  );
};

export default PredictionForm;
