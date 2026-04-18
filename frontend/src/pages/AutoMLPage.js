import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import '../styles/pages/AutoMLPage.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const MODEL_TYPES = [
  { id: 'logistic_regression', label: 'Logistic Regression', icon: '📊' },
  { id: 'svm', label: 'SVM', icon: '🔲' },
  { id: 'random_forest', label: 'Random Forest', icon: '🌲' },
  { id: 'naive_bayes', label: 'Naive Bayes', icon: '📐' },
  { id: 'gradient_boosting', label: 'Gradient Boosting', icon: '🚀' },
];

const AutoMLPage = () => {
  const [step, setStep] = useState(1); // 1=upload, 2=config, 3=training, 4=results
  const [dataset, setDataset] = useState([]);
  const [rawText, setRawText] = useState('');
  const [selectedModels, setSelectedModels] = useState(['logistic_regression', 'svm', 'random_forest']);
  const [task, setTask] = useState('sentiment');
  const [testSplit, setTestSplit] = useState(0.2);
  const [result, setResult] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { loadJobs(); }, []);

  const loadJobs = async () => {
    try {
      const res = await axios.get(`${API}/automl/jobs`);
      setJobs(res.data.jobs || []);
    } catch (e) { /* ignore */ }
  };

  const parseDataset = () => {
    const lines = rawText.split('\n').filter(l => l.trim());
    const parsed = lines.map(line => {
      const parts = line.split(/[,\t|]/).map(p => p.trim());
      if (parts.length >= 2) {
        return { text: parts[0], label: parts[1] };
      }
      return null;
    }).filter(Boolean);
    setDataset(parsed);
    if (parsed.length >= 10) {
      setStep(2);
    } else {
      setError(`Need at least 10 samples. Got ${parsed.length}. Format: text,label (one per line)`);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setRawText(ev.target.result);
    };
    reader.readAsText(file);
  };

  const toggleModel = (id) => {
    setSelectedModels(prev =>
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const startTraining = async () => {
    if (selectedModels.length === 0) { setError('Select at least one model'); return; }
    setLoading(true); setError(''); setStep(3);
    try {
      const res = await axios.post(`${API}/automl/train`, {
        dataset, model_types: selectedModels, task, test_split: testSplit
      });
      setResult(res.data);
      setStep(4);
      loadJobs();
    } catch (e) { setError(e.response?.data?.detail || 'Training failed'); setStep(2); }
    finally { setLoading(false); }
  };

  const metricColor = (val) => val >= 0.85 ? '#51CF66' : val >= 0.70 ? '#FFA94D' : '#FF6B6B';

  return (
    <div className="automl-page">
      <div className="container">
        <div className="page-header">
          <h1>🤖 Auto Model Trainer</h1>
          <p className="subtitle">Upload your dataset, auto-train models, and find the best one</p>
        </div>

        {error && <ErrorAlert message={error} onClose={() => setError('')} />}

        {/* Progress Steps */}
        <div className="step-progress">
          {['Upload Data', 'Configure', 'Training', 'Results'].map((label, i) => (
            <div key={i} className={`step-item ${step > i + 1 ? 'done' : ''} ${step === i + 1 ? 'active' : ''}`}>
              <div className="step-circle">{step > i + 1 ? '✓' : i + 1}</div>
              <span>{label}</span>
            </div>
          ))}
        </div>

        {/* Step 1: Upload */}
        {step === 1 && (
          <div className="step-content">
            <div className="upload-section">
              <h3>📁 Upload or Paste Your Dataset</h3>
              <p className="help-text">Format: <code>text,label</code> (one per line). Labels: positive/negative/neutral or 0/1</p>
              
              <div className="upload-options">
                <label className="file-upload-btn">
                  📎 Upload CSV/TXT
                  <input type="file" accept=".csv,.txt,.tsv" onChange={handleFileUpload} hidden />
                </label>
                <span>or paste below:</span>
              </div>

              <textarea
                className="dataset-textarea"
                placeholder={"I love this product, positive\nTerrible quality, negative\nIt's okay, neutral\n..."}
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                rows={10}
              />

              <div className="sample-data">
                <button className="sample-btn" onClick={() => setRawText(
`Great product love it, positive
Terrible waste of money, negative
It was okay nothing special, neutral
Amazing quality highly recommend, positive
Broke after one day, negative
Decent for the price, neutral
Best purchase ever made, positive
Worst experience of my life, negative
Pretty average overall, neutral
Absolutely fantastic service, positive
Complete garbage dont buy, negative
Fair enough I guess, neutral`
                )}>📋 Load Sample Data</button>
              </div>

              <button className="next-btn" onClick={parseDataset} disabled={!rawText.trim()}>
                Next: Configure →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Configure */}
        {step === 2 && (
          <div className="step-content">
            <div className="config-section">
              <div className="data-summary">
                <h3>✅ Dataset Loaded: {dataset.length} samples</h3>
                <div className="label-distribution">
                  {Object.entries(dataset.reduce((acc, d) => {
                    acc[d.label] = (acc[d.label] || 0) + 1;
                    return acc;
                  }, {})).map(([label, count]) => (
                    <span key={label} className="label-tag">{label}: {count}</span>
                  ))}
                </div>
              </div>

              <div className="config-group">
                <h3>🎯 Task</h3>
                <div className="task-toggle">
                  <button className={task === 'sentiment' ? 'active' : ''} onClick={() => setTask('sentiment')}>Sentiment Analysis</button>
                  <button className={task === 'sarcasm' ? 'active' : ''} onClick={() => setTask('sarcasm')}>Sarcasm Detection</button>
                </div>
              </div>

              <div className="config-group">
                <h3>🧠 Select Models</h3>
                <div className="model-selector">
                  {MODEL_TYPES.map(mt => (
                    <div
                      key={mt.id}
                      className={`model-chip ${selectedModels.includes(mt.id) ? 'selected' : ''}`}
                      onClick={() => toggleModel(mt.id)}
                    >
                      <span className="chip-icon">{mt.icon}</span>
                      <span>{mt.label}</span>
                      {selectedModels.includes(mt.id) && <span className="check">✓</span>}
                    </div>
                  ))}
                </div>
              </div>

              <div className="config-group">
                <h3>⚙️ Test Split: {(testSplit * 100).toFixed(0)}%</h3>
                <input
                  type="range" min="10" max="40" value={testSplit * 100}
                  onChange={(e) => setTestSplit(e.target.value / 100)}
                  className="split-slider"
                />
                <div className="split-info">
                  <span>Train: {Math.round(dataset.length * (1 - testSplit))}</span>
                  <span>Test: {Math.round(dataset.length * testSplit)}</span>
                </div>
              </div>

              <div className="config-actions">
                <button className="back-btn" onClick={() => setStep(1)}>← Back</button>
                <button className="train-btn" onClick={startTraining}>🚀 Start Training</button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Training */}
        {step === 3 && loading && (
          <div className="step-content training-step">
            <LoadingSpinner message="Training models... Comparing performance..." />
            <div className="training-models">
              {selectedModels.map(m => (
                <div key={m} className="training-model-card">
                  <span className="spinner-small" />
                  <span>{m.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Results */}
        {step === 4 && result && (
          <div className="step-content results-step">
            <div className="best-model-banner">
              <h2>🏆 Best Model: {result.best_model?.name?.replace(/_/g, ' ')}</h2>
              <div className="best-metrics">
                <span>Accuracy: <strong>{(result.best_model?.metrics?.accuracy * 100).toFixed(1)}%</strong></span>
                <span>F1 Score: <strong>{(result.best_model?.metrics?.f1_score * 100).toFixed(1)}%</strong></span>
                <span>Training Time: <strong>{result.best_model?.metrics?.training_time}s</strong></span>
              </div>
            </div>

            <div className="model-comparison-table">
              <h3>📊 Model Comparison</h3>
              <table>
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1 Score</th>
                    <th>Time</th>
                    <th>Winner</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(result.model_results || {}).sort(([,a],[,b]) => b.f1_score - a.f1_score).map(([name, metrics]) => (
                    <tr key={name} className={name === result.best_model?.name ? 'best-row' : ''}>
                      <td className="model-name">{name.replace(/_/g, ' ')}</td>
                      <td><span className="metric-val" style={{color: metricColor(metrics.accuracy)}}>{(metrics.accuracy * 100).toFixed(1)}%</span></td>
                      <td><span className="metric-val" style={{color: metricColor(metrics.precision)}}>{(metrics.precision * 100).toFixed(1)}%</span></td>
                      <td><span className="metric-val" style={{color: metricColor(metrics.recall)}}>{(metrics.recall * 100).toFixed(1)}%</span></td>
                      <td><span className="metric-val" style={{color: metricColor(metrics.f1_score)}}>{(metrics.f1_score * 100).toFixed(1)}%</span></td>
                      <td>{metrics.training_time}s</td>
                      <td>{name === result.best_model?.name ? '🏆' : ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="hyperparams-section">
              <h3>⚙️ Best Model Hyperparameters</h3>
              <div className="params-grid">
                {Object.entries(result.hyperparameters?.[result.best_model?.name] || {}).map(([k, v]) => (
                  <div key={k} className="param-item">
                    <span className="param-key">{k}</span>
                    <span className="param-val">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="result-actions">
              <button onClick={() => { setStep(1); setResult(null); setDataset([]); setRawText(''); }}>🔄 Train New Model</button>
            </div>
          </div>
        )}

        {/* Previous Jobs */}
        {jobs.length > 0 && (
          <div className="previous-jobs">
            <h3>📜 Previous Training Jobs</h3>
            <div className="jobs-list">
              {jobs.slice(0, 5).map(job => (
                <div key={job.job_id} className="job-card">
                  <span className="job-id">{job.job_id}</span>
                  <span className="job-task">{job.task}</span>
                  <span className="job-best">Best: {job.best_model?.name?.replace(/_/g, ' ')}</span>
                  <span className="job-acc">{(job.best_model?.metrics?.accuracy * 100).toFixed(1)}%</span>
                  <span className="job-samples">{job.n_samples} samples</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AutoMLPage;
