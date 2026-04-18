import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import "../styles/Header.css";

const Header = ({ isDarkMode, toggleTheme }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="header">
      <div className="header-container">

        {/* LOGO */}
        <div className="logo">
          <h1>🎭 Sarcasm Analyzer</h1>
          <span className="tagline">AI Review Intelligence</span>
        </div>

        {/* HAMBURGER */}
        <button className="hamburger" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
          <span className={`bar ${menuOpen ? 'open' : ''}`} />
          <span className={`bar ${menuOpen ? 'open' : ''}`} />
          <span className={`bar ${menuOpen ? 'open' : ''}`} />
        </button>

        {/* NAV */}
        <nav className={`navbar ${menuOpen ? "active" : ""}`}>
          <div className="nav-left">
            {/* Core */}
            <NavLink to="/" className="nav-link" onClick={closeMenu}>🏠 Home</NavLink>
            <NavLink to="/batch" className="nav-link" onClick={closeMenu}>📦 Batch</NavLink>
            <NavLink to="/compare" className="nav-link" onClick={closeMenu}>🔬 Compare</NavLink>

            {/* Analytics Group */}
            <div className="nav-dropdown">
              <span className="nav-link dropdown-trigger">📊 Analytics ▾</span>
              <div className="dropdown-menu">
                <NavLink to="/analytics" className="dropdown-item" onClick={closeMenu}>📊 Dashboard</NavLink>
                <NavLink to="/timeline" className="dropdown-item" onClick={closeMenu}>📈 Timeline</NavLink>
                <NavLink to="/history" className="dropdown-item" onClick={closeMenu}>📋 History</NavLink>
              </div>
            </div>

            {/* AI Tools Group */}
            <div className="nav-dropdown">
              <span className="nav-link dropdown-trigger">🤖 AI Tools ▾</span>
              <div className="dropdown-menu">
                <NavLink to="/emotions" className="dropdown-item" onClick={closeMenu}>💭 Emotions</NavLink>
                <NavLink to="/explain" className="dropdown-item" onClick={closeMenu}>🧠 XAI</NavLink>
                <NavLink to="/automl" className="dropdown-item" onClick={closeMenu}>⚙️ AutoML</NavLink>
              </div>
            </div>

            {/* Business Group */}
            <div className="nav-dropdown">
              <span className="nav-link dropdown-trigger">💼 Business ▾</span>
              <div className="dropdown-menu">
                <NavLink to="/business" className="dropdown-item" onClick={closeMenu}>📉 Dashboard</NavLink>
                <NavLink to="/social" className="dropdown-item" onClick={closeMenu}>📡 Social Media</NavLink>
              </div>
            </div>
          </div>

          <div className="nav-right">
            <button className="theme-toggle" onClick={toggleTheme}>
              {isDarkMode ? "☀️ Light" : "🌙 Dark"}
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Header;