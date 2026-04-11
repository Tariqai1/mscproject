/**
 * History Page - View past predictions
 */

import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { getHistory } from '../utils/api';
import '../styles/pages/HistoryPage.css';

const HistoryPage = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    fetchHistory();
  }, [limit]);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getHistory(limit);
      setPredictions(data.history || data.predictions || []);
    } catch (err) {
      setError(err.message || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentEmoji = (sentiment) => {
    switch (sentiment) {
      case 'Negative':
        return '😞';
      case 'Positive':
        return '😊';
      default:
        return '😐';
    }
  };

  const getSarcasmEmoji = (sarcasm) => {
    return sarcasm === 'Sarcastic' ? '😏' : '✓';
  };

  return (
    <div className="history-page">
      <div className="container">
        <h1>📜 Prediction History</h1>

        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError('')}
          />
        )}

        <div className="history-controls">
          <label>
            Show last:
            <select value={limit} onChange={(e) => setLimit(Number(e.target.value))}>
              <option value={10}>10 predictions</option>
              <option value={25}>25 predictions</option>
              <option value={50}>50 predictions</option>
              <option value={100}>100 predictions</option>
            </select>
          </label>
          <button onClick={fetchHistory} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>

        {loading ? (
          <LoadingSpinner message="Loading history..." />
        ) : predictions.length === 0 ? (
          <div className="empty-state">
            <p>📭 No prediction history yet. Go to Home and make your first prediction!</p>
          </div>
        ) : (
          <div className="history-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Review</th>
                  <th>Sentiment</th>
                  <th>Sarcasm</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred) => (
                  <tr key={pred.id} className="history-row">
                    <td className="id-col">#{pred.id}</td>
                    <td className="text-col">{pred.text?.substring(0, 50)}...</td>
                    <td className="sentiment-col">
                      {getSentimentEmoji(pred.sentiment_label)} {pred.sentiment_label}
                    </td>
                    <td className="sarcasm-col">
                      {getSarcasmEmoji(pred.sarcasm_label)} {pred.sarcasm_label}
                    </td>
                    <td className="timestamp-col">
                      {new Date(pred.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
