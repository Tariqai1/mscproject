import React, { useState } from 'react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import '../styles/pages/EmotionBreakdownPage.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const EmotionBreakdownPage = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('single'); // single | batch
  const [batchTexts, setBatchTexts] = useState('');

  const handleAnalyze = async () => {
    if (!text.trim()) { setError('Please enter a review'); return; }
    setLoading(true); setError('');
    try {
      const res = await axios.post(`${API}/emotions`, { text });
      setResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || 'Analysis failed'); }
    finally { setLoading(false); }
  };

  const handleBatch = async () => {
    const lines = batchTexts.split('\n').filter(l => l.trim());
    if (!lines.length) { setError('Enter at least one review'); return; }
    setLoading(true); setError('');
    try {
      const res = await axios.post(`${API}/emotions/batch`, { texts: lines });
      setResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || 'Batch analysis failed'); }
    finally { setLoading(false); }
  };

  const renderEmotionBar = (name, data) => (
    <div className="emotion-row" key={name}>
      <div className="emotion-label">
        <span className="emotion-emoji">{data.emoji}</span>
        <span className="emotion-name">{name.charAt(0).toUpperCase() + name.slice(1)}</span>
      </div>
      <div className="emotion-bar-track">
        <div
          className="emotion-bar-fill"
          style={{ width: `${data.score * 100}%`, backgroundColor: data.color }}
        />
      </div>
      <span className="emotion-score">{(data.score * 100).toFixed(0)}%</span>
      <span className={`emotion-intensity ${data.intensity}`}>{data.intensity}</span>
      {data.triggers?.length > 0 && (
        <div className="emotion-triggers">
          {data.triggers.map((t, i) => <span key={i} className="trigger-tag">{t}</span>)}
        </div>
      )}
    </div>
  );

  if (loading) return <LoadingSpinner message="Analyzing emotions..." />;

  return (
    <div className="emotion-breakdown-page">
      <div className="container">
        <div className="page-header">
          <h1>🎭 Emotion Breakdown</h1>
          <p className="subtitle">Fine-grained emotion analysis beyond simple positive/negative</p>
        </div>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        <div className="mode-toggle">
          <button className={mode === 'single' ? 'active' : ''} onClick={() => setMode('single')}>Single Review</button>
          <button className={mode === 'batch' ? 'active' : ''} onClick={() => setMode('batch')}>Batch Analysis</button>
        </div>

        {mode === 'single' ? (
          <div className="input-section">
            <textarea
              placeholder="Enter a review to analyze emotions..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              maxLength={5000}
            />
            <div className="input-actions">
              <button onClick={handleAnalyze} disabled={!text.trim()}>🔍 Analyze Emotions</button>
              <span className="char-count">{text.length}/5000</span>
            </div>
          </div>
        ) : (
          <div className="input-section">
            <textarea
              placeholder="Enter reviews (one per line)..."
              value={batchTexts}
              onChange={(e) => setBatchTexts(e.target.value)}
              rows={6}
            />
            <div className="input-actions">
              <button onClick={handleBatch}>📊 Batch Analyze</button>
              <span className="char-count">{batchTexts.split('\n').filter(l=>l.trim()).length} reviews</span>
            </div>
          </div>
        )}

        {/* Single result */}
        {result && result.emotions && !result.results && (
          <div className="result-section">
            <div className="dominant-card">
              <span className="dominant-emoji">{result.dominant_emoji}</span>
              <div>
                <h3>Dominant Emotion</h3>
                <p className="dominant-name">{result.dominant_emotion?.charAt(0).toUpperCase() + result.dominant_emotion?.slice(1)}</p>
                <p className="dominant-score">{(result.dominant_score * 100).toFixed(0)}% intensity</p>
              </div>
              <div className="meta-badges">
                <span className={`badge sentiment-${result.sentiment?.toLowerCase()}`}>{result.sentiment}</span>
                <span className={`badge sarcasm-${result.sarcasm === 'Sarcastic' ? 'yes' : 'no'}`}>{result.sarcasm}</span>
              </div>
            </div>

            <div className="emotion-chart">
              <h3>📊 Emotion Scores</h3>
              {Object.entries(result.emotions)
                .sort(([,a],[,b]) => b.score - a.score)
                .map(([name, data]) => renderEmotionBar(name, data))}
            </div>
          </div>
        )}

        {/* Batch result */}
        {result && result.results && (
          <div className="batch-result-section">
            <div className="aggregate-card">
              <h3>📊 Aggregate Emotions ({result.total} reviews)</h3>
              <div className="aggregate-grid">
                {Object.entries(result.aggregate || {}).sort(([,a],[,b])=>b-a).map(([emotion, score]) => (
                  <div key={emotion} className="agg-item">
                    <span className="agg-name">{emotion}</span>
                    <div className="agg-bar-track">
                      <div className="agg-bar-fill" style={{width: `${score * 100}%`}} />
                    </div>
                    <span className="agg-score">{(score * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="batch-list">
              {result.results.map((r, i) => (
                <div key={i} className="batch-item">
                  <p className="batch-text">"{r.text}"</p>
                  <span className="batch-dominant">{r.dominant_emoji} {r.dominant_emotion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmotionBreakdownPage;
