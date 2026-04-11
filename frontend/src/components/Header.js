import React, { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import "../styles/Header.css";

const Header = ({ isDarkMode, toggleTheme, onLanguageChange }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  // Helper to close menu on mobile after clicking a link
  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="header">
      <div className="header-container">

        {/* LOGO */}
        <div className="logo">
          <h1>🎭 Sarcasm Analyzer</h1>
          <span>AI Review Intelligence</span>
        </div>

        {/* NAV */}
        <nav className={`navbar ${menuOpen ? "active" : ""}`}>

          <div className="nav-left">
            <NavLink to="/" className="nav-link" onClick={closeMenu}>Home</NavLink>
            <NavLink to="/history" className="nav-link" onClick={closeMenu}>History</NavLink>
            <NavLink to="/analytics" className="nav-link" onClick={closeMenu}>Analytics</NavLink>
            <NavLink to="/timeline" className="nav-link" onClick={closeMenu}>Timeline</NavLink>
            <NavLink to="/batch" className="nav-link" onClick={closeMenu}>Batch</NavLink>
            <NavLink to="/compare" className="nav-link" onClick={closeMenu}>Compare</NavLink>
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