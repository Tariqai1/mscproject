import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import '../styles/pages/SocialMediaPage.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const SocialMediaPage = () => {
  const [query, setQuery] = useState('');
  const [platform, setPlatform] = useState('twitter');
  const [count, setCount] = useState(20);
  const [result, setResult] = useState(null);
  const [trending, setTrending] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => { loadTrending(); }, []);

  useEffect(() => {
    let interval;
    if (autoRefresh && query) {
      interval = setInterval(() => { handleSearch(); }, 15000);
    }
    return () => clearInterval(interval);
    // eslint-disable-next-line
  }, [autoRefresh, query, platform]);

  const loadTrending = async () => {
    try {
      const res = await axios.get(`${API}/social/trending`);
      setTrending(res.data);
    } catch (e) { /* ignore */ }
  };

  const handleSearch = async () => {
    if (!query.trim()) { setError('Enter a search query'); return; }
    setLoading(true); setError('');
    try {
      const res = await axios.post(`${API}/social/analyze`, { query, platform, count });
      setResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || 'Analysis failed'); }
    finally { setLoading(false); }
  };

  const sentimentIcon = (s) => s === 'Positive' ? '🟢' : s === 'Negative' ? '🔴' : '🟡';
  const platformIcons = { twitter: '🐦', reddit: '🤖', instagram: '📸', news: '📰' };

  return (
    <div className="social-media-page">
      <div className="container">
        <div className="page-header">
          <h1>📡 Real-Time Social Media Analyzer</h1>
          <p className="subtitle">Live sentiment tracking across social platforms</p>
        </div>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        {/* Search Bar */}
        <div className="search-section">
          <div className="search-row">
            <input
              type="text"
              placeholder="Search product, brand, or topic..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="search-input"
            />
            <div className="platform-selector">
              {Object.entries(platformIcons).map(([p, icon]) => (
                <button
                  key={p}
                  className={`platform-btn ${platform === p ? 'active' : ''}`}
                  onClick={() => setPlatform(p)}
                  title={p}
                >
                  {icon}
                </button>
              ))}
            </div>
            <select value={count} onChange={(e) => setCount(Number(e.target.value))} className="count-select">
              <option value={10}>10 posts</option>
              <option value={20}>20 posts</option>
              <option value={30}>30 posts</option>
              <option value={50}>50 posts</option>
            </select>
            <button onClick={handleSearch} className="search-btn" disabled={loading}>
              {loading ? '⏳' : '🔍'} Analyze
            </button>
          </div>
          <div className="search-options">
            <label className="auto-refresh-toggle">
              <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
              <span>Auto-refresh (15s)</span>
            </label>
            {autoRefresh && <span className="live-indicator">● LIVE</span>}
          </div>
        </div>

        {loading && !result && <LoadingSpinner message="Analyzing social media..." />}

        {/* Results */}
        {result && (
          <div className="results-section">
            {/* Stats Overview */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{result.stats?.total_posts}</div>
                <div className="stat-label">Posts Analyzed</div>
              </div>
              <div className="stat-card positive">
                <div className="stat-value">{result.stats?.positive_rate}%</div>
                <div className="stat-label">🟢 Positive</div>
              </div>
              <div className="stat-card negative">
                <div className="stat-value">{(100 - result.stats?.positive_rate - (result.stats?.total_posts ? (result.stats?.neutral / result.stats?.total_posts * 100) : 0)).toFixed(1)}%</div>
                <div className="stat-label">🔴 Negative</div>
              </div>
              <div className="stat-card sarcasm">
                <div className="stat-value">{result.stats?.sarcasm_rate}%</div>
                <div className="stat-label">🎭 Sarcasm</div>
              </div>
              <div className="stat-card trending">
                <div className="stat-value">{result.trending_score}</div>
                <div className="stat-label">🔥 Trending Score</div>
              </div>
            </div>

            {/* Sentiment Timeline */}
            {result.sentiment_timeline?.length > 0 && (
              <div className="timeline-section">
                <h3>📈 Sentiment Over Time</h3>
                <div className="timeline-chart">
                  {result.sentiment_timeline.map((bucket, i) => (
                    <div key={i} className="timeline-bar-group">
                      <div className="stacked-bar">
                        <div className="bar-pos" style={{height: `${(bucket.positive / bucket.total) * 120}px`}} title={`Positive: ${bucket.positive}`} />
                        <div className="bar-neu" style={{height: `${(bucket.neutral / bucket.total) * 120}px`}} title={`Neutral: ${bucket.neutral}`} />
                        <div className="bar-neg" style={{height: `${(bucket.negative / bucket.total) * 120}px`}} title={`Negative: ${bucket.negative}`} />
                      </div>
                      <span className="timeline-label">{bucket.period}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Live Feed */}
            <div className="live-feed">
              <h3>📱 Live Feed — "{result.query}" on {platformIcons[result.platform]} {result.platform}</h3>
              <div className="feed-list">
                {result.posts?.map((post, i) => (
                  <div key={i} className={`feed-card ${post.sarcasm === 'Sarcastic' ? 'sarcastic' : ''}`}>
                    <div className="feed-header">
                      <span className="feed-author">{post.author}</span>
                      <span className="feed-time">{post.minutes_ago}m ago</span>
                      <span className="feed-platform">{post.platform_icon}</span>
                    </div>
                    <p className="feed-text">{post.text}</p>
                    <div className="feed-meta">
                      <span className="feed-sentiment">{sentimentIcon(post.sentiment)} {post.sentiment}</span>
                      {post.sarcasm === 'Sarcastic' && <span className="feed-sarcasm">🎭 Sarcastic</span>}
                      <span className="feed-engagement">❤️ {post.likes} · 🔄 {post.shares}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Trending Topics */}
        {trending && (
          <div className="trending-section">
            <h3>🔥 Trending Topics</h3>
            <div className="trending-grid">
              {trending.trending?.slice(0, 8).map((topic, i) => (
                <div
                  key={i}
                  className="trending-card"
                  onClick={() => { setQuery(topic.topic); }}
                >
                  <div className="trending-rank">#{topic.rank}</div>
                  <div className="trending-info">
                    <h4>{topic.topic}</h4>
                    <div className="trending-meta">
                      <span>{sentimentIcon(topic.sentiment)} {topic.sentiment}</span>
                      <span>📊 {(topic.mention_count / 1000).toFixed(1)}K mentions</span>
                      <span className={`trend-badge ${topic.trend}`}>
                        {topic.trend === 'rising' ? '📈' : topic.trend === 'declining' ? '📉' : '➡️'} {topic.trend}
                      </span>
                    </div>
                    <div className="trending-sarcasm">🎭 {topic.sarcasm_rate}% sarcasm</div>
                  </div>
                  <div className={`change-badge ${topic.change_24h >= 0 ? 'up' : 'down'}`}>
                    {topic.change_24h >= 0 ? '+' : ''}{topic.change_24h}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialMediaPage;
