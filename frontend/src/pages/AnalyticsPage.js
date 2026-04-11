/**
 * Analytics Page - Charts and statistics
 */

import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { getStats, exportAsCSV, exportAsJSON, exportAsPDF } from '../utils/api';
import '../styles/pages/AnalyticsPage.css';

const AnalyticsPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      setError(err.message || 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      if (format === 'csv') {
        await exportAsCSV(500);
      } else if (format === 'json') {
        await exportAsJSON(500);
      } else if (format === 'pdf') {
        await exportAsPDF(100);
      }
    } catch (err) {
      setError(`Export failed: ${err.message || 'Unknown error'}`);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading analytics..." />;
  }

  if (!stats) {
    return (
      <div className="analytics-page">
        <div className="container">
          <h1>📊 Analytics</h1>
          <ErrorAlert
            message={error}
            onClose={() => setError('')}
          />
          <div className="empty-state">
            <p>No data available yet. Make some predictions first!</p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare data for charts
  const sentimentData = [
    { name: 'Positive', value: stats.sentiment_distribution?.positive || 0, fill: '#51CF66' },
    { name: 'Neutral', value: stats.sentiment_distribution?.neutral || 0, fill: '#4ECDC4' },
    { name: 'Negative', value: stats.sentiment_distribution?.negative || 0, fill: '#FF6B6B' }
  ];

  const sarcasmData = [
    { name: 'Sarcastic', value: stats.sarcasm_distribution?.sarcasm_detected || 0, fill: '#FFD93D' },
    { name: 'Non-Sarcastic', value: stats.sarcasm_distribution?.non_sarcasm || 0, fill: '#A8E6CF' }
  ];

  return (
    <div className="analytics-page">
      <div className="container">
        <div className="analytics-header">
          <h1>📊 Analytics & Statistics</h1>
          <div className="header-actions">
            <button onClick={fetchStats} className="action-btn" disabled={exporting}>
              🔄 Refresh
            </button>
            <div className="export-buttons">
              <button 
                onClick={() => handleExport('csv')} 
                className="export-btn csv-btn"
                disabled={exporting}
                title="Export as CSV"
              >
                📄 CSV
              </button>
              <button 
                onClick={() => handleExport('json')} 
                className="export-btn json-btn"
                disabled={exporting}
                title="Export as JSON"
              >
                ⚙️ JSON
              </button>
              <button 
                onClick={() => handleExport('pdf')} 
                className="export-btn pdf-btn"
                disabled={exporting}
                title="Export as PDF"
              >
                📑 PDF
              </button>
            </div>
          </div>
        </div>

        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError('')}
          />
        )}

        {/* Summary Cards */}
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-value">{stats.total_predictions}</div>
            <div className="stat-label">Total Predictions</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.sarcasm_percentage?.toFixed(1)}%</div>
            <div className="stat-label">Sarcasm Detected</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#51CF66' }}>
              {stats.sentiment_distribution?.positive || 0}
            </div>
            <div className="stat-label">😊 Positive Reviews</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#FF6B6B' }}>
              {stats.sentiment_distribution?.negative || 0}
            </div>
            <div className="stat-label">😞 Negative Reviews</div>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-grid">
          {/* Sentiment Distribution */}
          <div className="chart-container">
            <h3>Sentiment Distribution</h3>
            {stats.sentiment_distribution && (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Sarcasm Distribution */}
          <div className="chart-container">
            <h3>Sarcasm Detection</h3>
            {stats.sarcasm_distribution && (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={sarcasmData}
                  margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8">
                    {sarcasmData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="analysis-info">
          <h3>📈 Key Insights</h3>
          <ul>
            <li>Total predictions analyzed: <strong>{stats.total_predictions}</strong></li>
            <li>Sarcasm detection rate: <strong>{stats.sarcasm_percentage?.toFixed(1)}%</strong></li>
            <li>Most common sentiment: <strong>
              {stats.sentiment_distribution?.positive > stats.sentiment_distribution?.negative ? 'Positive' : 'Negative'}
            </strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
