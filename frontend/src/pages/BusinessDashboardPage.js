import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import '../styles/pages/BusinessDashboardPage.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const BusinessDashboardPage = () => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [singleResult, setSingleResult] = useState(null);

  const loadDashboard = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/business/dashboard`);
      setDashboard(res.data);
    } catch (e) { setError('Failed to load dashboard'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  const analyzeReview = async () => {
    if (!reviewText.trim()) return;
    try {
      const res = await axios.post(`${API}/business/analyze-review`, { text: reviewText });
      setSingleResult(res.data);
    } catch (e) { setError('Analysis failed'); }
  };

  const riskColors = { Low: '#51CF66', Medium: '#FFA94D', High: '#FF6B6B', Critical: '#E03131', 'No Data': '#868E96' };

  const renderStars = (rating) => {
    const full = Math.floor(rating);
    const half = rating - full >= 0.5;
    return (
      <span className="stars">
        {'★'.repeat(full)}{half ? '½' : ''}{'☆'.repeat(5 - full - (half ? 1 : 0))}
        <span className="star-value">{rating}</span>
      </span>
    );
  };

  if (loading) return <LoadingSpinner message="Loading Business Intelligence..." />;

  return (
    <div className="business-dashboard-page">
      <div className="container">
        <div className="page-header">
          <h1>📊 Business Intelligence Dashboard</h1>
          <p className="subtitle">AI-powered insights for business decision making</p>
          <button className="refresh-btn" onClick={loadDashboard}>🔄 Refresh</button>
        </div>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        {dashboard && (
          <>
            {/* KPI Cards */}
            <div className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-icon">📝</div>
                <div className="kpi-value">{dashboard.summary?.total_reviews || 0}</div>
                <div className="kpi-label">Total Reviews</div>
              </div>
              <div className="kpi-card satisfaction">
                <div className="kpi-icon">😊</div>
                <div className="kpi-value">{dashboard.summary?.avg_satisfaction || 0}%</div>
                <div className="kpi-label">Avg Satisfaction</div>
                <div className="kpi-bar">
                  <div style={{width: `${dashboard.summary?.avg_satisfaction || 0}%`, backgroundColor: '#51CF66'}} />
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon">⭐</div>
                <div className="kpi-value">{renderStars(dashboard.summary?.avg_rating || 0)}</div>
                <div className="kpi-label">Avg Rating</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon">🎭</div>
                <div className="kpi-value">{dashboard.summary?.sarcasm_rate || 0}%</div>
                <div className="kpi-label">Sarcasm Rate</div>
              </div>
              <div className="kpi-card" style={{borderColor: riskColors[dashboard.summary?.risk_level]}}>
                <div className="kpi-icon">⚠️</div>
                <div className="kpi-value" style={{color: riskColors[dashboard.summary?.risk_level]}}>{dashboard.summary?.risk_level}</div>
                <div className="kpi-label">Risk Level</div>
              </div>
            </div>

            {/* Sentiment Breakdown */}
            <div className="section-row">
              <div className="section-card sentiment-breakdown">
                <h3>📈 Sentiment Breakdown</h3>
                <div className="sentiment-bars">
                  <div className="sent-bar-row">
                    <span className="sent-label">👍 Positive</span>
                    <div className="sent-bar-track"><div className="sent-bar-fill positive" style={{width: `${dashboard.summary?.positive_rate || 0}%`}} /></div>
                    <span className="sent-pct">{dashboard.summary?.positive_rate || 0}%</span>
                  </div>
                  <div className="sent-bar-row">
                    <span className="sent-label">😐 Neutral</span>
                    <div className="sent-bar-track"><div className="sent-bar-fill neutral" style={{width: `${dashboard.summary?.neutral_rate || 0}%`}} /></div>
                    <span className="sent-pct">{dashboard.summary?.neutral_rate || 0}%</span>
                  </div>
                  <div className="sent-bar-row">
                    <span className="sent-label">👎 Negative</span>
                    <div className="sent-bar-track"><div className="sent-bar-fill negative" style={{width: `${dashboard.summary?.negative_rate || 0}%`}} /></div>
                    <span className="sent-pct">{dashboard.summary?.negative_rate || 0}%</span>
                  </div>
                </div>
              </div>

              <div className="section-card market-sentiment">
                <h3>📉 Market Sentiment</h3>
                <div className="market-info">
                  <div className="market-trend">
                    <span className={`trend-icon ${dashboard.market_sentiment?.trend}`}>
                      {dashboard.market_sentiment?.trend === 'improving' ? '📈' : dashboard.market_sentiment?.trend === 'declining' ? '📉' : '➡️'}
                    </span>
                    <span className="trend-text">{dashboard.market_sentiment?.trend?.toUpperCase()}</span>
                  </div>
                  <div className="momentum">
                    <span>Momentum: </span>
                    <strong style={{color: (dashboard.market_sentiment?.momentum || 0) >= 0 ? '#51CF66' : '#FF6B6B'}}>
                      {(dashboard.market_sentiment?.momentum || 0) >= 0 ? '+' : ''}{dashboard.market_sentiment?.momentum || 0}
                    </strong>
                  </div>
                </div>
              </div>
            </div>

            {/* Rating Distribution */}
            <div className="section-card rating-distribution">
              <h3>⭐ Rating Distribution</h3>
              <div className="rating-bars">
                {[5, 4, 3, 2, 1].map(star => {
                  const count = dashboard.rating_distribution?.[`${star}_star`] || 0;
                  const total = dashboard.summary?.total_reviews || 1;
                  const pct = ((count / total) * 100).toFixed(0);
                  return (
                    <div key={star} className="rating-bar-row">
                      <span className="rating-label">{star} ★</span>
                      <div className="rating-bar-track">
                        <div className="rating-bar-fill" style={{width: `${pct}%`}} />
                      </div>
                      <span className="rating-count">{count} ({pct}%)</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Top Issues */}
            {dashboard.top_issues?.length > 0 && (
              <div className="section-card top-issues">
                <h3>🔥 Top Customer Issues</h3>
                <div className="issues-list">
                  {dashboard.top_issues.map((issue, i) => (
                    <div key={i} className="issue-item">
                      <span className="issue-rank">#{i + 1}</span>
                      <span className="issue-name">{issue.issue}</span>
                      <span className="issue-count">{issue.count} mentions</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Satisfaction Trend */}
            {dashboard.satisfaction_trend?.length > 0 && (
              <div className="section-card trend-chart">
                <h3>📈 Satisfaction Trend</h3>
                <div className="mini-chart">
                  {dashboard.satisfaction_trend.map((pt, i) => (
                    <div key={i} className="chart-bar-wrapper">
                      <div className="chart-bar" style={{height: `${pt.score}%`, backgroundColor: pt.score >= 60 ? '#51CF66' : pt.score >= 40 ? '#FFA94D' : '#FF6B6B'}} />
                      <span className="chart-label">{pt.index}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Analyze */}
            <div className="section-card quick-analyze">
              <h3>🔍 Quick Business Analysis</h3>
              <div className="quick-input-row">
                <textarea
                  placeholder="Enter a review for business analysis..."
                  value={reviewText}
                  onChange={(e) => setReviewText(e.target.value)}
                  rows={3}
                />
                <button onClick={analyzeReview} disabled={!reviewText.trim()}>Analyze</button>
              </div>
              {singleResult && (
                <div className="quick-result">
                  <div className="quick-metrics">
                    <div className="qm"><span>Satisfaction</span><strong>{singleResult.satisfaction_score}%</strong></div>
                    <div className="qm"><span>Predicted Rating</span><strong>{renderStars(singleResult.predicted_rating)}</strong></div>
                    <div className="qm"><span>Sentiment</span><strong>{singleResult.sentiment}</strong></div>
                    <div className="qm"><span>Sarcasm</span><strong>{singleResult.sarcasm}</strong></div>
                    <div className="qm"><span>Emotion</span><strong>{singleResult.dominant_emotion}</strong></div>
                    {singleResult.risk_flag && <div className="qm risk"><span>⚠️ Risk Flag</span><strong>Yes</strong></div>}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {(!dashboard || dashboard.summary?.total_reviews === 0) && !loading && (
          <div className="empty-state">
            <h3>No data yet</h3>
            <p>Analyze some reviews on the Home page first, then come back here for business insights.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BusinessDashboardPage;
