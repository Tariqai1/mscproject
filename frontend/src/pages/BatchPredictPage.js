/**
 * Batch Predict Page - Bulk predictions
 */

import React, { useState, useRef } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import { batchPredict, uploadFilePredict } from '../utils/api';
import '../styles/pages/BatchPredictPage.css';

const BatchPredictPage = () => {
  const [textInput, setTextInput] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadedFileName, setUploadedFileName] = useState('');
  const fileInputRef = useRef(null);

  const handlePredict = async () => {
    // Parse input (one review per line)
    const texts = textInput
      .split('\n')
      .map(t => t.trim())
      .filter(t => t.length > 0);

    if (texts.length === 0) {
      setError('Please enter at least one review');
      return;
    }

    if (texts.length > 100) {
      setError('Maximum 100 reviews per batch');
      return;
    }

    setLoading(true);
    setError('');
    setPredictions([]);

    try {
      const result = await batchPredict(texts);
      setPredictions(result.predictions || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Batch prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (predictions.length === 0) return;

    const headers = ['Review', 'Sentiment', 'Sarcasm', 'Confidence'];
    const rows = predictions.map(p => [
      `"${p.text.replace(/"/g, '""')}"`,
      p.sentiment_label,
      p.sarcasm_label,
      p.overall_confidence.toFixed(3)
    ]);

    const csv = [headers, ...rows]
      .map(row => row.join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `predictions_${new Date().toISOString()}.csv`;
    a.click();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const validTypes = ['.txt', '.csv'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!validTypes.includes(ext)) {
      setError('Only .txt and .csv files are supported');
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setError('File size exceeds 2MB limit');
      return;
    }

    setUploadedFileName(file.name);
    setLoading(true);
    setError('');
    setPredictions([]);

    try {
      const result = await uploadFilePredict(file);
      setPredictions(result.predictions || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'File upload prediction failed');
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files[0];
    if (file) {
      const fakeEvent = { target: { files: [file] } };
      handleFileUpload(fakeEvent);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  return (
    <div className="batch-predict-page">
      <div className="container">
        <h1>🔄 Batch Prediction</h1>
        <p className="description">Analyze multiple reviews at once</p>

        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError('')}
          />
        )}

        {/* File Upload Section */}
        <div className="file-upload-section">
          <h2>📁 Upload a File</h2>
          <p className="upload-description">Upload a <strong>.txt</strong> (one review per line) or <strong>.csv</strong> file to analyze all reviews</p>
          <div
            className="file-drop-zone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <div className="drop-zone-content">
              <span className="drop-icon">📤</span>
              <p className="drop-text">
                {uploadedFileName
                  ? `Selected: ${uploadedFileName}`
                  : 'Drag & drop your file here or click to browse'}
              </p>
              <span className="drop-hint">Supports .txt and .csv files (max 2MB, 500 reviews)</span>
            </div>
          </div>
        </div>

        <div className="section-divider">
          <span>OR</span>
        </div>

        <div className="batch-input-section">
          <label>Enter reviews (one per line, max 100):</label>
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Enter your reviews here, one per line:&#10;Example 1&#10;Example 2&#10;Example 3"
            rows={10}
            disabled={loading}
            className="batch-textarea"
          />

          <div className="input-footer">
            <span>{textInput.split('\n').filter(t => t.trim()).length} reviews</span>
            <button
              onClick={handlePredict}
              disabled={loading || textInput.trim().length === 0}
              className="predict-btn"
            >
              {loading ? '⏳ Processing...' : '🚀 Analyze'}
            </button>
          </div>
        </div>

        {loading && (
          <LoadingSpinner message="Processing batch..." />
        )}

        {predictions.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h2>✅ Results ({predictions.length} predictions)</h2>
              <button onClick={downloadCSV} className="download-btn">
                📥 Download CSV
              </button>
            </div>

            <div className="results-table">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Review</th>
                    <th>Sentiment</th>
                    <th>Sarcasm</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.map((pred, idx) => (
                    <tr key={idx} className="result-row">
                      <td className="idx">{idx + 1}</td>
                      <td className="text">{pred.text?.substring(0, 50)}...</td>
                      <td className="sentiment">{pred.sentiment_label}</td>
                      <td className="sarcasm">{pred.sarcasm_label}</td>
                      <td className="confidence">
                        {(pred.overall_confidence * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="statistics">
              <div className="stat">
                <strong>Positive:</strong> {predictions.filter(p => p.sentiment_label === 'Positive').length}
              </div>
              <div className="stat">
                <strong>Neutral:</strong> {predictions.filter(p => p.sentiment_label === 'Neutral').length}
              </div>
              <div className="stat">
                <strong>Negative:</strong> {predictions.filter(p => p.sentiment_label === 'Negative').length}
              </div>
              <div className="stat">
                <strong>Sarcastic:</strong> {predictions.filter(p => p.sarcasm_label === 'Sarcastic').length}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchPredictPage;
