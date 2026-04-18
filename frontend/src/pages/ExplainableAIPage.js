import React, { useState } from 'react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import '../styles/pages/ExplainableAIPage.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const EXAMPLE_REVIEWS = [
  "Amazing service! Ordered one item, got something completely different. Love surprises",
  "This product is amazing... yeah right 🙄",
  "Great product! Fast delivery and works perfectly.",
  "Oh great, it broke on day one. Best purchase ever!",
  "Terrible quality. Complete waste of money.",
];

const ExplainableAIPage = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showLegend, setShowLegend] = useState(true);

  const handleExplain = async () => {
    if (!text.trim()) { setError('Please enter a review'); return; }
    setLoading(true); setError('');
    try {
      const res = await axios.post(`${API}/explain`, { text });
      setResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || 'Explanation failed'); }
    finally { setLoading(false); }
  };

  const getWordStyle = (word) => {
    if (word.role === 'neutral') return {};
    const opacity = 0.3 + word.importance * 0.7;
    return {
      backgroundColor: word.color,
      opacity: 1,
      padding: '2px 4px',
      borderRadius: '4px',
      color: word.role === 'sarcasm-trigger' ? '#000' : '#fff',
      fontWeight: word.importance > 0.5 ? '700' : '400',
      boxShadow: word.importance > 0.7 ? `0 0 8px ${word.color}` : 'none',
      filter: `saturate(${opacity * 1.5})`,
    };
  };

  if (loading) return <LoadingSpinner message="Generating explanation..." />;

  return (
    <div className="xai-page">
      <div className="container">
        <div className="page-header">
          <h1>🧠 Explainable AI</h1>
          <p className="subtitle">Understand why the model made its prediction — word by word</p>
        </div>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        {/* Input */}
        <div className="input-section">
          <textarea
            placeholder="Enter a review to get a detailed explanation..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            maxLength={5000}
          />
          <div className="input-actions">
            <button onClick={handleExplain} disabled={!text.trim()} className="explain-btn">
              🔍 Explain Prediction
            </button>
            <span className="char-count">{text.length}/5000</span>
          </div>

          <div className="example-reviews">
            <span>Try:</span>
            {EXAMPLE_REVIEWS.map((ex, i) => (
              <button key={i} className="example-btn" onClick={() => setText(ex)}>
                {ex.substring(0, 40)}...
              </button>
            ))}
          </div>
        </div>

        {/* Result */}
        {result && (
          <div className="explanation-result">
            {/* Summary */}
            <div className="summary-card">
              <div className="summary-badges">
                <span className={`badge sentiment-${result.true_sentiment?.toLowerCase()}`}>
                  {result.true_sentiment === 'Positive' ? '👍' : result.true_sentiment === 'Negative' ? '👎' : '😐'} {result.true_sentiment}
                </span>
                <span className={`badge ${result.is_sarcastic ? 'sarcasm-yes' : 'sarcasm-no'}`}>
                  {result.is_sarcastic ? '🎭 Sarcastic' : '✅ Not Sarcastic'}
                </span>
                <span className="badge confidence">
                  🎯 Confidence: {(result.sentiment_confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="summary-text">{result.summary}</p>
            </div>

            {/* Word Highlighting */}
            <div className="word-highlight-section">
              <div className="section-header">
                <h3>🔤 Word-Level Analysis</h3>
                <button className="legend-toggle" onClick={() => setShowLegend(!showLegend)}>
                  {showLegend ? 'Hide' : 'Show'} Legend
                </button>
              </div>

              {showLegend && (
                <div className="legend">
                  {result.legend?.map((item, i) => (
                    <div key={i} className="legend-item">
                      <span className="legend-color" style={{backgroundColor: item.color}} />
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="highlighted-text">
                {result.words?.map((word, i) => (
                  <span
                    key={i}
                    className={`word-token ${word.role}`}
                    style={getWordStyle(word)}
                    title={`${word.role} (importance: ${(word.importance * 100).toFixed(0)}%)`}
                  >
                    {word.word}
                  </span>
                ))}
              </div>
            </div>

            {/* Importance Chart */}
            <div className="importance-section">
              <h3>📊 Word Importance Scores</h3>
              <div className="importance-chart">
                {result.words
                  ?.filter(w => w.importance > 0.2)
                  .sort((a, b) => b.importance - a.importance)
                  .slice(0, 15)
                  .map((word, i) => (
                    <div key={i} className="importance-row">
                      <span className="imp-word">{word.word}</span>
                      <div className="imp-bar-track">
                        <div
                          className="imp-bar-fill"
                          style={{
                            width: `${word.importance * 100}%`,
                            backgroundColor: word.color || '#4ECDC4'
                          }}
                        />
                      </div>
                      <span className="imp-score">{(word.importance * 100).toFixed(0)}%</span>
                      <span className={`imp-role ${word.role}`}>{word.role}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Decision Flow */}
            <div className="decision-flow">
              <h3>🔀 Decision Flow</h3>
              <div className="flow-steps">
                <div className="flow-step">
                  <div className="flow-icon">📝</div>
                  <div className="flow-content">
                    <h4>Input Text</h4>
                    <p>"{result.text?.substring(0, 80)}{result.text?.length > 80 ? '...' : ''}"</p>
                  </div>
                </div>
                <div className="flow-arrow">→</div>
                <div className="flow-step">
                  <div className="flow-icon">🔍</div>
                  <div className="flow-content">
                    <h4>Surface Sentiment</h4>
                    <p>{result.sentiment} ({(result.sentiment_confidence * 100).toFixed(0)}%)</p>
                  </div>
                </div>
                <div className="flow-arrow">→</div>
                <div className="flow-step">
                  <div className="flow-icon">🎭</div>
                  <div className="flow-content">
                    <h4>Sarcasm Check</h4>
                    <p>{result.sarcasm} ({(result.sarcasm_confidence * 100).toFixed(0)}%)</p>
                  </div>
                </div>
                <div className="flow-arrow">→</div>
                <div className={`flow-step final ${result.true_sentiment?.toLowerCase()}`}>
                  <div className="flow-icon">✅</div>
                  <div className="flow-content">
                    <h4>True Sentiment</h4>
                    <p><strong>{result.true_sentiment}</strong></p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Instruction */}
        {!result && !loading && (
          <div className="info-section">
            <div className="info-card">
              <h3>🧪 How Explainable AI Works</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-icon" style={{color: '#51CF66'}}>■</span>
                  <div>
                    <h4>Green = Positive Signal</h4>
                    <p>Words expressing approval, satisfaction, praise</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="info-icon" style={{color: '#FF6B6B'}}>■</span>
                  <div>
                    <h4>Red = Negative Signal</h4>
                    <p>Words expressing criticism, problems, complaints</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="info-icon" style={{color: '#FFD93D'}}>■</span>
                  <div>
                    <h4>Yellow = Sarcasm Trigger</h4>
                    <p>Words/phrases that indicate ironic or sarcastic intent</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="info-icon" style={{color: '#FFA94D'}}>■</span>
                  <div>
                    <h4>Orange = Ironic Positive</h4>
                    <p>Positive words used sarcastically (context flips meaning)</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="info-icon" style={{color: '#748FFC'}}>■</span>
                  <div>
                    <h4>Blue = Negation</h4>
                    <p>Words like "not", "never" that flip sentiment of nearby words</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExplainableAIPage;
