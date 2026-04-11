/**
 * Error Alert Component
 */

import React from 'react';
import '../styles/ErrorAlert.css';

const ErrorAlert = ({ message, onClose }) => {
  if (!message) return null;

  return (
    <div className="error-alert">
      <div className="error-content">
        <span className="error-icon">⚠️</span>
        <span className="error-message">{message}</span>
        <button
          className="close-btn"
          onClick={onClose}
          aria-label="Close alert"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default ErrorAlert;
