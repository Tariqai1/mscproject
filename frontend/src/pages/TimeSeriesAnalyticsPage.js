/**
 * Time-Series Analytics Page
 * Displays historical trends and analytics over time
 */

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { fetchTimelineAnalytics } from '../utils/api';
import '../styles/TimeSeriesAnalyticsPage.css';

const TimeSeriesAnalyticsPage = () => {
  const [data, setData] = useState(null);
  const [period, setPeriod] = useState('daily');
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchTimelineAnalytics(period, days);
      setData(result.data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [period, days]);

  const handleRefresh = () => {
    loadAnalytics();
  };

  const handlePeriodChange = (e) => {
    setPeriod(e.target.value);
  };

  const handleDaysChange = (e) => {
    setDays(parseInt(e.target.value));
  };

  return (
    <div className="time-series-page">
      <div className="page-header">
        <h1>📊 Time-Series Analytics</h1>
        <p>Track sentiment and sarcasm trends over time</p>
      </div>

      {/* Controls */}
      <div className="analytics-controls">
        <div className="control-group">
          <label htmlFor="period-select">Time Period:</label>
          <select id="period-select" value={period} onChange={handlePeriodChange}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="days-select">Lookback Days:</label>
          <select id="days-select" value={days} onChange={handleDaysChange}>
            <option value={7}>Last 7 Days</option>
            <option value={14}>Last 14 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={60}>Last 60 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>
        </div>

        <button className="refresh-btn" onClick={handleRefresh} disabled={loading}>
          {loading ? '⏳ Loading...' : '🔄 Refresh'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      ) : data && data.timeline && data.timeline.length > 0 ? (
        <div className="analytics-content">
          {/* Summary Stats */}
          <div className="summary-stats">
            <div className="stat-card">
              <div className="stat-label">Total Predictions</div>
              <div className="stat-value">{data.total_predictions}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Period</div>
              <div className="stat-value">{period.charAt(0).toUpperCase() + period.slice(1)}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Lookback</div>
              <div className="stat-value">{days} days</div>
            </div>
          </div>

          {/* Prediction Volume Chart */}
          <div className="chart-container">
            <h2>Prediction Volume Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.timeline}>
                <defs>
                  <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4ECDC4" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#4ECDC4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-primary)', 
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)'
                  }}
                  formatter={(value) => value.toFixed(0)}
                />
                <Area 
                  type="monotone" 
                  dataKey="total_predictions" 
                  stroke="#4ECDC4" 
                  fillOpacity={1} 
                  fill="url(#colorVolume)" 
                  name="Predictions"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment Breakdown Chart */}
          <div className="chart-container">
            <h2>Sentiment Distribution Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-primary)', 
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)'
                  }}
                  formatter={(value) => value.toFixed(0)}
                />
                <Legend />
                <Area type="monotone" dataKey="positive_count" stackId="1" stroke="#51CF66" fill="#51CF66" name="Positive" />
                <Area type="monotone" dataKey="neutral_count" stackId="1" stroke="#FFD93D" fill="#FFD93D" name="Neutral" />
                <Area type="monotone" dataKey="negative_count" stackId="1" stroke="#FF6B6B" fill="#FF6B6B" name="Negative" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Sarcasm Trend Chart */}
          <div className="chart-container">
            <h2>Sarcasm Detection Trend</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-primary)', 
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)'
                  }}
                  formatter={(value) => value.toFixed(1)}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="sarcasm_count" 
                  stroke="#FFD93D" 
                  name="Sarcasm Count"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="sarcasm_percentage" 
                  stroke="#FF6B6B" 
                  name="Sarcasm %" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Confidence Score Trend */}
          <div className="chart-container">
            <h2>Average Sentiment Confidence Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-primary)', 
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)'
                  }}
                  formatter={(value) => value.toFixed(3)}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="avg_sentiment_confidence" 
                  stroke="#4ECDC4" 
                  name="Avg Confidence"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Per-period Statistics Table */}
          <div className="stats-table-container">
            <h2>Detailed Statistics by Period</h2>
            <div className="table-wrapper">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Total</th>
                    <th>Positive</th>
                    <th>Neutral</th>
                    <th>Negative</th>
                    <th>Sarcasm</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {data.timeline.map((entry, idx) => (
                    <tr key={idx} className="stat-row">
                      <td className="date-cell">{entry.date}</td>
                      <td className="number-cell">{entry.total_predictions}</td>
                      <td className="positive-cell">{entry.positive_count}</td>
                      <td className="neutral-cell">{entry.neutral_count}</td>
                      <td className="negative-cell">{entry.negative_count}</td>
                      <td className="sarcasm-cell">{entry.sarcasm_count}</td>
                      <td className="confidence-cell">
                        <div className="confidence-badge">
                          {(entry.avg_sentiment_confidence * 100).toFixed(1)}%
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <p>📭 No analytics data available yet</p>
          <p>Make some predictions to see trends over time!</p>
        </div>
      )}
    </div>
  );
};

export default TimeSeriesAnalyticsPage;
